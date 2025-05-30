# Discord Music Bot 🎵

A feature-rich Discord music bot that supports YouTube and Spotify playback.

## Features 🚀

- YouTube playback support
- Spotify integration (tracks and playlists)
- Queue management system
- Interactive music controls
- Real-time song information display
- High-quality audio streaming

## Prerequisites 📋

- Python 3.8 or higher
- FFmpeg installed on your system
- Discord Bot Token
- Spotify API credentials

## Installation 🔧

1. Clone this repository:
```bash
git clone https://github.com/Incredible-06/discord-music-bot.git
```

2. Create a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate it on Windows
.venv\Scripts\activate

# Or activate it on Linux/Mac
source .venv/bin/activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start with Batch File 🚀

1. Locate the `start_bot.bat` file in the project directory
2. Edit the file with your own credentials and virtual environment path:
```batch
:: If you used a different name for your virtual environment
:: modify this line accordingly (e.g., "venv" or "env")
set VENV_PATH=.venv\Scripts\activate.bat

set BOT_TOKEN=your_discord_bot_token_here
set SPOTIFY_CLIENT_ID=your_spotify_client_id_here
set SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
```
3. Double-click `start_bot.bat` to run the bot automatically

This method will:
- Activate your virtual environment (using the path specified in VENV_PATH)
- Set up your environment variables
- Start the bot

⚠️ Important: 
- Never share your `start_bot.bat` file or commit it to version control, as it contains your private credentials
- Make sure VENV_PATH matches your virtual environment location if you used a different name than `.venv`

## Manual Environment Setup 🔑

If you prefer to set up manually:

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a Spotify application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
3. Set your environment variables:
```powershell
$env:BOT_TOKEN="your_discord_bot_token"
$env:SPOTIFY_CLIENT_ID="your_spotify_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

## Usage 💻

Available commands:
- `!play [song/URL]` - Play a song from YouTube or Spotify
- `!queue` - Display the current music queue
- Interactive buttons:
  - ⏸️ Pause/Resume
  - ⏭️ Skip
  - ⏹️ Stop

## Bot Permissions 🔐

The bot requires the following Discord permissions:
- View Channels
- Send Messages
- Connect to Voice Channels
- Speak in Voice Channels
- Add Reactions
- Embed Links

## Error Handling 🔧

The bot includes comprehensive error handling for:
- Connection issues
- Invalid URLs
- Missing permissions
- Playback errors

## Contributing 🤝

Feel free to submit issues and enhancement requests!
