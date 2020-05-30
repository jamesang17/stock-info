import os
from dotenv import load_dotenv
load_dotenv()

NEWS_KEY = os.getenv("NEWS_API_KEY")
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")
GCP_BUCKET = os.getenv("GCP_BUCKET")
GOOGLE_APP_CREDS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
