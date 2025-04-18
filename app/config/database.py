from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        mongodb_url = os.getenv("MONGO_URI")
        if not mongodb_url:
            raise ValueError("MONGODB_URL not set in .env")
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client["cricketVenueInsights"]
        print(
            f"Connected to MongoDB at {mongodb_url.split('@')[1] if '@' in mongodb_url else mongodb_url}"
        )

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")


db = MongoDB()
