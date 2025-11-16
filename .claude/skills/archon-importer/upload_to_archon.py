#!/usr/bin/env python3
"""
Archon Uploader

Handles uploading documents and creating projects in Archon.
Implements retry logic and progress tracking.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Any


class ArchonUploader:
    """Uploads content to Archon backend."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.backend_url = config["archon_backend_url"]
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def upload_documents(self, file_paths: list[str]) -> dict[str, Any]:
        """Upload multiple documentation files to Archon knowledge base."""
        successful = 0
        failed = 0
        errors = []

        repo_path = Path(self.config.get("repository_path", "."))

        for i, file_path in enumerate(file_paths, 1):
            full_path = repo_path / file_path
            print(f"  [{i}/{len(file_paths)}] Uploading {file_path}...")

            try:
                result = await self._upload_single_document(full_path)
                if result["success"]:
                    successful += 1
                    # Poll for completion
                    if "progressId" in result:
                        await self._poll_upload_progress(result["progressId"])
                else:
                    failed += 1
                    errors.append(f"{file_path}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                failed += 1
                errors.append(f"{file_path}: {str(e)}")

        return {
            "successful": successful,
            "failed": failed,
            "total": len(file_paths),
            "errors": errors,
        }

    async def _upload_single_document(self, file_path: Path) -> dict[str, Any]:
        """Upload a single document file with retry logic."""
        url = f"{self.backend_url}/api/documents/upload"

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    # Prepare form data
                    data = aiohttp.FormData()
                    data.add_field(
                        "file",
                        open(file_path, "rb"),
                        filename=file_path.name,
                        content_type="application/octet-stream",
                    )
                    data.add_field(
                        "knowledge_type", self.config.get("knowledge_type", "technical")
                    )
                    data.add_field(
                        "extract_code_examples",
                        "true" if self.config.get("include_code_examples") else "false",
                    )
                    data.add_field("tags", "[]")  # Empty tags for now

                    async with session.post(
                        url, data=data, timeout=aiohttp.ClientTimeout(total=300)
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_data = await response.json()
                            return {
                                "success": False,
                                "error": error_data.get("error", f"HTTP {response.status}"),
                            }

            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return {"success": False, "error": f"Network error: {str(e)}"}

        return {"success": False, "error": "Max retries exceeded"}

    async def _poll_upload_progress(self, progress_id: str, timeout: int = 300) -> bool:
        """Poll upload progress until complete or timeout."""
        url = f"{self.backend_url}/api/crawl-progress/{progress_id}"
        start_time = asyncio.get_event_loop().time()

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    print(f"    ⏱️  Timeout waiting for upload to complete")
                    return False

                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            status = data.get("status")

                            if status == "completed":
                                print(f"    ✓ Upload completed")
                                return True
                            elif status == "failed":
                                print(f"    ✗ Upload failed: {data.get('error', 'Unknown error')}")
                                return False
                            elif status in ("processing", "storing"):
                                # Still processing, continue polling
                                await asyncio.sleep(2)
                            else:
                                # Unknown status
                                await asyncio.sleep(2)
                        elif response.status == 404:
                            # Progress not found yet, wait and retry
                            await asyncio.sleep(2)
                        else:
                            print(f"    ⚠️  Error checking progress: HTTP {response.status}")
                            await asyncio.sleep(5)

                except asyncio.TimeoutError:
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"    ⚠️  Error polling progress: {e}")
                    await asyncio.sleep(5)

    async def extract_code_examples(self, code_files: list[str]) -> dict[str, Any]:
        """Extract code examples from source files."""
        # For now, this uploads code files as documents
        # The Archon backend will extract code examples automatically
        return await self.upload_documents(code_files)

    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Create a project in Archon."""
        url = f"{self.backend_url}/api/projects"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json=project_data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "project_id": data.get("id") or data.get("project_id"),
                            "project": data,
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": error_data.get("error", f"HTTP {response.status}"),
                        }
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Retrieve a project by ID."""
        url = f"{self.backend_url}/api/projects/{project_id}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
            except Exception:
                return None
