@echo off
:: Edit the VENV_PATH if the name of your virtual environment is different
set VENV_PATH=.venv\Scripts\activate.bat

set BOT_TOKEN=your_discord_bot_token_here
set SPOTIFY_CLIENT_ID=your_spotify_client_id_here
set SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

:: Activate virtual environment and run bot
call %VENV_PATH%
python main.py

pause