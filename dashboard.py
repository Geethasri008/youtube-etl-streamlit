import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

#load_dotenv()

# DB connection
conn = psycopg2.connect(
    host=st.secrets["host"],
    port=st.secrets["port"],
    dbname=st.secrets["dbname"],
    user=st.secrets["user"],
    password=st.secrets["password"]
)
cur = conn.cursor()

# Load channel data
def load_channels():
    cur.execute("SELECT * FROM channels")
    return pd.DataFrame(cur.fetchall(), columns=[
        "channel_id", "title", "description", "published_at",
        "subscriber_count", "view_count", "video_count"
    ])

# Load videos for a channel
def load_videos(channel_id):
    cur.execute("SELECT * FROM videos WHERE channel_id = %s", (channel_id,))
    rows = cur.fetchall()

    return pd.DataFrame(rows, columns=[
        "video_id", "channel_id", "title", "description",
        "published_at", "view_count", "like_count", "comment_count"
    ])


# Load comments for a video
def load_comments(video_id):
    cur.execute("""
        SELECT * FROM comments
        WHERE video_id = %s
    """, (video_id,))
    return pd.DataFrame(cur.fetchall(), columns=[
        "comment_id", "video_id", "author_display_name", "text_display", "published_at"
    ])

# 🎨 Streamlit UI
st.set_page_config(page_title="YouTube Dashboard", layout="wide")
st.title("📺 YouTube Channel Dashboard")

channels_df = load_channels()
st.write(channels_df)

channel_titles = channels_df["title"].dropna().unique()
selected_channel = st.selectbox("Select a Channel", channel_titles)

# Show Channel Info
matched_rows = channels_df[channels_df["title"] == selected_channel]

if not matched_rows.empty:
    channel_row = matched_rows.iloc[0]

    st.subheader(f"📌 {channel_row['title']}")
    st.write(channel_row["description"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Subscribers", channel_row["subscriber_count"])
    col2.metric("Total Views", channel_row["view_count"])
    col3.metric("Total Videos", channel_row["video_count"])

    st.markdown("---")

    # Load videos
    videos_df = load_videos(channel_row["channel_id"])

    if not videos_df.empty:
        st.write("🎥 All Videos:")
        st.dataframe(videos_df[["title", "published_at", "view_count", "like_count", "comment_count"]])

        st.subheader("🔥 Top 5 Videos by Views")
        top_videos = videos_df.sort_values(by="view_count", ascending=False).head(5)
        st.dataframe(top_videos[["title", "view_count", "like_count", "comment_count"]])

        # Select a video to view comments
        video_titles = videos_df["title"].tolist()
        selected_video_title = st.selectbox("🎯 Select a Video to View Comments", video_titles)

        selected_video_id = videos_df[videos_df["title"] == selected_video_title]["video_id"].values[0]
        comments_df = load_comments(selected_video_id)

        st.subheader("💬 Top Comments")
        if not comments_df.empty:
            st.dataframe(comments_df[["author_display_name", "text_display", "published_at"]])
        else:
            st.info("No comments found for this video.")

    else:
        st.info("No videos found for this channel.")
else:
    st.warning("⚠️ Selected channel not found in the database.")

cur.close()
conn.close()



