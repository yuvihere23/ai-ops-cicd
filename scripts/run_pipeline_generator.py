# import requests
# import time
# import random
# import json
# import subprocess
# import os
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# # GitHub config
# REPO_OWNER = "yuvihere23"
# REPO_NAME = "ai-ops-cicd"
# BRANCH = "main"
# WORKFLOW_FILE_NAME = "main-pipeline.yml"

# # GitHub Token
# GITHUB_TOKEN = os.getenv("GITHUB_PAT")

# # Output paths
# DATASET_FILE = "dataset/dataset.json"
# os.makedirs("dataset", exist_ok=True)

# HEADERS = {
#     "Authorization": f"Bearer {GITHUB_TOKEN}",
#     "Accept": "application/vnd.github+json"
# }


# def inject_code(issue_type):
#     """Injects code into backend/test_config.py based on issue type"""
#     with open("backend/test_config.py", "w") as f:
#         if issue_type == "fail":
#             f.write("# INJECT_FAIL\n")
#         elif issue_type == "secret":
#             f.write('AWS_SECRET_ACCESS_KEY = "AKIAEXAMPLE"\n')
#         elif issue_type == "delay":
#             f.write("import time\n")
#             f.write("time.sleep(5)\n")
#         else:
#             f.write("# clean run\n")
#     print(f"🔧 Injected issue: {issue_type}")

#     # Stage the file
#     subprocess.run(["git", "add", "backend/test_config.py"], check=True)

#     # Commit if there are changes
#     commit_result = subprocess.run(
#         ["git", "commit", "-m", f"Inject issue: {issue_type}"],
#         capture_output=True,
#         text=True
#     )

#     if commit_result.returncode != 0:
#         if "nothing to commit" in commit_result.stderr.lower():
#             print("⚠️ No changes to commit. Skipping commit step.")
#         else:
#             print("❌ Git commit failed:", commit_result.stderr)
#             exit(1)
#     else:
#         print("✅ Commit created.")

#     # Push to remote
#     subprocess.run(["git", "push", "origin", BRANCH], check=True)
#     print("🚀 Code pushed to remote.")



# def trigger_workflow():
#     """Triggers the GitHub Actions workflow manually"""
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE_NAME}/dispatches"
#     payload = {"ref": BRANCH}
#     response = requests.post(url, headers=HEADERS, json=payload)
#     if response.status_code == 204:
#         print("✅ Workflow triggered successfully.")
#     else:
#         print("❌ Failed to trigger workflow:", response.text)
#         exit(1)


# def get_latest_run_id():
#     """Get latest workflow run ID"""
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
#     response = requests.get(url, headers=HEADERS)
#     response.raise_for_status()
#     runs = response.json()["workflow_runs"]
#     if not runs:
#         raise Exception("No workflow runs found.")
#     return runs[0]["id"]


# def wait_for_completion(run_id):
#     """Waits until the triggered workflow run is completed"""
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
#     status = "in_progress"
#     while status in ["queued", "in_progress"]:
#         response = requests.get(url, headers=HEADERS)
#         response.raise_for_status()
#         status = response.json()["status"]
#         conclusion = response.json().get("conclusion")
#         print("⏳ Waiting for workflow to complete...")
#         time.sleep(5)
#     print(f"🎯 Run complete | Result: {conclusion}")
#     return conclusion


# def get_run_logs(run_id):
#     """Downloads logs for the run"""
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/logs"
#     response = requests.get(url, headers=HEADERS)
#     if response.status_code != 200:
#         print("⚠️ Could not fetch logs.")
#         return ""
#     log_path = f"dataset/log_{run_id}.zip"
#     with open(log_path, "wb") as f:
#         f.write(response.content)
#     return log_path


# def save_to_dataset(build_number, result, duration, issue_type, injected_stage, log_excerpt):
#     entry = {
#         "build_number": build_number,
#         "result": result,
#         "duration_sec": duration,
#         "issue_type": issue_type,
#         "injected_stage": injected_stage,
#         "log_excerpt": log_excerpt
#     }

#     data = []
#     if os.path.exists(DATASET_FILE):
#         with open(DATASET_FILE, "r") as f:
#             try:
#                 data = json.load(f)
#             except json.JSONDecodeError:
#                 data = []

#     data.append(entry)

#     with open(DATASET_FILE, "w") as jf:
#         json.dump(data, jf, indent=2)
#     print("📦 Saved run to dataset.\n")


# def main():
#     total_runs = 100
#     issue_types = ["fail", "secret", "delay", "none"]
#     injected_stage = "test-backend"

#     for run_number in range(1, total_runs + 1):
#         issue_type = random.choices(issue_types, weights=[0.25, 0.25, 0.25, 0.25])[0]
#         print(f"▶️ Triggering run {run_number}/{total_runs} | Issue: {issue_type}")

#         inject_code(issue_type)
#         trigger_workflow()

#         time.sleep(10)
#         run_id = get_latest_run_id()
#         print(f"🔄 Waiting for Run ID: {run_id}")

#         start_time = time.time()
#         result = wait_for_completion(run_id)
#         end_time = time.time()

#         duration = round(end_time - start_time, 2)
#         log_excerpt = f"{issue_type} run"  # Placeholder, can improve later

#         save_to_dataset(run_number, result, duration, issue_type, injected_stage, log_excerpt)


# if __name__ == "__main__":
#     main()

import os
import json
import random
import subprocess
import time
import requests
from dotenv import load_dotenv
load_dotenv()

GITHUB_REPO = "yuvihere23/ai-ops-cicd"
WORKFLOW_FILE_NAME = "main-pipeline.yml"
DATASET_PATH = "dataset/dataset.json"
ISSUE_TYPES = ["none", "fail", "secret", "delay"]
INJECTION_FILE = "backend/test_config.py"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ.get('GITHUB_PAT')}"
}


def reset_injection():
    with open(INJECTION_FILE, "r") as f:
        lines = f.readlines()
    with open(INJECTION_FILE, "w") as f:
        for line in lines:
            if not any(x in line for x in ["INJECT_FAIL", "AWS_SECRET_ACCESS_KEY", "time.sleep(10)"]):
                f.write(line)


def inject_code(issue_type):
    reset_injection()
    with open(INJECTION_FILE, "a") as f:
        if issue_type == "fail":
            f.write(f"\n# INJECT_FAIL {random.randint(1000,9999)}\n")
        elif issue_type == "secret":
            f.write(f"\nAWS_SECRET_ACCESS_KEY=\"{random.randint(100000,999999)}XYZ\"\n")
        elif issue_type == "delay":
            f.write("\nimport time\ntime.sleep(10)  # delay injected\n")


def get_latest_run_id():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    runs = response.json()["workflow_runs"]
    return runs[0]["id"] if runs else None


def get_run_status(run_id):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["conclusion"]


def trigger_workflow():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE_NAME}/dispatches"
    response = requests.post(url, headers=HEADERS, json={"ref": "main"})
    response.raise_for_status()


def append_to_dataset(record):
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, "r") as f:
            dataset = json.load(f)
    else:
        dataset = []
    dataset.append(record)
    with open(DATASET_PATH, "w") as f:
        json.dump(dataset, f, indent=2)


# def main():
#     for i in range(1, 101):
#         issue_type = random.choice(ISSUE_TYPES)
#         print(f"\n▶️ Triggering run {i}/100 | Issue: {issue_type}")

#         inject_code(issue_type)
#         print(f"🔧 Injected issue: {issue_type}")

#         try:
#             subprocess.run(["git", "add", INJECTION_FILE], check=True)
#             subprocess.run(["git", "commit", "-m", f"Inject issue: {issue_type}"], check=True)
#             print("✅ Commit created.")
#         except subprocess.CalledProcessError:
#             print("❌ Git commit failed (probably no changes). Skipping run.\n")
#             continue

#         subprocess.run(["git", "push"], check=True)
#         print("🚀 Code pushed to remote.")

#         trigger_workflow()
#         print("✅ Workflow triggered successfully.")

#         run_id = None
#         for _ in range(10):
#             time.sleep(3)
#             run_id = get_latest_run_id()
#             if run_id:
#                 break
#         if not run_id:
#             print("❌ Failed to retrieve run ID.")
#             continue

#         print(f"🔄 Waiting for Run ID: {run_id}")
#         for _ in range(20):
#             time.sleep(6)
#             result = get_run_status(run_id)
#             if result in ["success", "failure"]:
#                 break
#         else:
#             result = "unknown"

#         print(f"🎯 Run complete | Result: {result}")

#         append_to_dataset({
#             "build_number": i,
#             "result": result,
#             "issue_type": issue_type,
#             "run_id": run_id
#         })
#         print("📦 Saved run to dataset.")
def main():
    issue_pool = (["delay"] * 20) + (["none"] * 30)
    random.shuffle(issue_pool)

    # Load existing dataset to get the correct starting build number
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, "r") as f:
            dataset = json.load(f)
        existing_numbers = [entry.get("build_number", 0) for entry in dataset]
        start_number = max(existing_numbers) + 1
    else:
        dataset = []
        start_number = 1

    for i, issue_type in enumerate(issue_pool, start=start_number):
        print(f"\n▶️ Triggering run {i} | Issue: {issue_type}")

        inject_code(issue_type)
        print(f"🔧 Injected issue: {issue_type}")

        try:
            subprocess.run(["git", "add", INJECTION_FILE], check=True)
            subprocess.run(["git", "commit", "-m", f"Inject issue: {issue_type}"], check=True)
            print("✅ Commit created.")
        except subprocess.CalledProcessError:
            print("⚠️ No changes to commit — skipping.")
            continue

        subprocess.run(["git", "push"], check=True)
        print("🚀 Code pushed to remote.")

        trigger_workflow()
        print("✅ Workflow triggered successfully.")

        # Get run ID
        run_id = None
        for _ in range(10):
            time.sleep(3)
            run_id = get_latest_run_id()
            if run_id:
                break
        if not run_id:
            print("❌ Could not retrieve run ID.")
            continue

        print(f"🔄 Waiting for Run ID: {run_id}")
        for _ in range(20):
            time.sleep(6)
            result = get_run_status(run_id)
            if result in ["success", "failure"]:
                break
        else:
            result = "unknown"

        print(f"🎯 Run complete | Result: {result}")

        # Save to dataset
        entry = {
            "build_number": i,
            "result": result,
            "issue_type": issue_type,
            "run_id": run_id
        }
        dataset.append(entry)
        with open(DATASET_PATH, "w") as f:
            json.dump(dataset, f, indent=2)

        print("📦 Saved run to dataset.")



if __name__ == "__main__":
    main()

