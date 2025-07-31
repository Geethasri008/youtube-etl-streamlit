# 📊 YouTube ETL Pipeline with Comments, PostgreSQL & Task Scheduler

A complete end-to-end ETL (Extract, Transform, Load) project that fetches YouTube channel data using the YouTube Data API v3, stores it in PostgreSQL, and runs automatically every day using Windows Task Scheduler.

---

## 🚀 Features

- ✅ Fetches channel details, videos, and top-level comments  
- ✅ Stores data in PostgreSQL database  
- ✅ Logs daily ETL activity with timestamps  
- ✅ Scheduled to run daily via `.bat` file and Task Scheduler  
- ✅ Modular, clean code with environment variable support  

---

## 📁 Project Structure

youtube_etl_project/
│── dashboard.py
├── fetch_youtube_data.py # Main ETL script
├── requirements.txt # Dependencies
├── .env # API keys & DB credentials
├── run_etl.bat # Batch file to trigger ETL
├── logs/ # Stores daily log files
│ └── youtube_etl_log_YYYY-MM-DD.log
└── README.md # Project documentation


---

## 🧪 Technologies Used

- Python 3.8+  
- YouTube Data API v3  
- PostgreSQL  
- psycopg2  
- python-dotenv  
- Google API Client  
- Windows Task Scheduler  

---

## 🔐 .env Configuration

Create a `.env` file in the root directory:

YOUTUBE_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password


---

## 🛠️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/youtube-etl-project.git
   cd youtube-etl-project
Create virtual environment & install dependencies

pip install -r requirements.txt
Set up PostgreSQL tables

Ensure your database has these tables:

channels

videos

comments

Add your .env file

Run the script manually to test

python fetch_youtube_data.py
🖥️ Automating with Task Scheduler
Create a run_etl.bat file:


cd /d "C:\Users\geeth\OneDrive\Desktop\youtube_etl_project"
C:\Users\geeth\AppData\Local\Programs\Python\Python38\python.exe fetch_youtube_data.py


Open Task Scheduler > Create Basic Task

Set:

Trigger: Daily

Action: Start a program → Select run_etl.bat



🧾 Sample Log Output
2025-07-31 10:00:00 [INFO] 📺 Fetching data for channel: UCX6b17PVsYBQ0ip5gyeme-Q
2025-07-31 10:00:03 [INFO] ✅ Channel data inserted
2025-07-31 10:00:07 [INFO] ✅ Video data inserted
2025-07-31 10:00:12 [INFO] ✅ Comments inserted
2025-07-31 10:00:12 [INFO] ✅ All data inserted successfully including comments!

🧠 Learning Outcomes
Practical usage of YouTube Data API

Writing ETL pipelines in Python

Working with relational databases (PostgreSQL)

Automating tasks on Windows

Implementing logging for production readiness

## 🧑‍💻 Author

**Geetha Sri**  
B.Tech Graduate in CSE (AI & ML) | Aspiring Data Engineer  
[LinkedIn](https://www.linkedin.com/in/geetha-sri-chekka/) • [GitHub](https://github.com/Geethasri008)
