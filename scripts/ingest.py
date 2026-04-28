#!/usr/bin/env python3
"""
Ingest pipeline: MongoDB Atlas → NDJSON → Exasol RAW_WRAPPER."survey_raw"
Then creates RECIPES schema with SCIENTIST and CHEF tables.

Usage:
    python3 scripts/ingest.py

Required env vars:
    MONGODB_URI      — full Atlas connection string
    EXASOL_HOST      — Exasol cluster hostname
    EXASOL_USER      — Exasol username
    EXASOL_PASSWORD  — Exasol password or PAT token
Optional env vars:
    EXASOL_PORT      — Exasol port (default 8563)
"""

import json
import os
import ssl
import subprocess
import sys
import pyexasol

NDJSON_PATH = "data/survey_raw.ndjson"


def check_env():
    required = ['MONGODB_URI', 'EXASOL_HOST', 'EXASOL_USER', 'EXASOL_PASSWORD']
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        for v in missing:
            print(f"ERROR: {v} is not set")
        sys.exit(1)


def step1_mongoexport():
    uri = os.environ["MONGODB_URI"]
    os.makedirs("data", exist_ok=True)
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

    # Creates RAW."survey_raw" (source) and RAW_WRAPPER."survey_raw" (wrapped, queryable).
    # If this step fails, re-run manually with the same flags; do not change --name or schemas.
    print(f'[2/3] Ingesting {NDJSON_PATH} → RAW_WRAPPER."survey_raw" ...')
    cmd = [
        "exasol-json-tables", "ingest-and-wrap",
        "--input", NDJSON_PATH,
        "--dsn", f"{host}:{port}",
        "--user", user,
        "--password", password,
        "--name", "survey_docs",
        "--source-schema", "RAW",
        "--wrapper-schema", "RAW_WRAPPER",
        "--tls",
        "--exasol-cleanup",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print("     ", line, end='', flush=True)
    proc.wait()
    if proc.returncode != 0:
        print("exasol-json-tables failed")
        sys.exit(1)
    print('      Done.')


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
        websocket_sslopt={"cert_reqs": ssl.CERT_NONE},
    )

    ddl = [
        "CREATE SCHEMA IF NOT EXISTS RECIPES",

        """CREATE TABLE IF NOT EXISTS RECIPES.SCIENTIST (
            recipe_id       VARCHAR(50),
            agent_name      VARCHAR(50)      DEFAULT 'scientist',
            status          VARCHAR(20)      DEFAULT 'pending',
            created_at      TIMESTAMP,
            pattern_count   INT,
            payload         VARCHAR(1000000)
        )""",

        """CREATE TABLE IF NOT EXISTS RECIPES.CHEF (
            recipe_id       VARCHAR(50),
            agent_name      VARCHAR(50)      DEFAULT 'chef',
            status          VARCHAR(20)      DEFAULT 'pending',
            created_at      TIMESTAMP,
            view_count      INT,
            payload         VARCHAR(1000000)
        )""",

        "CREATE SCHEMA IF NOT EXISTS ANALYTICS",
    ]

    for stmt in ddl:
        conn.execute(stmt)
        print(f"      OK: {stmt[:60].strip()} ...")

    conn.close()
    print("      RECIPES.SCIENTIST, RECIPES.CHEF, and ANALYTICS schema ready.")


if __name__ == "__main__":
    check_env()
    step1_mongoexport()
    step2_ingest_exasol()
    step3_create_recipe_tables()
    print('\nIngest complete. RAW_WRAPPER."survey_raw" is live in Exasol.')
