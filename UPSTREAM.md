# Upstream provenance

- Project: MWM Harness
- Repository: https://github.com/Matswm86/mwm-harness
- Imported commit: `6f70724e6b84ade0f13600d5ab058153a7e34418`
- Copyright: Copyright (c) 2026 MWM AI
- License: MIT; the original LICENSE is retained without modification.
- Import preparation date: 2026-10-06

All 73 upstream file blobs were verified against their Git SHA-1 identifiers before local edits. The working copy excludes upstream `.git` metadata. This is an import and adaptation of existing open-source code, not a claim of original authorship of the upstream implementation.

Local changes:

1. Replace the README with concise Chinese setup and feature documentation.
2. Harden transcript loading against invalid record and message object shapes.
3. Describe interrupted tool outcomes as unknown instead of assuming no execution.
4. Iterate transcript lines instead of reading and splitting the entire file.
5. Add focused regression tests for recovery behavior.

Other upstream files, including the implementation namespace and LICENSE, are unchanged. Upstream compatibility reports and historical documentation describe upstream work; they are not local validation results.
