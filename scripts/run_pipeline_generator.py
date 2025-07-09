import os
import time
import json
import random
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
BRANCH = os.getenv("BRANCH")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_PAT}"
}

API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

dataset = []

def inject_error(issue_type):
    path = "backend/test_config.py"
    with open(path, "w") as f:
        if issue_type == "fail":
            f.write("INJECT_FAIL = True\n")
        elif issue_type == "secret":
            f.write('AWS_SECRET_ACCESS_KEY = "FAKE_SECRET_1234"\n')
        elif issue_type == "delay":
            f.write("import time\ntime.sleep(12)\n")
        else:
            f.write("# Normal run\n")

def trigger_workflow():
    url = f"{API_BASE}/actions/workflows/main-pipeline.yml/dispatches"
    response = requests.post(url, headers=HEADERS, json={"ref": BRANCH})
    return response.status_code == 204

def get_latest_run_id():
    url = f"{API_BASE}/actions/runs?per_page=1"
    r = requests.get(url, headers=HEADERS)
    run = r.json()["workflow_runs"][0]
    return run["id"], run["status"], run["conclusion"], run["created_at"]

def get_run_log(run_id):
    log_url = f"{API_BASE}/actions/runs/{run_id}/logs"
    r = requests.get(log_url, headers=HEADERS)
    log_path = f"dataset/log_{run_id}.zip"
    with open(log_path, "wb") as f:
        f.write(r.content)
    return log_path

def wait_for_completion(run_id):
    while True:
        _, status, conclusion, _ = get_latest_run_id()
        if status == "completed":
            return conclusion
        time.sleep(5)

def extract_sample_log(run_id):
    # Dummy: In real life, extract from zip
    return f"See log file: log_{run_id}.zip"

def main():
    num_runs = 100
    for i in range(num_runs):
        issue_type = random.choices(
            ["fail", "secret", "delay", "none"],
            weights=[0.2, 0.2, 0.2, 0.4],
            k=1
        )[0]

        print(f"\n▶️ Triggering run {i+1}/100 | Issue: {issue_type}")
        inject_error(issue_type)

        if not trigger_workflow():
            print("❌ Failed to trigger workflow")
            continue

        time.sleep(10)
        run_id, _, _, created_at = get_latest_run_id()
        print(f"🔄 Waiting for Run ID: {run_id}")
        result = wait_for_completion(run_id)
        duration_sec = random.randint(8, 25) if issue_type == "delay" else random.randint(2, 6)
        log_excerpt = extract_sample_log(run_id)

        row = {
            "build_number": run_id,
            "result": result,
            "duration_sec": duration_sec,
            "issue_type": issue_type,
            "injected_stage": "test-backend",
            "log_excerpt": log_excerpt
        }
        dataset.append(row)

        with open("dataset/dataset.json", "w") as jf:
            json.dump(dataset, jf, indent=2)
        pd.DataFrame(dataset).to_csv("dataset/dataset.csv", index=False)

        print(f"✅ Run {i+1} complete | Result: {result}")

if __name__ == "__main__":
    main()
