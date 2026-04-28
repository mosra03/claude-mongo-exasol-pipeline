#!/usr/bin/env python3
"""
Ingest pipeline: MongoDB Atlas → NDJSON → Exasol RAW.SURVEY_DOCS
Then creates RECIPES schema with SCIENTIST and CHEF tables.

Usage:
    python3 scripts/ingest.py

Required env vars:
    MONGODB_URI      — full Atlas connection string
    EXASOL_HOST      — Exasol cluster hostname
    EXASOL_PORT      — Exasol port (default 8563)
    EXASOL_USER      — Exasol username
    EXASOL_PASSWORD  — Exasol password or PAT token
"""

import os
import subprocess
import sys
import pyexasol

NDJSON_PATH = "data/survey_raw.ndjson"


def step1_mongoexport():
    uri = os.environ["MONGODB_URI"]
    cmd = [
        "mongoexport",
        "--uri", uri,
        "--db", "stackoverflow",
        "--collection", "survey_2025",
        "--out", NDJSON_PATH,
    ]
    print(f"[1/3] Exporting MongoDB → {NDJSON_PATH} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("mongoexport failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"      Done. {result.stderr.strip()}")


def step2_ingest_exasol():
    host = os.environ["EXASOL_HOST"]
    port = os.environ.get("EXASOL_PORT", "8563")
    user = os.environ["EXASOL_USER"]
    password = os.environ["EXASOL_PASSWORD"]

    print(f"[2/3] Ingesting {NDJSON_PATH} → Exasol RAW.SURVEY_DOCS ...")
    cmd = [
        "exasol-json-tables",
        "ingest-and-wrap",
        "--host", host,
        "--port", port,
        "--user", user,
        "--password", password,
        "--schema", "RAW",
        "--table", "SURVEY_DOCS",
        "--file", NDJSON_PATH,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("exasol-json-tables failed:")
        print(result.stderr)
        sys.exit(1)
    print(f"      Done. {result.stdout.strip()}")


def step3_create_recipe_tables():
    host = os.environ["EXASOL_HOST"]
    port = int(os.environ.get("EXASOL_PORT", "8563"))
    user = os.environ["EXASOL_USER"]
    password = os.environ["EXASOL_PASSWORD"]

    print("[3/3] Creating RECIPES schema and tables in Exasol ...")

    conn = pyexasol.connect(
        dsn=f"{host}:{port}",
        user=user,
        password=password,
    )

    ddl = [
        "CREATE SCHEMA IF NOT EXISTS RECIPES",

        """CREATE OR REPLACE TABLE RECIPES.SCIENTIST (
            recipe_id       VARCHAR(50),
            agent_name      VARCHAR(50)      DEFAULT 'scientist',
            status          VARCHAR(20)      DEFAULT 'pending',
            created_at      TIMESTAMP,
            pattern_count   INT,
            payload         VARCHAR(2000000)
        )""",

        """CREATE OR REPLACE TABLE RECIPES.CHEF (
            recipe_id       VARCHAR(50),
            agent_name      VARCHAR(50)      DEFAULT 'chef',
            status          VARCHAR(20)      DEFAULT 'pending',
            created_at      TIMESTAMP,
            view_count      INT,
            payload         VARCHAR(2000000)
        )""",
    ]

    for stmt in ddl:
        conn.execute(stmt)
        print(f"      OK: {stmt[:60].strip()} ...")

    conn.close()
    print("      RECIPES.SCIENTIST and RECIPES.CHEF ready.")


if __name__ == "__main__":
    step1_mongoexport()
    step2_ingest_exasol()
    step3_create_recipe_tables()
    print("\nIngest complete. RAW.SURVEY_DOCS is live in Exasol.")
