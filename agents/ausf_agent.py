from fastapi import FastAPI
from pydantic import BaseModel
import requests
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="AUSF Agent")

# ------------------------------------
# Configuration
# ------------------------------------

UDM_URL = "http://127.0.0.1:8002"

JWT_SECRET = "my_super_secret_key"

JWT_ALGORITHM = "HS256"

JWT_EXPIRY_MINUTES = 30

# ------------------------------------
# Models
# ------------------------------------

class AuthenticationRequest(BaseModel):

    device_id: str

    imsi: str

    imei: str


# ------------------------------------
# Home
# ------------------------------------

@app.get("/")
def home():

    return {

        "Agent": "AUSF",

        "Status": "Running"

    }


# ------------------------------------
# Authenticate
# ------------------------------------

@app.post("/authenticate")
def authenticate(request: AuthenticationRequest):

    try:

        response = requests.post(

            f"{UDM_URL}/get-subscriber",

            json={

                "imsi": request.imsi

            }

        )

    except Exception:

        return {

            "status": "Failed",

            "message": "Unable to contact UDM"

        }

    udm_response = response.json()

    if udm_response["status"] != "Success":

        return {

            "status": "Failed",

            "message": "Subscriber Not Found"

        }

    subscriber = udm_response["subscriber"]

    # Verify IMEI

    if subscriber["imei"] != request.imei:

        return {

            "status": "Failed",

            "message": "IMEI Verification Failed"

        }

    expiry = datetime.utcnow() + timedelta(

        minutes=JWT_EXPIRY_MINUTES

    )

    payload = {

        "device_id": request.device_id,

        "imsi": request.imsi,

        "exp": expiry

    }

    session_token = jwt.encode(

        payload,

        JWT_SECRET,

        algorithm=JWT_ALGORITHM

    )

    return {

        "status": "Success",

        "message": "Authentication Successful",

        "session_token": session_token,

        "expires_at": expiry.isoformat()

    }


# ------------------------------------
# Status
# ------------------------------------

@app.get("/status")
def status():

    return {

        "status": "Running"

    }


# ------------------------------------
# Run
# ------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8001

    )