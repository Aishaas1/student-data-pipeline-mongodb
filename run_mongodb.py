from pathlib import Path
import json

from pymongo import MongoClient

BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "raw" / "mongodb_data.json"

def seed_mongodb():
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client["student_pipeline"]
    collection = database["student_profiles"]
    collection.delete_many({})
    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    collection.insert_many(records)
    print(f"Inserted {len(records)} MongoDB documents.")
    client.close()

if __name__ == "__main__":
    seed_mongodb()
