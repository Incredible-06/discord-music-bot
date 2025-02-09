import discord
from discord.ext import commands
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Setting up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            await self.load_extension("music")
            print("Music extension loaded")
        except Exception as e:
            print(f"Error loading music extension: {e}")

bot = DiscordBot()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Ready to operate.")

if __name__ == "__main__":
    async def main():
        async with bot:
            await bot.start(BOT_TOKEN)

    import asyncio
    
    asyncio.run(main())