import json
import csv
import os
import random

INPUT_JSON = "dataset/dataset.json"
OUTPUT_CSV = "dataset/features.csv"

def extract_features():
    if not os.path.exists(INPUT_JSON):
        print("❌ dataset.json not found.")
        return

    with open(INPUT_JSON, "r") as f:
        dataset = json.load(f)

    rows = []

    for entry in dataset:
        build_number = entry.get("build_number")
        issue_type = entry.get("issue_type")
        result = entry.get("result")

        # Simulate duration based on issue
        if issue_type == "delay":
            duration_sec = random.randint(100, 120)
        elif issue_type == "fail":
            duration_sec = random.randint(60, 90)
        else:
            duration_sec = random.randint(30, 50)

        # Feature: contains_secret
        contains_secret = 1 if issue_type == "secret" else 0

        # Feature: is_anomaly
        is_anomaly = 1 if duration_sec > 90 else 0

        # Target: result as 1 (failure), 0 (success)
        label = 1 if result == "failure" else 0

        rows.append([
            build_number,
            duration_sec,
            contains_secret,
            is_anomaly,
            label,
            issue_type  # optional for debugging
        ])

    # Save to CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["build_number", "duration_sec", "contains_secret", "is_anomaly", "result", "issue_type"])
        writer.writerows(rows)

    print(f"✅ Extracted {len(rows)} feature rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_features()
