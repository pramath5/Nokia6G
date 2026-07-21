from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="UE Agent")

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SUPERVISOR_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------
# UE State (Stored in Memory)
# ---------------------------------------------------------

ue_state = {
    "device_id": "UE-001",
    "imsi": "404450123456789",
    "imei": "356938035643809",
    "jwt_token": None,
    "authenticated": False
}

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class RegisterRequest(BaseModel):
    device_id: str
    imsi: str
    imei: str


class AuthenticationRequest(BaseModel):
    device_id: str
    secret_key: str


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "Agent": "UE Agent",
        "Status": "Running"
    }


# ---------------------------------------------------------
# Register UE
# ---------------------------------------------------------

@app.post("/register")
def register(request: RegisterRequest):

    response = requests.post(

        f"{SUPERVISOR_URL}/register",

        json={
            "device_id": request.device_id,
            "imsi": request.imsi,
            "imei": request.imei
        }

    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    ue_state["device_id"] = request.device_id
    ue_state["imsi"] = request.imsi
    ue_state["imei"] = request.imei

    return response.json()


# ---------------------------------------------------------
# Authenticate
# ---------------------------------------------------------

@app.post("/authenticate")
def authenticate(request: AuthenticationRequest):

    response = requests.post(

        f"{SUPERVISOR_URL}/authenticate",

        json={
            "device_id": request.device_id,
            "secret_key": request.secret_key
        }

    )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    result = response.json()

    ue_state["authenticated"] = True
    ue_state["jwt_token"] = result["jwt_token"]

    return result


# ---------------------------------------------------------
# UE Status
# ---------------------------------------------------------

@app.get("/status")
def status():

    return {
        "device_id": ue_state["device_id"],
        "authenticated": ue_state["authenticated"],
        "jwt_token": ue_state["jwt_token"]
    }


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@app.post("/logout")
def logout():

    ue_state["authenticated"] = False
    ue_state["jwt_token"] = None

    return {
        "status": "Success",
        "message": "Logged Out Successfully"
    }


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8005
    )
