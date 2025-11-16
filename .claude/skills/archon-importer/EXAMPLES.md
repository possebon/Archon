# Import Examples

Real-world examples of importing different types of projects into Archon.

## Example 0: Import Current Codebase (Most Common)

**Scenario**: You're working on a project with Claude Code and want to import it into Archon.

```bash
# You're already in the project directory
# Just run the current codebase importer

# First, preview what will be imported
python import_current_codebase.py --dry-run

# Output shows:
# 🔍 Importing current codebase from: /Users/you/projects/my-app
#    Project name: my-app
# 📦 Detected Git repository: https://github.com/you/my-app
#
# 📋 Phase 1: Planning
# --------------------------------------------------
# 🔍 Scanning repository for documentation and code...
#   ✓ Found 1 README files
#   ✓ Found 12 documentation files
#   ✓ Found 45 code files
#   ✓ Estimated size: 3.2 MB
#   ⏱️  Estimated processing time: 4.5 minutes

# If preview looks good, run for real
python import_current_codebase.py
```

**What happens**:
1. Detects you're in `/Users/you/projects/my-app`
2. Automatically finds Git remote URL
3. Scans for all documentation and code
4. Uploads to Archon with intelligent defaults
5. Generates PRD and specs automatically

**Time**: ~4-5 minutes

**Claude Code Usage**:
```
User: Import this project into Archon

Claude: I'll import the current codebase into Archon. Let me first preview
what will be imported.

[Runs: python import_current_codebase.py --dry-run]

The scan found:
- 1 README file
- 12 documentation files
- 45 code files (will extract examples)
- Estimated size: 3.2 MB
- Processing time: ~4.5 minutes

Should I proceed with the import and generate AI documentation (PRD, specs)?

User: Yes

Claude: Starting the import...

[Runs: python import_current_codebase.py]

✅ Import completed successfully!

Project created: http://localhost:8181/projects/abc-123-def
- Uploaded 13 documentation files
- Extracted 45 code examples
- Generated PRD and Technical Specification

You can now search this content in Archon's knowledge base and use it with MCP tools.
```

---

## Example 1: Import Open Source Project from GitHub

Import a popular open-source library with full documentation generation:

```bash
python import_repository.py \
  --repo-url https://github.com/fastapi/fastapi \
  --include-code-examples \
  --generate-docs \
  --archon-url http://localhost:8181
```

**What happens**:
1. Clones FastAPI repository
2. Finds README.md, docs/**/*.md
3. Uploads ~50 documentation files
4. Extracts Python code examples
5. Creates "fastapi" project in Archon
6. Generates PRD and Technical Spec (detects API framework)

**Time**: ~5-8 minutes

---

## Example 2: Import Local Project (Dry Run First)

Import a local project, previewing first:

```bash
# Preview what would be imported
python import_repository.py \
  --local-path ~/projects/my-app \
  --dry-run

# If preview looks good, run for real
python import_repository.py \
  --local-path ~/projects/my-app \
  --include-code-examples \
  --generate-docs
```

**What happens**:
1. Scans ~/projects/my-app
2. Dry run shows: 15 docs, 200 code files, 25MB
3. Real run uploads docs and extracts code
4. Creates project with AI-generated documentation

**Time**: ~3-5 minutes

---

## Example 3: Import Documentation Only (No Code)

Import just the documentation without code examples:

```bash
python import_repository.py \
  --repo-url https://github.com/anthropics/anthropic-sdk-python \
  --doc-patterns "*.md,docs/**/*,examples/**/*.md" \
  --archon-url http://localhost:8181
```

**What happens**:
1. Clones repository
2. Only scans for .md files in specified patterns
3. Skips code extraction (no `--include-code-examples`)
4. Creates project without AI docs (no `--generate-docs`)

**Time**: ~2-3 minutes

---

## Example 4: Import with Custom Patterns

Import a Rust project with specific file patterns:

```bash
python import_repository.py \
  --repo-url https://github.com/tokio-rs/tokio \
  --doc-patterns "*.md,*.rst,doc/**/*,guides/**/*" \
  --exclude-patterns "node_modules/**,target/**,.git/**" \
  --include-code-examples \
  --generate-docs
```

**What happens**:
1. Finds README.md, doc/**/*.md, guides/**/*.md
2. Excludes Rust build artifacts (target/**)
3. Extracts Rust code examples from .rs files
4. Generates documentation (PRD, Tech Spec)

**Time**: ~6-10 minutes

---

## Example 5: Import Database-Heavy Project

Import a project with database schema:

```bash
python import_repository.py \
  --repo-url https://github.com/supabase/supabase \
  --include-code-examples \
  --generate-docs \
  --archon-url http://localhost:8181
```

**What happens**:
1. Scans large repository
2. Detects database files (migrations/, schema.sql)
3. Generates PRD + Tech Spec + **ERD diagram**
4. ERD includes table definitions and relationships

**Time**: ~10-15 minutes (large repo)

---

## Example 6: Incremental Update

Update an existing project with new documentation:

```bash
# Initial import
python import_repository.py \
  --repo-url https://github.com/user/my-project

# Later, re-import to update (not yet implemented)
python import_repository.py \
  --repo-url https://github.com/user/my-project \
  --project-id abc-123-def \
  --incremental
```

**Note**: Incremental mode is planned but not yet implemented.

---

## Example 7: Batch Import Multiple Repositories

Import multiple projects from a list:

```bash
# Create repositories.txt
cat > repositories.txt <<EOF
https://github.com/django/django
https://github.com/pallets/flask
https://github.com/fastapi/fastapi
EOF

# Batch import (script not yet created)
python batch_import.py --repos-file repositories.txt --generate-docs
```

**What happens**:
1. Reads repository list
2. Imports each sequentially
3. Generates documentation for all
4. Creates separate projects for each

**Time**: ~20-30 minutes for 3 projects

---

## Example 8: Import Documentation Site

Import from live documentation website:

```bash
# First, create project
python import_repository.py \
  --repo-url https://github.com/user/project \
  --archon-url http://localhost:8181

# Then manually crawl docs site in Archon UI
# Navigate to Knowledge Base → Add Source → Crawl Website
# URL: https://docs.example.com
# This will link docs to the project
```

**What happens**:
1. Creates project from GitHub repo
2. Manually crawl live docs site
3. Docs and code are in same project

---

## Example 9: Import Private Repository (Future)

For private repositories (requires authentication):

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Import (requires authentication support - not yet implemented)
python import_repository.py \
  --repo-url https://github.com/private-org/private-repo \
  --github-token $GITHUB_TOKEN
```

**Note**: Private repository support is planned.

---

## Example 10: Import with Size Limits

Import large project with size constraints:

```bash
python import_repository.py \
  --repo-url https://github.com/kubernetes/kubernetes \
  --max-file-size-mb 5 \
  --exclude-patterns "*.pdf,*.zip,vendor/**,node_modules/**" \
  --doc-patterns "*.md,docs/**/*.md" \
  --archon-url http://localhost:8181
```

**What happens**:
1. Skips files larger than 5MB
2. Excludes vendor directories
3. Only processes markdown files
4. Prevents memory issues with huge repo

**Time**: ~8-12 minutes

---

## Troubleshooting Common Scenarios

### Scenario: Import Fails During Upload

```bash
# Run with dry-run first to validate
python import_repository.py \
  --repo-url https://github.com/user/project \
  --dry-run

# Check the preview, then run for real
python import_repository.py \
  --repo-url https://github.com/user/project
```

### Scenario: Too Many Files

```bash
# Limit to just essential docs
python import_repository.py \
  --local-path ~/huge-project \
  --doc-patterns "README.md,docs/getting-started.md,docs/api.md" \
  --exclude-patterns "**/*" \
  --archon-url http://localhost:8181
```

### Scenario: Check What Would Be Imported

```bash
# Use dry-run to see scan results
python import_repository.py \
  --repo-url https://github.com/user/project \
  --dry-run

# Results show:
# ✓ Found 12 README files
# ✓ Found 45 documentation files
# ✓ Found 230 code files
# ✓ Estimated size: 18.5 MB
# ⏱️  Estimated processing time: 8.2 minutes
```

---

## Results and Verification

After successful import, check:

1. **Console Output**: Shows progress and summary
2. **Results File**: `.archon-import-result.json` with full details
3. **Archon UI**: Navigate to project and verify documents
4. **Knowledge Base**: Search imported content

Example result file:
```json
{
  "status": "success",
  "project_id": "abc-123-def",
  "project_url": "http://localhost:8181/projects/abc-123-def",
  "phases": {
    "plan": { "total_files": 57 },
    "execute": {
      "documents_uploaded": 57,
      "code_examples": 120,
      "ai_docs_generated": true
    }
  }
}
```
