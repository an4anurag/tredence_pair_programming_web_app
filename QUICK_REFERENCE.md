# Quick Reference Guide

## 🚀 Quick Start Commands

### Docker Setup
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Local Setup
```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rooms` | Create new room |
| GET | `/rooms/{room_id}` | Get room details |
| DELETE | `/rooms/{room_id}` | Delete room |
| POST | `/autocomplete` | Get code suggestion |
| GET | `/` | Health check |
| GET | `/docs` | API documentation |

### WebSocket

```
ws://localhost:8000/ws/{room_id}
```

## 💻 Code Examples

### Create Room (cURL)
```bash
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}'
```

### Create Room (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/rooms",
    json={"language": "python"}
)
room_id = response.json()["roomId"]
print(f"Room created: {room_id}")
```

### Create Room (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/rooms', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ language: 'python' })
});
const data = await response.json();
console.log('Room ID:', data.roomId);
```

### WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/' + roomId);

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.type === 'code_update') {
    editor.setValue(data.code);
  }
};

// Send code update
ws.send(JSON.stringify({
  type: 'code_update',
  code: editor.getValue()
}));
```

### WebSocket Connection (Python)
```python
import asyncio
import websockets
import json

async def connect():
    uri = f"ws://localhost:8000/ws/{room_id}"
    async with websockets.connect(uri) as ws:
        # Receive initial state
        msg = await ws.recv()
        print(json.loads(msg))
        
        # Send update
        await ws.send(json.dumps({
            "type": "code_update",
            "code": "print('Hello')"
        }))

asyncio.run(connect())
```

### Autocomplete Request
```bash
curl -X POST http://localhost:8000/autocomplete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(",
    "cursorPosition": 25,
    "language": "python"
  }'
```

## 🗄️ Database Commands

### PostgreSQL Access
```bash
# Docker
docker-compose exec db psql -U postgres -d pair_programming

# Local
psql -h localhost -U postgres -d pair_programming
```

### Useful Queries
```sql
-- List all rooms
SELECT id, language, created_at FROM rooms;

-- Count active rooms
SELECT COUNT(*) FROM rooms;

-- Get room code
SELECT code FROM rooms WHERE id = 'abc123';

-- Delete old rooms (older than 24 hours)
DELETE FROM rooms WHERE created_at < NOW() - INTERVAL '24 hours';

-- View code snapshots for a room
SELECT * FROM code_snapshots WHERE room_id = 'abc123' ORDER BY timestamp DESC;
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Current version
alembic current
```

## 🧪 Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rooms.py -v

# Run and show print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run in parallel
pytest tests/ -n auto
```

## 📊 Monitoring

### Check Server Status
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Docker
docker-compose logs -f backend

# Local (if using systemd)
journalctl -u pair-programming -f
```

### Database Monitoring
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Connection details
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE datname = 'pair_programming';

-- Table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables WHERE schemaname = 'public';
```

## 🔧 Development Workflow

### Adding New Feature

1. **Create branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Add database model** (if needed)
   ```python
   # app/models.py
   class NewModel(Base):
       __tablename__ = "new_table"
       id = Column(Integer, primary_key=True)
   ```

3. **Create migration**
   ```bash
   alembic revision --autogenerate -m "Add new_table"
   alembic upgrade head
   ```

4. **Add Pydantic schema**
   ```python
   # app/schemas.py
   class NewSchema(BaseModel):
       field: str
   ```

5. **Create service**
   ```python
   # app/services/new_service.py
   class NewService:
       def __init__(self, db: Session):
           self.db = db
   ```

6. **Add router**
   ```python
   # app/routers/new_router.py
   router = APIRouter()
   
   @router.post("/endpoint")
   async def endpoint():
       pass
   ```

7. **Register router**
   ```python
   # main.py
   from app.routers import new_router
   app.include_router(new_router.router, prefix="/prefix")
   ```

8. **Write tests**
   ```python
   # tests/test_new_feature.py
   def test_new_feature():
       response = client.get("/endpoint")
       assert response.status_code == 200
   ```

9. **Run tests**
   ```bash
   pytest tests/test_new_feature.py -v
   ```

## 🐛 Debugging

### Enable Debug Logging
```python
# main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Debugging
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use ipdb (better)
import ipdb; ipdb.set_trace()
```

### Debug WebSocket Issues
```bash
# Test WebSocket with curl
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws/test-room
```

## 📦 Dependency Management

```bash
# Add new dependency
pip install package-name
pip freeze > requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt

# Check outdated packages
pip list --outdated
```

## 🔐 Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://user:pass@host:5432/db
DEBUG=True
LOG_LEVEL=INFO
```

## 🚢 Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_ORIGINS`
- [ ] Setup proper logging
- [ ] Enable HTTPS
- [ ] Setup database backups
- [ ] Configure rate limiting
- [ ] Add monitoring/alerting
- [ ] Document deployment process
- [ ] Test rollback procedure

## 📝 Useful SQL Snippets

```sql
-- Backup database
pg_dump -U postgres pair_programming > backup.sql

-- Restore database
psql -U postgres pair_programming < backup.sql

-- Reset database
DROP DATABASE pair_programming;
CREATE DATABASE pair_programming;

-- Vacuum database
VACUUM ANALYZE;
```

## 🔗 Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- PostgreSQL Docs: https://www.postgresql.org/docs
- WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- Pydantic Docs: https://docs.pydantic.dev

## 💡 Tips & Tricks

### Restart Server on File Change
```bash
uvicorn main:app --reload
```

### Run Server in Background
```bash
nohup uvicorn main:app &
```

### Format Code
```bash
# Install
pip install black isort

# Format
black app/
isort app/
```

### Lint Code
```bash
# Install
pip install flake8 pylint

# Lint
flake8 app/
pylint app/
```

### Type Checking
```bash
# Install
pip install mypy

# Check
mypy app/
```

---

**Keep this handy! 📌**