from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uuid
import uvicorn

app = FastAPI(title="UE Agent")

SUPERVISOR_URL = "http://127.0.0.1:8000"

UE = {
    "device_id": str(uuid.uuid4()),
    "imsi": "404450123456789",
    "imei": "356938035643809",
    "authenticated": False,
    "session_token": None
}


class ServiceRequest(BaseModel):
    service: str


@app.get("/")
def home():
    return {
        "Agent": "UE",
        "Details": UE
    }


@app.post("/register")
def register():

    payload = {

        "device_id": UE["device_id"],

        "imsi": UE["imsi"],

        "imei": UE["imei"]

    }

    try:

        response = requests.post(

            f"{SUPERVISOR_URL}/register",

            json=payload

        )

        return response.json()

    except Exception as e:

        return {

            "status": "Failed",

            "error": str(e)

        }


@app.post("/authenticate")
def authenticate():

    payload = {

        "device_id": UE["device_id"],

        "imsi": UE["imsi"],

        "imei": UE["imei"]

    }

    try:

        response = requests.post(

            f"{SUPERVISOR_URL}/authenticate",

            json=payload

        )

        data = response.json()

        if data["status"] == "Success":

            UE["authenticated"] = True

            UE["session_token"] = data["session_token"]

        return data

    except Exception as e:

        return {

            "status": "Failed",

            "error": str(e)

        }


@app.post("/request-service")
def request_service(request: ServiceRequest):

    if UE["session_token"] is None:

        return {

            "status": "Failed",

            "message": "Authenticate First"

        }

    payload = {

        "service": request.service,

        "session_token": UE["session_token"]

    }

    response = requests.post(

        f"{SUPERVISOR_URL}/service",

        json=payload

    )

    return response.json()


@app.get("/status")
def status():

    return UE


if __name__ == "__main__":

    uvicorn.run(app,
                host="127.0.0.1",
                port=8005)