# FastAPI Backend

A simple FastAPI backend server.

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

Start the server with:
```
python main.py
```

Or using uvicorn directly:
```
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

FastAPI automatically generates API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 