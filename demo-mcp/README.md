# File Reader and Notion Integration MCP Server

A Model Context Protocol (MCP) server built with Python and FastMCP that provides tools to read files and create pages in Notion.

## Features

- **File Reading Tools**:
  - Read text files (.txt, .md, .py, etc.)
  - Parse JSON files with validation
  - Process CSV files with pandas
  - List files in directories with filtering

- **Notion Integration Tools**:
  - Create pages in Notion databases
  - Create pages directly from file content
  - List available Notion databases
  - Rich content formatting support

## Prerequisites

- Python 3.8+
- Notion API integration token
- Access to a Notion workspace with database permissions

## Installation

1. Clone or download this project:
```bash
git clone 
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env file with your Notion API key
```

## Notion Setup

1. **Create a Notion Integration**:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name and select your workspace
   - Copy the "Internal Integration Token"

2. **Share Database with Integration**:
   - Open your Notion database
   - Click "Share" in the top right
   - Add your integration and give it "Edit" permissions

3. **Get Database ID**:
   - Open your database in Notion
   - Copy the database ID from the URL:
     `https://notion.so/workspace/DATABASE_ID?v=...`

## Usage

### Running the Server

```bash
python src/server.py
```

The server will start and provide MCP tools for file reading and Notion integration.

### Available Tools

#### File Reading Tools

- `read_text_file(file_path)` - Read content from text files
- `read_json_file(file_path)` - Parse and read JSON files
- `read_csv_file(file_path, delimiter=",", max_rows=None)` - Process CSV files
- `list_files_in_directory(directory_path, file_extensions=None)` - List directory contents

#### Notion Integration Tools

- `create_notion_page(database_id, title, content=None, properties=None)` - Create a new Notion page
- `create_notion_page_from_file(database_id, file_path, page_title=None)` - Create page from file content
- `get_notion_databases()` - List available Notion databases

### Example Usage with MCP Client

```python
# Read a JSON file
result = await mcp_client.call_tool("read_json_file", {
    "file_path": "/path/to/data.json"
})

# Create a Notion page from file
result = await mcp_client.call_tool("create_notion_page_from_file", {
    "database_id": "your-database-id",
    "file_path": "/path/to/document.md",
    "page_title": "My Document"
})

# List CSV files in a directory
result = await mcp_client.call_tool("list_files_in_directory", {
    "directory_path": "/path/to/data",
    "file_extensions": [".csv", ".json"]
})
```

## Configuration

### Environment Variables

- `NOTION_API_KEY` - Your Notion integration token (required)
- `DEFAULT_DATABASE_ID` - Default database ID for testing (optional)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### File Format Support

- **Text files**: .txt, .md, .py, .js, .html, etc.
- **JSON files**: .json with validation and parsing
- **CSV files**: .csv with pandas processing and type inference

## Error Handling

The server includes comprehensive error handling for:
- File not found errors
- Invalid file formats
- Notion API errors
- Network connectivity issues
- Permission errors

## Security Notes

- Keep your Notion API key secure and never commit it to version control
- The server only reads files and creates Notion pages - no file deletion or modification
- All file paths are validated to prevent directory traversal attacks

## Troubleshooting

### Common Issues

1. **"Notion API key not configured"**
   - Ensure `NOTION_API_KEY` is set in your `.env` file
   - Verify the key is valid and not expired

2. **"Database not found"**
   - Check the database ID is correct
   - Ensure the integration has access to the database
   - Verify database permissions are set to "Edit"

3. **File reading errors**
   - Check file paths are absolute and correct
   - Ensure the server has read permissions
   - Verify file encoding (UTF-8 is assumed)

### Logging

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file to see detailed operation logs.

## Development

### Project Structure

```
demo-mcp/
├── src/
│   └── server.py          # Main MCP server implementation
├── examples/
│   ├── sample_data.json   # Example JSON file
│   ├── sample_data.csv    # Example CSV file
│   └── test_document.md   # Example markdown file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

### Adding New File Types

To add support for new file types, extend the `create_notion_page_from_file` function and add new reading tools as needed.

## License

This project is provided as an example for educational purposes.