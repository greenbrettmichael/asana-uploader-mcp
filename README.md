# asana-attachments-mcp

A local [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that adds **file attachment support** to Asana — functionality missing from Asana's official remote MCP server.

## Why this exists

Asana's hosted MCP server does not expose the Attachments API. This server fills that gap by running locally and proxying multipart file uploads directly to Asana on your behalf.

## Tools provided

| Tool | Description |
|---|---|
| `upload_attachment` | Upload a local file to an Asana task |
| `get_attachments_for_task` | List all attachments on a task |
| `delete_attachment` | Delete an attachment by GID |

## Prerequisites

- Python 3.10+
- An [Asana Personal Access Token](https://app.asana.com/0/my-apps)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Or with a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set your Asana access token

```bash
export ASANA_ACCESS_TOKEN=your_token_here
```

Get a token from **Asana → My Profile → Apps → Personal Access Tokens**.

### 3. Configure your MCP client

#### Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "asana-attachments": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "ASANA_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Claude Code (`.claude/settings.json` or `~/.claude/settings.json`)

```json
{
  "mcpServers": {
    "asana-attachments": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "ASANA_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

Restart your MCP client after saving the config.

## Usage examples

Once connected, ask your AI assistant things like:

- *"Upload ~/Downloads/report.pdf to Asana task 1234567890"*
- *"List the attachments on task 1234567890"*
- *"Delete attachment 9876543210 from Asana"*

Task and attachment GIDs can be found in Asana task URLs: `https://app.asana.com/0/<project>/<task_gid>`.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ASANA_ACCESS_TOKEN` | Yes | Asana Personal Access Token |

## Running directly

```bash
ASANA_ACCESS_TOKEN=your_token python server.py
```

The server communicates over stdio (standard MCP transport) and exits when the client disconnects.
