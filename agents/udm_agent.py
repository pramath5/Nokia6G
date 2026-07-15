from fastapi import FastAPI
from pydantic import BaseModel

from database.mongo import subscriber_collection

app = FastAPI(title="UDM Agent")


# -----------------------------
# Models
# -----------------------------

class SubscriberRequest(BaseModel):
    imsi: str


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():

    return {
        "Agent": "UDM",
        "Status": "Running"
    }


# -----------------------------
# Get Subscriber
# -----------------------------

@app.post("/get-subscriber")
def get_subscriber(request: SubscriberRequest):

    subscriber = subscriber_collection.find_one(
        {
            "imsi": request.imsi
        },
        {
            "_id": 0
        }
    )

    if subscriber is None:

        return {

            "status": "Failed",

            "message": "Subscriber Not Found"

        }

    return {

        "status": "Success",

        "subscriber": subscriber

    }


# -----------------------------
# Status
# -----------------------------

@app.get("/status")
def status():

    return {

        "Subscriber Count":

        subscriber_collection.count_documents({})

    }


# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8002

    )