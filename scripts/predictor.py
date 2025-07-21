# from fastapi import FastAPI
# from pydantic import BaseModel
# import joblib
# import pandas as pd
# import uvicorn
# import os
# import smtplib
# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Load env vars
# load_dotenv()

# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_SENDER = os.getenv("EMAIL_SENDER")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# # Load model
# model = joblib.load("model.pkl")

# # FastAPI setup
# app = FastAPI(title="AIOps CI/CD Failure Predictor")

# class PredictionRequest(BaseModel):
#     duration_sec: int
#     contains_secret: int
#     is_anomaly: int

# def send_email_alert(input_data, prediction, prob):
#     subject = "🚨 AIOps Alert: Hardcoded Secret Detected in Pipeline"

#     body = f"""
# 🚨 AIOps Agent has detected a hardcoded secret in your recent CI/CD run.

# 🔍 Input Details:
# - Duration: {input_data['duration_sec']} sec
# - Secret Present: ✅ YES
# - Anomaly Detected: {"✅ YES" if input_data['is_anomaly'] else "❌ NO"}

# 🧠 Model Prediction: {"FAILURE" if prediction else "SUCCESS"}
# 📊 Probability of Failure: {round(prob, 3)}

# ⚠️ Note: Even if the model predicts this run will succeed, presence of hardcoded secrets in source code or workflow YAML poses a critical security risk. Please review and secure credentials.

# -- AIOps Predictive Agent
# """

#     try:
#         msg = MIMEMultipart()
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = EMAIL_RECEIVER
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         server.starttls()
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
#         server.quit()
#         print("✅ Email alert sent.")
#     except Exception as e:
#         print(f"[!] Failed to send email: {e}")

# @app.post("/predict")
# def predict(request: PredictionRequest):
#     input_df = pd.DataFrame([{
#         "duration_sec": request.duration_sec,
#         "contains_secret": request.contains_secret,
#         "is_anomaly": request.is_anomaly
#     }])

#     prediction = model.predict(input_df)[0]
#     prob = model.predict_proba(input_df)[0][1]

#     # 🔐 Send alert if secret is present
#     if request.contains_secret == 1:
#         send_email_alert(
#         input_data=request.dict(),
#         prediction=prediction,
#         prob=prob
#     )

#     return {
#         "prediction": "FAILURE" if prediction == 1 else "SUCCESS",
#         "probability_of_failure": round(prob, 3),
#         "input": request.dict()
#     }

# @app.get("/")
# def root():
#     return {"status": "running"}

# if __name__ == "__main__":
#     uvicorn.run("predictor:app", host="0.0.0.0", port=8001, reload=True)
# from fastapi import FastAPI
# from pydantic import BaseModel
# import joblib
# import pandas as pd
# import os
# import smtplib
# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import uvicorn

# # Load environment variables
# load_dotenv()

# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_SENDER = os.getenv("EMAIL_SENDER")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# model = joblib.load("model.pkl")
# app = FastAPI(title="AIOps CI/CD Predictor")

# class PredictionRequest(BaseModel):
#     duration_sec: int
#     contains_secret: int
#     is_anomaly: int

# def send_email_alert(subject, body):
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = EMAIL_RECEIVER
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         server.starttls()
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
#         server.quit()
#         print("✅ Email alert sent.")
#     except Exception as e:
#         print(f"[!] Failed to send email: {e}")

# @app.post("/predict")
# def predict(request: PredictionRequest):
#     input_df = pd.DataFrame([{
#         "duration_sec": request.duration_sec,
#         "contains_secret": request.contains_secret,
#         "is_anomaly": request.is_anomaly
#     }])
#     prediction = model.predict(input_df)[0]
#     prob = model.predict_proba(input_df)[0][1]

#     # Alert if secret is present
#     if request.contains_secret == 1:
#         subject = "🚨 Secret Detected in Commit"
#         body = f"A hardcoded secret was found.\n\nInput: {request.dict()}\nPrediction: {'FAILURE' if prediction else 'SUCCESS'}\nProbability of Failure: {round(prob, 3)}"
#         send_email_alert(subject, body)

#     # Alert if failure is predicted
#     if prediction == 1:
#         subject = "🚨 CI/CD Run Predicted to FAIL"
#         body = f"The ML model predicted a pipeline failure.\n\nInput: {request.dict()}\nPrediction: FAILURE\nProbability: {round(prob, 3)}"
#         send_email_alert(subject, body)

#     return {
#         "prediction": "FAILURE" if prediction == 1 else "SUCCESS",
#         "probability_of_failure": round(prob, 3),
#         "input": request.dict()
#     }

# @app.get("/")
# def root():
#     return {"status": "Model server is running."}

# if __name__ == "__main__":
#     uvicorn.run("predictor:app", host="0.0.0.0", port=8001, reload=False)

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn

# Load model
model = joblib.load("model.pkl")

app = FastAPI(title="AIOps CI/CD Predictor")

class PredictionRequest(BaseModel):
    duration_sec: int
    contains_secret: int
    is_anomaly: int

@app.post("/predict")
def predict(request: PredictionRequest):
    input_df = pd.DataFrame([{
        "duration_sec": request.duration_sec,
        "contains_secret": request.contains_secret,
        "is_anomaly": request.is_anomaly
    }])
    prediction = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0][1]

    return {
        "prediction": "FAILURE" if prediction == 1 else "SUCCESS",
        "probability_of_failure": round(prob, 3),
        "input": request.dict()
    }

@app.get("/")
def root():
    return {"status": "Model server is running."}

if __name__ == "__main__":
    uvicorn.run("predictor:app", host="0.0.0.0", port=8001, reload=False)
