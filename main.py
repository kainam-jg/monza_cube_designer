from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import json
import subprocess
from cube_manager import CubeManager, CreateCubeRequest

# Load configuration
def load_config():
    """Load configuration from config.json file"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Warning: config.json not found, using default configuration")
        return {"xml_file_path": "./Monza.xml"}
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        return {"xml_file_path": "./Monza.xml"}

# Load configuration on startup
config = load_config()
XML_FILE_PATH = config.get("xml_file_path", "./Monza.xml")

# Initialize cube manager
cube_manager = CubeManager(XML_FILE_PATH)

app = FastAPI(
    title="XML File Server", 
    description="A simple server to serve and replace XML files"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    """Log configuration on startup"""
    print(f"XML File Server starting up...")
    print(f"XML file path: {XML_FILE_PATH}")
    print(f"Server will be available at: http://localhost:8000")

@app.get("/application/list", summary="Retrieve the XML file")
async def get_xml():
    """
    Retrieve the current XML file.
    
    Returns:
        The XML file as a response
    """
    if not os.path.exists(XML_FILE_PATH):
        raise HTTPException(status_code=404, detail="XML file not found")
    
    return FileResponse(
        path=XML_FILE_PATH,
        media_type="application/xml",
        filename="Monza.xml"
    )

@app.post("/application/replace", summary="Replace the XML file")
async def replace_xml(file: UploadFile = File(...)):
    """
    Replace the current XML file with a new one.
    
    Args:
        file: The new XML file to upload
        
    Returns:
        Success message
    """
    # Validate file type
    if not file.content_type or "xml" not in file.content_type.lower():
        raise HTTPException(status_code=400, detail="File must be an XML file")
    
    # Validate file extension
    if not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must have .xml extension")
    
    try:
        # Save the uploaded file
        with open(XML_FILE_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"message": "XML file replaced successfully", "filename": file.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

@app.post("/application/restart", summary="Restart Application")
async def restart_tomcat():
    """
    Restart the Tomcat server using systemctl.
    
    Returns:
        Success or error message
    """
    try:
        # Execute the systemctl restart command
        result = subprocess.run(
            ["sudo", "systemctl", "restart", "tomcat"],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            return {
                "message": "Tomcat server restarted successfully",
                "status": "success",
                "stdout": result.stdout.strip() if result.stdout else "",
                "timestamp": "restart completed"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart Tomcat: {result.stderr.strip()}"
            )
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Tomcat restart timed out after 30 seconds"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="systemctl command not found or sudo not available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error restarting Tomcat: {str(e)}"
        )

@app.get("/application/status", summary="Check Application Status")
async def check_tomcat_status():
    """
    Check the status of the Tomcat server using systemctl.
    
    Returns:
        Tomcat service status information
    """
    try:
        # Execute the systemctl status command
        result = subprocess.run(
            ["sudo", "systemctl", "status", "tomcat"],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout for status check
        )
        
        if result.returncode == 0:
            return {
                "message": "Tomcat service status retrieved successfully",
                "status": "success",
                "stdout": result.stdout.strip() if result.stdout else "",
                "timestamp": "status check completed"
            }
        else:
            # systemctl status returns non-zero for inactive services, but we still want to show the output
            return {
                "message": "Tomcat service status retrieved",
                "status": "service_inactive",
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "return_code": result.returncode,
                "timestamp": "status check completed"
            }
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Tomcat status check timed out after 10 seconds"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="systemctl command not found or sudo not available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Tomcat status: {str(e)}"
        )

@app.get("/application/enumerate", summary="Count cubes in XML file")
async def enumerate_cubes():
    """
    Count the number of cubes defined in the Monza.xml file.
    
    Returns:
        JSON with cube count and cube names
    """
    return cube_manager.enumerate_cubes()

@app.get("/cubes/{cube_name}", summary="Get cube by name")
async def get_cube_by_name(cube_name: str):
    """
    Get a specific cube by name from the Monza.xml file.
    
    Args:
        cube_name: The name of the cube to retrieve
        
    Returns:
        The complete cube XML element
    """
    return cube_manager.get_cube_by_name(cube_name)

@app.post("/cubes/create", summary="Create a new cube")
async def create_cube(cube_request: CreateCubeRequest):
    """
    Create a new cube in the Monza.xml file.
    
    Args:
        cube_request: JSON object containing cube definition
        
    Returns:
        Success message with cube details
    """
    return cube_manager.create_cube(cube_request)

@app.delete("/cubes/{cube_name}", summary="Delete a cube")
async def delete_cube(cube_name: str):
    """
    Delete a cube from the Monza.xml file.
    
    Args:
        cube_name: The name of the cube to delete
        
    Returns:
        Success message
    """
    return cube_manager.delete_cube(cube_name)

@app.put("/cubes/{cube_name}", summary="Update a cube")
async def update_cube(cube_name: str, cube_request: CreateCubeRequest):
    """
    Update an existing cube in the Monza.xml file.
    
    Args:
        cube_name: The name of the cube to update
        cube_request: JSON object containing new cube definition
        
    Returns:
        Success message with cube details
    """
    return cube_manager.update_cube(cube_name, cube_request)

@app.get("/", summary="API Information")
async def root():
    """
    Get API information and available endpoints.
    """
    return {
        "message": "XML File Server",
        "base_path": "/",
        "endpoints": {
            "Application Level (entire XML file)": {
                "GET /application/list": "Retrieve the current XML file",
                "GET /application/enumerate": "Count cubes in XML file",
                "POST /application/replace": "Replace the XML file (upload new XML file)"
            },
            "Cube Level (individual cubes)": {
                "GET /cubes/{cube_name}": "Get specific cube by name",
                "POST /cubes/create": "Create a new cube",
                "DELETE /cubes/{cube_name}": "Delete a cube",
                "PUT /cubes/{cube_name}": "Update a cube"
            },
            "System": {
                "GET /application/status": "Check Application Status",
                "POST /application/restart": "Restart Application",
                "GET /": "This information page"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 