#!/usr/bin/env python3
"""
Simple Telegram Message Sender
Reuses CCNotify configuration for sending messages via Telegram Bot API.
Designed for use in command pipelines.

Usage:
    echo "message" | telegram_sender.py
    echo "message" | telegram_sender.py "Custom Title"
    command | telegram_sender.py "Command Output"
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime


class TelegramSender:
    def __init__(self):
        """Initialize with CCNotify config"""
        self.load_config()
    
    def load_config(self):
        """Load configuration from CCNotify's config.json"""
        # Use same config path as ccnotify
        config_dir = os.path.expanduser("~/.claude/ccnotify")
        config_path = os.path.join(config_dir, "config.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"CCNotify config not found at {config_path}. "
                "Please run ccnotify.py first to create the configuration."
            )
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        
        # Validate telegram configuration
        telegram_config = self.config.get("notifications", {}).get("telegram", {})
        if not telegram_config.get("enabled", False):
            raise ValueError("Telegram notifications are not enabled in CCNotify config")
        
        self.bot_token = telegram_config.get("bot_token", "")
        self.chat_id = telegram_config.get("chat_id", "")
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot_token and chat_id must be configured in CCNotify config")
    
    def send_message(self, title, message):
        """Send message via Telegram Bot API"""
        # Format message - simpler than ccnotify notifications
        if title:
            formatted_message = f"*{title}*\n\n{message}"
        else:
            formatted_message = message
        
        # Send via Telegram Bot API
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': self.chat_id,
            'text': formatted_message,
            'parse_mode': 'Markdown'
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    response_text = response.read().decode('utf-8')
                    raise Exception(f"Telegram API error {response.status}: {response_text}")
                
                return True
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e}")
        except Exception as e:
            raise Exception(f"Failed to send telegram message: {e}")


def main():
    """Main entry point"""
    try:
        # Get optional title from command line argument
        title = sys.argv[1] if len(sys.argv) > 1 else None
        
        # Read message content from stdin
        if sys.stdin.isatty():
            print("Error: No input provided. Use in a pipeline or redirect input.", file=sys.stderr)
            print("Usage: echo 'message' | telegram_sender.py [title]", file=sys.stderr)
            sys.exit(1)
        
        message = sys.stdin.read().strip()
        if not message:
            print("Error: Empty message received from stdin", file=sys.stderr)
            sys.exit(1)
        
        # Initialize sender and send message
        sender = TelegramSender()
        sender.send_message(title, message)
        
        # Success output for pipeline debugging
        if title:
            print(f"Message sent to Telegram: {title}")
        else:
            print("Message sent to Telegram")
    
    except FileNotFoundError as e:
        print(f"Config Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()