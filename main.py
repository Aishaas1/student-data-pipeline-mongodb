from pathlib import Path
import time

from app.sources.csv_source import extract_csv
from app.sources.api_source import start_mock_api, extract_api
from app.sources.database_source import extract_database
from app.sources.mongodb_source import extract_mongodb
from app.sources.web_scraping_source import start_mock_web_source, extract_web_scraping
from app.transformation.cleaner import (
    clean_csv_data,
    clean_api_data,
    clean_database_data,
    clean_mongodb_data,
    clean_web_scraping_data,
)
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import (
    validate_csv_data,
    validate_api_data,
    validate_database_data,
    validate_mongodb_data,
    validate_web_scraping_data,
    validate_final_data,
)
from app.output.csv_writer import save_csv
from app.utils.logger import get_logger

BASE = Path(__file__).parent
CSV_PATH = BASE / "data" / "raw" / "students.csv"
API_DATA_PATH = BASE / "data" / "raw" / "api_data.json"
SQLITE_PATH = BASE / "database" / "students.db"
MONGO_SEED_PATH = BASE / "data" / "raw" / "mongodb_data.json"
WEB_SCRAPING_HTML_PATH = BASE / "data" / "raw" / "web_scraping_source.html"
FINAL_PATH = BASE / "data" / "processed" / "final_dataset.csv"
REJECTED_PATH = BASE / "data" / "rejected" / "rejected_records.csv"
LOG_PATH = BASE / "logs" / "pipeline.log"

def run_pipeline():
    started = time.perf_counter()
    logger = get_logger(LOG_PATH)

    logger.info("Pipeline started")

    csv_raw = extract_csv(CSV_PATH)
    logger.info("CSV records: %s", len(csv_raw))

    api_server, _ = start_mock_api(API_DATA_PATH)
    try:
        api_raw = extract_api(f"http://127.0.0.1:{api_server.server_port}")
    finally:
        api_server.shutdown()
        api_server.server_close()
    logger.info("API records: %s", len(api_raw))

    sqlite_raw = extract_database(SQLITE_PATH)
    logger.info("SQLite records: %s", len(sqlite_raw))

    mongo_raw = extract_mongodb(
        uri="mongodb://localhost:27017",
        database_name="student_pipeline",
        collection_name="student_profiles",
        seed_path=MONGO_SEED_PATH,
        use_mock=True,
    )
    logger.info("MongoDB records: %s", len(mongo_raw))

    web_server, _ = start_mock_web_source(WEB_SCRAPING_HTML_PATH)
    try:
        web_raw = extract_web_scraping(f"http://127.0.0.1:{web_server.server_port}")
    finally:
        web_server.shutdown()
        web_server.server_close()
    logger.info("Web Scraping records: %s", len(web_raw))

    csv_clean, csv_duplicates = clean_csv_data(csv_raw)
    api_clean = clean_api_data(api_raw)
    sqlite_clean = clean_database_data(sqlite_raw)
    mongo_clean = clean_mongodb_data(mongo_raw)
    web_clean = clean_web_scraping_data(web_raw)

    csv_valid, csv_rejected = validate_csv_data(csv_clean)
    api_valid, api_rejected = validate_api_data(api_clean)
    sqlite_valid, sqlite_rejected = validate_database_data(sqlite_clean)
    mongo_valid, mongo_rejected = validate_mongodb_data(mongo_clean)
    web_valid, web_rejected = validate_web_scraping_data(web_clean)

    integrated = integrate_data(
        csv_valid, api_valid, sqlite_valid, mongo_valid, web_valid
    )
    transformed = transform_data(integrated)
    final_valid, final_rejected = validate_final_data(transformed)

    rejected = (
        __import__("pandas").concat(
            [csv_rejected, api_rejected, sqlite_rejected, mongo_rejected, web_rejected, final_rejected],
            ignore_index=True,
        )
        .drop_duplicates()
    )

    save_csv(final_valid, FINAL_PATH)
    save_csv(rejected, REJECTED_PATH)

    elapsed = time.perf_counter() - started
    logger.info("CSV duplicates: %s", csv_duplicates)
    logger.info("Web Scraping records: %s", len(web_raw))
    logger.info("Integrated records: %s", len(integrated))
    logger.info("Valid records: %s", len(final_valid))
    logger.info("Rejected records: %s", len(rejected))
    logger.info("Processing time: %.2f seconds", elapsed)
    logger.info("Final dataset created")

    print("-----------------------------------")
    print("PIPELINE EXECUTION SUMMARY")
    print("-----------------------------------")
    print(f"CSV Records       : {len(csv_raw)}")
    print(f"API Records       : {len(api_raw)}")
    print(f"SQLite Records    : {len(sqlite_raw)}")
    print(f"MongoDB Records   : {len(mongo_raw)}")
    print(f"Web Scraping      : {len(web_raw)}")
    print(f"Integrated Records: {len(integrated)}")
    print(f"Valid Records     : {len(final_valid)}")
    print(f"Rejected Records  : {len(rejected)}")
    print(f"Duplicate Records : {csv_duplicates}")
    print(f"Processing Time   : {elapsed:.2f} seconds")
    print("-----------------------------------")

if __name__ == "__main__":
    run_pipeline()
