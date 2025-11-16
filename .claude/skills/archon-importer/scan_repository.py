#!/usr/bin/env python3
"""
Repository Scanner

Scans repositories for documentation and code files.
Implements robust file detection with configurable patterns.
"""

import fnmatch
import subprocess
from pathlib import Path
from typing import Any


class RepositoryScanner:
    """Scans repositories for importable content."""

    # Default documentation patterns
    DOC_PATTERNS = [
        "README*",
        "*.md",
        "*.rst",
        "*.txt",
        "docs/**/*",
        "documentation/**/*",
        "*.pdf",
    ]

    # Default code file patterns
    CODE_PATTERNS = [
        "*.py",
        "*.js",
        "*.ts",
        "*.jsx",
        "*.tsx",
        "*.java",
        "*.go",
        "*.rs",
        "*.rb",
        "*.php",
        "*.c",
        "*.cpp",
        "*.h",
        "*.cs",
        "*.swift",
    ]

    # Default exclude patterns
    EXCLUDE_PATTERNS = [
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
    ]

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.repo_path = self._get_repo_path()

    def _get_repo_path(self) -> Path:
        """Get repository path, cloning if needed."""
        if self.config.get("local_path"):
            return Path(self.config["local_path"]).resolve()
        elif self.config.get("repo_url"):
            # Clone to temporary directory
            return self._clone_repository(self.config["repo_url"])
        else:
            raise ValueError("Either repo_url or local_path must be provided")

    def _clone_repository(self, repo_url: str) -> Path:
        """Clone repository to temporary location."""
        import tempfile

        temp_dir = Path(tempfile.mkdtemp(prefix="archon_import_"))

        print(f"  📥 Cloning repository from {repo_url}...")

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(temp_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"  ✓ Cloned to {temp_dir}")
            return temp_dir
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repository: {e.stderr}")

    async def scan(self) -> dict[str, Any]:
        """Scan repository and categorize files."""
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path not found: {self.repo_path}")

        # Get all files
        all_files = self._get_all_files()

        # Categorize files
        readme_files = self._filter_files(all_files, ["README*"])
        doc_files = self._filter_files(
            all_files, self.config.get("doc_patterns", self.DOC_PATTERNS)
        )
        code_files = (
            self._filter_files(all_files, self.CODE_PATTERNS)
            if self.config.get("include_code_examples")
            else []
        )

        # Remove READMEs from doc_files to avoid duplication
        doc_files = [f for f in doc_files if not self._is_readme(f)]

        # Get config files for metadata
        config_files = self._filter_files(
            all_files,
            ["package.json", "setup.py", "pyproject.toml", "Cargo.toml", "pom.xml"],
        )

        # Calculate total size
        total_size = sum(f.stat().st_size for f in readme_files + doc_files + code_files)
        size_mb = total_size / (1024 * 1024)

        return {
            "readme_files": [str(f.relative_to(self.repo_path)) for f in readme_files],
            "documentation": [str(f.relative_to(self.repo_path)) for f in doc_files],
            "code_files": [str(f.relative_to(self.repo_path)) for f in code_files],
            "config_files": [str(f.relative_to(self.repo_path)) for f in config_files],
            "total_files": len(readme_files) + len(doc_files) + len(code_files),
            "estimated_size_mb": size_mb,
            "repository_path": str(self.repo_path),
        }

    def _get_all_files(self) -> list[Path]:
        """Get all non-excluded files in repository."""
        all_files = []
        exclude_patterns = self.config.get("exclude_patterns", self.EXCLUDE_PATTERNS)

        for path in self.repo_path.rglob("*"):
            if not path.is_file():
                continue

            # Check if excluded
            relative_path = str(path.relative_to(self.repo_path))
            if self._is_excluded(relative_path, exclude_patterns):
                continue

            # Check file size (skip files > 10MB by default)
            max_size = self.config.get("max_file_size_mb", 10) * 1024 * 1024
            if path.stat().st_size > max_size:
                continue

            all_files.append(path)

        return all_files

    def _filter_files(self, files: list[Path], patterns: list[str]) -> list[Path]:
        """Filter files by patterns."""
        matched = []

        for file_path in files:
            relative_path = str(file_path.relative_to(self.repo_path))

            for pattern in patterns:
                # Handle glob patterns
                if "**" in pattern:
                    if fnmatch.fnmatch(relative_path, pattern):
                        matched.append(file_path)
                        break
                # Handle simple patterns
                elif fnmatch.fnmatch(file_path.name, pattern):
                    matched.append(file_path)
                    break

        return matched

    def _is_excluded(self, relative_path: str, exclude_patterns: list[str]) -> bool:
        """Check if file matches exclusion patterns."""
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
        return False

    def _is_readme(self, path: Path) -> bool:
        """Check if file is a README."""
        return path.name.upper().startswith("README")
