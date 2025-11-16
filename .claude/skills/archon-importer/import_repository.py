#!/usr/bin/env python3
"""
Archon Repository Importer - Main Orchestrator

Imports existing codebases and documentation into Archon knowledge base.
Follows plan → validate → execute → verify pattern for robust operation.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Import helper modules
from scan_repository import RepositoryScanner
from validate_archon_connection import ArchonValidator
from upload_to_archon import ArchonUploader
from generate_documentation import DocumentationGenerator


class ImportOrchestrator:
    """Orchestrates the full import workflow with progress tracking."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.results = {
            "start_time": datetime.now().isoformat(),
            "status": "initializing",
            "phases": {},
            "errors": [],
            "warnings": [],
        }

    async def run(self) -> dict[str, Any]:
        """Execute the full import workflow."""
        try:
            print("🚀 Starting Archon Repository Import")
            print("=" * 50)

            # Phase 1: Plan
            if not await self.plan_phase():
                return self._failure_result("Planning phase failed")

            # Phase 2: Validate
            if not await self.validate_phase():
                return self._failure_result("Validation phase failed")

            # Phase 3: Execute (skip if dry-run)
            if self.config.get("dry_run"):
                print("\n✅ Dry run completed successfully")
                return self._success_result(dry_run=True)

            if not await self.execute_phase():
                return self._failure_result("Execution phase failed")

            # Phase 4: Verify
            if not await self.verify_phase():
                return self._failure_result("Verification phase failed")

            print("\n✅ Import completed successfully!")
            return self._success_result()

        except KeyboardInterrupt:
            print("\n\n⚠️  Import cancelled by user")
            return self._failure_result("Cancelled by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.results["errors"].append(str(e))
            return self._failure_result(str(e))
        finally:
            # Always save results
            self._save_results()

    async def plan_phase(self) -> bool:
        """Phase 1: Plan the import by scanning repository."""
        print("\n📋 Phase 1: Planning")
        print("-" * 50)

        try:
            # Initialize scanner
            scanner = RepositoryScanner(self.config)

            # Scan repository
            print("🔍 Scanning repository for documentation and code...")
            scan_result = await scanner.scan()

            self.results["phases"]["plan"] = scan_result

            # Display scan summary
            print(f"  ✓ Found {len(scan_result['readme_files'])} README files")
            print(f"  ✓ Found {len(scan_result['documentation'])} documentation files")
            print(f"  ✓ Found {len(scan_result['code_files'])} code files")
            print(f"  ✓ Estimated size: {scan_result['estimated_size_mb']:.2f} MB")

            # Check if anything to import
            total_files = (
                len(scan_result["readme_files"])
                + len(scan_result["documentation"])
                + len(scan_result.get("code_files", []))
            )

            if total_files == 0:
                print("\n⚠️  No files found to import")
                self.results["warnings"].append("No files found to import")
                return False

            # Estimate processing time
            estimated_minutes = self._estimate_processing_time(scan_result)
            print(f"  ⏱️  Estimated processing time: {estimated_minutes:.1f} minutes")

            return True

        except Exception as e:
            print(f"❌ Planning failed: {e}")
            self.results["errors"].append(f"Planning phase: {e}")
            return False

    async def validate_phase(self) -> bool:
        """Phase 2: Validate prerequisites and connectivity."""
        print("\n🔐 Phase 2: Validation")
        print("-" * 50)

        try:
            validator = ArchonValidator(self.config)
            validation_result = await validator.validate()

            self.results["phases"]["validate"] = validation_result

            # Check backend connectivity
            if not validation_result["backend_reachable"]:
                print("❌ Cannot reach Archon backend")
                print(f"   URL: {self.config['archon_backend_url']}")
                print("   → Ensure Archon backend is running")
                return False

            print(f"  ✓ Archon backend reachable at {self.config['archon_backend_url']}")

            # Check LLM provider (required for doc generation)
            if self.config.get("generate_docs"):
                if not validation_result["llm_provider_configured"]:
                    print("⚠️  LLM provider not configured")
                    print("   → AI documentation generation will be skipped")
                    self.config["generate_docs"] = False
                    self.results["warnings"].append(
                        "LLM provider not configured - skipping doc generation"
                    )
                else:
                    print("  ✓ LLM provider configured for doc generation")

            # Check embedding provider (required for knowledge base)
            if not validation_result["embedding_provider_configured"]:
                print("❌ Embedding provider not configured")
                print("   → Configure embedding provider in Archon settings")
                return False

            print("  ✓ Embedding provider configured")

            # Check for duplicate projects
            if await self._check_duplicate_project():
                print("⚠️  Project with this name or GitHub URL already exists")
                if not self._confirm_continue("Continue anyway?"):
                    return False

            return True

        except Exception as e:
            print(f"❌ Validation failed: {e}")
            self.results["errors"].append(f"Validation phase: {e}")
            return False

    async def execute_phase(self) -> bool:
        """Phase 3: Execute the import."""
        print("\n⚙️  Phase 3: Execution")
        print("-" * 50)

        try:
            uploader = ArchonUploader(self.config)
            scan_result = self.results["phases"]["plan"]

            # Step 1: Upload documentation files
            print("\n📤 Uploading documentation files...")
            doc_files = scan_result["readme_files"] + scan_result["documentation"]
            upload_result = await uploader.upload_documents(doc_files)

            print(f"  ✓ Uploaded {upload_result['successful']} files")
            if upload_result["failed"] > 0:
                print(f"  ⚠️  Failed to upload {upload_result['failed']} files")
                self.results["warnings"].extend(upload_result["errors"])

            # Step 2: Extract and upload code examples (if enabled)
            if self.config.get("include_code_examples"):
                print("\n🔍 Extracting code examples...")
                code_result = await uploader.extract_code_examples(scan_result["code_files"])
                print(f"  ✓ Extracted {code_result['successful']} code examples")

            # Step 3: Create project in Archon
            print("\n📦 Creating project in Archon...")
            project_data = self._prepare_project_data(scan_result)
            project_result = await uploader.create_project(project_data)

            if not project_result["success"]:
                print(f"❌ Failed to create project: {project_result['error']}")
                return False

            project_id = project_result["project_id"]
            print(f"  ✓ Project created: {project_id}")

            self.results["project_id"] = project_id
            self.results["project_url"] = f"{self.config['archon_backend_url']}/projects/{project_id}"

            # Step 4: Generate AI documentation (if enabled)
            if self.config.get("generate_docs"):
                print("\n🤖 Generating AI documentation...")
                doc_generator = DocumentationGenerator(self.config)
                doc_result = await doc_generator.generate_for_project(
                    project_id, scan_result
                )

                if doc_result["success"]:
                    print(f"  ✓ Generated {len(doc_result['documents'])} documents")
                    for doc in doc_result["documents"]:
                        print(f"    • {doc['type']}: {doc['title']}")
                else:
                    print("  ⚠️  AI documentation generation failed")
                    self.results["warnings"].append(
                        f"Doc generation failed: {doc_result.get('error')}"
                    )

            self.results["phases"]["execute"] = {
                "documents_uploaded": upload_result["successful"],
                "code_examples": code_result.get("successful", 0) if self.config.get("include_code_examples") else 0,
                "project_id": project_id,
                "ai_docs_generated": doc_result.get("success", False) if self.config.get("generate_docs") else False,
            }

            return True

        except Exception as e:
            print(f"❌ Execution failed: {e}")
            self.results["errors"].append(f"Execution phase: {e}")
            return False

    async def verify_phase(self) -> bool:
        """Phase 4: Verify the import was successful."""
        print("\n✅ Phase 4: Verification")
        print("-" * 50)

        try:
            project_id = self.results.get("project_id")
            if not project_id:
                print("❌ No project ID found - import incomplete")
                return False

            # Verify project exists and is accessible
            uploader = ArchonUploader(self.config)
            project = await uploader.get_project(project_id)

            if not project:
                print("❌ Cannot retrieve created project")
                return False

            print(f"  ✓ Project verified: {project['title']}")

            # Verify document count
            expected_docs = self.results["phases"]["execute"]["documents_uploaded"]
            actual_docs = len(project.get("docs", []))

            if actual_docs >= expected_docs:
                print(f"  ✓ Documents verified: {actual_docs} documents")
            else:
                print(f"  ⚠️  Document count mismatch: expected {expected_docs}, found {actual_docs}")
                self.results["warnings"].append(
                    f"Document count mismatch: expected {expected_docs}, found {actual_docs}"
                )

            # Check for critical errors
            if self.results["errors"]:
                print(f"\n⚠️  {len(self.results['errors'])} errors occurred during import:")
                for error in self.results["errors"][:5]:  # Show first 5
                    print(f"    • {error}")
                return False

            self.results["phases"]["verify"] = {
                "project_accessible": True,
                "document_count": actual_docs,
                "verification_passed": True,
            }

            return True

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            self.results["errors"].append(f"Verification phase: {e}")
            return False

    def _estimate_processing_time(self, scan_result: dict) -> float:
        """Estimate processing time in minutes based on scan results."""
        # Base time: 1 minute
        base_time = 1.0

        # Add time per document (30 seconds each)
        doc_count = len(scan_result["readme_files"]) + len(scan_result["documentation"])
        doc_time = doc_count * 0.5

        # Add time for code extraction if enabled (10 seconds per file)
        code_time = 0.0
        if self.config.get("include_code_examples"):
            code_time = len(scan_result.get("code_files", [])) * 0.16

        # Add time for AI doc generation if enabled (2-3 minutes)
        ai_time = 2.5 if self.config.get("generate_docs") else 0.0

        return base_time + doc_time + code_time + ai_time

    async def _check_duplicate_project(self) -> bool:
        """Check if project with same name or repo already exists."""
        # TODO: Implement check against Archon API
        # GET /api/projects?search={title}
        # GET /api/projects?github_repo={repo_url}
        return False

    def _confirm_continue(self, message: str) -> bool:
        """Ask user for confirmation."""
        if self.config.get("non_interactive"):
            return False

        response = input(f"{message} [y/N] ").strip().lower()
        return response in ("y", "yes")

    def _prepare_project_data(self, scan_result: dict) -> dict:
        """Prepare project metadata from scan results."""
        repo_name = self._extract_repo_name()

        # Try to extract description from README
        description = ""
        if scan_result.get("readme_files"):
            # TODO: Read first README and extract description
            description = f"Imported from {self.config.get('repo_url', 'local repository')}"

        return {
            "title": repo_name,
            "description": description,
            "github_repo": self.config.get("repo_url"),
            "tags": ["imported", "archon-importer"],
        }

    def _extract_repo_name(self) -> str:
        """Extract repository name from URL or path."""
        if self.config.get("repo_url"):
            # Extract from GitHub URL: https://github.com/user/repo
            parts = self.config["repo_url"].rstrip("/").split("/")
            return parts[-1].replace(".git", "")
        elif self.config.get("local_path"):
            # Extract from local path
            return Path(self.config["local_path"]).name
        else:
            return "Imported Project"

    def _save_results(self):
        """Save import results to JSON file."""
        self.results["end_time"] = datetime.now().isoformat()

        result_file = Path.cwd() / ".archon-import-result.json"
        with open(result_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Results saved to: {result_file}")

    def _success_result(self, dry_run: bool = False) -> dict:
        """Create success result."""
        self.results["status"] = "success_dry_run" if dry_run else "success"
        return self.results

    def _failure_result(self, reason: str) -> dict:
        """Create failure result."""
        self.results["status"] = "failed"
        self.results["failure_reason"] = reason
        return self.results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import existing codebases into Archon knowledge base"
    )

    # Input source (one required)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo-url", help="GitHub repository URL")
    source_group.add_argument("--local-path", help="Local repository path")

    # Archon configuration
    parser.add_argument(
        "--archon-url",
        default="http://localhost:8181",
        help="Archon backend URL (default: http://localhost:8181)",
    )

    # Import options
    parser.add_argument(
        "--include-code-examples",
        action="store_true",
        help="Extract code snippets from source files",
    )
    parser.add_argument(
        "--generate-docs",
        action="store_true",
        help="Generate PRD/specs using DocumentAgent",
    )
    parser.add_argument(
        "--doc-patterns",
        default="*.md,*.rst,*.txt,docs/**/*",
        help="File patterns to scan (comma-separated)",
    )
    parser.add_argument(
        "--exclude-patterns",
        default="node_modules/**,.git/**,*.min.js",
        help="Patterns to exclude (comma-separated)",
    )

    # Execution options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be imported without making changes",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Don't prompt for confirmations",
    )

    args = parser.parse_args()

    # Build configuration
    config = {
        "repo_url": args.repo_url,
        "local_path": args.local_path,
        "archon_backend_url": args.archon_url,
        "include_code_examples": args.include_code_examples,
        "generate_docs": args.generate_docs,
        "doc_patterns": args.doc_patterns.split(","),
        "exclude_patterns": args.exclude_patterns.split(","),
        "dry_run": args.dry_run,
        "non_interactive": args.non_interactive,
    }

    # Run orchestrator
    orchestrator = ImportOrchestrator(config)
    result = await orchestrator.run()

    # Exit with appropriate code
    sys.exit(0 if result["status"].startswith("success") else 1)


if __name__ == "__main__":
    asyncio.run(main())
