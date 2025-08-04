# XML File Server

A simple FastAPI server that serves and manages XML files.

## Features

- **GET /xml**: Retrieve the current XML file (Monza.xml)
- **POST /xml**: Replace the XML file with a new one
- **GET /**: API information and available endpoints
- **Configuration**: Loads XML file path from `config.json`

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Option 1: Direct Python execution
```bash
python main.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using the management scripts (Recommended)

```bash
# Start the server
./start_server.sh

# Check server status
./check_server.sh

# Stop the server
./stop_server.sh
```

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## Usage Examples

### Retrieve the XML file
```bash
curl http://localhost:8000/xml
```

### Replace the XML file
```bash
curl -X POST http://localhost:8000/xml \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_new_file.xml"
```

### Using Python requests
```python
import requests

# Get the XML file
response = requests.get('http://localhost:8000/xml')
print(response.text)

# Replace the XML file
with open('new_data.xml', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/xml', files=files)
    print(response.json())
```

## Configuration

The server uses a `config.json` file to specify the path to the XML file:

```json
{
    "xml_file_path": "./Monza.xml",
    "description": "Configuration for XML File Server"
}
```

You can modify the `xml_file_path` to point to any location where you want to store the Monza.xml file.

## File Structure

```
monza_cube_designer/
├── main.py              # FastAPI application
├── config.json          # Configuration file
├── Monza.xml            # Sample XML file
├── requirements.txt      # Python dependencies
├── start_server.sh      # Server start script
├── stop_server.sh       # Server stop script
├── check_server.sh      # Server status script
└── README.md            # This file
```

## Notes

- The server stores the XML file as `Monza.xml` at the path specified in `config.json`
- Only XML files are accepted for upload
- The file must have a `.xml` extension
- The server validates both content-type and file extension
- If `config.json` is not found, the server uses `./Monza.xml` as the default path
- Server logs are stored in `logs/server.log`
- PID files are used to track running server processes 