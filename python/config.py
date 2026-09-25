from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# DATA DIRECTORIES
# ============================================================

DATA_DIR = BASE_DIR / "data"

SAMPLE_DIR = DATA_DIR / "sample"

SALES_DIR = SAMPLE_DIR / "sales_clean"

MASTER_DATA_DIR = SAMPLE_DIR / "master_data"

TARGETS_DIR = SAMPLE_DIR / "targets"

DATA_QUALITY_DIR = SAMPLE_DIR / "data_quality_tests"


# ============================================================
# PIPELINE DIRECTORIES
# ============================================================

LANDING_DIR = DATA_DIR / "landing"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"

REJECTED_DIR = DATA_DIR / "rejected"

ARCHIVE_DIR = DATA_DIR / "archive"


# ============================================================
# LOGS
# ============================================================

LOGS_DIR = BASE_DIR / "logs"


# ============================================================
# DATABASE
# ============================================================

DATABASE_DIR = BASE_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "data_pipeline_360.db"
