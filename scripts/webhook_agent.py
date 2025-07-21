

# import uvicorn
# from fastapi import FastAPI, Request
# import httpx
# import json
# import logging
# import base64
# import os
# from dotenv import load_dotenv
# from scripts.email_alert import send_email_alert

# # Load environment variables
# load_dotenv()
# GITHUB_TOKEN = os.getenv("GITHUB_PAT")

# # Constants
# MODEL_SERVER_URL = "http://localhost:8001/predict"
# ALERT_THRESHOLD = 0.65
# SECRET_KEYWORDS = [
#     "AWS_SECRET_ACCESS_KEY", "API_KEY", "PRIVATE_KEY",
#     "SECRET", "TOKEN", "PASSWORD"
# ]

# # Setup FastAPI
# app = FastAPI()

# # Setup logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# logger = logging.getLogger("webhook-agent")

# # 🔍 Utility: Detect secret in text
# def detect_secret_in_text(text: str) -> bool:
#     return any(keyword in text for keyword in SECRET_KEYWORDS)

# @app.post("/webhook")
# async def github_webhook(request: Request):
#     headers = request.headers
#     event_type = headers.get("X-GitHub-Event", "")

#     if event_type == "ping":
#         logger.info("📡 Ping event received.")
#         return {"message": "pong"}

#     if event_type != "push":
#         logger.warning(f"⚠️ Unhandled event type: {event_type}")
#         return {"message": f"Unhandled event: {event_type}"}

#     try:
#         payload = await request.json()
#     except Exception as e:
#         logger.error(f"❌ Failed to parse JSON payload: {e}")
#         return {"message": "Invalid payload"}

#     # Extract metadata
#     repo = payload.get("repository", {}).get("full_name", "unknown")
#     repo_name = payload.get("repository", {}).get("name")
#     owner = payload.get("repository", {}).get("owner", {}).get("login")
#     pusher = payload.get("pusher", {}).get("name", "unknown")
#     head_commit = payload.get("head_commit", {})
#     commit_message = head_commit.get("message", "no message")
#     commit_sha = head_commit.get("id")
#     changed_files = (
#         head_commit.get("modified", []) +
#         head_commit.get("added", []) +
#         head_commit.get("removed", [])
#     )

#     logger.info(f"📩 GitHub PUSH Event from {repo}")
#     logger.info(f"👤 Pusher: {pusher}")
#     logger.info(f"📝 Commit message: {commit_message}")
#     logger.info(f"📂 Files Changed: {changed_files}")

#     # 🔐 Check commit message for secret indicators
#     contains_secret = detect_secret_in_text(commit_message)

#     # 📂 Inspect contents of each file
#     file_contents = ""
#     if GITHUB_TOKEN and owner and repo_name and commit_sha:
#         async with httpx.AsyncClient() as client:
#             for file_path in changed_files:
#                 file_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}?ref={commit_sha}"
#                 try:
#                     response = await client.get(
#                         file_url,
#                         headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
#                     )
#                     logger.info(f"HTTP Request: GET {file_url} {response.status_code}")

#                     if response.status_code == 200:
#                         content_json = response.json()
#                         encoded_content = content_json.get("content", "")
#                         encoding = content_json.get("encoding", "")

#                         if encoding == "base64":
#                             decoded_content = base64.b64decode(encoded_content).decode("utf-8", errors="ignore")
#                             file_contents += f"\n# File: {file_path}\n{decoded_content}\n"
#                         else:
#                             logger.warning(f"⚠️ Unexpected encoding for {file_path}: {encoding}")
#                     else:
#                         logger.warning(f"❌ Could not fetch {file_path}: {response.status_code}")
#                 except Exception as e:
#                     logger.warning(f"⚠️ Failed to fetch or decode {file_path}: {e}")
#     else:
#         logger.warning("⚠️ Missing GitHub PAT or metadata. Skipping file inspection.")

#     # 🧪 Check if file contents include secrets
#     if detect_secret_in_text(file_contents):
#         contains_secret = True

#     # 🧠 Determine anomaly
#     is_anomaly = int("INJECT_FAIL" in commit_message)

#     # 🧾 Prepare data for ML model
#     input_payload = {
#         "duration_sec": 36,
#         "contains_secret": int(contains_secret),
#         "is_anomaly": is_anomaly
#     }

#     prediction = None
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(MODEL_SERVER_URL, json=input_payload)
#             logger.info(f"📬 ML server responded with status: {response.status_code}")
#             if response.status_code == 200:
#                 prediction = response.json()
#                 logger.info(f"🤖 ML Prediction: {prediction}")
#             else:
#                 logger.warning(f"⚠️ Unexpected ML response: {response.text}")
#     except Exception as e:
#         logger.error(f"🚨 Failed to contact ML model: {e}")

#     # 📬 Alert if needed
#     if prediction and (contains_secret or prediction["probability_of_failure"] > ALERT_THRESHOLD):
#         subject = f"[AIOps Alert] Risky Commit by {pusher} in {repo}"
#         body = f"""
# 🚨 AIOps Agent detected a risky commit in {repo}

# 👤 Pusher: {pusher}
# 📝 Commit Message: {commit_message}
# 📂 Files: {', '.join(changed_files)}

# 🧠 Prediction: {prediction['prediction']}
# 📊 Failure Probability: {prediction['probability_of_failure']}

# {"⚠️ Hardcoded Secret Detected!" if contains_secret else ""}
# {"⚠️ Anomaly Detected!" if is_anomaly else ""}
#         """
#         send_email_alert(subject, body)
#         logger.info("📬 Email alert sent.")
#     else:
#         logger.info("✅ Commit looks safe. No alert sent.")

#     return {"status": "processed"}

# @app.get("/")
# def root():
#     return {"status": "Webhook agent is live"}

# if __name__ == "__main__":
#     uvicorn.run("scripts.webhook_agent:app", host="0.0.0.0", port=8002, reload=True)
import uvicorn
from fastapi import FastAPI, Request
import httpx
import json
import logging
import base64
import os
from dotenv import load_dotenv
from scripts.email_alert import send_email_alert

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

MODEL_SERVER_URL = "http://localhost:8001/predict"
ALERT_THRESHOLD = 0.65

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("webhook-agent")

SECRET_KEYWORDS = [
    "AWS_SECRET_ACCESS_KEY", "API_KEY", "PRIVATE_KEY", "SECRET", "TOKEN", "PASSWORD"
]

def detect_new_secret_lines(before_content: str, after_content: str) -> bool:
    """Check if any secret keyword was newly added in the diff."""
    before_lines = set(before_content.splitlines())
    after_lines = set(after_content.splitlines())

    new_lines = after_lines - before_lines
    for line in new_lines:
        for keyword in SECRET_KEYWORDS:
            if keyword in line:
                return True
    return False

async def fetch_file_content(repo: str, filepath: str, ref: str) -> str:
    """Fetch and decode a file at specific commit SHA."""
    url = f"https://api.github.com/repos/{repo}/contents/{filepath}?ref={ref}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            logger.info(f"HTTP Request: GET {url} {response.status_code}")
            if response.status_code == 200:
                content_json = response.json()
                if content_json.get("encoding") == "base64":
                    return base64.b64decode(content_json["content"]).decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch {filepath} at {ref}: {e}")
    return ""

@app.post("/webhook")
async def github_webhook(request: Request):
    headers = request.headers
    event_type = headers.get("X-GitHub-Event", "")

    if event_type == "ping":
        logger.info("📡 Ping event received.")
        return {"message": "pong"}

    if event_type != "push":
        logger.warning(f"⚠️ Unhandled event type: {event_type}")
        return {"message": f"Unhandled event: {event_type}"}

    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON payload: {e}")
        return {"message": "Invalid payload"}

    repo = payload.get("repository", {}).get("full_name", "unknown")
    owner = payload.get("repository", {}).get("owner", {}).get("login")
    pusher = payload.get("pusher", {}).get("name", "unknown")
    commit_message = payload.get("head_commit", {}).get("message", "no message")
    after_sha = payload.get("after")
    before_sha = payload.get("before")
    changed_files = payload.get("head_commit", {}).get("modified", []) + \
                    payload.get("head_commit", {}).get("added", [])

    logger.info(f"📩 GitHub PUSH Event from {repo}")
    logger.info(f"👤 Pusher: {pusher}")
    logger.info(f"📝 Commit message: {commit_message}")
    logger.info(f"📂 Files Changed: {changed_files}")

    contains_secret = False

    # Check if any newly added line has secrets
    for file in changed_files:
        after_content = await fetch_file_content(repo, file, after_sha)
        before_content = await fetch_file_content(repo, file, before_sha)

        if detect_new_secret_lines(before_content, after_content):
            contains_secret = True
            logger.warning(f"🔐 New secret detected in file: {file}")
            break

    is_anomaly = int("INJECT_FAIL" in commit_message)

    input_payload = {
        "duration_sec": 36,
        "contains_secret": int(contains_secret),
        "is_anomaly": is_anomaly
    }

    prediction = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MODEL_SERVER_URL, json=input_payload)
            logger.info(f"📬 ML server responded with status: {response.status_code}")
            if response.status_code == 200:
                prediction = response.json()
                logger.info(f"🤖 ML Prediction: {prediction}")
            else:
                logger.warning(f"⚠️ ML error: {response.text}")
    except Exception as e:
        logger.error(f"🚨 ML server connection error: {e}")

    # Send alert only if secret added or failure predicted
    if prediction and (contains_secret or prediction["probability_of_failure"] > ALERT_THRESHOLD):
        subject = f"[AIOps Alert] Risky Commit by {pusher} in {repo}"
        body = f"""
🚨 AIOps Agent detected a risky commit in {repo}

👤 Pusher: {pusher}
📝 Commit Message: {commit_message}
📂 Files: {', '.join(changed_files)}

🧠 Prediction: {prediction['prediction']}
📊 Failure Probability: {prediction['probability_of_failure']}

{"⚠️ Hardcoded Secret Introduced!" if contains_secret else ""}
{"⚠️ Anomaly Detected!" if is_anomaly else ""}
        """
        send_email_alert(subject, body)
        logger.info("📬 Email alert sent.")
    else:
        logger.info("✅ Commit looks safe. No alert sent.")

    return {"status": "processed"}

@app.get("/")
def root():
    return {"status": "Webhook agent is live"}

if __name__ == "__main__":
    uvicorn.run("scripts.webhook_agent:app", host="0.0.0.0", port=8002, reload=True)
