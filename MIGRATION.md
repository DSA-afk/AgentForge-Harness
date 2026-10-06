# Migration and validation

Prepared on 2026-10-06 from upstream commit `6f70724e6b84ade0f13600d5ab058153a7e34418`.

## Checks performed

- Verified all 73 upstream file blobs against their Git SHA-1 identifiers before modification.
- Kept the upstream MIT LICENSE unchanged.
- Reproduced two recovery defects before fixing them: one failing assertion and one exception, with two control tests passing.
- After the fixes, all four focused recovery regression tests passed on Python 3.12.14 / Windows.
- Parsed 53 implementation and test Python files successfully with `ast.parse`.

Run the focused checks from the repository root without third-party dependencies:

```bash
python -m unittest discover -s tests -p test_transcript_recovery.py -v
```

The full upstream pytest suite has not been run. No live model, MCP server, Web UI or Linux sandbox integration was exercised during this preparation. The incremental log reader removes the temporary full-file string and split-line list; no timing or memory benchmark was performed. The restored message history still resides in memory.

## Commit organization

The migration retains the original repository history. Four `chore: import upstream ...` commits identify imported modules explicitly, followed by two recovery fixes, an incremental log-reading change and documentation updates. No upstream commit is presented as original local implementation, and no commit dates are fabricated.
