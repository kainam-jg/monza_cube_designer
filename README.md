# Monza Cube Designer

A FastAPI server for managing Mondrian OLAP XML schemas with comprehensive cube management capabilities.

## Features

### Core Functionality
- **XML File Management**: Serve and manage Mondrian OLAP XML schema files
- **Cube Operations**: Full CRUD operations for OLAP cubes
- **Database Integration**: ClickHouse database connectivity and table inspection
- **Application Management**: Restart application remotely
- **Configuration Management**: Load XML file path and database settings from `config.json`
- **Cross-Platform Support**: Management scripts for both Linux/macOS and Windows
- **CORS Support**: Full cross-origin request support for web applications

### API Organization
The API is organized into logical groups:

#### Application-Level Endpoints (entire XML file operations)
- **GET /application/list**: Retrieve the complete XML schema
- **GET /application/enumerate**: Count and list all cubes in the schema
- **POST /application/replace**: Replace the XML file with a new upload
- **GET /application/status**: Check application status
- **POST /application/restart**: Restart the application

#### Cube-Level Endpoints (individual cube operations)
- **GET /cubes/{cube_name}**: Get a specific cube by name
- **POST /cubes/create**: Create a new cube with JSON input
- **PUT /cubes/{cube_name}**: Update an existing cube
- **DELETE /cubes/{cube_name}**: Delete a cube from the schema

#### Database-Level Endpoints (ClickHouse database operations)
- **GET /database/tables/{schema_name}**: List all tables with '_k' in their names
- **GET /database/columns/{schema_name}/{table_name}**: Get table columns and data types

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

3. Configure the XML file path and database settings in `config.json`:
```json
{
    "xml_file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml",
    "description": "Configuration for XML File Server",
    "database": {
        "host": "3.135.214.254",
        "port": 8123,
        "username": "default",
        "password": "your_password",
        "database": "default",
        "secure": false
    }
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

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc
- **API Information**: http://localhost:8000/ (root endpoint)

## API Endpoints

### Application-Level Operations

#### List All Cubes
```bash
curl http://localhost:8000/application/enumerate
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

#### Retrieve XML File
```bash
curl http://localhost:8000/application/list
```
**Response:** Returns the complete XML file as a download

#### Replace XML File
```bash
curl -X POST http://localhost:8000/application/replace \
  -F "file=@new_schema.xml"
```

#### Check Application Status
```bash
curl http://localhost:8000/application/status
```
**Response:**
```json
{
    "message": "Tomcat service status retrieved successfully",
    "status": "success",
    "stdout": "● tomcat.service - Apache Tomcat...",
    "timestamp": "status check completed"
}
```

#### Restart Application
```bash
curl -X POST http://localhost:8000/application/restart
```

### Cube-Level Operations

#### Get Specific Cube
```bash
curl http://localhost:8000/cubes/Vehicle%20Sales
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
curl -X POST http://localhost:8000/cubes/create \
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
curl -X PUT http://localhost:8000/cubes/Vehicle%20Sales \
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
curl -X DELETE http://localhost:8000/cubes/Vehicle%20Sales
```

### Database-Level Operations

#### List Tables with '_k' in Name
```bash
curl http://localhost:8000/database/tables/default
```
**Response:**
```json
{
    "status": "success",
    "schema": "default",
    "tables_found": 4,
    "tables": [
        "daily_vehicle_sales_k",
        "foodmart_k",
        "ntsb_ontime_k",
        "vehicle_sales_variance_k"
    ],
    "query": "SELECT name as table_name FROM system.tables WHERE database = 'default' AND name LIKE '%_k%' ORDER BY name"
}
```

#### Get Table Columns and Data Types
```bash
curl http://localhost:8000/database/columns/default/foodmart_k
```
**Response:**
```json
{
    "status": "success",
    "schema": "default",
    "table": "foodmart_k",
    "columns_found": 65,
    "columns": [
        {
            "column_name": "calendar_date",
            "data_type": "Date"
        },
        {
            "column_name": "calendar_year",
            "data_type": "UInt16"
        },
        {
            "column_name": "calendar_qtr",
            "data_type": "LowCardinality(String)"
        }
    ],
    "query": "DESCRIBE default.foodmart_k"
}
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
- **`database.py`**: ClickHouse database connection and query management
- **`config.json`**: Configuration management for XML file and database settings
- **Management Scripts**: Cross-platform server management

### Key Components

#### CubeManager Class
- **XML Parsing**: Robust XML file handling with error management
- **Validation**: Comprehensive input validation using Pydantic models
- **Formatting**: Automatic XML formatting with proper indentation
- **Error Handling**: Detailed error messages with available cube suggestions

#### ClickHouseManager Class
- **Database Connection**: Automatic connection management with reconnection
- **Query Execution**: Safe query execution with error handling
- **Configuration**: Database settings loaded from config.json
- **Connection Testing**: Built-in connection validation and testing

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
├── database.py          # ClickHouse database connection management
├── config.json          # Configuration file (gitignored)
├── requirements.txt     # Python dependencies
├── start_server.sh      # Linux/macOS start script (gitignored)
├── stop_server.sh       # Linux/macOS stop script (gitignored)
├── check_server.sh      # Linux/macOS status script (gitignored)
├── start_server.bat     # Windows start script (gitignored)
├── stop_server.bat      # Windows stop script (gitignored)
├── check_server.bat     # Windows status script (gitignored)
├── samples/             # Sample XML files for reference
├── logs/                # Server log files
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Configuration

### config.json (gitignored)
```json
{
    "xml_file_path": "C:/cursor/tomcat11/apache-tomcat-11.0.9/lib/Monza.xml",
    "description": "Configuration for XML File Server",
    "database": {
        "host": "3.135.214.254",
        "port": 8123,
        "username": "default",
        "password": "your_password",
        "database": "default",
        "secure": false
    }
}
```

### .gitignore Configuration
The following files are excluded from version control:
- **`*.sh`**: Linux/Unix shell scripts
- **`*.bat`**: Windows batch files  
- **`config.json`**: Configuration file (may contain sensitive paths)

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
- **Logical Organization**: Endpoints are organized by scope (application vs cube level)

## Dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
clickhouse-connect==0.6.23
```

## License

This project is part of the Monza Cube Designer system for managing Mondrian OLAP schemas. 