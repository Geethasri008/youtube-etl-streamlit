import os
import logging
from datetime import datetime
import psycopg2
from googleapiclient.discovery import build
from dotenv import load_dotenv

# other imports like googleapiclient, pymongo, etc.

# 📁 Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# 📝 Set up logging to file
log_filename = f"logs/youtube_etl_log_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# Load environment variables
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

# PostgreSQL connection
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# Fetch channel info
def fetch_channel_info(channel_id):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    item = response['items'][0]
    return {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "published_at": item["snippet"]["publishedAt"],
        "subscriber_count": item["statistics"].get("subscriberCount", 0),
        "view_count": item["statistics"].get("viewCount", 0),
        "video_count": item["statistics"].get("videoCount", 0)
    }

# Fetch recent video IDs
def fetch_channel_videos(channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=5,
        order="date",
        type="video"
    )
    response = request.execute()
    videos = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        videos.append(fetch_video_details(video_id, channel_id))
    return videos

# Fetch video details
def fetch_video_details(video_id, channel_id):
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    item = response["items"][0]
    return {
        "video_id": video_id,
        "channel_id": channel_id,
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "published_at": item["snippet"]["publishedAt"],
        "view_count": item["statistics"].get("viewCount", 0),
        "like_count": item["statistics"].get("likeCount", 0),
        "comment_count": item["statistics"].get("commentCount", 0),
    }

# Fetch video comments
def fetch_video_comments(video_id):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=20,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id": item["id"],
                "video_id": video_id,
                "author_display_name": top_comment.get("authorDisplayName", "Anonymous"),
                "text_display": top_comment.get("textDisplay", ""),
                "published_at": top_comment.get("publishedAt")
            })
    except Exception as e:
        logging.warning(f"Could not fetch comments for video {video_id}: {e}")

    return comments

# Insert into channels table
def insert_channel(channel):
    cur.execute("""
        INSERT INTO channels (
            channel_id, title, description, published_at,
            subscriber_count, view_count, video_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (channel_id) DO UPDATE
        SET subscriber_count = EXCLUDED.subscriber_count,
            view_count = EXCLUDED.view_count,
            video_count = EXCLUDED.video_count
    """, (
        channel["channel_id"],
        channel["title"],
        channel["description"],
        channel["published_at"],
        channel["subscriber_count"],
        channel["view_count"],
        channel["video_count"]
    ))
    conn.commit()


# Insert into videos table
def insert_videos(videos):
    for video in videos:
        cur.execute("""
            INSERT INTO videos (video_id, channel_id, title, description, published_at, view_count, like_count, comment_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO NOTHING
        """, (
            video["video_id"],
            video["channel_id"],
            video["title"],
            video["description"],
            video["published_at"],
            video["view_count"],
            video["like_count"],
            video["comment_count"]
        ))
    conn.commit()

# Insert into comments table
def insert_comments(comments):
    for comment in comments:
        cur.execute("""
            INSERT INTO comments (comment_id, video_id, author_display_name, text_display, published_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (comment_id) DO NOTHING
        """, (
            comment["comment_id"],
            comment["video_id"],
            comment["author_display_name"],
            comment["text_display"],
            comment["published_at"]
        ))
    conn.commit()

# 🎯 Main execution
if __name__ == "__main__":
    try:
        channel_ids = [
            "UCYzEMRKqrh01-tauv7MYyVQ",
            "UCsXVk37bltHxD1rDPwtNM8Q",
            "UCAuUUnT6oDeKwE6v1NGQxug",
            "UCHnyfMqiRRG1u-2MsSQLbXA",
            "UCX6b17PVsYBQ0ip5gyeme-Q",
            "UC8butISFwT-Wl7EV0hUK0BQ",
            "UCJr72fY4cTaNZv7WPbvjaSw",
            "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "UC295-Dw_tDNtZXFeAPAW6Aw",
            "UC29ju8bIPH5as8OGnQzwJyA"
        ]

        for channel_id in channel_ids:
            logging.info(f"Fetching data for channel: {channel_id}")

            try:
                channel_data = fetch_channel_info(channel_id)
                insert_channel(channel_data)

                video_data = fetch_channel_videos(channel_id)
                insert_videos(video_data)

                for video in video_data:
                    comments = fetch_video_comments(video["video_id"])
                    insert_comments(comments)

                logging.info(f"Data inserted for channel: {channel_id}")
            
            except Exception as e:
                logging.error(f"Failed to process channel {channel_id}: {e}")

        logging.info("All channels processed successfully!")

    except Exception as e:
        logging.critical(f"ETL pipeline failed unexpectedly: {e}")

    finally:
        cur.close()
        conn.close()
        logging.info("Database connection closed.")
