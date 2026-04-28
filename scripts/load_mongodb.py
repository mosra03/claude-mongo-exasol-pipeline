#!/usr/bin/env python3
"""
Load a file into MongoDB.

Usage:
  python3 scripts/load_mongodb.py --file /path/to/data.csv
  python3 scripts/load_mongodb.py --file /path/to/data.json --collection my_events
  python3 scripts/load_mongodb.py --file /path/to/data.json --no-drop  # append
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time

DATA_DIR = "data"
TMP_NDJSON = os.path.join(DATA_DIR, "tmp_import.ndjson")


def csv_to_ndjson(input_file, tmp_path):
    os.makedirs(DATA_DIR, exist_ok=True)
    csv.field_size_limit(10000000)
    count = 0
    with open(input_file, 'r', encoding='utf-8') as csvf, \
         open(tmp_path, 'w', encoding='utf-8') as jsonf:
        reader = csv.DictReader(csvf)
        for row in reader:
            jsonf.write(json.dumps(row) + '\n')
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description='Load a file into MongoDB')
    parser.add_argument('--file', required=True, help='Path to input file (.csv or .json/.ndjson)')
    parser.add_argument('--collection', default='survey_2025', help='MongoDB collection (default: survey_2025)')
    parser.add_argument('--db', default='stackoverflow', help='MongoDB database (default: stackoverflow)')
    parser.add_argument('--no-drop', action='store_true', dest='no_drop', help='Append instead of replacing the collection')
    args = parser.parse_args()

    start = time.time()

    # Step 1: Validate file exists
    input_file = os.path.expanduser(args.file)
    if not os.path.exists(input_file):
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)

    uri = os.environ.get('MONGODB_URI')
    if not uri:
        print("ERROR: MONGODB_URI environment variable is not set")
        sys.exit(1)

    # Step 2: If CSV, convert to NDJSON
    ext = os.path.splitext(input_file)[1].lower()
    json_array = False
    if ext == '.csv':
        print(f"Converting {input_file} → {TMP_NDJSON} ...")
        row_count = csv_to_ndjson(input_file, TMP_NDJSON)
        import_file = TMP_NDJSON
        print(f"  Converted {row_count} rows to NDJSON")
    else:
        import_file = input_file
        with open(import_file, 'r', encoding='utf-8') as f:
            first_char = f.read(1).strip()
        json_array = (first_char == '[')

    # Step 3: Test MongoDB connection
    try:
        import pymongo
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        client.close()
    except Exception as e:
        print("ERROR: Cannot connect. Check IP at MongoDB Atlas → Security → Network Access")
        print(f"  {e}")
        sys.exit(1)

    # Step 4: Run mongoimport with --drop (unless --no-drop)
    cmd = [
        'mongoimport',
        '--uri', uri,
        '--db', args.db,
        '--collection', args.collection,
        '--file', import_file,
    ]
    if not args.no_drop:
        cmd.append('--drop')
    if json_array:
        cmd.append('--jsonArray')

    print(f"Importing {import_file} → {args.db}.{args.collection} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("mongoimport failed:")
        print(result.stderr)
        sys.exit(1)

    # Step 5: Verify with pymongo count_documents
    client = pymongo.MongoClient(uri)
    count = client[args.db][args.collection].count_documents({})
    client.close()

    elapsed = time.time() - start

    # Step 6 & 7: Print result and time
    print(f"✓ Loaded {count} documents into {args.db}.{args.collection}")
    print(f"  Time taken: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
