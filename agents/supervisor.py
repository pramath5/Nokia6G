from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

from database.mongo import ue_collection, session_collection

app = FastAPI(title="Supervisor Agent")

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

AUSF_URL = "http://127.0.0.1:8001"
SECURITY_URL = "http://127.0.0.1:8004"

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class UERegistration(BaseModel):
    device_id: str
    imsi: str
    imei: str


class AuthenticationRequest(BaseModel):
    device_id: str
    secret_key: str


class AuthorizationRequest(BaseModel):
    jwt_token: str
    requested_bandwidth: int


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "Agent": "Supervisor Agent",
        "Status": "Running"
    }


# ---------------------------------------------------------
# Register UE
# ---------------------------------------------------------

@app.post("/register")
def register(ue: UERegistration):

    existing = ue_collection.find_one(
        {
            "device_id": ue.device_id
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


# ---------------------------------------------------------
# Authenticate UE
# ---------------------------------------------------------

@app.post("/authenticate")
def authenticate(request: AuthenticationRequest):

    ue = ue_collection.find_one(
        {
            "device_id": request.device_id
        }
    )

    if ue is None:

        raise HTTPException(
            status_code=404,
            detail="UE Not Registered"
        )

    try:

        response = requests.post(

            f"{AUSF_URL}/authenticate",

            json={
                "device_id": request.device_id,
                "secret_key": request.secret_key
            }

        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to contact AUSF Agent"
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    ausf_response = response.json()

    if ausf_response.get("status") != "Authentication Successful":

        return ausf_response

    ue_collection.update_one(

        {
            "device_id": request.device_id
        },

        {
            "$set": {
                "authenticated": True
            }
        }

    )

    return ausf_response


# ---------------------------------------------------------
# Authorize Resource Request
# ---------------------------------------------------------

@app.post("/authorize-resource")
def authorize_resource(request: AuthorizationRequest):

    try:

        response = requests.post(

            f"{SECURITY_URL}/authorize",

            json={

                "jwt_token": request.jwt_token,

                "requested_bandwidth": request.requested_bandwidth

            }

        )

    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Unable to contact Security Agent"

        )

    if response.status_code != 200:

        raise HTTPException(

            status_code=response.status_code,

            detail=response.text

        )

    return response.json()


# ---------------------------------------------------------
# Status
# ---------------------------------------------------------

@app.get("/status")
def status():

    return {

        "registered_devices": ue_collection.count_documents({}),

        "authenticated_devices": ue_collection.count_documents(
            {
                "authenticated": True
            }
        ),

        "active_sessions": session_collection.count_documents(
            {}
        )

    }


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000

    )