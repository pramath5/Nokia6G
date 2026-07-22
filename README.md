# Nokia6G

A FastAPI-based 5G simulation project that models a small multi-agent network workflow for UE registration, authentication, session handling, and bandwidth authorization using MongoDB.

## Overview

This project is organized around multiple lightweight agents that cooperate to simulate a simplified 5G control and service flow:

- **Supervisor Agent** coordinates UE registration, authentication, and resource authorization.
- **AUSF Agent** authenticates devices and issues JWT tokens.
- **UDM Agent** fetches subscriber data from MongoDB.
- **Subscriber Agent** validates subscriber state and allocates bandwidth.
- **Security Agent** verifies JWTs and enforces authorization checks.
- **UE Agent** simulates a user equipment device interacting with the system.
- **Application Agent** simulates an application requesting network bandwidth.

MongoDB is used to store UE, subscriber, and session data.

## Project Structure

```text
Nokia6G/
├── agents/
│   ├── application_agent.py
│   ├── ausf_agent.py
│   ├── security_agent.py
│   ├── subscriber_agent.py
│   ├── supervisor.py
│   ├── udm_agent.py
│   └── ue_agent.py
├── database/
│   ├── mongo.py
│   ├── seed_database.py
│   └── test_db.py
├── postman/
│   ├── collections/
│   ├── environments/
│   ├── flows/
│   ├── globals/
│   ├── mocks/
│   └── specs/
├── overview.txt
├── README.md
└── requirements.txt
```

## Agent Ports

| Agent | Port |
|---|---:|
| Supervisor Agent | 8000 |
| AUSF Agent | 8001 |
| UDM Agent | 8002 |
| Subscriber Agent | 8003 |
| Security Agent | 8004 |
| UE Agent | 8005 |
| Application Agent | 8006 |

## Prerequisites

- Python 3.10+
- MongoDB instance
- pip

## Installation

1. Clone or download the project.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root and define the following values:

```env
MONGO_URI=your_mongodb_connection_string
DATABASE_NAME=5g_ai_agents
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30
```

## Running the Services

Start each agent in a separate terminal from the project root.

### Supervisor Agent

```bash
python agents/supervisor.py
```

### AUSF Agent

```bash
python agents/ausf_agent.py
```

### UDM Agent

```bash
python agents/udm_agent.py
```

### Subscriber Agent

```bash
python agents/subscriber_agent.py
```

### Security Agent

```bash
python agents/security_agent.py
```

### UE Agent

```bash
python agents/ue_agent.py
```

### Application Agent

```bash
python agents/application_agent.py
```

## Main API Endpoints

### Supervisor Agent

- `GET /`
- `POST /register`
- `POST /authenticate`
- `POST /authorize-resource`
- `GET /status`

### AUSF Agent

- `GET /`
- `POST /authenticate`

### UDM Agent

- `GET /`
- `POST /subscriber`

### Subscriber Agent

- `GET /`
- `POST /allocate-bandwidth`
- `GET /subscriber/{device_id}`

### Security Agent

- `GET /`
- `POST /authorize`

### UE Agent

- `GET /`
- `POST /register`
- `POST /authenticate`
- `GET /status`
- `POST /logout`

### Application Agent

- `GET /`
- `POST /request-bandwidth`

## Typical Flow

1. Register a UE through the Supervisor Agent or UE Agent.
2. Authenticate the UE using a valid `device_id` and `secret_key`.
3. Receive a JWT token from the AUSF Agent.
4. Use the JWT token to request bandwidth through the Application Agent.
5. The Security Agent validates the token and the Subscriber Agent approves or rejects bandwidth allocation.

## Dependencies

The project uses:

- fastapi
- uvicorn
- pymongo
- python-dotenv
- pyjwt
- cryptography
- pydantic
- requests

## Notes

- Make sure MongoDB is reachable before starting the agents.
- The database layer raises an error if `MONGO_URI` is missing.
- Seed subscriber data before testing the full authentication and authorization flow if required by your setup.

## Future Improvements

- Add a Postman collection for end-to-end testing.
- Add automated tests for each agent.
- Add Docker support for running all services together.
- Document request and response examples for each endpoint.
