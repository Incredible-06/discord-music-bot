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
cd bot_music
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the project root with your credentials:
```env
BOT_TOKEN=your_discord_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

## Usage 💻

1. Start the bot:
```bash
python main.py
```

2. Available commands:
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

## Environment Setup 🔑

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a Spotify application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
3. Configure your bot token and Spotify credentials in the `.env` file

## Error Handling 🔧

The bot includes comprehensive error handling for:
- Connection issues
- Invalid URLs
- Missing permissions
- Playback errors

## Contributing 🤝

Feel free to submit issues and enhancement requests!
