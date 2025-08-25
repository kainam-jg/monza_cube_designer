import os
import xml.etree.ElementTree as ET
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path


# Pydantic models for cube creation
class Level(BaseModel):
    name: str = Field(..., description="Level name")
    column: str = Field(..., description="Level column name")
    type: str = Field(default="String", description="Level type")
    uniqueMembers: Optional[bool] = Field(default=None, description="Whether members are unique")

class Hierarchy(BaseModel):
    name: Optional[str] = Field(default=None, description="Hierarchy name")
    hasAll: bool = Field(default=True, description="Whether hierarchy has 'All' member")
    allMemberName: Optional[str] = Field(default=None, description="Name of the 'All' member")
    levels: List[Level] = Field(..., min_items=1, description="List of levels in the hierarchy")

class Dimension(BaseModel):
    name: str = Field(..., description="Dimension name")
    hierarchies: List[Hierarchy] = Field(..., min_items=1, description="List of hierarchies")

class Measure(BaseModel):
    name: str = Field(..., description="Measure name")
    column: str = Field(..., description="Measure column name")
    aggregator: str = Field(default="sum", description="Measure aggregator")
    formatString: Optional[str] = Field(default=None, description="Format string for the measure")

class CreateCubeRequest(BaseModel):
    cube_name: str = Field(..., description="Name of the cube")
    table_name: str = Field(..., description="Name of the fact table")
    dimensions: List[Dimension] = Field(..., min_items=1, description="List of dimensions")
    measures: List[Measure] = Field(..., min_items=1, description="List of measures")


class CubeManager:
    """Manages cube operations for Mondrian OLAP XML files"""
    
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
    
    def _format_xml(self, root):
        """Format XML with proper indentation and line breaks"""
        def indent(elem, level=0):
            i = "\n" + level*"  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for subelem in elem:
                    indent(subelem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        
        indent(root)
    
    def _validate_file_exists(self):
        """Validate that the XML file exists"""
        if not os.path.exists(self.xml_file_path):
            raise HTTPException(status_code=404, detail="XML file not found")
    
    def _parse_xml(self):
        """Parse the XML file and return the root element"""
        try:
            tree = ET.parse(self.xml_file_path)
            return tree, tree.getroot()
        except ET.ParseError as e:
            raise HTTPException(status_code=500, detail=f"Error parsing XML file: {str(e)}")
    
    def enumerate_cubes(self):
        """Count and list all cubes in the XML file"""
        self._validate_file_exists()
        tree, root = self._parse_xml()
        
        # Find all Cube elements
        cubes = root.findall('.//Cube')
        
        # Get cube names
        cube_names = [cube.get('name', 'Unnamed Cube') for cube in cubes]
        
        return {
            "message": f"Found {len(cubes)} cube(s) in Monza.xml",
            "count": len(cubes),
            "cubes": cube_names,
            "file_path": self.xml_file_path
        }
    
    def get_cube_by_name(self, cube_name: str):
        """Get a specific cube by name from the XML file"""
        self._validate_file_exists()
        tree, root = self._parse_xml()
        
        # Find the specific cube by name
        cube = root.find(f".//Cube[@name='{cube_name}']")
        
        if cube is None:
            # Get available cube names for better error message
            available_cubes = [c.get('name', 'Unnamed Cube') for c in root.findall('.//Cube')]
            raise HTTPException(
                status_code=404, 
                detail=f"Cube '{cube_name}' not found. Available cubes: {', '.join(available_cubes)}"
            )
        
        # Convert the cube element back to XML string
        cube_xml = ET.tostring(cube, encoding='unicode')
        
        return {
            "message": f"Retrieved cube '{cube_name}'",
            "cube_name": cube_name,
            "xml": cube_xml,
            "file_path": self.xml_file_path
        }
    
    def create_cube(self, cube_request: CreateCubeRequest):
        """Create a new cube in the XML file"""
        self._validate_file_exists()
        tree, root = self._parse_xml()
        
        # Check if cube with this name already exists
        existing_cube = root.find(f".//Cube[@name='{cube_request.cube_name}']")
        if existing_cube is not None:
            raise HTTPException(
                status_code=400, 
                detail=f"Cube '{cube_request.cube_name}' already exists"
            )
        
        # Find the Schema element (should be the root or first child)
        schema = root.find('.//Schema')
        if schema is None:
            # If no Schema found, assume root is the Schema
            schema = root
        
        # Find all existing cubes to determine insertion position
        existing_cubes = schema.findall('.//Cube')
        
        # Create the new cube element
        cube_elem = ET.SubElement(schema, "Cube")
        cube_elem.set("name", cube_request.cube_name)
        
        # Create the table element
        table_elem = ET.SubElement(cube_elem, "Table")
        table_elem.set("name", cube_request.table_name)
        
        # Create dimensions
        for dim in cube_request.dimensions:
            dimension_elem = ET.SubElement(cube_elem, "Dimension")
            dimension_elem.set("name", dim.name)
            
            # Create hierarchies for the dimension
            for hierarchy in dim.hierarchies:
                hierarchy_elem = ET.SubElement(dimension_elem, "Hierarchy")
                
                # Set hierarchy attributes
                if hierarchy.name:
                    hierarchy_elem.set("name", hierarchy.name)
                hierarchy_elem.set("hasAll", str(hierarchy.hasAll).lower())
                if hierarchy.allMemberName:
                    hierarchy_elem.set("allMemberName", hierarchy.allMemberName)
                
                # Create levels for the hierarchy
                for level in hierarchy.levels:
                    level_elem = ET.SubElement(hierarchy_elem, "Level")
                    level_elem.set("name", level.name)
                    level_elem.set("column", level.column)
                    level_elem.set("type", level.type)
                    if level.uniqueMembers is not None:
                        level_elem.set("uniqueMembers", str(level.uniqueMembers).lower())
        
        # Create measures
        for measure in cube_request.measures:
            measure_elem = ET.SubElement(cube_elem, "Measure")
            measure_elem.set("name", measure.name)
            measure_elem.set("column", measure.column)
            measure_elem.set("aggregator", measure.aggregator)
            if measure.formatString:
                measure_elem.set("formatString", measure.formatString)
        
        # Move the new cube to the end (after all existing cubes)
        if existing_cubes:
            # Remove the cube from its current position
            schema.remove(cube_elem)
            # Insert it at the end (after all existing cubes)
            schema.append(cube_elem)
        
        # Write the updated XML back to file with proper formatting
        try:
            self._format_xml(root)
            tree.write(self.xml_file_path, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing XML file: {str(e)}")
        
        return {
            "message": f"Cube '{cube_request.cube_name}' created successfully",
            "cube_name": cube_request.cube_name,
            "table_name": cube_request.table_name,
            "dimensions_count": len(cube_request.dimensions),
            "measures_count": len(cube_request.measures),
            "file_path": self.xml_file_path
        }
    
    def delete_cube(self, cube_name: str):
        """Delete a cube from the XML file"""
        self._validate_file_exists()
        tree, root = self._parse_xml()
        
        # Find the specific cube by name
        cube = root.find(f".//Cube[@name='{cube_name}']")
        
        if cube is None:
            # Get available cube names for better error message
            available_cubes = [c.get('name', 'Unnamed Cube') for c in root.findall('.//Cube')]
            raise HTTPException(
                status_code=404, 
                detail=f"Cube '{cube_name}' not found. Available cubes: {', '.join(available_cubes)}"
            )
        
        # Remove the cube element
        cube.getparent().remove(cube)
        
        # Write the updated XML back to file with proper formatting
        try:
            self._format_xml(root)
            tree.write(self.xml_file_path, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing XML file: {str(e)}")
        
        return {
            "message": f"Cube '{cube_name}' deleted successfully",
            "cube_name": cube_name,
            "file_path": self.xml_file_path
        }
    
    def update_cube(self, cube_name: str, cube_request: CreateCubeRequest):
        """Update an existing cube in the XML file"""
        # First delete the existing cube
        self.delete_cube(cube_name)
        
        # Then create the new cube (this handles the case where cube_name might be different)
        return self.create_cube(cube_request)
