# agents/udm_agent.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database.mongo import subscriber_collection

app = FastAPI(title="UDM Agent")


# ------------------------------------------------------------------
# Request Model
# ------------------------------------------------------------------

class SubscriberRequest(BaseModel):
    device_id: str


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "agent": "UDM Agent",
        "status": "Running"
    }


# ------------------------------------------------------------------
# Get Subscriber Details
# ------------------------------------------------------------------

@app.post("/subscriber")
def get_subscriber(request: SubscriberRequest):

    subscriber = subscriber_collection.find_one(
        {"device_id": request.device_id},
        {"_id": 0}
    )

    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="Subscriber not found"
        )

    return {
        "status": "Success",
        "subscriber": subscriber
    }


# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002
    )