from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Application Agent")


SUPERVISOR_URL = "http://127.0.0.1:8000"


class ResourceRequest(BaseModel):
    jwt_token: str


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return {

        "Agent": "Application Agent",

        "Status": "Running"

    }


# ---------------------------------------------------------
# Request Bandwidth
# ---------------------------------------------------------

@app.post("/request-bandwidth")
def request_bandwidth(request: ResourceRequest):

    try:

        response = requests.post(

            f"{SUPERVISOR_URL}/authorize-resource",

            json={

                "jwt_token": request.jwt_token,

                "requested_bandwidth": 30

            }

        )

    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Unable to contact Supervisor Agent"

        )

    if response.status_code != 200:

        raise HTTPException(

            status_code=response.status_code,

            detail=response.text

        )

    return response.json()


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8006

    )