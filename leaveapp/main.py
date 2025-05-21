from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
from email.message import EmailMessage
import os

app = FastAPI()

# Simpan data cuti sementara dalam memory (mock DB)
leave_records = []
approved_leaves = []

# Model data
class LeaveApplication(BaseModel):
    employee_email: EmailStr
    start_date: str
    end_date: str
    reason: str

class LeaveApproval(BaseModel):
    employee_email: EmailStr
    approved: bool

# Contoh baki cuti per employee (mock)
leave_balance = {
    "user1@example.com": 10,
    "user2@example.com": 8,
}

# Helper function hantar email (Gmail SMTP contoh)
def send_approval_email(to_email: str):
    msg = EmailMessage()
    msg.set_content("Cuti anda telah diluluskan. Terima kasih.")
    msg['Subject'] = 'Pengesahan Kelulusan Cuti'
    msg['From'] = os.environ.get("SMTP_USER")
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.send_message(msg)

@app.get("/")
async def root():
    return {"message": "Welcome to Leave Management API"}

@app.post("/apply-leave")
async def apply_leave(application: LeaveApplication):
    # Kurangkan baki cuti jika ada cukup
    balance = leave_balance.get(application.employee_email, 0)
    requested_days =  (parse_date(application.end_date) - parse_date(application.start_date)).days + 1

    if requested_days > balance:
        raise HTTPException(status_code=400, detail="Baki cuti tidak cukup")

    leave_records.append(application.dict())
    return {"message": "Permohonan cuti diterima", "requested_days": requested_days}

@app.get("/leave-records/{employee_email}")
async def get_leave_records(employee_email: str):
    records = [r for r in leave_records if r["employee_email"] == employee_email]
    return {"leave_records": records}

@app.get("/leave-balance/{employee_email}")
async def get_leave_balance(employee_email: str):
    balance = leave_balance.get(employee_email, 0)
    return {"leave_balance": balance}

@app.post("/approve-leave")
async def approve_leave(approval: LeaveApproval):
    # Check ada permohonan
    found = None
    for record in leave_records:
        if record["employee_email"] == approval.employee_email:
            found = record
            break

    if not found:
        raise HTTPException(status_code=404, detail="Permohonan cuti tidak dijumpai")

    if approval.approved:
        approved_leaves.append(found)
        # Update baki cuti
        balance = leave_balance.get(approval.employee_email, 0)
        requested_days =  (parse_date(found["end_date"]) - parse_date(found["start_date"])).days + 1
        leave_balance[approval.employee_email] = balance - requested_days

        # Hantar email (simple print kalau tak set SMTP)
        try:
            send_approval_email(approval.employee_email)
        except Exception as e:
            print("Failed to send email:", e)

        return {"message": "Cuti diluluskan dan email dihantar"}
    else:
        return {"message": "Cuti ditolak"}

# Simple helper untuk parse tarikh
from datetime import datetime
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

