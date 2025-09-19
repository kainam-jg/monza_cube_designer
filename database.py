import clickhouse_connect
from typing import Optional, Dict, Any
import json
import os

class ClickHouseManager:
    """Manages ClickHouse database connections and operations"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize with configuration from config.json"""
        self.config = self._load_config(config_file)
        self.client = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load database configuration from config.json"""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            # Extract database configuration
            db_config = config.get("database", {})
            
            # Set defaults if not provided
            return {
                "host": db_config.get("host", "localhost"),
                "port": db_config.get("port", 8123),
                "username": db_config.get("username", "default"),
                "password": db_config.get("password", ""),
                "database": db_config.get("database", "default"),
                "secure": db_config.get("secure", False)
            }
            
        except FileNotFoundError:
            print(f"Warning: {config_file} not found, using default database configuration")
            return {
                "host": "localhost",
                "port": 8123,
                "username": "default", 
                "password": "",
                "database": "default",
                "secure": False
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing {config_file}: {e}")
            return {
                "host": "localhost",
                "port": 8123,
                "username": "default",
                "password": "",
                "database": "default", 
                "secure": False
            }
    
    def connect(self) -> bool:
        """Establish connection to ClickHouse database"""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.config["host"],
                port=self.config["port"],
                username=self.config["username"],
                password=self.config["password"],
                database=self.config["database"],
                secure=self.config["secure"]
            )
            
            # Test the connection
            result = self.client.query("SELECT 1")
            print(f"✅ Successfully connected to ClickHouse at {self.config['host']}:{self.config['port']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to ClickHouse: {str(e)}")
            self.client = None
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            self.client = None
            print("🔌 ClickHouse connection closed")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the database connection and return status"""
        try:
            if not self.client:
                if not self.connect():
                    return {
                        "status": "error",
                        "message": "Failed to establish connection",
                        "connected": False
                    }
            
            # Run a simple test query
            result = self.client.query("SELECT version() as version, now() as current_time")
            version = result.result_rows[0][0] if result.result_rows else "Unknown"
            current_time = result.result_rows[0][1] if result.result_rows else "Unknown"
            
            return {
                "status": "success",
                "message": "Connection successful",
                "connected": True,
                "version": version,
                "current_time": str(current_time),
                "host": self.config["host"],
                "port": self.config["port"],
                "database": self.config["database"]
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection test failed: {str(e)}",
                "connected": False
            }
    
    def get_client(self):
        """Get the ClickHouse client (reconnect if needed)"""
        if not self.client:
            self.connect()
        return self.client

# Global instance
db_manager = ClickHouseManager()
