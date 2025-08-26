# Monza Cube Designer

A FastAPI server for managing Mondrian OLAP XML schemas with comprehensive cube management capabilities.

## Features

### Core Functionality
- **XML File Management**: Serve and manage Mondrian OLAP XML schema files
- **Cube Operations**: Full CRUD operations for OLAP cubes
- **Tomcat Integration**: Restart Tomcat server remotely
- **Configuration Management**: Load XML file path from `config.json`
- **Cross-Platform Support**: Management scripts for both Linux/macOS and Windows

### Cube Management Endpoints
- **GET /monza/admin/cubes/list**: Retrieve the complete XML schema
- **GET /monza/admin/cubes/enumerate**: Count and list all cubes in the schema
- **GET /monza/admin/cubes/{cube_name}**: Get a specific cube by name
- **POST /monza/admin/cubes/create**: Create a new cube with JSON input
- **PUT /monza/admin/cubes/{cube_name}**: Update an existing cube
- **DELETE /monza/admin/cubes/{cube_name}**: Delete a cube from the schema

### System Management
- **POST /monza/admin/restart-tomcat**: Restart Tomcat server (Linux)
- **GET /monza/admin**: API information and available endpoints

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kainam-jg/monza_cube_designer.git
cd monza_cube_designer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the XML file path in `config.json`:
```json
{
    "xml_file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml",
    "description": "Configuration for XML File Server"
}
```

## Running the Server

### Option 1: Direct Python execution
```bash
python main.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 3: Using the management scripts (Recommended)

#### Linux/macOS:
```bash
# Start the server (activates virtual environment automatically)
./start_server.sh

# Check server status
./check_server.sh

# Stop the server
./stop_server.sh
```

#### Windows:
```cmd
# Start the server (activates virtual environment automatically)
start_server.bat

# Check server status
check_server.bat

# Stop the server
stop_server.bat
```

The server will be available at `http://localhost:8000/monza/admin`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/monza/admin/docs
- **Alternative API docs**: http://localhost:8000/monza/admin/redoc

## API Endpoints

### Cube Management

#### List All Cubes
```bash
curl http://localhost:8000/monza/admin/cubes/enumerate
```
**Response:**
```json
{
    "message": "Found 2 cube(s) in Monza.xml",
    "count": 2,
    "cubes": ["Vehicle Sales", "FoodMart Cube"],
    "file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml"
}
```

#### Get Specific Cube
```bash
curl http://localhost:8000/monza/admin/cubes/Vehicle%20Sales
```
**Response:**
```json
{
    "message": "Retrieved cube 'Vehicle Sales'",
    "cube_name": "Vehicle Sales",
    "xml": "<Cube name=\"Vehicle Sales\">...</Cube>",
    "file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml"
}
```

#### Create New Cube
```bash
curl -X POST http://localhost:8000/monza/admin/cubes/create \
  -H "Content-Type: application/json" \
  -d '{
    "cube_name": "Sales Analytics",
    "table_name": "sales_facts",
    "dimensions": [
      {
        "name": "Time",
        "hierarchies": [
          {
            "hasAll": true,
            "allMemberName": "All Time",
            "levels": [
              {
                "name": "Year",
                "column": "year",
                "type": "Numeric",
                "uniqueMembers": true
              },
              {
                "name": "Quarter",
                "column": "quarter",
                "type": "String",
                "uniqueMembers": false
              }
            ]
          }
        ]
      }
    ],
    "measures": [
      {
        "name": "Total Sales",
        "column": "sales_amount",
        "aggregator": "sum",
        "formatString": "#,##0.00"
      }
    ]
  }'
```

#### Update Cube
```bash
curl -X PUT http://localhost:8000/monza/admin/cubes/Vehicle%20Sales \
  -H "Content-Type: application/json" \
  -d '{
    "cube_name": "Vehicle Sales Updated",
    "table_name": "vehicle_sales",
    "dimensions": [...],
    "measures": [...]
  }'
```

#### Delete Cube
```bash
curl -X DELETE http://localhost:8000/monza/admin/cubes/Vehicle%20Sales
```

### System Management

#### Restart Tomcat Server
```bash
curl -X POST http://35.208.212.1:8000/monza/admin/restart-tomcat
```

## Cube Schema Structure

The API supports creating complex Mondrian OLAP cubes with the following structure:

### Dimension Structure
```json
{
  "name": "Dimension Name",
  "hierarchies": [
    {
      "name": "Hierarchy Name (optional)",
      "hasAll": true,
      "allMemberName": "All Members",
      "levels": [
        {
          "name": "Level Name",
          "column": "database_column",
          "type": "String|Numeric|Integer|Boolean",
          "uniqueMembers": true
        }
      ]
    }
  ]
}
```

### Measure Structure
```json
{
  "name": "Measure Name",
  "column": "database_column",
  "aggregator": "sum|count|avg|min|max",
  "formatString": "#,##0.00"
}
```

## Architecture

### Modular Design
- **`main.py`**: FastAPI application with endpoint definitions
- **`cube_manager.py`**: Core cube management logic and XML operations
- **`config.json`**: Configuration management
- **Management Scripts**: Cross-platform server management

### Key Components

#### CubeManager Class
- **XML Parsing**: Robust XML file handling with error management
- **Validation**: Comprehensive input validation using Pydantic models
- **Formatting**: Automatic XML formatting with proper indentation
- **Error Handling**: Detailed error messages with available cube suggestions

#### Pydantic Models
- **Level**: Individual hierarchy levels with type and uniqueness settings
- **Hierarchy**: Complete hierarchy definitions with multiple levels
- **Dimension**: Dimension definitions with multiple hierarchies
- **Measure**: Measure definitions with aggregators and formatting
- **CreateCubeRequest**: Complete cube creation request structure

## File Structure

```
monza_cube_designer/
├── main.py              # FastAPI application with endpoints
├── cube_manager.py      # Core cube management logic
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── start_server.sh      # Linux/macOS start script
├── stop_server.sh       # Linux/macOS stop script
├── check_server.sh      # Linux/macOS status script
├── start_server.bat     # Windows start script
├── stop_server.bat      # Windows stop script
├── check_server.bat     # Windows status script
├── samples/             # Sample XML files for reference
└── README.md           # This file
```

## Configuration

### config.json
```json
{
    "xml_file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml",
    "description": "Configuration for XML File Server"
}
```

### Environment Setup
- **Virtual Environment**: Scripts automatically activate `/opt/tomcat/.venv` (Linux) or `/opt/tomcat/.venv/Scripts/activate.bat` (Windows)
- **Logging**: Server logs are stored in `logs/server.log`
- **Process Management**: PID files track running server processes

## Error Handling

The API provides comprehensive error handling:

- **404 Not Found**: Cube or XML file not found
- **400 Bad Request**: Invalid cube data or duplicate cube names
- **500 Internal Server Error**: XML parsing or file system errors

All errors include detailed messages and suggestions for resolution.

## Development Notes

- **XML Formatting**: All XML operations automatically format output with proper indentation
- **Validation**: Strict validation ensures only valid Mondrian OLAP schemas are created
- **Modularity**: Cube management logic is separated for maintainability
- **Cross-Platform**: Full support for both Linux and Windows environments
- **Production Ready**: Includes proper logging, error handling, and process management

## Dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
```

## License

This project is part of the Monza Cube Designer system for managing Mondrian OLAP schemas. 