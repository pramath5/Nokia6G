from mongo import (
    ue_collection,
    subscriber_collection,
    session_collection,
)

ue = {
    "device_id": "UE-001",
    "imei": "356938035643809",
    "imsi": "404450123456789",
    "model": "Pixel 9",
    "manufacturer": "Google",
    "status": "Registered"
}


subscriber = {
    "device_id": "UE-001",
    "subscriber_name": "Pavan",

    "imsi": "404450123456789",
    "imei": "356938035643809",

    "status": "Active",

    "plan": "Premium",

    "secret_key": "ABC123XYZ",

    "trust_score": 95,

    "risk_level": "Low",

    "allowed_services": [
        "Streaming",
        "Gaming",
        "VoIP"
    ],

    "available_bandwidth": 100,
    "allocated_bandwidth": 0
}


session = {
    "device_id": "UE-001",
    "authenticated": False,
    "jwt_token": None
}


ue_collection.insert_one(ue)
subscriber_collection.insert_one(subscriber)
session_collection.insert_one(session)

print("Database Seeded Successfully")   

print("\nUE Collection")
print(ue)

print("\nSubscriber Collection")
print(subscriber)

print("\nSession Collection")
print(session)