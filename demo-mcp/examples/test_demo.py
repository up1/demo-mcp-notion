#!/usr/bin/env python3
"""
Test script for the MCP File Reader and Notion Integration Server

This script demonstrates how to use the MCP server tools to read files
and create Notion pages. Run this after setting up your MCP server.

Note: This is a demonstration script. In practice, you would interact
with the MCP server through an MCP client like Claude Desktop or
other MCP-compatible applications.
"""

import asyncio
import os
from pathlib import Path

# Mock MCP client for demonstration
class MockMCPClient:
    """Mock MCP client to simulate tool calls"""
    
    def __init__(self):
        self.tools = {
            'read_text_file': self.read_text_file,
            'read_json_file': self.read_json_file,
            'read_csv_file': self.read_csv_file,
            'list_files_in_directory': self.list_files_in_directory,
            'create_notion_page': self.create_notion_page,
            'create_notion_page_from_file': self.create_notion_page_from_file,
            'get_notion_databases': self.get_notion_databases
        }
    
    async def call_tool(self, tool_name: str, args: dict):
        """Simulate calling an MCP tool"""
        if tool_name in self.tools:
            print(f"🔧 Calling tool: {tool_name}")
            print(f"   Args: {args}")
            try:
                result = await self.tools[tool_name](**args)
                print(f"✅ Success: {type(result).__name__} returned")
                return result
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                return {"error": str(e)}
        else:
            print(f"❌ Tool not found: {tool_name}")
            return {"error": f"Tool not found: {tool_name}"}
    
    # Mock tool implementations (would be actual MCP calls in practice)
    async def read_text_file(self, file_path: str):
        return {"filename": Path(file_path).name, "content_type": "text", "status": "mock_success"}
    
    async def read_json_file(self, file_path: str):
        return {"filename": Path(file_path).name, "content_type": "json", "status": "mock_success"}
    
    async def read_csv_file(self, file_path: str, delimiter: str = ",", max_rows=None):
        return {"filename": Path(file_path).name, "content_type": "csv", "status": "mock_success"}
    
    async def list_files_in_directory(self, directory_path: str, file_extensions=None):
        return {"directory": directory_path, "files": ["mock_file1.txt", "mock_file2.json"], "status": "mock_success"}
    
    async def create_notion_page(self, database_id: str, title: str, content=None, properties=None):
        return {"page_id": "mock_page_id", "title": title, "status": "mock_success"}
    
    async def create_notion_page_from_file(self, database_id: str, file_path: str, page_title=None):
        return {"page_id": "mock_page_id", "file_path": file_path, "status": "mock_success"}
    
    async def get_notion_databases(self):
        return [{"id": "mock_db_id", "title": "Mock Database", "status": "mock_success"}]


async def test_file_reading():
    """Test file reading tools"""
    print("\n📖 Testing File Reading Tools")
    print("=" * 40)
    
    client = MockMCPClient()
    examples_dir = Path(__file__).parent
    
    # Test reading different file types
    test_cases = [
        {
            "tool": "read_text_file",
            "args": {"file_path": str(examples_dir / "test_document.md")},
            "description": "Reading markdown file"
        },
        {
            "tool": "read_json_file", 
            "args": {"file_path": str(examples_dir / "sample_data.json")},
            "description": "Reading JSON file"
        },
        {
            "tool": "read_csv_file",
            "args": {"file_path": str(examples_dir / "sample_data.csv"), "max_rows": 5},
            "description": "Reading CSV file (first 5 rows)"
        },
        {
            "tool": "list_files_in_directory",
            "args": {"directory_path": str(examples_dir), "file_extensions": [".json", ".csv", ".md"]},
            "description": "Listing example files"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        result = await client.call_tool(test["tool"], test["args"])


async def test_notion_integration():
    """Test Notion integration tools"""
    print("\n📝 Testing Notion Integration Tools")
    print("=" * 40)
    
    client = MockMCPClient()
    
    # Mock database ID (replace with real one for actual testing)
    mock_db_id = "mock-database-id-12345"
    
    test_cases = [
        {
            "tool": "get_notion_databases",
            "args": {},
            "description": "Listing available databases"
        },
        {
            "tool": "create_notion_page",
            "args": {
                "database_id": mock_db_id,
                "title": "Test Page from MCP",
                "content": "This page was created using the MCP File Reader server!"
            },
            "description": "Creating a simple Notion page"
        },
        {
            "tool": "create_notion_page_from_file",
            "args": {
                "database_id": mock_db_id,
                "file_path": str(Path(__file__).parent / "test_document.md"),
                "page_title": "Test Document from File"
            },
            "description": "Creating Notion page from markdown file"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        result = await client.call_tool(test["tool"], test["args"])


async def demo_workflow():
    """Demonstrate a complete workflow"""
    print("\n🚀 Complete Workflow Demonstration")
    print("=" * 40)
    
    client = MockMCPClient()
    examples_dir = Path(__file__).parent
    
    print("\n1. Discovering files in examples directory...")
    files_result = await client.call_tool("list_files_in_directory", {
        "directory_path": str(examples_dir),
        "file_extensions": [".json", ".csv", ".md"]
    })
    
    print("\n2. Reading project data from JSON...")
    json_result = await client.call_tool("read_json_file", {
        "file_path": str(examples_dir / "sample_data.json")
    })
    
    print("\n3. Processing employee data from CSV...")
    csv_result = await client.call_tool("read_csv_file", {
        "file_path": str(examples_dir / "sample_data.csv"),
        "max_rows": 3
    })
    
    print("\n4. Creating Notion pages from files...")
    # In a real scenario, you'd use actual database IDs
    mock_db_id = "your-actual-database-id-here"
    
    for filename in ["sample_data.json", "sample_data.csv", "test_document.md"]:
        page_result = await client.call_tool("create_notion_page_from_file", {
            "database_id": mock_db_id,
            "file_path": str(examples_dir / filename),
            "page_title": f"Imported: {filename}"
        })
    
    print("\n✅ Workflow completed successfully!")


def print_setup_instructions():
    """Print setup instructions for actual usage"""
    print("\n🔧 Setup Instructions for Real Usage")
    print("=" * 50)
    print("""
To use this MCP server with real data:

1. Install dependencies:
   pip install -r requirements.txt

2. Set up Notion API:
   - Create integration at https://www.notion.so/my-integrations
   - Copy API key to .env file
   - Share databases with your integration

3. Configure environment:
   cp .env.example .env
   # Edit .env with your Notion API key

4. Run the MCP server:
   python src/server.py

5. Connect via MCP client:
   - Claude Desktop
   - Other MCP-compatible applications
   - Custom MCP client implementation

Example MCP client configuration for Claude Desktop:
{
  "mcpServers": {
    "file-notion-mcp": {
      "command": "python",
      "args": ["path/to/your/src/server.py"],
      "env": {
        "NOTION_API_KEY": "your_notion_api_key"
      }
    }
  }
}
""")


async def main():
    """Run all tests and demonstrations"""
    print("🎯 MCP File Reader & Notion Integration Server Demo")
    print("=" * 60)
    
    print("This is a demonstration of the MCP server capabilities.")
    print("The tests below use mock responses to show the expected workflow.")
    
    # Run all test suites
    await test_file_reading()
    await test_notion_integration()
    await demo_workflow()
    
    # Show setup instructions
    print_setup_instructions()
    
    print("\n🎉 Demo completed! Check the output above for results.")


if __name__ == "__main__":
    asyncio.run(main())