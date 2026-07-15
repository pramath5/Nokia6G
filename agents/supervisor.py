from fastapi import FastAPI
from pydantic import BaseModel
import requests

from database.mongo import ue_collection, session_collection

app = FastAPI(title="Supervisor Agent")

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

AUSF_URL = "http://127.0.0.1:8001"

# ---------------------------------------------------
# Models
# ---------------------------------------------------

class UERegistration(BaseModel):
    device_id: str
    imsi: str
    imei: str


class AuthenticationRequest(BaseModel):
    device_id: str
    imsi: str
    imei: str


class ServiceRequest(BaseModel):
    session_token: str
    service: str


# ---------------------------------------------------
# Home
# ---------------------------------------------------

@app.get("/")
def home():

    return {
        "Agent": "Supervisor",
        "Status": "Running"
    }


# ---------------------------------------------------
# Register UE
# ---------------------------------------------------

@app.post("/register")
def register(ue: UERegistration):

    existing = ue_collection.find_one(
        {
            "imsi": ue.imsi
        }
    )

    if existing:

        return {

            "status": "Success",

            "message": "UE Already Registered"

        }

    ue_collection.insert_one(

        {

            "device_id": ue.device_id,

            "imsi": ue.imsi,

            "imei": ue.imei,

            "authenticated": False

        }

    )

    return {

        "status": "Success",

        "message": "UE Registered Successfully"

    }


# ---------------------------------------------------
# Authenticate UE
# ---------------------------------------------------

@app.post("/authenticate")
def authenticate(request: AuthenticationRequest):

    existing = ue_collection.find_one(

        {

            "imsi": request.imsi

        }

    )

    if existing is None:

        return {

            "status": "Failed",

            "message": "UE Not Registered"

        }

    response = requests.post(

        f"{AUSF_URL}/authenticate",

        json={

            "device_id": request.device_id,

            "imsi": request.imsi,

            "imei": request.imei

        }

    )

    ausf_response = response.json()

    if ausf_response["status"] != "Success":

        return ausf_response

    session_collection.insert_one(

        {

            "device_id": request.device_id,

            "imsi": request.imsi,

            "session_token": ausf_response["session_token"],

            "expires_at": ausf_response["expires_at"]

        }

    )

    ue_collection.update_one(

        {

            "imsi": request.imsi

        },

        {

            "$set": {

                "authenticated": True

            }

        }

    )

    return ausf_response


# ---------------------------------------------------
# Service Request
# ---------------------------------------------------

@app.post("/service")
def service(request: ServiceRequest):

    session = session_collection.find_one(

        {

            "session_token": request.session_token

        }

    )

    if session is None:

        return {

            "status": "Failed",

            "message": "Invalid Session"

        }

    return {

        "status": "Success",

        "message": f"{request.service} Access Granted"

    }


# ---------------------------------------------------
# Status
# ---------------------------------------------------

@app.get("/status")
def status():

    return {

        "registered_devices": ue_collection.count_documents({}),

        "active_sessions": session_collection.count_documents({})

    }


# ---------------------------------------------------
# Run
# ---------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000

    )