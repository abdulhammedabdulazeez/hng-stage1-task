# HNG Stage 1 Task - String Analyzer API

A FastAPI-based string analysis service that provides various string operations and properties analysis.

## Features

- **String Analysis**: Analyze strings for various properties
- **Palindrome Detection**: Check if strings are palindromes (ignoring non-alphanumeric characters)
- **Character Frequency**: Get frequency count of characters in strings
- **Word Count**: Count words in strings
- **SHA-256 Hashing**: Generate unique identifiers for strings
- **Filtering & Search**: Query stored strings with various filters
- **Natural Language Queries**: Search using natural language

## API Endpoints

### POST `/strings`
Create and analyze a new string.

**Request:**
```json
{
  "value": "Hello World"
}
```

**Response:**
```json
{
  "id": "sha256_hash",
  "value": "Hello World",
  "properties": {
    "length": 11,
    "is_palindrome": false,
    "unique_characters": 8,
    "word_count": 2,
    "sha256_hash": "sha256_hash",
    "character_frequency_map": {"H": 1, "e": 1, "l": 3, "o": 2, " ": 1, "W": 1, "r": 1, "d": 1}
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET `/strings`
Get all stored strings with optional filtering.

**Query Parameters:**
- `is_palindrome`: Filter by palindrome status
- `min_length`: Minimum string length
- `max_length`: Maximum string length
- `word_count`: Exact word count
- `contains_character`: Character to search for

### GET `/strings/{string_value}`
Get a specific string by its value.

### DELETE `/strings/{string_value}`
Delete a string by its value.

### GET `/strings/query`
Search strings using natural language queries.

## Installation & Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd hng-stage1-task
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

### Create a string:
```bash
curl -X POST "http://localhost:8000/strings" \
  -H "Content-Type: application/json" \
  -d '{"value": "A man, a plan, a canal: Panama"}'
```

### Get all strings:
```bash
curl "http://localhost:8000/strings"
```

### Filter palindromes:
```bash
curl "http://localhost:8000/strings?is_palindrome=true"
```

## Project Structure

```
hng-stage1-task/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── routes.py        # API endpoints
│   ├── services.py      # Business logic
│   ├── schemas.py       # Pydantic models
│   └── storage.py       # In-memory storage
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Deployment

### Railway Deployment

This application is configured for easy deployment to Railway using a `start.sh` script:

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login to Railway:**
```bash
railway login
```

3. **Initialize Railway project:**
```bash
railway init
```

4. **Deploy to Railway:**
```bash
railway up
```

5. **Get your deployment URL:**
```bash
railway domain
```

### Manual Railway Deployment

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect the Python project and use the `start.sh` script
4. The app will be deployed automatically

### Environment Variables

The application uses the following environment variables:
- `PORT`: Automatically set by Railway (default: 8000)

## Technologies Used

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server
- **Python 3.12+**: Programming language
- **Railway**: Cloud deployment platform
