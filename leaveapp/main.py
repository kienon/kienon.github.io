from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import smtplib
import os

app = FastAPI()

# Configure CORS
origins = [
    "https://kienon.github.io",
    "http://kienon.github.io",
    "https://kienon.github.io/leaveapp",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeaveRequest(BaseModel):
    start_date: str
    end_date: str
    reason: str

@app.post("/users/{user_id}/leave/")
def apply_leave(user_id: int, data: LeaveRequest):
    # Simpan ke DB atau file (bagi demo skip)
    send_email_notification(user_id, data.start_date, data.end_date, data.reason)
    return {"message": "Leave request submitted"}

def send_email_notification(user_id, start, end, reason):
    sender = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    receiver = os.environ.get("ADMIN_EMAIL") or "admin@example.com"

    subject = "Leave Application Notification"
    body = f"User {user_id} applied leave from {start} to {end}.\nReason: {reason}"
    msg = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
