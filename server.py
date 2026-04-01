#!/usr/bin/env python3
"""Local Asana MCP server — adds file attachment support missing from the remote MCP."""

import asyncio
import mimetypes
import os
from pathlib import Path

import httpx
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

ASANA_BASE_URL = "https://app.asana.com/api/1.0"

server = Server("asana-uploader-mcp")


def _token() -> str:
    token = os.environ.get("ASANA_ACCESS_TOKEN")
    if not token:
        raise ValueError("ASANA_ACCESS_TOKEN environment variable is not set")
    return token


def _headers() -> dict:
    return {"Authorization": f"Bearer {_token()}"}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="upload_attachment",
            description=(
                "Upload a local file as an attachment to an Asana task. "
                "Provide the task GID and a file path (absolute or ~/…). "
                "Returns the attachment GID and permanent URL on success."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_gid": {
                        "type": "string",
                        "description": "GID of the Asana task to attach the file to.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Local path to the file (e.g. ~/Downloads/report.pdf).",
                    },
                    "file_name": {
                        "type": "string",
                        "description": "Display name for the attachment. Defaults to the file's basename.",
                    },
                },
                "required": ["task_gid", "file_path"],
            },
        ),
        types.Tool(
            name="get_attachments_for_task",
            description="List all attachments on an Asana task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_gid": {
                        "type": "string",
                        "description": "GID of the Asana task.",
                    },
                },
                "required": ["task_gid"],
            },
        ),
        types.Tool(
            name="delete_attachment",
            description="Delete an Asana attachment by its GID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "attachment_gid": {
                        "type": "string",
                        "description": "GID of the attachment to delete.",
                    },
                },
                "required": ["attachment_gid"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "upload_attachment":
        return await _upload_attachment(arguments)
    if name == "get_attachments_for_task":
        return await _get_attachments(arguments)
    if name == "delete_attachment":
        return await _delete_attachment(arguments)
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def _upload_attachment(args: dict) -> list[types.TextContent]:
    task_gid = args["task_gid"]
    file_path = Path(args["file_path"]).expanduser().resolve()

    if not file_path.exists():
        return [types.TextContent(type="text", text=f"Error: file not found: {file_path}")]

    file_name = args.get("file_name") or file_path.name
    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"

    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as fh:
            response = await client.post(
                f"{ASANA_BASE_URL}/attachments",
                headers=_headers(),
                data={"parent": task_gid},
                files={"file": (file_name, fh, mime_type)},
                timeout=120.0,
            )

    if response.status_code == 200:
        data = response.json().get("data", {})
        lines = [
            "Attachment uploaded successfully.",
            f"GID: {data.get('gid')}",
            f"Name: {data.get('name')}",
            f"URL: {data.get('permanent_url') or data.get('view_url', 'N/A')}",
        ]
        return [types.TextContent(type="text", text="\n".join(lines))]

    return [types.TextContent(type="text", text=f"Error {response.status_code}: {response.text}")]


async def _get_attachments(args: dict) -> list[types.TextContent]:
    task_gid = args["task_gid"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/attachments",
            headers=_headers(),
            params={
                "parent": task_gid,
                "opt_fields": "gid,name,created_at,size,permanent_url,view_url",
            },
            timeout=30.0,
        )

    if response.status_code != 200:
        return [types.TextContent(type="text", text=f"Error {response.status_code}: {response.text}")]

    attachments = response.json().get("data", [])
    if not attachments:
        return [types.TextContent(type="text", text="No attachments found on this task.")]

    lines = [f"Found {len(attachments)} attachment(s):"]
    for a in attachments:
        size = f"{a['size']} bytes" if a.get("size") else "unknown size"
        lines.append(f"  • {a.get('name')}  (GID: {a.get('gid')}, {size})")
    return [types.TextContent(type="text", text="\n".join(lines))]


async def _delete_attachment(args: dict) -> list[types.TextContent]:
    gid = args["attachment_gid"]

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{ASANA_BASE_URL}/attachments/{gid}",
            headers=_headers(),
            timeout=30.0,
        )

    if response.status_code == 200:
        return [types.TextContent(type="text", text="Attachment deleted successfully.")]
    return [types.TextContent(type="text", text=f"Error {response.status_code}: {response.text}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
