![Notification Screenshot](alert.jpg)

# CCNotify

CCNotify provides notifications for Claude Code, alerting you when Claude needs your input or completes tasks.

## Important Notes
Starting from claude-code v1.0.95 (2025-08-31), any invalid settings in `~/.claude/settings.json` will disable hooks. See [Why not working](#why-not-working) for solutions.

## Features

- 🔔 **Get notified** when Claude requires your input or completes a task
- 🔗 **Click to jump back** when notifications are clicked, automatically taking you to the corresponding project in VS Code (macOS only)
- ⏱️ **Task Duration**: Displays started time, and how long the task took to complete
- 🤖 **Telegram Support**: Cross-platform notifications via Telegram bot (works on any platform, including SSH environments)
- 🖥️ **Dual Mode**: Use terminal notifications, Telegram, or both simultaneously

**Platform Support**: 
- **macOS**: Terminal notifications + Telegram
- **All platforms**: Telegram notifications (Linux, Windows, SSH environments)


## Installation Guide

### 1. Install CCNotify
```bash
# Create the directory if it doesn't exist
mkdir -p ~/.claude/ccnotify

# soft link ccnotify.py to the directory
ln -f ccnotify.py ~/.claude/ccnotify/

chmod a+x ~/.claude/ccnotify/ccnotify.py

# run this script, should print: ok
~/.claude/ccnotify/ccnotify.py

ok

```
### 2. Choose Your Notification Method

#### Option A: Terminal Notifications (macOS only)
Install `terminal-notifier` for native macOS notifications:

```bash
brew install terminal-notifier
```

For alternative installation methods, visit: https://github.com/julienXX/terminal-notifier

#### Option B: Telegram Notifications (All platforms)
Set up a Telegram bot for cross-platform notifications. See [Telegram Bot Setup](#telegram-bot-setup) section below.

### 3. Configure Claude Hooks
Add the following hooks to your Claude configuration to enable ccnotify:

 ~/.claude/settings.json 
 
```json

  "hooks": {
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/ccnotify/ccnotify.py UserPromptSubmit"
        }
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/ccnotify/ccnotify.py Stop"
        }
      ]
    }
  ],
  "Notification": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/ccnotify/ccnotify.py Notification"
        }
      ]
    }
  ]
}

```

## Try It Out

To verify the notification system works, start a new Claude Code session and run:
```
after 1 second, echo 'hello'
```
You should see a notification appear (terminal notification on macOS, or Telegram message if configured).

## Configuration

CCNotify creates a `config.json` file in `~/.claude/ccnotify/` on first run. You can customize notification methods:

```json
{
  "notifications": {
    "terminal": {
      "enabled": true
    },
    "telegram": {
      "enabled": false,
      "bot_token": "your_bot_token_here",
      "chat_id": "your_chat_id_here"
    }
  }
}
```

**Configuration Options:**
- Set `terminal.enabled: false` to disable macOS notifications
- Set `telegram.enabled: true` and add your bot credentials to enable Telegram
- You can enable both methods simultaneously

## Telegram Bot Setup

### Step 1: Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Claude Notifier")
4. Choose a username (must end with `bot`, e.g., "my_claude_notifier_bot")
5. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Send any message to your bot (e.g., `/start`)
2. Open this URL in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` and copy the ID number

### Step 3: Configure CCNotify
Edit `~/.claude/ccnotify/config.json`:
```json
{
  "notifications": {
    "terminal": {
      "enabled": true
    },
    "telegram": {
      "enabled": true,
      "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
      "chat_id": "123456789"
    }
  }
}
```

## Why not working
1. Ensure hooks configuration is active. Here's an example where other configurations prevent hooks from working:

`claude -p --model haiku -d hooks --verbose "hi"`

Expected output:

```
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: ~/.claude/ccnotify/ccnotify.py UserPromptSubmit with timeout 60000ms
[DEBUG] Hook command completed with status 0: ~/.claude/ccnotify/ccnotify.py UserPromptSubmit
```

Actual output:

```
[DEBUG] Invalid settings in userSettings source - key: permissions.allow.0, error:.....
[DEBUG] Found 0 hook commands to execute
```
Reason: In September 2025, claude-code strengthened validation rules for settings.json. Any invalid configuration will disable hooks.
You need to modify the relevant configurations in `~/.claude/settings.json` until the `Invalid settings` error stops appearing.



## How It Works

ccnotify tracks Claude sessions and provides notifications at key moments:

- **When you submit a prompt**: Records the start time and project context
- **When Claude completes**: Calculates duration and sends a completion notification
- **When Claude waits for input**: Immediately alerts you that input is needed

All activity is logged to `~/.claude/ccnotify/ccnotify.log` and session data is stored in `~/.claude/ccnotify/ccnotify.db` locally. No data is uploaded or shared externally.

## Telegram Sender Tool

CCNotify includes a standalone `telegram_sender.py` script for sending messages directly to Telegram from command pipelines. This tool reuses the CCNotify Telegram configuration.

### Features
- 📤 **Pipeline friendly**: Reads from stdin for easy integration
- 🔧 **Uses existing config**: Leverages CCNotify's Telegram bot setup
- 📝 **Optional titles**: Add custom titles to messages
- 🚀 **Lightweight**: Simple script with no additional dependencies

### Usage

```bash
# Basic usage
echo "Task completed!" | ./telegram_sender.py

# With custom title
echo "Training accuracy: 95.2%" | ./telegram_sender.py "ML Model Results"

# In command pipelines
model_train | ./telegram_sender.py "Training Complete"

# With Claude Code integration
your_command | claude "summarize this output" | ./telegram_sender.py "Command Summary"
```

### Creating a Convenient Alias

For frequent use with Claude Code, create a `telecc` alias that combines Claude summarization with Telegram sending:

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias telecc='claude "Please provide a concise summary of this output, highlighting key results, errors, or important information:" | ./telegram_sender.py'

# Usage examples:
model_training_script | telecc "Training Results"
long_running_process | telecc "Process Complete"
pytest --verbose | telecc "Test Results"
```

### Installation

1. Ensure CCNotify is configured with Telegram enabled
2. Copy or link `telegram_sender.py` to your desired location:
   ```bash
   # Copy to local directory
   cp telegram_sender.py ~/bin/
   
   # Or create symlink in your PATH
   ln -s $(pwd)/telegram_sender.py ~/bin/telegram_sender
   ```
3. Make sure the script is executable: `chmod +x telegram_sender.py`

### Requirements

- CCNotify must be installed and configured with Telegram enabled
- Valid `config.json` file at `~/.claude/ccnotify/config.json`
- Network access to Telegram Bot API

## Uninstall

Edit `~/.claude/settings.json` and remove all hook commands related to `ccnotify`.

Remove all files with a single command:
```bash
rm -rf ~/.claude/ccnotify
```

