from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")


class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client.get_database("cricketVenueInsights")
        print("Connected to MongoDB")

    async def disconnect(self):
        self.client.close()
        print("Disconnected from MongoDB")


db = Database()
