# Level 2 Squad Fragmented Changelogs

This directory contains the isolated developmental logs ("Bitácoras") for all individual Level 2 Swarm execution units (Cursor, Copilot, etc.). 

## Protocol (Never Edit the Root CHANGELOG.md)
To eliminate "Merge Hell" when working in parallel:
1. When you start an IDE session, adopt your callsign (e.g. `cursor_alpha`, `copilot_omega`).
2. Do **NOT** write to the project's root `CHANGELOG.md`.
3. Create or update your specific markdown file here (e.g., `cursor_alpha.md`).
4. Log your progress, implementations, and gap closures here.

Level 1 Antigravity will periodically squash and compile these fragment files into the root `CHANGELOG.md` during the integration phase.
