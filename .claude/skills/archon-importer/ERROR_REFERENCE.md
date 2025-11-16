# Error Reference Guide

This document provides detailed error codes, causes, and solutions for the Archon Importer.

## Table of Contents
- [Planning Phase Errors](#planning-phase-errors)
- [Validation Phase Errors](#validation-phase-errors)
- [Execution Phase Errors](#execution-phase-errors)
- [Verification Phase Errors](#verification-phase-errors)
- [Network Errors](#network-errors)

## Planning Phase Errors

### E001: Repository Not Found
**Error**: `Failed to clone repository: Repository not found`

**Cause**: The specified GitHub repository URL is invalid or private.

**Solutions**:
1. Verify the repository URL is correct
2. Check if repository is public (private repos require authentication)
3. Ensure you have network connectivity to GitHub

---

### E002: No Files to Import
**Error**: `No files found to import`

**Cause**: The repository contains no documentation or code files matching the patterns.

**Solutions**:
1. Check the `--doc-patterns` and verify they match your files
2. Review `--exclude-patterns` to ensure they're not too broad
3. Verify the repository actually contains documentation files

---

### E003: File Size Exceeded
**Error**: `File size exceeds maximum allowed (10MB)`

**Cause**: One or more files exceed the size limit.

**Solutions**:
1. Increase the limit with `--max-file-size-mb 20`
2. Exclude large files using `--exclude-patterns "*.pdf"`
3. Process large files separately or manually

---

## Validation Phase Errors

### E101: Backend Unreachable
**Error**: `Cannot reach Archon backend`

**Cause**: Archon backend is not running or URL is incorrect.

**Solutions**:
1. Start Archon backend: `cd python && uv run python -m src.server.main`
2. Or use Docker: `docker compose up -d`
3. Verify URL with `--archon-url http://localhost:8181`
4. Check firewall/network settings

---

### E102: LLM Provider Not Configured
**Error**: `LLM provider not configured`

**Cause**: No LLM API key is set in Archon settings.

**Solutions**:
1. Open Archon UI → Settings
2. Configure OpenAI, Anthropic, or other LLM provider
3. Note: This is only required if using `--generate-docs`
4. Skip AI generation: remove `--generate-docs` flag

---

### E103: Embedding Provider Not Configured
**Error**: `Embedding provider not configured - required for knowledge base`

**Cause**: No embedding provider (OpenAI/Ollama) is configured.

**Solutions**:
1. Open Archon UI → Settings
2. Configure OpenAI API key (provides embeddings)
3. Or set up local Ollama for embeddings
4. This is **required** for importing documents

---

### E104: Project Already Exists
**Error**: `Project with this name or GitHub URL already exists`

**Cause**: A project with the same name or repository URL exists.

**Solutions**:
1. Use `--incremental` flag to update existing project
2. Delete the existing project in Archon UI
3. Continue anyway (will create duplicate)

---

## Execution Phase Errors

### E201: Document Upload Failed
**Error**: `Failed to upload document: [filename]`

**Cause**: File upload to Archon failed (network, file format, or API error).

**Solutions**:
1. Check file is a supported format (MD, RST, TXT, PDF)
2. Verify file is not corrupted
3. Check Archon backend logs for specific error
4. Retry upload manually via Archon UI

---

### E202: Project Creation Failed
**Error**: `Failed to create project: [error message]`

**Cause**: Project creation API call failed.

**Solutions**:
1. Check Archon database is running
2. Verify Supabase connection in Archon config
3. Review backend logs: `docker compose logs archon-server`
4. Try creating project manually in UI first

---

### E203: Code Extraction Failed
**Error**: `Failed to extract code examples from [filename]`

**Cause**: Code extraction service encountered an error.

**Solutions**:
1. Check if file is a valid code file
2. Verify file encoding is UTF-8
3. Skip code extraction: remove `--include-code-examples`
4. Process code files separately

---

### E204: AI Documentation Generation Failed
**Error**: `AI generation failed: [error]`

**Cause**: DocumentAgent encountered an error or LLM API failed.

**Solutions**:
1. Verify LLM API key is valid
2. Check LLM API rate limits (wait and retry)
3. Review backend logs for specific error
4. Generate docs manually later via Archon UI

---

## Verification Phase Errors

### E301: Project Not Found After Creation
**Error**: `Cannot retrieve created project`

**Cause**: Project was created but cannot be fetched from database.

**Solutions**:
1. Check database connection
2. Verify project ID in logs
3. Manually navigate to project in Archon UI
4. Check Supabase dashboard for project record

---

### E302: Document Count Mismatch
**Error**: `Document count mismatch: expected X, found Y`

**Cause**: Some documents failed to upload but errors weren't caught.

**Solutions**:
1. Review upload warnings in output
2. Re-run import to upload missing files
3. Upload missing files manually via UI
4. This is a warning, not a fatal error

---

## Network Errors

### E401: Connection Timeout
**Error**: `Request timeout`

**Cause**: Network request took too long.

**Solutions**:
1. Check internet connection
2. Verify Archon backend is responsive
3. Retry the operation
4. For large files, increase timeout (not configurable yet)

---

### E402: Max Retries Exceeded
**Error**: `Max retries exceeded`

**Cause**: Network request failed 3 times.

**Solutions**:
1. Check network stability
2. Verify Archon backend is running
3. Wait a moment and retry entire import
4. Check for API rate limiting

---

## General Troubleshooting

### Debug Mode
Enable verbose logging:
```bash
export ARCHON_IMPORTER_DEBUG=1
python import_repository.py [options]
```

### Check Logs
1. **Import logs**: See console output
2. **Results file**: `.archon-import-result.json`
3. **Backend logs**: `docker compose logs archon-server`
4. **Browser console**: Check network tab in DevTools

### Common Issues

**Import hangs during upload**:
- Large files take time (10MB ~ 30-60 seconds)
- Check backend logs for progress
- Use `--dry-run` first to estimate time

**Partial import succeeded**:
- Check `.archon-import-result.json` for details
- Re-run with same parameters (will skip uploaded files)
- Or manually upload missing files

**Cannot find imported project**:
- Refresh Archon UI
- Check URL in import results
- Search by project name in UI

---

## Getting Help

If you encounter an error not listed here:

1. **Check import results**: `.archon-import-result.json`
2. **Review backend logs**: `docker compose logs archon-server`
3. **Enable debug mode**: See above
4. **Create GitHub issue**: Include error message and logs
