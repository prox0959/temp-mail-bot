# README.md

```markdown
# 📬 TempMail Discord Bot

<div align="center">

![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![aiohttp](https://img.shields.io/badge/aiohttp-2C5BB4?style=for-the-badge&logo=aiohttp&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A fully async Discord bot that provides private temporary email inboxes using the [Mail.tm](https://mail.tm) API.**

*Made by **prox0959***

</div>

---

## 📖 Table of Contents

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Bot Setup (Discord Developer Portal)](#-bot-setup-discord-developer-portal)
- [Running the Bot](#-running-the-bot)
- [Commands](#-commands)
- [Button Actions](#-button-actions)
- [Permissions](#-permissions)
- [Project Structure](#-project-structure)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Made By](#-made-by)

---

## ✨ Features

- 📧 **Instant Temp Email Generation** — Creates a real, working temporary email address via [Mail.tm](https://mail.tm)
- 🔒 **Private Channels** — Each user gets their own private Discord text channel for their inbox
- 🔄 **Auto Email Polling** — Checks for new emails every 30 seconds automatically
- 📨 **Full Email Display** — Shows sender, subject, and full message body in rich embeds
- 🗑️ **Delete Messages** — Delete individual or all messages from the inbox
- 🧹 **Account Cleanup** — Deletes the Mail.tm account and Discord channel when done
- 👑 **Admin Controls** — Admin can create multiple inboxes and manage all channels
- 🌐 **Bilingual UI** — Interface supports both English and Turkish
- 📌 **Pinned Info Message** — Email address info is pinned in each private channel
- ♻️ **Persistent Views** — Buttons remain functional even after bot restarts

---

## 🔧 How It Works

```
User clicks "Create Temp Mail" button
        │
        ▼
Bot calls Mail.tm API to get available domain
        │
        ▼
Bot creates a random email account on Mail.tm
        │
        ▼
Bot creates a private Discord channel for the user
        │
        ▼
Bot sends & pins the email address in the channel
        │
        ▼
Every 30 seconds: Bot polls Mail.tm for new emails
        │
        ▼
New emails are sent as embeds and mentioning the user
        │
        ▼
User can delete messages or close the inbox via button/commands
```

---

## 📋 Requirements

- Python **3.10** or higher
- A Discord Bot Token
- The following Python libraries:
  - `discord.py` >= 2.3.0
  - `aiohttp` >= 3.8.0

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/prox0959/tempmail-discord-bot.git
cd tempmail-discord-bot
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**
```
discord.py>=2.3.0
aiohttp>=3.8.0
```

Or install manually:
```bash
pip install discord.py aiohttp
```

---

## ⚙️ Configuration

Open `main.py` and fill in the following constants near the top of the file:

```python
ADMIN_ID = 123456789012345678        # Your Discord User ID (integer)
PANEL_CHANNEL_ID = 123456789012345678 # Channel ID where the panel embed appears
CATEGORY_ID = 123456789012345678      # Category ID where temp mail channels are created
TOKEN = "your_bot_token_here"         # Your Discord Bot Token
```

### How to get these IDs?

> Enable **Developer Mode** in Discord:
> `Settings → Advanced → Developer Mode → ON`

| Value | How to Get |
|-------|-----------|
| `ADMIN_ID` | Right-click your profile → Copy User ID |
| `PANEL_CHANNEL_ID` | Right-click the panel channel → Copy Channel ID |
| `CATEGORY_ID` | Right-click the category → Copy Channel ID |
| `TOKEN` | Discord Developer Portal → Your App → Bot → Token |

---

## 🤖 Bot Setup (Discord Developer Portal)

1. Go to [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Go to the **Bot** tab and click **"Add Bot"**
4. Copy the **Token** and paste it in `main.py`
5. Under **Privileged Gateway Intents**, enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent *(optional but recommended)*
6. Go to **OAuth2 → URL Generator**
7. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
8. Select bot permissions:
   - ✅ Manage Channels
   - ✅ Send Messages
   - ✅ Read Messages / View Channels
   - ✅ Embed Links
   - ✅ Pin Messages
   - ✅ Read Message History
   - ✅ Manage Messages
9. Copy the generated URL and invite the bot to your server

---

## 🚀 Running the Bot

```bash
python main.py
```

Or using an environment variable for the token (more secure):

```bash
# Linux / macOS
export DISCORD_TOKEN="your_bot_token_here"
python main.py

# Windows CMD
set DISCORD_TOKEN=your_bot_token_here
python main.py

# Windows PowerShell
$env:DISCORD_TOKEN="your_bot_token_here"
python main.py
```

When the bot starts successfully, you will see:
```
Logged in as YourBotName#1234
```
And the panel embed will automatically appear in your configured panel channel.

---

## 💬 Commands

All slash commands are synced automatically on bot startup.

| Command | Description | Where to Use |
|---------|-------------|--------------|
| `/inbox` | Lists up to 10 emails currently in your inbox | Inside your temp mail channel |
| `/delete <message_id>` | Deletes a specific email by its ID | Inside your temp mail channel |
| `/delete all` | Deletes **all** emails in your inbox | Inside your temp mail channel |

> ⚠️ Commands only work inside your own private temp mail channel.

---

## 🖱️ Button Actions

### Panel Channel Button

| Button | Action |
|--------|--------|
| ✅ **Create Temp Mail / Oluştur** | Generates a new temporary email address and creates a private channel |

### Inside Temp Mail Channel

| Button | Action |
|--------|--------|
| 🗑️ **Delete Temp Mail / Sil** | Deletes the Mail.tm account and removes the Discord channel |

---

## 🔐 Permissions

### User Permissions
- Can create **one** temp mail inbox at a time
- Can only access their own private channel
- Can delete their own messages and close their inbox

### Admin Permissions (ADMIN_ID)
- Can create **multiple** temp mail inboxes
- Has access to **all** temp mail channels
- Can delete **any** user's temp mail account

---

## 📁 Project Structure

```
tempmail-discord-bot/
│
├── main.py                  # Main bot file (all logic)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Class Overview

```
TempMailBot          → Main bot class, manages accounts and polling
├── MailTmClient     → Async HTTP client for Mail.tm API
├── PanelView        → Persistent UI view for the panel channel
└── DeleteAccountView → Persistent UI view inside temp mail channels
```

### Key Data Structures

```python
# Stores all accounts per user
user_accounts: Dict[int, list]
# key: Discord user ID
# value: list of account dicts

# Stores account data per channel
channel_accounts: Dict[int, Dict]
# key: Discord channel ID
# value: account dict {
#     "owner_id": int,
#     "address": str,
#     "password": str,
#     "token": str,
#     "account_id": str,
#     "channel_id": int,
#     "seen_ids": set
# }
```

---

## ❓ FAQ

**Q: Is this free to use?**
> A: Yes. The bot uses [Mail.tm](https://mail.tm) which is a free service. No API key needed.

**Q: How long do temp emails last?**
> A: Mail.tm accounts are temporary. They exist until you delete them via the bot. The bot deletes the account when you press the delete button or use the delete view.

**Q: What happens to emails if the bot restarts?**
> A: The in-memory data (`user_accounts`, `channel_accounts`) is lost on restart. Existing channels will remain in Discord but the bot won't monitor them anymore. You would need to implement a database for persistence.

**Q: Can multiple users create inboxes at the same time?**
> A: Yes. Each user gets their own private channel and Mail.tm account. They run fully independently.

**Q: Can I customize the polling interval?**
> A: Yes. Find this line in `main.py` and change the seconds value:
> ```python
> @tasks.loop(seconds=30)
> ```

**Q: Is the email address visible to other users?**
> A: No. The email is sent only to the user's private channel which is invisible to others (except admins).

---

## 🛠️ Troubleshooting

### Bot doesn't come online
- Double-check your `TOKEN` value
- Make sure you haven't reset the token in the Developer Portal

### Panel embed doesn't appear
- Verify `PANEL_CHANNEL_ID` is correct
- Ensure the bot has **Send Messages** and **Embed Links** permissions in that channel

### Temp mail channel is not created
- Verify `CATEGORY_ID` is correct
- Ensure the bot has **Manage Channels** permission

### Commands not appearing in Discord
- Wait up to 1 hour for global slash command sync
- Try kicking and re-inviting the bot
- Make sure `applications.commands` scope was used during invite

### "No domains available from mail.tm"
- Mail.tm may be temporarily down
- Check [https://mail.tm](https://mail.tm) directly
- Try again after a few minutes

### Emails not appearing in the channel
- The bot polls every 30 seconds, wait a bit
- Use `/inbox` to manually check
- Ensure the bot has **Send Messages** permission in the temp channel

---

## 👤 Made By

<div align="center">

```
 ██████╗ ██████╗  ██████╗ ██╗  ██╗ ██████╗  █████╗ ███████╗ █████╗ 
 ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝██╔═████╗██╔══██╗██╔════╝██╔══██╗
 ██████╔╝██████╔╝██║   ██║ ╚███╔╝ ██║██╔██║╚██████║███████╗╚██████║
 ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗ ████╔╝██║ ╚═══██║╚════██║ ╚═══██║
 ██║     ██║  ██║╚██████╔╝██╔╝ ██╗╚██████╔╝ █████╔╝███████║ █████╔╝
 ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚════╝ 
```

**Made with ❤️ by [prox0959](https://github.com/prox0959)**

*Feel free to contribute, open issues, or suggest features!*

</div>

---

<div align="center">
<sub>Built with discord.py • Powered by Mail.tm</sub>
</div>
```
