# Security Policy

## Reporting a vulnerability

Please do not disclose exploitable vulnerabilities, credentials, or private repository data in public issue comments.

Use the private vulnerability reporting mechanism provided by the GitHub repository, if enabled. If private reporting is unavailable, contact the maintainers through a verified private channel before publishing details.

## Scope

Security reports may include:
- Credential exposure
- Repository path traversal
- Unsafe agent tool execution
- Prompt-injection handling weaknesses
- Sensitive data leakage through LLM prompts or telemetry
- API authorization or analytics data exposure
- Unsafe dependency or deployment configuration

## Supported versions

Security fixes should target the latest maintained version. Check the repository's release notes for supported release information.

## Disclosure

Please allow maintainers reasonable time to investigate and prepare a fix before public disclosure.

## Security design notes

CodeMind includes tool allowlisting, input validation, repository path checks, bounded source retrieval, prompt-injection pattern scanning, and likely-secret redaction. These controls are not a guarantee of complete protection. Users should review LLM provider data handling and avoid sending sensitive source code unless permitted.
