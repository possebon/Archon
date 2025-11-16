# Archon Importer - Claude Code Skill

A Claude Code skill for importing existing codebases and documentation into Archon's knowledge management system.

## Overview

The `archon-importer` skill enables Claude to:
- 📂 Scan repositories for documentation and code
- ☁️ Clone from GitHub or import local directories
- 📤 Upload files to Archon knowledge base
- 🔍 Extract code examples automatically
- 📦 Create organized projects with metadata
- 🤖 Generate AI-powered documentation (PRDs, specs, ERDs)

## Quick Start

### Prerequisites

1. **Archon Backend Running**
   ```bash
   cd python && uv run python -m src.server.main
   # Or: docker compose up -d
   ```

2. **Archon Configuration**
   - LLM provider configured (for AI doc generation)
   - Embedding provider configured (required for uploads)
   - Access to Archon UI at http://localhost:8181

### Basic Usage

```bash
# MOST COMMON: Import current codebase (when Claude is working in a project)
python import_current_codebase.py --dry-run  # Preview first
python import_current_codebase.py            # Then import

# Import from GitHub
python import_repository.py --repo-url https://github.com/user/repo

# Import local directory
python import_repository.py --local-path /path/to/project

# Full import with AI docs
python import_repository.py \
  --repo-url https://github.com/user/repo \
  --include-code-examples \
  --generate-docs
```

### Preview Before Importing

```bash
# Dry run to see what would be imported
python import_repository.py --repo-url URL --dry-run
```

## File Structure

```
archon-importer/
├── SKILL.md                          # Main skill documentation
├── README.md                         # This file
├── import_current_codebase.py        # ⭐ Import current working directory
├── import_repository.py              # Main orchestrator for external repos
├── scan_repository.py                # Repository scanner
├── validate_archon_connection.py     # Connection validator
├── upload_to_archon.py               # Upload handler
├── generate_documentation.py         # AI doc generator
├── ERROR_REFERENCE.md                # Error codes and solutions
├── EXAMPLES.md                       # Real-world examples
└── .archon-importer-config.json.example  # Configuration template
```

## Features

### Intelligent Scanning
- Detects README, documentation, and code files
- Configurable file patterns and exclusions
- Handles multiple documentation formats (MD, RST, TXT, PDF)
- Estimates processing time

### Robust Upload
- Retry logic with exponential backoff
- Progress tracking for long operations
- Handles large files (configurable size limits)
- Batch processing with error recovery

### AI Documentation Generation
- Automatic PRD creation
- Technical specification (if API detected)
- ERD diagram (if database detected)
- Uses Archon's DocumentAgent

### Validation & Error Handling
- **Plan** → **Validate** → **Execute** → **Verify** workflow
- Pre-flight checks before making changes
- Comprehensive error messages
- Results saved to JSON file

## Configuration

### Command Line Options

```bash
python import_repository.py [OPTIONS]

Required (one of):
  --repo-url URL              GitHub repository URL
  --local-path PATH           Local repository path

Optional:
  --archon-url URL            Archon backend URL (default: http://localhost:8181)
  --include-code-examples     Extract code snippets from source files
  --generate-docs             Generate PRD/specs using DocumentAgent
  --doc-patterns PATTERNS     File patterns to scan (comma-separated)
  --exclude-patterns PATTERNS Patterns to exclude (comma-separated)
  --dry-run                   Preview without making changes
  --non-interactive           Don't prompt for confirmations
```

### Config File

Create `.archon-importer-config.json`:

```json
{
  "archon_backend_url": "http://localhost:8181",
  "default_knowledge_type": "technical",
  "doc_patterns": ["*.md", "*.rst", "docs/**/*"],
  "exclude_patterns": ["node_modules/**", ".git/**"],
  "max_file_size_mb": 10,
  "generate_docs_by_default": true
}
```

## Workflow

### Phase 1: Planning
1. Clone repository (if remote)
2. Scan for documentation and code files
3. Estimate processing time
4. Display preview of what will be imported

### Phase 2: Validation
1. Check Archon backend connectivity
2. Verify LLM provider configured (if generating docs)
3. Verify embedding provider configured
4. Check for duplicate projects

### Phase 3: Execution
1. Upload documentation files to knowledge base
2. Extract and upload code examples
3. Create project in Archon
4. Generate AI documentation (PRD, specs, ERD)

### Phase 4: Verification
1. Confirm project created successfully
2. Verify document count matches expected
3. Check for any errors or warnings
4. Save results to `.archon-import-result.json`

## Examples

See `EXAMPLES.md` for detailed real-world examples including:
- Open source projects
- Local projects with dry-run
- Documentation-only imports
- Custom file patterns
- Database-heavy projects
- Batch imports

## Error Handling

See `ERROR_REFERENCE.md` for:
- Complete error code reference
- Causes and solutions
- Troubleshooting guide
- Debug mode instructions

## Integration with Claude Code

### How Claude Should Use This Skill

When a user wants to import a project into Archon:

1. **Activate the skill** by reading SKILL.md
2. **Run validation first** using dry-run
3. **Show preview** to user
4. **Ask for confirmation** before importing
5. **Monitor progress** and report to user
6. **Handle errors** gracefully using ERROR_REFERENCE.md
7. **Verify success** and provide project URL

### Example Claude Conversation

```
User: Import the FastAPI repository into Archon

Claude: I'll import the FastAPI repository into Archon. Let me first run a
dry-run to preview what will be imported.

[Runs: python import_repository.py --repo-url https://github.com/fastapi/fastapi --dry-run]

The scan found:
- 1 README file
- 48 documentation files
- 156 code files
- Estimated size: 12.3 MB
- Processing time: ~5 minutes

Should I proceed with the import and generate AI documentation (PRD, specs)?

User: Yes, go ahead

Claude: Starting the import with AI documentation generation...

[Runs: python import_repository.py --repo-url URL --include-code-examples --generate-docs]

✅ Import completed successfully!

Project created: http://localhost:8181/projects/abc-123-def
- Uploaded 49 documentation files
- Extracted 156 code examples
- Generated PRD and Technical Specification

You can now search this content in Archon's knowledge base.
```

## Limitations

- **File Size**: Individual files > 10MB skipped (configurable)
- **Repository Size**: Very large repos (>1GB) may take 15+ minutes
- **Private Repos**: Authentication not yet implemented
- **Incremental Updates**: Not yet implemented

## Development

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run specific test
pytest tests/test_scanner.py
```

### Adding New Features

1. Update SKILL.md with new capability
2. Implement in appropriate module
3. Add error codes to ERROR_REFERENCE.md
4. Add example to EXAMPLES.md
5. Test with real repositories

## Troubleshooting

### Import Hangs

- Check backend logs: `docker compose logs archon-server`
- Large files take time (be patient)
- Use `--dry-run` first to estimate time

### Backend Unreachable

```bash
# Start Archon backend
docker compose up -d

# Or run locally
cd python && uv run python -m src.server.main
```

### Missing Dependencies

```bash
# Install Python dependencies
pip install aiohttp requests

# For repository cloning
git --version  # Ensure git is installed
```

## Contributing

To improve this skill:

1. Test with different repository types
2. Report issues with error details
3. Suggest improvements to workflow
4. Add more examples to EXAMPLES.md

## License

This skill is part of the Archon project. See project LICENSE file.
