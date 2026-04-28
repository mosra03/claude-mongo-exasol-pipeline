#!/usr/bin/env python3
"""
Export from MongoDB → load into Exasol.

Usage:
  python3 scripts/ingest_exasol.py
  python3 scripts/ingest_exasol.py --collection my_events --db mydb

Required env vars: EXASOL_HOST, EXASOL_USER, EXASOL_PASSWORD, MONGODB_URI
Optional env vars: EXASOL_PORT (default 8563)
"""

import argparse
import json
import os
import ssl
import subprocess
import sys
import time

NDJSON_PATH = "data/survey_raw.ndjson"


def main():
    # Step 1: Venv check
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        print("ERROR: Not in a virtual environment. Activate your venv first:")
        print("  source venv/bin/activate")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Export from MongoDB and load into Exasol')
    parser.add_argument('--db', default='stackoverflow', help='MongoDB database (default: stackoverflow)')
    parser.add_argument('--collection', default='survey_2025', help='MongoDB collection (default: survey_2025)')
    args = parser.parse_args()

    # Step 2: Check env vars
    required = ['EXASOL_HOST', 'EXASOL_USER', 'EXASOL_PASSWORD', 'MONGODB_URI']
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        for v in missing:
            print(f"ERROR: {v} is not set")
        sys.exit(1)

    host = os.environ['EXASOL_HOST']
    user = os.environ['EXASOL_USER']
    password = os.environ['EXASOL_PASSWORD']
    uri = os.environ['MONGODB_URI']
    port = os.environ.get('EXASOL_PORT', '8563')

    start = time.time()

    # Step 3: Test Exasol connection
    import pyexasol
    try:
        conn = pyexasol.connect(
            dsn=f"{os.environ['EXASOL_HOST']}:{os.environ.get('EXASOL_PORT', '8563')}",
            user=os.environ['EXASOL_USER'],
            password=os.environ['EXASOL_PASSWORD'],
            websocket_sslopt={"cert_reqs": ssl.CERT_NONE}
        )
        print(f"✓ Connected to Exasol: {host}")
    except Exception as e:
        print("ERROR: Cannot connect to Exasol. Is the cluster running at cloud.exasol.com?")
        print(f"  {e}")
        sys.exit(1)

    # Step 4: Test MongoDB connection
    import pymongo
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        mongo_count = client[args.db][args.collection].count_documents({})
        client.close()
        print(f"✓ Connected to MongoDB: {args.collection} — {mongo_count} documents")
    except Exception as e:
        print("ERROR: Cannot connect to MongoDB. Check IP at MongoDB Atlas → Security → Network Access")
        print(f"  {e}")
        sys.exit(1)

    # Step 5: Export from MongoDB using mongoexport
    os.makedirs("data", exist_ok=True)
    print(f"\nStep 1 — Exporting {args.db}.{args.collection} → {NDJSON_PATH} ...")
    cmd = [
        'mongoexport',
        '--uri', uri,
        '--db', args.db,
        '--collection', args.collection,
        '--out', NDJSON_PATH,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("mongoexport failed:")
        print(result.stderr)
        sys.exit(1)

    with open(NDJSON_PATH) as f:
        exported_count = sum(1 for _ in f)
    print(f"✓ Exported {exported_count} documents to {NDJSON_PATH}")

    # Step 6: Validate NDJSON — auto-convert if JSON array
    with open(NDJSON_PATH, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()

    print(f"\nStep 2 — Validating NDJSON format ...")
    if first_line.startswith('['):
        with open(NDJSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(NDJSON_PATH, 'w', encoding='utf-8') as f:
            for obj in data:
                f.write(json.dumps(obj) + '\n')
        print("✓ Converted JSON array to NDJSON")
    else:
        print("✓ NDJSON format confirmed")

    # Step 7: Run exasol-json-tables ingest-and-wrap (stream output)
    print(f"\nStep 3 — Loading {NDJSON_PATH} → RAW.SURVEY_DOCS ...")
    cmd = [
        'exasol-json-tables', 'ingest-and-wrap',
        '--input', NDJSON_PATH,
        '--table', 'RAW.SURVEY_DOCS',
        '--dsn', f"{host}:{port}",
        '--user', user,
        '--password', password,
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line, end='', flush=True)
    proc.wait()
    if proc.returncode != 0:
        print("exasol-json-tables failed")
        sys.exit(1)
    print("✓ RAW.SURVEY_DOCS created in Exasol")

    # Step 8: Verify row count
    print(f"\nStep 4 — Verifying row count ...")
    row = conn.execute("SELECT COUNT(*) FROM RAW.SURVEY_DOCS").fetchone()
    exasol_count = row[0]
    print(f"✓ Verified: {exasol_count} rows in RAW.SURVEY_DOCS")

    # Step 9: Create RECIPES and ANALYTICS schemas
    print(f"\nStep 5 — Creating RECIPES and ANALYTICS schemas ...")

    conn.execute("CREATE SCHEMA IF NOT EXISTS RECIPES")

    conn.execute("""CREATE TABLE IF NOT EXISTS RECIPES.SCIENTIST (
        recipe_id     VARCHAR(50),
        agent_name    VARCHAR(50)   DEFAULT 'scientist',
        status        VARCHAR(20)   DEFAULT 'pending',
        created_at    TIMESTAMP,
        pattern_count INT,
        payload       VARCHAR(1000000)
    )""")
    print("✓ RECIPES.SCIENTIST ready")

    conn.execute("""CREATE TABLE IF NOT EXISTS RECIPES.CHEF (
        recipe_id  VARCHAR(50),
        agent_name VARCHAR(50)  DEFAULT 'chef',
        status     VARCHAR(20)  DEFAULT 'pending',
        created_at TIMESTAMP,
        view_count INT,
        payload    VARCHAR(1000000)
    )""")
    print("✓ RECIPES.CHEF ready")

    conn.execute("CREATE SCHEMA IF NOT EXISTS ANALYTICS")
    print("✓ ANALYTICS schema ready")

    conn.close()

    elapsed = time.time() - start

    # Step 10: Final summary
    print(f"""
════════════════════════════════
Ingest complete
════════════════════════════════
MongoDB collection : {args.db}.{args.collection}
Rows exported      : {exported_count}
Rows in Exasol     : {exasol_count}
Schemas ready      : RAW, RECIPES, ANALYTICS
Next step          : Open Claude Code → Run full pipeline
════════════════════════════════""")

    # Step 11: Time taken
    print(f"Time taken: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
