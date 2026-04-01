# asana-uploader-mcp

A local [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that adds **file attachment support** to Asana — functionality missing from Asana's official remote MCP server.

## Tools provided

| Tool | Description |
|---|---|
| `upload_attachment` | Upload a local file to an Asana task |
| `get_attachments_for_task` | List all attachments on a task |
| `delete_attachment` | Delete an attachment by GID |

## Prerequisites

- Python 3.10+
- An [Asana Personal Access Token](https://app.asana.com/0/my-apps) (My Profile → Apps → Personal Access Tokens)

## Setup

### 1. Install

```bash
pip install git+https://github.com/greenbrettmichael/asana-uploader-mcp.git
```

### 2. Add to Claude Code

```bash
ASANA_ACCESS_TOKEN=your_token_here claude mcp add asana-uploader-mcp -- asana-uploader-mcp
```

Or set the token in your environment first and reference it:

```bash
export ASANA_ACCESS_TOKEN=your_token_here
claude mcp add asana-uploader-mcp -e ASANA_ACCESS_TOKEN=$ASANA_ACCESS_TOKEN -- asana-uploader-mcp
```

That's it — restart Claude Code and the tools will be available.

## Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "asana-uploader-mcp": {
      "command": "asana-uploader-mcp",
      "env": {
        "ASANA_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Usage examples

- *"Upload ~/Downloads/report.pdf to Asana task 1234567890"*
- *"List the attachments on task 1234567890"*
- *"Delete attachment 9876543210"*

Task GIDs appear in Asana task URLs: `https://app.asana.com/0/<project>/<task_gid>`.
