from mongo import subscriber_collection

subscriber = {
    "device_id": "UE-001",
    "imsi": "404450123456789",
    "imei": "356938035643809",
    "subscriber_name": "Pavan",
    "status": "Active",
    "plan": "Premium",
    "secret_key": "ABC123XYZ",
    "services": [
        "Internet",
        "VoLTE",
        "SMS"
    ],
    "trust_score": 100,
    "risk_level": "Low"
}

existing = subscriber_collection.find_one(
    {"imsi": subscriber["imsi"]}
)

if existing:
    print("Subscriber already exists.")
else:
    subscriber_collection.insert_one(subscriber)
    print("Subscriber inserted successfully.")