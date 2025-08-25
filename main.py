from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

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

app = FastAPI(
    title="XML File Server", 
    description="A simple server to serve and replace XML files"
)

@app.on_event("startup")
async def startup_event():
    """Log configuration on startup"""
    print(f"XML File Server starting up...")
    print(f"XML file path: {XML_FILE_PATH}")
    print(f"Server will be available at: http://localhost:8000")

@app.get("/cubes/list", summary="Retrieve the XML file")
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

@app.post("/xml", summary="Replace the XML file")
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

@app.post("/restart-tomcat", summary="Restart Tomcat Server")
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

@app.get("/cubes/enumerate", summary="Count cubes in XML file")
async def enumerate_cubes():
    """
    Count the number of cubes defined in the Monza.xml file.
    
    Returns:
        JSON with cube count and cube names
    """
    try:
        if not os.path.exists(XML_FILE_PATH):
            raise HTTPException(status_code=404, detail="XML file not found")
        
        # Parse the XML file
        tree = ET.parse(XML_FILE_PATH)
        root = tree.getroot()
        
        # Find all Cube elements
        cubes = root.findall('.//Cube')
        
        # Get cube names
        cube_names = [cube.get('name', 'Unnamed Cube') for cube in cubes]
        
        return {
            "message": f"Found {len(cubes)} cube(s) in Monza.xml",
            "count": len(cubes),
            "cubes": cube_names,
            "file_path": XML_FILE_PATH
        }
        
    except ET.ParseError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing XML file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting cubes: {str(e)}")

@app.get("/", summary="API Information")
async def root():
    """
    Get API information and available endpoints.
    """
    return {
        "message": "XML File Server",
        "base_path": "/",
        "endpoints": {
            "GET /cubes/list": "Retrieve the current XML file",
            "GET /cubes/enumerate": "Count cubes in XML file",
            "POST /xml": "Replace the XML file (upload new XML file)",
            "POST /restart-tomcat": "Restart Tomcat server",
            "GET /": "This information page"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 