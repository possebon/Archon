#!/usr/bin/env python3
"""
Import Current Codebase to Archon

Special variant for importing the codebase that Claude Code is currently working in.
Detects the current working directory and imports it directly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Import the main orchestrator
from import_repository import ImportOrchestrator


async def import_current_codebase(
    include_code_examples: bool = True,
    generate_docs: bool = True,
    dry_run: bool = False,
    archon_url: str = "http://localhost:8181",
) -> dict:
    """
    Import the current working directory codebase into Archon.

    Args:
        include_code_examples: Extract code snippets from source files
        generate_docs: Generate PRD/specs using DocumentAgent
        dry_run: Preview without making changes
        archon_url: Archon backend URL

    Returns:
        Import results dictionary
    """
    # Get current working directory
    current_dir = Path.cwd().resolve()

    print(f"🔍 Importing current codebase from: {current_dir}")
    print(f"   Project name: {current_dir.name}")
    print()

    # Detect if it's a git repository
    is_git_repo = (current_dir / ".git").exists()
    repo_url = None

    if is_git_repo:
        # Try to get remote URL
        import subprocess
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=str(current_dir),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                repo_url = result.stdout.strip()
                print(f"📦 Detected Git repository: {repo_url}")
        except Exception:
            pass

    # Build configuration
    config = {
        "local_path": str(current_dir),
        "repo_url": repo_url,  # Optional, for metadata only
        "archon_backend_url": archon_url,
        "include_code_examples": include_code_examples,
        "generate_docs": generate_docs,
        "doc_patterns": [
            "*.md",
            "*.rst",
            "*.txt",
            "docs/**/*",
            "documentation/**/*",
            "README*",
            "CONTRIBUTING*",
            "CHANGELOG*",
            "LICENSE*",
        ],
        "exclude_patterns": [
            "node_modules/**",
            ".git/**",
            "*.min.js",
            "*.min.css",
            "dist/**",
            "build/**",
            "__pycache__/**",
            "*.pyc",
            ".venv/**",
            "venv/**",
            "*.lock",
            ".next/**",
            ".nuxt/**",
            "target/**",  # Rust
            "bin/**",
            "obj/**",     # C#
            ".claude/**",  # Don't import Claude Code files
        ],
        "dry_run": dry_run,
        "non_interactive": False,
    }

    # Run the import
    orchestrator = ImportOrchestrator(config)
    result = await orchestrator.run()

    return result


async def main():
    """Main entry point for importing current codebase."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import current codebase (working directory) into Archon"
    )

    parser.add_argument(
        "--archon-url",
        default="http://localhost:8181",
        help="Archon backend URL (default: http://localhost:8181)",
    )
    parser.add_argument(
        "--include-code-examples",
        action="store_true",
        default=True,
        help="Extract code snippets from source files (default: True)",
    )
    parser.add_argument(
        "--no-code-examples",
        dest="include_code_examples",
        action="store_false",
        help="Skip code example extraction",
    )
    parser.add_argument(
        "--generate-docs",
        action="store_true",
        default=True,
        help="Generate PRD/specs using DocumentAgent (default: True)",
    )
    parser.add_argument(
        "--no-docs",
        dest="generate_docs",
        action="store_false",
        help="Skip AI documentation generation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be imported without making changes",
    )

    args = parser.parse_args()

    # Run the import
    result = await import_current_codebase(
        include_code_examples=args.include_code_examples,
        generate_docs=args.generate_docs,
        dry_run=args.dry_run,
        archon_url=args.archon_url,
    )

    # Exit with appropriate code
    sys.exit(0 if result["status"].startswith("success") else 1)


if __name__ == "__main__":
    asyncio.run(main())
