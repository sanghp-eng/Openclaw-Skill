# Openclaw-Skill

This repository contains a collection of skills for the OpenClaw AI agent. Skills are modular extensions that add new capabilities to the agent, such as:

- **switch-config**: Configure network switches (Cisco IOS, Juniper EX/JunOS, ArubaOS-CX, etc.)
- **telegram-direct-send**: Send direct Telegram messages bypassing Gateway session restrictions
- **healthcheck**: Audit and harden hosts for security and performance
- **weather**: Get current weather and forecasts
- **gog**: Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs
- **brave-search**: Search the web using Brave Search API
- **summarize**: Summarize conversations, URLs, videos, podcasts, articles, transcripts, PDFs, and local files
- **clawhub**: Search, install, update, sync, or publish agent skills with the ClawHub CLI and registry
- **openclaw-agent-trainer**: Guide for setting up a new OpenClaw instance on a remote server
- **skill-creator**: Create, edit, improve, tidy, review, audit, or restructure AgentSkills and SKILL.md files
- **taskflow**: Coordinate multi-step detached tasks as one durable TaskFlow job
- **telegram-direct-send**: Send direct Telegram messages bypassing Gateway session restrictions
- **node-connect**: Diagnose OpenClaw Android, iOS, or macOS node pairing, QR/setup code, route, auth, and connection failures
- **it-ops-health-auditor**: Comprehensive system health auditing for IT operations
- **networking**: Network diagnostics and troubleshooting for Linux environments
- **switch-config**: Configure network switches (Cisco IOS, Juniper EX/JunOS, ArubaOS-CX, etc.)
- **cliaudio**: Placeholder
- **and more...**

## Usage

Skills are automatically loaded by OpenClaw when placed in `~/.openclaw/workspace/skills/`.

To manually sync a skill to GitHub and remote nodes:

1. Modify the skill locally in `~/.openclaw/workspace/skills/<skill-name>/SKILL.md`
2. Run the sync workflow (or use the provided backup process in MEMORY.md)
3. Push changes to this repository
4. Pull and restart Gateway on remote nodes (e.g., node .115)

See the [Standard Operating Procedure (SOP)](MEMORY.md) in the OpenClaw workspace for detailed steps.

## Contributing

Feel free to submit issues or pull requests to improve existing skills or add new ones.

## License

MIT
