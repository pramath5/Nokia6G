from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Security Agent")

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

SUBSCRIBER_URL = "http://127.0.0.1:8003"

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class AuthorizationRequest(BaseModel):
    jwt_token: str
    requested_bandwidth: int


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return {

        "Agent": "Security Agent",

        "Status": "Running"

    }


# ---------------------------------------------------------
# Authorize Resource Request
# ---------------------------------------------------------

@app.post("/authorize")
def authorize(request: AuthorizationRequest):

    # ---------------------------------------------
    # Validate JWT
    # ---------------------------------------------

    try:

        payload = jwt.decode(

            request.jwt_token,

            JWT_SECRET,

            algorithms=[JWT_ALGORITHM]

        )

    except jwt.ExpiredSignatureError:

        return {

            "status": "Rejected",

            "reason": "JWT Expired"

        }

    except jwt.InvalidTokenError:

        return {

            "status": "Rejected",

            "reason": "Invalid JWT"

        }

    device_id = payload["device_id"]

    # ---------------------------------------------
    # Call Subscriber Agent
    # ---------------------------------------------

    try:

        response = requests.post(

            f"{SUBSCRIBER_URL}/allocate-bandwidth",

            json={

                "device_id": device_id,

                "requested_bandwidth": request.requested_bandwidth

            }

        )

    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Unable to contact Subscriber Agent"

        )

    if response.status_code != 200:

        raise HTTPException(

            status_code=response.status_code,

            detail=response.text

        )

    subscriber_response = response.json()

    if subscriber_response["status"] != "Approved":

        return subscriber_response

    return {

        "status": "Approved",

        "device_id": device_id,

        "allocated_bandwidth": subscriber_response["allocated_bandwidth"],

        "remaining_bandwidth": subscriber_response["remaining_bandwidth"]

    }


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8004

    )