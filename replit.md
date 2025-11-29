# Echo Discord Bot

## Overview
Echo is a lightweight Discord proxy bot designed for roleplay (RP) servers. It allows users to register multiple characters with custom triggers and avatars, then send messages as those characters using a simple prefix system.

**Current State:** Fully functional and running on Replit

## Purpose & Features
- **Character Registration:** Users can register multiple roleplay characters with custom names, triggers, and avatars
- **Webhook-Based Proxying:** Messages sent with character triggers are proxied through webhooks to appear as the character
- **Character Management:** Full CRUD operations for managing characters (rename, update avatar, change triggers, delete)
- **Simple Trigger System:** Uses colon-ending prefixes (e.g., `Idh: Hello there`)

## Recent Changes (November 29, 2025)
- Imported from GitHub and configured for Replit environment
- Fixed duplicate bot initialization and function declaration issues
- Installed dependencies: discord.py and python-dotenv
- Changed help command to 'commands' to avoid conflict with discord.py's built-in help
- Configured workflow to run the bot automatically
- Created .gitignore for Python project
- Bot successfully connected and running

## Project Architecture

### File Structure
```
.
├── echo.py              # Main bot file with all commands and logic
├── requirements.txt     # Python dependencies
├── Procfile            # Legacy deployment config (not used on Replit)
├── .replit             # Replit configuration
├── .gitignore          # Git ignore rules
└── replit.md           # This documentation file
```

### Dependencies
- **discord.py** (2.6.4): Discord API wrapper for Python
- **python-dotenv** (1.2.1): Environment variable management
- **Python 3.12**: Runtime environment

### Bot Configuration
- **Command Prefix:** `Echo/`
- **Required Intents:** message_content
- **Authentication:** DISCORD_TOKEN (stored in Replit Secrets)

### Data Structure
Characters are stored in memory using this structure:
```python
characters = {
    user_id: {
        "CharacterName": {
            "trigger": "Prefix:",
            "avatar": "url"
        }
    }
}
```

**Note:** Character data is currently stored in-memory only. All registered characters will be lost when the bot restarts.

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `Echo/register "Name" Trigger:` | Register a new character (optional: attach avatar image) | `Echo/register "Idhren" Idh:` |
| `Echo/rename Old New` | Rename a character | `Echo/rename Idhren Idh` |
| `Echo/avatar Name` | Update character avatar (attach image) | `Echo/avatar Idhren` |
| `Echo/bracket Name NewTrigger:` | Change character trigger | `Echo/bracket Idhren Idhr:` |
| `Echo/list` | List all your registered characters | `Echo/list` |
| `Echo/search keyword` | Search your characters by name or trigger | `Echo/search Idh` |
| `Echo/delete Name` | Delete a character | `Echo/delete Idhren` |
| `Echo/commands` | Show command list | `Echo/commands` |

## How to Use

### Registering a Character
1. Use `Echo/register "CharacterName" Trigger:` in any channel
2. Optionally attach an image for the character's avatar
3. The trigger must end with a colon

### Sending Messages as a Character
Simply type the trigger followed by your message:
```
Idh: Hello, I'm Idhren!
```
The bot will delete your message and resend it through a webhook as your character.

## Environment Variables
- **DISCORD_TOKEN** (Secret): Discord bot token from Developer Portal

## Workflow Configuration
- **Name:** Discord Bot
- **Command:** `python echo.py`
- **Type:** Console (always-on bot)

## Setup Instructions
1. Ensure DISCORD_TOKEN is set in Replit Secrets
2. Dependencies are auto-installed from requirements.txt
3. The workflow starts automatically and keeps the bot running
4. Invite the bot to your Discord server with proper permissions (Manage Webhooks, Send Messages, Read Messages)

## Required Discord Permissions
- Read Messages/View Channels
- Send Messages
- Manage Webhooks (required for proxying)
- Read Message History

## Known Limitations
- Character data is not persistent (stored in-memory only)
- No database integration
- Limited to one bot instance
- Characters are per-user (not server-wide)

## Future Improvement Ideas
- Add persistent storage (database) for character data
- Server-wide character management options
- Character import/export functionality
- More advanced proxy features (embeds, attachments, etc.)
- Multi-server support with per-server configurations
