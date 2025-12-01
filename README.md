# Real-Time Pair Programming Application

A full-stack web application for real-time collaborative coding with AI-powered autocomplete suggestions. Built with FastAPI, WebSockets, PostgreSQL, and React.

## 🚀 Features

- **Real-Time Collaboration**: Multiple users can edit code simultaneously with instant synchronization
- **Room Management**: Create and join coding rooms with unique IDs
- **AI Autocomplete**: Context-aware code suggestions (mock implementation, easily replaceable with real AI)
- **WebSocket Communication**: Low-latency bidirectional communication for seamless collaboration
- **Persistent Storage**: Code state saved in PostgreSQL database
- **Modern Architecture**: Clean separation of concerns with services, routers, and models
- **Type Safety**: Full type hints with Pydantic schemas
- **Docker Support**: Easy deployment with Docker Compose

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [WebSocket Protocol](#websocket-protocol)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [Limitations](#limitations)

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────┐         WebSocket          ┌──────────────┐
│             │◄──────────────────────────►│              │
│   Client 1  │         HTTP/REST          │   FastAPI    │
│  (Browser)  │◄──────────────────────────►│   Backend    │
└─────────────┘                            │              │
                                           └───────┬──────┘
┌─────────────┐         WebSocket                 │
│             │◄────────────────────────────┐     │
│   Client 2  │         HTTP/REST           │     │
│  (Browser)  │◄────────────────────────────┘     │
└─────────────┘                                   │
                                                  ▼
                                         ┌─────────────────┐
                                         │   PostgreSQL    │
                                         │    Database     │
                                         └─────────────────┘
```

### Backend Architecture

```
main.py (FastAPI App)
    │
    ├── /routers
    │   ├── rooms.py          → Room creation/management
    │   ├── autocomplete.py   → AI suggestions
    │   └── websocket.py      → Real-time sync
    │
    ├── /services
    │   ├── room_service.py         → Business logic for rooms
    │   ├── autocomplete_service.py → Suggestion generation
    │   └── websocket_manager.py    → Connection management
    │
    ├── /models
    │   └── models.py         → SQLAlchemy ORM models
    │
    ├── /schemas
    │   └── schemas.py        → Pydantic validation models
    │
    └── database.py           → Database configuration
```

### Data Flow

1. **Room Creation**: Client → POST /rooms → RoomService → PostgreSQL → Response with roomId
2. **WebSocket Connection**: Client → WS /ws/{roomId} → WebSocketManager → Authenticated
3. **Code Update**: Client types → WebSocket message → Broadcast to all clients → Database update
4. **Autocomplete**: Client stops typing (600ms) → POST /autocomplete → AutocompleteService → Suggestion

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Robust relational database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server

### Frontend (Optional - Included as React demo)
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icon library

### DevOps
- **Docker & Docker Compose**: Containerization
- **Alembic**: Database migrations
- **pytest**: Testing framework

## 📁 Project Structure

```
pair-programming-app/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── database.py            # Database configuration
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── rooms.py           # Room endpoints
│   │   │   ├── autocomplete.py    # Autocomplete endpoint
│   │   │   └── websocket.py       # WebSocket endpoint
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── room_service.py         # Room business logic
│   │       ├── autocomplete_service.py # Autocomplete logic
│   │       └── websocket_manager.py    # WebSocket management
│   │
│   ├── alembic/                   # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                     # Test files
│   │   ├── test_rooms.py
│   │   ├── test_autocomplete.py
│   │   └── test_websocket.py
│   │
│   ├── main.py                    # Application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Docker configuration
│   ├── .env.example               # Environment variables template
│   └── alembic.ini                # Alembic configuration
│
├── docker-compose.yml             # Docker Compose configuration
└── README.md                      # This file
```

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- Docker & Docker Compose (optional, for containerized setup)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pair-programming-app
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Local Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd pair-programming-app/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt-get install postgresql postgresql-contrib
   
   # Create database
   sudo -u postgres psql
   CREATE DATABASE pair_programming;
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE pair_programming TO postgres;
   \q
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Verify installation**
   - Open http://localhost:8000/docs
   - You should see the interactive API documentation

## 📚 API Documentation

### REST Endpoints

#### Create Room
```http
POST /rooms
Content-Type: application/json

{
  "language": "python"  // optional
}

Response:
{
  "roomId": "a1b2c3d4",
  "code": "# Write your Python code here\n\n",
  "language": "python",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Get Room
```http
GET /rooms/{room_id}

Response:
{
  "roomId": "a1b2c3d4",
  "code": "print('Hello, World!')",
  "language": "python",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Autocomplete Suggestion
```http
POST /autocomplete
Content-Type: application/json

{
  "code": "def hello():\n    print(",
  "cursorPosition": 25,
  "language": "python"
}

Response:
{
  "suggestion": "'Hello, World!')",
  "confidence": 0.85,
  "type": "completion"
}
```

### WebSocket Protocol

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{roomId}');
```

#### Client → Server Messages

**Code Update**
```json
{
  "type": "code_update",
  "code": "print('Hello, World!')"
}
```

#### Server → Client Messages

**Code Update**
```json
{
  "type": "code_update",
  "code": "print('Hello, World!')"
}
```

**User Count Update**
```json
{
  "type": "user_count",
  "count": 2
}
```

## 🧪 Testing

### Run Tests
```bash
cd backend
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing with cURL

**Create Room**
```bash
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}'
```

**Get Autocomplete**
```bash
curl -X POST http://localhost:8000/autocomplete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(",
    "cursorPosition": 25,
    "language": "python"
  }'
```

### WebSocket Testing

**Using websocat (CLI WebSocket client)**
```bash
# Install websocat
cargo install websocat

# Connect to room
websocat ws://localhost:8000/ws/a1b2c3d4

# Send message
{"type": "code_update", "code": "print('test')"}
```

**Using Browser DevTools**
```javascript
// Open browser console
const ws = new WebSocket('ws://localhost:8000/ws/a1b2c3d4');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: 'code_update', code: "print('hello')"}));
```

## 🔧 Development

### Adding New Features

1. **Add Database Model** (if needed)
   ```python
   # app/models.py
   class YourModel(Base):
       __tablename__ = "your_table"
       id = Column(Integer, primary_key=True)
       # ...
   ```

2. **Create Migration**
   ```bash
   alembic revision --autogenerate -m "Add your_table"
   alembic upgrade head
   ```

3. **Add Pydantic Schema**
   ```python
   # app/schemas.py
   class YourSchema(BaseModel):
       field: str
   ```

4. **Implement Service**
   ```python
   # app/services/your_service.py
   class YourService:
       def __init__(self, db: Session):
           self.db = db
   ```

5. **Create Router**
   ```python
   # app/routers/your_router.py
   router = APIRouter()
   
   @router.get("/endpoint")
   async def your_endpoint():
       pass
   ```

6. **Register Router**
   ```python
   # main.py
   app.include_router(your_router, prefix="/your-prefix")
   ```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Keep functions focused and small
- Use meaningful variable names

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

## 🚀 Deployment

### Using Docker (Production)

1. **Build and push image**
   ```bash
   docker build -t pair-programming-backend:latest ./backend
   docker tag pair-programming-backend:latest your-registry/pair-programming:latest
   docker push your-registry/pair-programming:latest
   ```

2. **Deploy with docker-compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables for Production

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
DEBUG=False
LOG_LEVEL=INFO
```

### Scaling Considerations

For production deployments handling many concurrent users:

1. **Use Redis for WebSocket state**
   - Current implementation uses in-memory state
   - For multiple backend instances, use Redis pub/sub

2. **Add connection pooling**
   - Configure SQLAlchemy pool size
   - Use pgbouncer for PostgreSQL

3. **Enable horizontal scaling**
   - Deploy behind load balancer
   - Use sticky sessions for WebSocket connections

4. **Add rate limiting**
   - Prevent abuse of autocomplete endpoint
   - Limit WebSocket message frequency

## 🔮 Future Improvements

### High Priority

1. **Real AI Integration**
   - Replace mock autocomplete with OpenAI Codex/GPT
   - Integrate local models (CodeLlama, StarCoder)
   - Add model selection UI

2. **Enhanced Collaboration**
   - Cursor position sharing (see where others are typing)
   - Syntax highlighting
   - Multiple file support
   - Chat functionality

3. **Authentication & Authorization**
   - User accounts (OAuth, JWT)
   - Private rooms
   - Room permissions

### Medium Priority

4. **Code Execution**
   - Run code in sandboxed environment
   - Support multiple languages
   - Display output in UI

5. **Version Control**
   - Full undo/redo history
   - Time-travel debugging
   - Code snapshots
   - Export history

6. **Advanced Features**
   - Voice chat integration
   - Video calls
   - Screen sharing
   - Drawing/whiteboard

### Low Priority

7. **Performance**
   - Code diff optimization (currently last-write-wins)
   - Compression for large files
   - Lazy loading for large codebases

8. **UI/UX**
   - Themes (dark/light)
   - Custom keybindings
   - Split-screen view
   - Minimap

9. **Analytics**
   - Usage statistics
   - Collaboration metrics
   - Error tracking

## ⚠️ Limitations

### Current Implementation

1. **Conflict Resolution**
   - Uses simple last-write-wins strategy
   - No Operational Transformation (OT) or CRDT
   - Can lose edits if two users type simultaneously
   - **Production Solution**: Implement OT or use CRDT library

2. **Scalability**
   - WebSocket state stored in memory
   - Single server limitation
   - **Production Solution**: Use Redis for distributed state

3. **Autocomplete**
   - Mock implementation with pattern matching
   - Not context-aware beyond simple patterns
   - **Production Solution**: Integrate real AI models

4. **Security**
   - No authentication/authorization
   - Rooms are public if you know the ID
   - No input sanitization for code
   - **Production Solution**: Add auth system, validate inputs

5. **Persistence**
   - Code saved but no version history UI
   - Snapshots created but not exposed
   - **Production Solution**: Build history viewer

6. **Error Handling**
   - Basic error handling
   - No retry logic for failed connections
   - **Production Solution**: Add exponential backoff, reconnection

### Known Issues

- Large files (>1MB) may cause performance issues
- WebSocket connections may drop on network changes
- No mobile optimization
- Browser compatibility: Modern browsers only (WebSocket required)

## 📝 License

This project is created for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Built with ❤️ using FastAPI and React**