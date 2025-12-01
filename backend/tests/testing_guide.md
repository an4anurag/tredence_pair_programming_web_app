# Testing Guide

This guide provides comprehensive instructions for testing the Pair Programming application.

## Table of Contents

1. [Quick Test](#quick-test)
2. [Manual Testing](#manual-testing)
3. [Automated Testing](#automated-testing)
4. [WebSocket Testing](#websocket-testing)
5. [Performance Testing](#performance-testing)

## Quick Test

### Using the Interactive API Documentation

1. Start the server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Open browser to: http://localhost:8000/docs

3. Test the flow:
   - Click on `POST /rooms` → Try it out → Execute
   - Copy the `roomId` from the response
   - Open two browser tabs to test WebSocket collaboration

## Manual Testing

### 1. Test Room Creation

```bash
# Create a room
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}' | jq

# Expected response:
# {
#   "roomId": "abc12345",
#   "code": "# Write your Python code here\n\n",
#   "language": "python",
#   "created_at": "2025-01-15T10:30:00Z"
# }
```

### 2. Test Room Retrieval

```bash
# Get room details (replace ROOM_ID)
curl http://localhost:8000/rooms/ROOM_ID | jq
```

### 3. Test Autocomplete

```bash
# Get autocomplete suggestion
curl -X POST http://localhost:8000/autocomplete \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(",
    "cursorPosition": 25,
    "language": "python"
  }' | jq

# Expected response:
# {
#   "suggestion": "'Hello, World!')",
#   "confidence": 0.85,
#   "type": "completion"
# }
```

### 4. Test Health Check

```bash
curl http://localhost:8000/health | jq

# Expected: {"status": "healthy"}
```

## Automated Testing

### Running Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rooms.py -v

# Run specific test
pytest tests/test_rooms.py::test_create_room -v
```

### Test Structure

```
tests/
├── test_rooms.py          # Room endpoint tests
├── test_autocomplete.py   # Autocomplete tests
└── test_websocket.py      # WebSocket tests (to be implemented)
```

### Writing New Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_your_feature():
    """Test description."""
    response = client.get("/your-endpoint")
    assert response.status_code == 200
    assert "expected_key" in response.json()
```

## WebSocket Testing

### Option 1: Using Browser Console

```javascript
// Open browser console (F12)

// Create WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/ROOM_ID');

// Listen for messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send code update
ws.send(JSON.stringify({
    type: 'code_update',
    code: 'print("Hello from WebSocket!")'
}));

// Check connection status
console.log('WebSocket state:', ws.readyState);
// 0 = CONNECTING, 1 = OPEN, 2 = CLOSING, 3 = CLOSED
```

### Option 2: Using Python Client

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/ROOM_ID"
    
    async with websockets.connect(uri) as websocket:
        # Receive initial state
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Send code update
        await websocket.send(json.dumps({
            "type": "code_update",
            "code": "print('Hello')"
        }))
        
        # Receive echo
        response = await websocket.recv()
        print(f"Received: {response}")

# Run test
asyncio.run(test_websocket())
```

### Option 3: Using websocat (CLI tool)

```bash
# Install websocat
cargo install websocat
# Or on macOS: brew install websocat

# Connect to room
websocat ws://localhost:8000/ws/ROOM_ID

# Type message and press Enter:
{"type": "code_update", "code": "print('test')"}
```

### Multi-User Testing

Open multiple terminals/browsers and connect to the same room:

**Terminal 1:**
```bash
websocat ws://localhost:8000/ws/test-room
{"type": "code_update", "code": "# User 1 typing"}
```

**Terminal 2:**
```bash
websocat ws://localhost:8000/ws/test-room
# Should receive message from User 1
# Send your own message
{"type": "code_update", "code": "# User 2 typing"}
```

## Performance Testing

### Load Testing with locust

1. Install locust:
   ```bash
   pip install locust
   ```

2. Create `locustfile.py`:
   ```python
   from locust import HttpUser, task, between
   
   class PairProgrammingUser(HttpUser):
       wait_time = between(1, 3)
       
       @task(3)
       def create_room(self):
           self.client.post("/rooms", json={"language": "python"})
       
       @task(1)
       def get_autocomplete(self):
           self.client.post("/autocomplete", json={
               "code": "def hello():\n    print(",
               "cursorPosition": 25,
               "language": "python"
           })
   ```

3. Run load test:
   ```bash
   locust -f locustfile.py --host=http://localhost:8000
   ```

4. Open http://localhost:8089 and configure:
   - Number of users: 10
   - Spawn rate: 2
   - Host: http://localhost:8000

### WebSocket Performance Testing

Test concurrent WebSocket connections:

```python
import asyncio
import websockets
import json
import time

async def connect_user(room_id, user_id, duration=30):
    """Simulate a user connecting and sending messages."""
    uri = f"ws://localhost:8000/ws/{room_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"User {user_id} connected")
            
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < duration:
                # Send code update
                await websocket.send(json.dumps({
                    "type": "code_update",
                    "code": f"# User {user_id} - Update {message_count}"
                }))
                message_count += 1
                
                # Wait for response
                await websocket.recv()
                await asyncio.sleep(1)
            
            print(f"User {user_id} sent {message_count} messages")
    except Exception as e:
        print(f"User {user_id} error: {e}")

async def stress_test(num_users=10, duration=30):
    """Run stress test with multiple concurrent users."""
    room_id = "stress-test-room"
    
    # Create room first
    import requests
    response = requests.post("http://localhost:8000/rooms")
    room_id = response.json()["roomId"]
    
    print(f"Starting stress test with {num_users} users for {duration}s")
    print(f"Room ID: {room_id}")
    
    # Create tasks for all users
    tasks = [
        connect_user(room_id, i, duration)
        for i in range(num_users)
    ]
    
    # Run all users concurrently
    await asyncio.gather(*tasks)
    
    print("Stress test complete")

# Run stress test
if __name__ == "__main__":
    asyncio.run(stress_test(num_users=5, duration=10))
```

### Database Performance

Monitor database performance:

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;

-- Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## Integration Testing Scenarios

### Scenario 1: Full Collaboration Flow

1. User A creates room
2. User B joins room via roomId
3. User A types code
4. User B sees updates in real-time
5. User B modifies code
6. User A sees User B's updates
7. Both users request autocomplete
8. Both users disconnect

### Scenario 2: Autocomplete Integration

1. Create room
2. Connect via WebSocket
3. Send code update with incomplete statement
4. Request autocomplete
5. Apply suggestion
6. Verify code updated in database

### Scenario 3: Error Handling

1. Try to join non-existent room
2. Send invalid WebSocket message
3. Send autocomplete with invalid cursor position
4. Disconnect during code update
5. Verify graceful error handling

## Test Data

### Sample Code Snippets

```python
# Python samples for testing
test_codes = [
    "def hello():\n    print(",
    "class MyClass:\n    ",
    "for i in range(",
    "if x > 10:\n    ",
    "import numpy as ",
]
```

### Expected Autocomplete Results

```json
{
  "print(": "'Hello, World!')",
  "class MyClass:": "def __init__(self):",
  "for i in range(": "10):",
  "if x > 10:": "pass",
  "import numpy as ": "np"
}
```

## Troubleshooting Tests

### Common Issues

**1. Database Connection Errors**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d pair_programming
```

**2. WebSocket Connection Refused**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://localhost:8000/ws/test-room
```

**3. Import Errors in Tests**
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: pair_programming_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=app
```

## Test Checklist

Before deploying:

- [ ] All unit tests pass
- [ ] Room creation/retrieval/deletion works
- [ ] Autocomplete returns valid suggestions
- [ ] WebSocket connections establish successfully
- [ ] Multiple users can collaborate in real-time
- [ ] Code persists in database
- [ ] Disconnections handled gracefully
- [ ] Error responses are appropriate
- [ ] API documentation is accurate
- [ ] Performance is acceptable under load

---

**Happy Testing! 🧪**