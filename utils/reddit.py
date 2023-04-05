import os

import asyncpraw
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET_ID")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")

def create_reddit_object(self):
    reddit = asyncpraw.Reddit(client_id = CLIENT_ID,
                              client_secret = CLIENT_SECRET,
                              user_agent = USER_AGENT,
                              user_name = USERNAME,
                              password = PASSWORD)
    
    return reddit