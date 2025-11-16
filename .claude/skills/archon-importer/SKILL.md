---
name: archon-importer
description: Import existing codebases and documentation into Archon knowledge base. Scans repositories for documentation, uploads files, extracts code examples, creates projects with metadata, and generates AI-powered documentation (PRDs, technical specs, ERDs). Use when user wants to import/onboard a project into Archon.
---

# Archon Project Importer

Import existing codebases and documentation into Archon's knowledge management system with automatic documentation generation.

## When to Use This Skill

Invoke this skill when the user wants to:
- Import an existing project/repository into Archon
- Onboard a codebase to Archon's knowledge base
- Generate documentation for an undocumented project
- Create Archon project from GitHub repository
- Scan and index a local codebase

## Quick Start

```bash
# Import CURRENT codebase (working directory)
python import_current_codebase.py

# Import current codebase with dry-run first
python import_current_codebase.py --dry-run
python import_current_codebase.py  # Run for real after preview

# Import from GitHub URL
python import_repository.py --repo-url https://github.com/user/repo

# Import from local path
python import_repository.py --local-path /path/to/repo

# Import with custom options
python import_repository.py --repo-url https://github.com/user/repo \
  --include-code-examples \
  --generate-docs \
  --doc-patterns "*.md,*.rst,docs/**"
```

## Import Workflow

The import process follows a **plan → validate → execute → verify** pattern:

### 1. Plan Phase
- Detect repository type (Git, local directory)
- Scan for documentation files
- Identify codebase structure
- Estimate processing time

### 2. Validate Phase
- Check Archon backend connectivity
- Verify API credentials (LLM provider for doc generation)
- Validate file access permissions
- Confirm no duplicate projects exist

### 3. Execute Phase
- Clone repository (if remote)
- Upload documentation files to Archon knowledge base
- Extract code examples from source files
- Create Archon project with metadata
- Generate AI documentation (PRD, specs, ERD)

### 4. Verify Phase
- Confirm all files uploaded successfully
- Check project creation in Archon
- Verify generated documents
- Report any failures or warnings

## Available Scripts

### `import_current_codebase.py`
**Import the codebase Claude Code is currently working in.**

This is the RECOMMENDED script when Claude is already working in a codebase and the user wants to import it into Archon.

**Usage:**
```bash
python import_current_codebase.py [OPTIONS]
```

**Options:**
- `--archon-url URL`: Archon backend URL (default: http://localhost:8181)
- `--include-code-examples`: Extract code snippets (default: True)
- `--no-code-examples`: Skip code extraction
- `--generate-docs`: Generate PRD/specs (default: True)
- `--no-docs`: Skip AI doc generation
- `--dry-run`: Preview without making changes

**What it does:**
- Automatically detects current working directory
- Detects Git repository and remote URL (if available)
- Scans for documentation and code in current project
- Imports everything into Archon with intelligent defaults

**Example:**
```bash
# User is working in ~/projects/my-app with Claude Code
# Simply run:
python import_current_codebase.py --dry-run  # Preview first
python import_current_codebase.py             # Then import
```

---

### `import_repository.py`
Main import orchestrator - handles full workflow for external repositories.

**Usage:**
```bash
python import_repository.py [OPTIONS]
```

**Options:**
- `--repo-url URL`: GitHub repository URL
- `--local-path PATH`: Local repository path
- `--archon-url URL`: Archon backend URL (default: http://localhost:8181)
- `--include-code-examples`: Extract code snippets from source files
- `--generate-docs`: Generate PRD/specs using DocumentAgent
- `--doc-patterns PATTERNS`: File patterns to scan (comma-separated)
- `--exclude-patterns PATTERNS`: Patterns to exclude
- `--dry-run`: Preview what would be imported without making changes

**Output:**
- Progress updates to console
- JSON summary file: `.archon-import-result.json`
- Project ID and URLs on success

### `scan_repository.py`
Scan repository for documentation files (used by main script).

**Returns:**
```json
{
  "readme_files": ["README.md", "docs/README.md"],
  "documentation": ["CONTRIBUTING.md", "docs/api.md"],
  "code_files": ["src/main.py", "lib/util.js"],
  "config_files": ["package.json", "setup.py"],
  "estimated_size_mb": 5.2
}
```

### `validate_archon_connection.py`
Validate Archon backend connectivity and credentials.

**Returns:**
```json
{
  "backend_reachable": true,
  "llm_provider_configured": true,
  "embedding_provider_configured": true,
  "errors": []
}
```

## Configuration

Create `.archon-importer-config.json` in skill directory or repository root:

```json
{
  "archon_backend_url": "http://localhost:8181",
  "default_knowledge_type": "technical",
  "doc_patterns": ["*.md", "*.rst", "*.txt", "docs/**/*", "*.pdf"],
  "exclude_patterns": ["node_modules/**", ".git/**", "*.min.js"],
  "code_file_patterns": ["*.py", "*.js", "*.ts", "*.java", "*.go"],
  "max_file_size_mb": 10,
  "generate_docs_by_default": true,
  "include_code_examples_by_default": true
}
```

## Error Handling

All scripts implement robust error handling:
- **Network errors**: Retry with exponential backoff
- **File access errors**: Skip file and log warning
- **API errors**: Clear error messages with resolution steps
- **Validation failures**: Stop before making changes

See `ERROR_REFERENCE.md` for detailed error codes and solutions.

## Integration with Archon

### API Endpoints Used
- `POST /api/documents/upload` - Upload documentation files
- `POST /api/projects` - Create project entry
- `POST /api/knowledge-items/crawl` - Crawl online docs (if provided)
- `GET /api/progress/{id}` - Track upload progress

### Data Flow
1. **Repository → Scanner** → Identifies files
2. **Files → Uploader** → Sends to Archon `/api/documents/upload`
3. **Metadata → Project Creator** → Creates project via `/api/projects`
4. **Project → DocumentAgent** → Generates PRD/specs
5. **Results → Verification** → Confirms success

## Advanced Features

### Custom Documentation Generation
Override default PRD generation with custom templates:

```bash
python import_repository.py --repo-url URL \
  --doc-template-prd templates/custom_prd.md \
  --doc-template-spec templates/custom_spec.md
```

### Incremental Updates
Re-import to update existing project:

```bash
python import_repository.py --repo-url URL \
  --project-id existing-uuid-here \
  --incremental
```

### Batch Import
Import multiple repositories:

```bash
python batch_import.py --repos-file repositories.txt
```

## Limitations

- **File Size**: Individual files > 10MB are skipped (configurable)
- **Total Size**: Repositories > 1GB may take 10+ minutes
- **API Rate Limits**: Respects Archon backend rate limits
- **Code Examples**: Only extracts from supported languages (see `CODE_EXTRACTION_REFERENCE.md`)

## Reference Documentation

Load these files only when needed:
- `ERROR_REFERENCE.md` - Error codes and troubleshooting
- `CODE_EXTRACTION_REFERENCE.md` - Supported languages and patterns
- `API_INTEGRATION_REFERENCE.md` - Archon API details
- `EXAMPLES.md` - Real-world import examples

## Success Criteria

A successful import produces:
- ✅ Project created in Archon
- ✅ All documentation files uploaded to knowledge base
- ✅ Code examples extracted (if enabled)
- ✅ AI-generated PRD document
- ✅ Technical specifications (if enabled)
- ✅ ERD diagram (if database detected)
- ✅ No critical errors in log

## Tips for Claude

- **Use import_current_codebase.py when user is working in a codebase**: This is the most common scenario
- **Always validate first**: Run validation before attempting import
- **Check dry-run**: Use `--dry-run` to preview before actual import
- **Ask for confirmation**: Show the preview and ask user before proceeding
- **Read error reference**: If errors occur, consult `ERROR_REFERENCE.md`
- **Progressive disclosure**: Only read reference files when encountering specific issues
- **Report progress**: Keep user informed during long operations

## Common Scenarios for Claude

### Scenario 1: User Says "Import this project into Archon"
When Claude is already working in a codebase:
1. Run `python import_current_codebase.py --dry-run`
2. Show user the preview (files found, size, estimated time)
3. Ask: "Should I proceed with importing X files (~Y minutes)?"
4. If yes: Run `python import_current_codebase.py`
5. Report results and provide project URL

### Scenario 2: User Provides GitHub URL
When user gives a specific repository URL:
1. Run `python import_repository.py --repo-url URL --dry-run`
2. Show preview to user
3. Ask for confirmation
4. Run actual import with `--include-code-examples --generate-docs`

### Scenario 3: Import Fails with Error
When import fails:
1. Read `ERROR_REFERENCE.md` to find the error code
2. Explain the issue to user
3. Suggest the recommended solution
4. If user wants, retry with fixes applied
