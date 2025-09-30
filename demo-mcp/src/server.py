#!/usr/bin/env python3
"""
MCP Server for File Reading and Notion Integration

This server provides tools to:
1. Read data from various file formats (JSON, CSV, TXT, MD)
2. Create pages in Notion using the Notion API
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

try:
    import aiofiles
    import pandas as pd
    from fastmcp import FastMCP
    from notion_client import AsyncClient
    from pydantic import BaseModel
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please run: pip install -r requirements.txt")
    exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("File Reader and Notion Integration Server")

# Initialize Notion client
notion_token = os.getenv("NOTION_API_KEY")
if not notion_token:
    logger.warning("NOTION_API_KEY not found in environment variables")
    notion_client = None
else:
    notion_client = AsyncClient(auth=notion_token)


class FileContent(BaseModel):
    """Model for file content response"""
    filename: str
    content_type: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    size: int
    encoding: str = "utf-8"


class NotionPageRequest(BaseModel):
    """Model for Notion page creation request"""
    database_id: str
    title: str
    content: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


@mcp.tool()
async def read_text_file(file_path: str) -> FileContent:
    """
    Read content from a text file (.txt, .md, .py, etc.)
    
    Args:
        file_path: Path to the text file to read
        
    Returns:
        FileContent object with file information and content
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            content = await file.read()
        
        return FileContent(
            filename=path.name,
            content_type="text",
            content=content,
            size=len(content),
            encoding="utf-8"
        )
    
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {str(e)}")
        raise


@mcp.tool()
async def read_json_file(file_path: str) -> FileContent:
    """
    Read and parse content from a JSON file
    
    Args:
        file_path: Path to the JSON file to read
        
    Returns:
        FileContent object with parsed JSON data
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            content_str = await file.read()
        
        try:
            content = json.loads(content_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        return FileContent(
            filename=path.name,
            content_type="json",
            content=content,
            size=len(content_str),
            encoding="utf-8"
        )
    
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {str(e)}")
        raise


@mcp.tool()
async def read_csv_file(file_path: str, delimiter: str = ",", max_rows: Optional[int] = None) -> FileContent:
    """
    Read and parse content from a CSV file
    
    Args:
        file_path: Path to the CSV file to read
        delimiter: CSV delimiter (default: ",")
        max_rows: Maximum number of rows to read (optional)
        
    Returns:
        FileContent object with CSV data as list of dictionaries
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read CSV using pandas for better handling
        df = pd.read_csv(file_path, delimiter=delimiter, nrows=max_rows)
        
        # Convert to list of dictionaries
        content = df.to_dict('records')
        
        # Get file size
        file_size = path.stat().st_size
        
        return FileContent(
            filename=path.name,
            content_type="csv",
            content=content,
            size=file_size,
            encoding="utf-8"
        )
    
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise


@mcp.tool()
async def list_files_in_directory(directory_path: str, file_extensions: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    List files in a directory, optionally filtered by file extensions
    
    Args:
        directory_path: Path to the directory to list
        file_extensions: List of file extensions to filter (e.g., ['.txt', '.json'])
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                if file_extensions is None or item.suffix.lower() in [ext.lower() for ext in file_extensions]:
                    files.append(str(item))
        
        return {
            "directory": str(path),
            "files": files,
            "total_count": len(files)
        }
    
    except Exception as e:
        logger.error(f"Error listing files in directory {directory_path}: {str(e)}")
        raise


@mcp.tool()
async def create_notion_page(database_id: str, title: str, content: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new page in a Notion database
    
    Args:
        database_id: ID of the target Notion database
        title: Title for the new page
        content: Optional content to add to the page body
        properties: Optional additional properties for the page
        
    Returns:
        Dictionary with created page information
    """
    if not notion_client:
        raise RuntimeError("Notion API key not configured. Please set NOTION_API_KEY environment variable.")
    
    try:
        # Prepare page properties
        page_properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        # Add custom properties if provided
        if properties:
            page_properties.update(properties)
        
        # Prepare page content/children
        children = []
        if content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            })
        
        # Create the page
        page_data = {
            "parent": {"database_id": database_id},
            "properties": page_properties
        }
        
        if children:
            page_data["children"] = children
        
        response = await notion_client.pages.create(**page_data)
        
        return {
            "page_id": response["id"],
            "url": response["url"],
            "title": title,
            "created_time": response["created_time"],
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error creating Notion page: {str(e)}")
        raise


@mcp.tool()
async def create_notion_page_from_file(database_id: str, file_path: str, page_title: Optional[str] = None) -> Dict[str, Any]:
    """
    Read a file and create a Notion page with its content
    
    Args:
        database_id: ID of the target Notion database
        file_path: Path to the file to read
        page_title: Optional custom title for the page (defaults to filename)
        
    Returns:
        Dictionary with created page information and file content summary
    """
    try:
        # Read file content based on extension
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.json':
            file_content = await read_json_file(file_path)
            content_text = json.dumps(file_content.content, indent=2)
        elif extension == '.csv':
            file_content = await read_csv_file(file_path)
            # Convert CSV data to readable text
            if isinstance(file_content.content, list) and file_content.content:
                content_text = f"CSV Data ({len(file_content.content)} rows):\n\n"
                # Add headers
                headers = list(file_content.content[0].keys())
                content_text += " | ".join(headers) + "\n"
                content_text += " | ".join(["---"] * len(headers)) + "\n"
                # Add first 10 rows as sample
                for row in file_content.content[:10]:
                    content_text += " | ".join(str(row.get(h, "")) for h in headers) + "\n"
                if len(file_content.content) > 10:
                    content_text += f"\n... and {len(file_content.content) - 10} more rows"
            else:
                content_text = "Empty CSV file"
        else:
            # Default to text file
            file_content = await read_text_file(file_path)
            content_text = file_content.content
        
        # Use custom title or filename
        title = page_title or f"File: {file_content.filename}"
        
        # Create Notion page
        page_result = await create_notion_page(
            database_id=database_id,
            title=title,
            content=content_text
        )
        
        return {
            **page_result,
            "file_info": {
                "filename": file_content.filename,
                "content_type": file_content.content_type,
                "file_size": file_content.size
            }
        }
    
    except Exception as e:
        logger.error(f"Error creating Notion page from file {file_path}: {str(e)}")
        raise


@mcp.tool()
async def get_notion_databases() -> List[Dict[str, Any]]:
    """
    List available Notion databases (requires appropriate permissions)
    
    Returns:
        List of available databases with their IDs and titles
    """
    if not notion_client:
        raise RuntimeError("Notion API key not configured. Please set NOTION_API_KEY environment variable.")
    
    try:
        response = await notion_client.search(filter={"property": "object", "value": "database"})
        
        databases = []
        for db in response.get("results", []):
            title = "Untitled"
            if db.get("title") and len(db["title"]) > 0:
                title = db["title"][0].get("plain_text", "Untitled")
            
            databases.append({
                "id": db["id"],
                "title": title,
                "url": db.get("url", ""),
                "created_time": db.get("created_time", ""),
                "last_edited_time": db.get("last_edited_time", "")
            })
        
        return databases
    
    except Exception as e:
        logger.error(f"Error fetching Notion databases: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the server
    mcp.run()