# agents/ausf_agent.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import requests
import jwt
import os

from dotenv import load_dotenv
from datetime import datetime, timedelta

from database.mongo import session_collection

# ------------------------------------------------------------
# Load Environment Variables
# ------------------------------------------------------------

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", 30))

UDM_URL = "http://127.0.0.1:8002/subscriber"

app = FastAPI(title="AUSF Agent")


# ------------------------------------------------------------
# Request Model
# ------------------------------------------------------------

class AuthenticationRequest(BaseModel):
    device_id: str
    secret_key: str


# ------------------------------------------------------------
# Health Check
# ------------------------------------------------------------

@app.get("/")
def home():
    return {
        "agent": "AUSF Agent",
        "status": "Running"
    }


# ------------------------------------------------------------
# Authenticate Subscriber
# ------------------------------------------------------------

@app.post("/authenticate")
def authenticate(request: AuthenticationRequest):

    # --------------------------------------------------------
    # Ask UDM for subscriber information
    # --------------------------------------------------------

    try:
        response = requests.post(
            UDM_URL,
            json={
                "device_id": request.device_id
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to contact UDM Agent"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Subscriber not found"
        )

    subscriber = response.json()["subscriber"]

    # --------------------------------------------------------
    # Verify Subscriber
    # --------------------------------------------------------

    if subscriber["status"] != "Active":
        raise HTTPException(
            status_code=401,
            detail="Subscriber is inactive"
        )

    if subscriber["secret_key"] != request.secret_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid Secret Key"
        )

    # --------------------------------------------------------
    # Generate JWT
    # --------------------------------------------------------

    expiry = datetime.utcnow() + timedelta(
        minutes=JWT_EXPIRY_MINUTES
    )

    payload = {
        "device_id": subscriber["device_id"],
        "subscriber_name": subscriber["subscriber_name"],
        "plan": subscriber["plan"],
        "trust_score": subscriber["trust_score"],
        "exp": expiry
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    # --------------------------------------------------------
    # Store Session
    # --------------------------------------------------------

    session_collection.update_one(
        {
            "device_id": subscriber["device_id"]
        },
        {
            "$set": {
                "authenticated": True,
                "jwt_token": token,
                "login_time": datetime.utcnow()
            }
        },
        upsert=True
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "status": "Authentication Successful",
        "jwt_token": token,
        "subscriber": {
            "device_id": subscriber["device_id"],
            "subscriber_name": subscriber["subscriber_name"],
            "plan": subscriber["plan"],
            "trust_score": subscriber["trust_score"]
        }
    }


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001
    )