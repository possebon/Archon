#!/usr/bin/env python3
"""
Documentation Generator

Generates AI-powered documentation (PRDs, specs, ERDs) for imported projects.
Uses Archon's DocumentAgent via API.
"""

import aiohttp
from typing import Any


class DocumentationGenerator:
    """Generates AI documentation for imported projects."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.backend_url = config["archon_backend_url"]

    async def generate_for_project(
        self, project_id: str, scan_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate comprehensive documentation for a project."""
        documents_generated = []
        errors = []

        # Extract project metadata from scan
        repo_name = self._extract_project_name()
        has_database = self._detect_database(scan_result)
        has_api = self._detect_api(scan_result)

        # Generate PRD (always)
        print("  📝 Generating PRD...")
        prd_result = await self._generate_prd(project_id, repo_name, scan_result)
        if prd_result["success"]:
            documents_generated.append(prd_result["document"])
        else:
            errors.append(f"PRD generation failed: {prd_result.get('error')}")

        # Generate Technical Spec (if API detected)
        if has_api:
            print("  📝 Generating Technical Specification...")
            spec_result = await self._generate_technical_spec(project_id, repo_name)
            if spec_result["success"]:
                documents_generated.append(spec_result["document"])
            else:
                errors.append(f"Tech spec generation failed: {spec_result.get('error')}")

        # Generate ERD (if database detected)
        if has_database:
            print("  📝 Generating Entity Relationship Diagram...")
            erd_result = await self._generate_erd(project_id, repo_name)
            if erd_result["success"]:
                documents_generated.append(erd_result["document"])
            else:
                errors.append(f"ERD generation failed: {erd_result.get('error')}")

        return {
            "success": len(documents_generated) > 0,
            "documents": documents_generated,
            "errors": errors,
        }

    async def _generate_prd(
        self, project_id: str, project_name: str, scan_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate Product Requirements Document."""
        # Use Archon's agent API to generate PRD
        url = f"{self.backend_url}/api/agents/document/chat"

        # Build context from scan results
        context = f"Project: {project_name}\n"
        if scan_result.get("readme_files"):
            context += f"\nFound README files: {', '.join(scan_result['readme_files'][:3])}"
        if scan_result.get("config_files"):
            context += f"\nConfig files: {', '.join(scan_result['config_files'])}"

        prompt = f"""Create a comprehensive PRD (Product Requirements Document) for the project "{project_name}".

{context}

Generate a well-structured PRD that includes:
- Project Overview
- Goals and Objectives
- Scope (In-Scope and Out-of-Scope)
- Technical Requirements
- Architecture Overview
- User Stories
- Timeline & Milestones
- Risks & Mitigations

Make it detailed and professional."""

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json={
                        "project_id": project_id,
                        "message": prompt,
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "document": {
                                "type": "prd",
                                "title": f"{project_name} - Product Requirements Document",
                            },
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _generate_technical_spec(
        self, project_id: str, project_name: str
    ) -> dict[str, Any]:
        """Generate Technical Specification."""
        url = f"{self.backend_url}/api/agents/document/chat"

        prompt = f"""Create a Technical Specification document for the project "{project_name}".

Include:
- System Architecture
- API Design (endpoints, request/response formats)
- Data Models
- Technology Stack
- Integration Points
- Security Considerations
- Performance Requirements
- Deployment Architecture

Make it comprehensive and technically detailed."""

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json={
                        "project_id": project_id,
                        "message": prompt,
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "document": {
                                "type": "technical_spec",
                                "title": f"{project_name} - Technical Specification",
                            },
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _generate_erd(self, project_id: str, project_name: str) -> dict[str, Any]:
        """Generate Entity Relationship Diagram."""
        url = f"{self.backend_url}/api/agents/document/chat"

        prompt = f"""Create an Entity Relationship Diagram (ERD) for the database schema of "{project_name}".

Analyze the codebase to identify:
- All database entities/tables
- Attributes for each entity
- Relationships between entities
- Primary and foreign keys
- Generate SQL schema statements

Create a comprehensive ERD with proper normalization."""

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json={
                        "project_id": project_id,
                        "message": prompt,
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "document": {
                                "type": "erd",
                                "title": f"{project_name} - Entity Relationship Diagram",
                            },
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def _extract_project_name(self) -> str:
        """Extract project name from config."""
        if self.config.get("repo_url"):
            parts = self.config["repo_url"].rstrip("/").split("/")
            return parts[-1].replace(".git", "")
        elif self.config.get("local_path"):
            from pathlib import Path

            return Path(self.config["local_path"]).name
        else:
            return "Imported Project"

    def _detect_database(self, scan_result: dict[str, Any]) -> bool:
        """Detect if project has database components."""
        # Check for database-related files
        db_indicators = [
            "models.py",
            "schema.sql",
            "migrations/",
            "prisma/schema.prisma",
            "database/",
        ]

        all_files = (
            scan_result.get("documentation", [])
            + scan_result.get("code_files", [])
            + scan_result.get("config_files", [])
        )

        for file_path in all_files:
            for indicator in db_indicators:
                if indicator in file_path.lower():
                    return True

        return False

    def _detect_api(self, scan_result: dict[str, Any]) -> bool:
        """Detect if project has API components."""
        # Check for API-related files
        api_indicators = [
            "api/",
            "routes/",
            "controllers/",
            "endpoints/",
            "fastapi",
            "express",
            "router",
        ]

        all_files = (
            scan_result.get("documentation", [])
            + scan_result.get("code_files", [])
            + scan_result.get("config_files", [])
        )

        for file_path in all_files:
            lower_path = file_path.lower()
            for indicator in api_indicators:
                if indicator in lower_path:
                    return True

        return False
