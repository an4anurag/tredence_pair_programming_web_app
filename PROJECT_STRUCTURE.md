# Project Structure

## Complete Directory Tree

```
pair-programming-app/
│
├── README.md                           # Main documentation
├── TESTING_GUIDE.md                    # Testing instructions
├── QUICK_REFERENCE.md                  # Developer quick reference
├── PROJECT_STRUCTURE.md                # This file
├── setup.sh                            # Setup script
├── docker-compose.yml                  # Docker orchestration
│
└── backend/                            # Backend application
    │
    ├── main.py                         # FastAPI application entry point
    ├── requirements.txt                # Python dependencies
    ├── Dockerfile                      # Docker container config
    ├── .env.example                    # Environment variables template
    ├── .env                            # Environment variables (gitignored)
    ├── .gitignore                      # Git ignore rules
    ├── alembic.ini                     # Alembic migration config
    │
    ├── app/                            # Main application package
    │   ├── __init__.py                 # Package initialization
    │   ├── database.py                 # Database configuration
    │   ├── models.py                   # SQLAlchemy ORM models
    │   ├── schemas.py                  # Pydantic validation schemas
    │   │
    │   ├── routers/                    # API route handlers
    │   │   ├── __init__.py
    │   │   ├── rooms.py                # Room creation/management
    │   │   ├── autocomplete.py         # Autocomplete suggestions
    │   │   └── websocket.py            # WebSocket connections
    │   │
    │   └── services/                   # Business logic layer
    │       ├── __init__.py
    │       ├── room_service.py         # Room operations
    │       ├── autocomplete_service.py # Suggestion generation
    │       └── websocket_manager.py    # WebSocket management
    │
    ├── alembic/                        # Database migrations
    │   ├── env.py                      # Migration environment
    │   ├── script.py.mako              # Migration template
    │   ├── README
    │   └── versions/                   # Migration files
    │       └── (migration files here)
    │
    └── tests/                          # Test suite
        ├── __init__.py
        ├── conftest.py                 # Pytest configuration
        ├── test_rooms.py               # Room endpoint tests
        ├── test_autocomplete.py        # Autocomplete tests
        └── test_websocket.py           # WebSocket tests
```

## File Descriptions

### Root Level

| File | Purpose | Key Contents |
|------|---------|--------------|
| `README.md` | Main documentation | Architecture, setup instructions, API docs |
| `TESTING_GUIDE.md` | Testing documentation | Test strategies, examples, scenarios |
| `QUICK_REFERENCE.md` | Developer cheat sheet | Common commands, code snippets |
| `setup.sh` | Setup automation | Installation and configuration script |
| `docker-compose.yml` | Docker orchestration | PostgreSQL + Backend services |

### Backend Core

| File | Purpose | Dependencies | Key Exports |
|------|---------|--------------|-------------|
| `main.py` | Application entry | FastAPI, routers | `app` (FastAPI instance) |
| `requirements.txt` | Python packages | - | All dependencies |
| `Dockerfile` | Container image | Python 3.11 | Backend service |
| `.env.example` | Config template | - | Environment variables |
| `alembic.ini` | Migration config | Alembic | Database connection |

### App Package (`app/`)

#### Core Modules

| File | Purpose | Key Classes/Functions | Imports |
|------|---------|----------------------|---------|
| `database.py` | DB configuration | `engine`, `SessionLocal`, `get_db()` | SQLAlchemy |
| `models.py` | ORM models | `Room`, `CodeSnapshot` | SQLAlchemy, database |
| `schemas.py` | Data validation | `RoomResponse`, `AutocompleteRequest` | Pydantic |

#### Routers (`app/routers/`)

| File | Endpoints | Methods | Purpose |
|------|-----------|---------|---------|
| `rooms.py` | `/rooms`, `/rooms/{id}` | POST, GET, DELETE | Room management |
| `autocomplete.py` | `/autocomplete` | POST | Code suggestions |
| `websocket.py` | `/ws/{room_id}` | WebSocket | Real-time sync |

#### Services (`app/services/`)

| File | Class | Key Methods | Purpose |
|------|-------|-------------|---------|
| `room_service.py` | `RoomService` | `create_room()`, `get_room()`, `update_room_code()` | Room business logic |
| `autocomplete_service.py` | `AutocompleteService` | `generate_suggestion()` | Suggestion logic |
| `websocket_manager.py` | `WebSocketManager` | `connect()`, `disconnect()`, `broadcast()` | Connection management |

### Database Migrations (`alembic/`)

```
alembic/
├── env.py                  # Migration environment setup
├── script.py.mako          # Template for new migrations
└── versions/               # Migration history
    ├── 001_initial.py      # Initial tables
    ├── 002_add_snapshots.py # Code snapshots feature
    └── ...
```

### Tests (`tests/`)

| File | Tests | Coverage |
|------|-------|----------|
| `test_rooms.py` | Room CRUD operations | Create, read, update, delete |
| `test_autocomplete.py` | Autocomplete logic | Various code patterns |
| `test_websocket.py` | WebSocket connections | Connect, disconnect, broadcast |

## File Dependencies Graph

```
main.py
  ├── app.routers.rooms
  │     ├── app.services.room_service
  │     │     ├── app.models
  │     │     └── app.database
  │     └── app.schemas
  │
  ├── app.routers.autocomplete
  │     ├── app.services.autocomplete_service
  │     └── app.schemas
  │
  └── app.routers.websocket
        ├── app.services.websocket_manager
        ├── app.services.room_service
        └── app.database
```

## Module Responsibilities

### 1. Entry Point Layer (`main.py`)
- Initialize FastAPI application
- Configure CORS middleware
- Register all routers
- Setup database tables
- Configure logging

### 2. Router Layer (`app/routers/`)
- Handle HTTP requests
- Validate input with Pydantic
- Call service layer
- Return formatted responses
- Handle errors and status codes

### 3. Service Layer (`app/services/`)
- Implement business logic
- Interact with database
- Manage WebSocket connections
- Generate autocomplete suggestions
- Handle complex operations

### 4. Model Layer (`app/models.py`)
- Define database schema
- ORM mappings
- Relationships between tables
- Database constraints

### 5. Schema Layer (`app/schemas.py`)
- Request/response validation
- Data serialization
- Type checking
- API documentation

### 6. Database Layer (`app/database.py`)
- Connection management
- Session handling
- Engine configuration

## Data Flow Examples

### 1. Create Room Flow
```
Client
  ↓ POST /rooms
main.py
  ↓ route to
rooms.py (router)
  ↓ validate with RoomCreate schema
  ↓ call
room_service.py
  ↓ interact with
models.py (Room)
  ↓ save to
PostgreSQL
  ↓ return
RoomResponse schema
  ↓ JSON response
Client
```

### 2. WebSocket Flow
```
Client
  ↓ WS /ws/{room_id}
websocket.py (router)
  ↓ verify room exists
room_service.py
  ↓ add connection
websocket_manager.py
  ↓ broadcast updates
All connected clients
  ↓ save to
PostgreSQL
```

### 3. Autocomplete Flow
```
Client
  ↓ POST /autocomplete
autocomplete.py (router)
  ↓ validate AutocompleteRequest
  ↓ call
autocomplete_service.py
  ↓ pattern matching
  ↓ return AutocompleteResponse
Client
```

## Configuration Files

### Environment Variables (`.env`)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pair_programming
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

### Docker Compose (`docker-compose.yml`)
- PostgreSQL service (port 5432)
- Backend service (port 8000)
- Volume for data persistence
- Health checks
- Auto-restart policies

### Alembic (`alembic.ini`)
- Migration script location
- Database URL
- Logging configuration
- Version locations

## Import Conventions

```python
# Standard library
import asyncio
import json
from typing import Dict, List

# Third-party
from fastapi import FastAPI, WebSocket
from sqlalchemy import Column, String
from pydantic import BaseModel

# Local
from app.database import get_db
from app.models import Room
from app.services.room_service import RoomService
```

## Code Organization Best Practices

1. **One responsibility per file**
   - Routers handle HTTP
   - Services handle logic
   - Models handle data

2. **Clear naming**
   - `room_service.py` not `service.py`
   - `test_rooms.py` not `test1.py`

3. **Type hints everywhere**
   ```python
   def get_room(room_id: str) -> Room | None:
       pass
   ```

4. **Docstrings for all public functions**
   ```python
   def create_room(language: str = "python") -> Room:
       """
       Create a new collaborative coding room.
       
       Args:
           language: Programming language
           
       Returns:
           Room: Created room instance
       """
   ```

5. **Consistent error handling**
   ```python
   try:
       # operation
   except SpecificError as e:
       logger.error(f"Context: {e}")
       raise HTTPException(status_code=500)
   ```

## Adding New Components

### New Router
1. Create `app/routers/new_router.py`
2. Define router: `router = APIRouter()`
3. Add endpoints with decorators
4. Import in `app/routers/__init__.py`
5. Register in `main.py`

### New Service
1. Create `app/services/new_service.py`
2. Define service class
3. Add methods with type hints
4. Import in `app/services/__init__.py`
5. Use in router

### New Model
1. Add class to `app/models.py`
2. Create migration: `alembic revision --autogenerate`
3. Apply migration: `alembic upgrade head`
4. Add corresponding Pydantic schema

---

**Understanding the structure helps navigate and extend the codebase efficiently!**