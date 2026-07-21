from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database.mongo import subscriber_collection

app = FastAPI(title="Subscriber Agent")


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class BandwidthRequest(BaseModel):
    device_id: str
    requested_bandwidth: int


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "Agent": "Subscriber Agent",
        "Status": "Running"
    }


# ---------------------------------------------------------
# Allocate Bandwidth
# ---------------------------------------------------------

@app.post("/allocate-bandwidth")
def allocate_bandwidth(request: BandwidthRequest):

    subscriber = subscriber_collection.find_one(
        {
            "device_id": request.device_id
        }
    )

    if subscriber is None:

        raise HTTPException(
            status_code=404,
            detail="Subscriber Not Found"
        )

    # ---------------------------------------------
    # Check Subscriber Status
    # ---------------------------------------------

    if subscriber["status"] != "Active":

        return {
            "status": "Rejected",
            "reason": "Subscriber Inactive"
        }

    # ---------------------------------------------
    # Check Trust Score
    # ---------------------------------------------

    if subscriber["trust_score"] < 80:

        return {
            "status": "Rejected",
            "reason": "Low Trust Score"
        }

    # ---------------------------------------------
    # Check Available Bandwidth
    # ---------------------------------------------

    available = subscriber["available_bandwidth"]

    if available < request.requested_bandwidth:

        return {
            "status": "Rejected",
            "reason": "Insufficient Bandwidth"
        }

    # ---------------------------------------------
    # Allocate Bandwidth
    # ---------------------------------------------

    remaining = available - request.requested_bandwidth

    allocated = subscriber["allocated_bandwidth"] + request.requested_bandwidth

    subscriber_collection.update_one(

        {
            "device_id": request.device_id
        },

        {
            "$set": {

                "available_bandwidth": remaining,

                "allocated_bandwidth": allocated

            }
        }

    )

    return {

        "status": "Approved",

        "device_id": request.device_id,

        "allocated_bandwidth": request.requested_bandwidth,

        "remaining_bandwidth": remaining

    }


# ---------------------------------------------------------
# Subscriber Details
# ---------------------------------------------------------

@app.get("/subscriber/{device_id}")
def get_subscriber(device_id: str):

    subscriber = subscriber_collection.find_one(
        {
            "device_id": device_id
        },
        {
            "_id": 0
        }
    )

    if subscriber is None:

        raise HTTPException(
            status_code=404,
            detail="Subscriber Not Found"
        )

    return subscriber


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8003
    )