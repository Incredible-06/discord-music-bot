import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
from discord.ui import Button, View
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import os

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify Configuration
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = SPOTIFY_CLIENT_ID,
    client_secret = SPOTIFY_CLIENT_SECRET
))

# yt-dlp Configuration
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
}

# FFmpeg Configuration for audio streaming
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class MusicButtons(View):
    def __init__(self, music_player):
        super().__init__(timeout=None)
        self.music_player = music_player

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("I'm not playing any music.", ephemeral=True)
            return

        if vc.is_paused():
            vc.resume()
            button.label = "⏸️ Pause"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ Music resumed", ephemeral=True)
        else:
            vc.pause()
            button.label = "▶️ Resume"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ Music paused", ephemeral=True)

    @discord.ui.button(label="⏭️ Next", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("I'm not playing any music.", ephemeral=True)
            return

        if not vc.is_playing() and not vc.is_paused():
            await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)
            return

        vc.stop()
        await interaction.response.send_message("⏭️ Skipping to next song...", ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)
            return

        await self.music_player.stop_and_disconnect(interaction.guild.id)
        await interaction.response.send_message("⏹️ Playback stopped", ephemeral=True)

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.now_playing = {}
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.loading_playlists = set()

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def stop_and_disconnect(self, guild_id):
        if guild_id in self.queues:
            self.queues[guild_id].clear()
        
        vc = self.bot.get_guild(guild_id).voice_client
        if vc:
            await vc.disconnect()

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue:
            await ctx.send("🎵 No more songs in queue")
            await self.stop_and_disconnect(guild_id)
            return

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return

        try:
            song = queue.popleft()
            next_song = queue[0] if queue else None
            source = await discord.FFmpegOpusAudio.from_probe(song['url'], **FFMPEG_OPTIONS)
            
            def after_playing(error):
                if error:
                    print(f"Error playing audio: {error}")
                asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

            ctx.voice_client.play(source, after=after_playing)
            
            # Create embed with clickable title
            embed = discord.Embed(color=discord.Color.blurple())
            
            # Now Playing title with clickable link
            if 'webpage_url' in song:
                song_title = f"[{song['title']}]({song['webpage_url']})"
            else:
                song_title = song['title']
                
            embed.add_field(
                name="Now Playing 🎵",
                value=song_title,
                inline=False
            )
            
            # Song duration formatting
            duration_text = ""
            if 'duration' in song:
                minutes = song['duration'] // 60
                seconds = song['duration'] % 60
                duration_text = f"Length: {minutes}:{seconds:02d}\n"
            
            # Requester
            requester_text = f"Requested by: {ctx.author.name}\n"
            
            # Next song
            next_song_text = ""
            if next_song:
                # Also make the next title clickable if URL is available
                if 'webpage_url' in next_song:
                    next_song_text = f"Up Next: [{next_song['title']}]({next_song['webpage_url']})"
                else:
                    next_song_text = f"Up Next: {next_song['title']}"
            
            # Combine all info in a single field
            embed.add_field(
                name="",
                value=f"{duration_text}{requester_text}{next_song_text}".strip(),
                inline=False
            )
            
            # Set thumbnail if available
            if song.get('thumbnail'):
                embed.set_thumbnail(url=song['thumbnail'])

            if guild_id in self.now_playing:
                try:
                    await self.now_playing[guild_id].delete()
                except:
                    pass

            self.now_playing[guild_id] = await ctx.send(embed=embed, view=MusicButtons(self))

        except Exception as e:
            print(f"Error in play_next: {e}")
            await self.play_next(ctx)

    async def process_playlist_tracks(self, ctx, tracks, start_index=3):
        """Process the rest of the playlist songs in the background"""
        guild_id = ctx.guild.id
        if guild_id not in self.loading_playlists:
            return

        queue = self.get_queue(guild_id)
        for item in tracks['items'][start_index:]:
            if guild_id not in self.loading_playlists:
                break

            if not item['track']:
                continue
                
            track = item['track']
            search_query = f"{track['name']} {track['artists'][0]['name']}"
            
            try:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.ydl.extract_info(f"ytsearch:{search_query}", download=False)
                )
                
                if not info.get('entries'):
                    continue
                    
                video = info['entries'][0]
                song_info = {
                    'url': video['url'],
                    'title': video['title'],
                    'thumbnail': video.get('thumbnail'),
                    'duration': video.get('duration', 0)  # Add duration
                }
                
                queue.append(song_info)

            except Exception as e:
                print(f"Error adding track {search_query}: {e}")
                continue

        if guild_id in self.loading_playlists:
            self.loading_playlists.remove(guild_id)

    async def add_spotify_playlist(self, ctx, playlist_url):
        try:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            playlist = sp.playlist(playlist_id)
            tracks = sp.playlist_tracks(playlist_id)
            
            # Create confirmation embed
            formatted_date = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            embed = discord.Embed(
                title="📌 **PLAYLIST ADDED** 🎶",
                description=(
                    f"The playlist `{playlist['name']}` contains `{len(tracks['items'])}` songs 🎶\n\n"
                    f"Total duration: `{sum(track['track']['duration_ms'] for track in tracks['items']) // 60000} minutes`\n"
                    f"Added by: `{ctx.author.name}` • {formatted_date} UTC"
                ),
                color=discord.Color.green()
            )
            
            if playlist['images']:
                embed.set_thumbnail(url=playlist['images'][0]['url'])
            
            await ctx.send(embed=embed)

            # Load the first 3 songs immediately
            loading_msg = await ctx.send("⏳ Loading first songs...")
            queue = self.get_queue(ctx.guild.id)
            
            initial_tracks = tracks['items'][:3]
            for item in initial_tracks:
                if not item['track']:
                    continue
                    
                track = item['track']
                search_query = f"{track['name']} {track['artists'][0]['name']}"
                
                try:
                    info = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.ydl.extract_info(f"ytsearch:{search_query}", download=False)
                    )
                    
                    if not info.get('entries'):
                        continue
                        
                    video = info['entries'][0]
                    song_info = {
                        'url': video['url'],
                        'webpage_url': video['webpage_url'],  # YouTube page URL
                        'title': video['title'],
                        'thumbnail': video.get('thumbnail'),
                        'duration': video.get('duration', 0)
                    }
                    
                    queue.append(song_info)

                except Exception as e:
                    print(f"Error adding initial track {search_query}: {e}")
                    continue

            await loading_msg.delete()

            # Start playback if nothing is playing
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

            # Load the rest of the playlist in the background
            guild_id = ctx.guild.id
            self.loading_playlists.add(guild_id)
            self.bot.loop.create_task(self.process_playlist_tracks(ctx, tracks))

        except Exception as e:
            await ctx.send(f"❌ Error loading playlist: {str(e)}")

    async def add_spotify_track(self, ctx, track_url):
        try:
            track_id = track_url.split('/')[-1].split('?')[0]
            track = sp.track(track_id)
            
            search_query = f"{track['name']} {track['artists'][0]['name']}"
            info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ydl.extract_info(f"ytsearch:{search_query}", download=False)
            )
            
            if not info.get('entries'):
                await ctx.send("❌ Song not found")
                return
                
            video = info['entries'][0]
            song_info = {
                'url': video['url'],
                'webpage_url': video['webpage_url'],  # YouTube URL
                'title': f"{track['name']} - {track['artists'][0]['name']}",
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'duration': track['duration_ms'] // 1000
            }
            
            queue = self.get_queue(ctx.guild.id)
            queue.append(song_info)
            
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)
            else:
                await ctx.send(f"🎵 Added to queue: **{song_info['title']}**")

        except Exception as e:
            await ctx.send(f"❌ Error loading song: {str(e)}")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_player = MusicPlayer(bot)

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """Play music from YouTube or Spotify"""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel")
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        try:
            if 'spotify.com' in query:
                if 'playlist' in query:
                    await self.music_player.add_spotify_playlist(ctx, query)
                else:
                    await self.music_player.add_spotify_track(ctx, query)
                return

            # YouTube or direct search
            # Temporarily modify yt_dlp configuration to get all info
            ydl_opts_with_info = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'force_generic_extractor': False  # Ensure we get all metadata
            }

            # If it's a direct YouTube URL, extract the information directly
            if 'youtube.com' in query or 'youtu.be' in query:
                info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.music_player.ydl.extract_info(query, download=False)
                )
                video = info  # The info is already of the video directly
            else:
                # If it's a search, keep the current behavior
                info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.music_player.ydl.extract_info(f"ytsearch:{query}", download=False)
                )
                if not info.get('entries'):
                    await ctx.send("❌ Song not found")
                    return
                video = info['entries'][0]

            # Create song_info consistently
            song_info = {
                'url': video.get('url', video.get('formats', [{}])[0].get('url')),
                'webpage_url': video.get('webpage_url', ''),
                'title': video.get('title', 'Unknown Title'),
                'thumbnail': video.get('thumbnail', None),
                'duration': video.get('duration', 0)
            }
            
            queue = self.music_player.get_queue(ctx.guild.id)
            queue.append(song_info)
            
            if not ctx.voice_client.is_playing():
                await self.music_player.play_next(ctx)
            else:
                await ctx.send(f"🎵 Added to queue: **{song_info['title']}**")

        except Exception as e:
            print(f"Error in play command: {e}")  # For debugging
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """Display the current music queue"""
        queue = self.music_player.get_queue(ctx.guild.id)
        
        if not queue:
            await ctx.send("Queue is empty")
            return
            
        embed = discord.Embed(
            title="📜 Music Queue",
            color=discord.Color.blue()
        )
        
        for i, song in enumerate(queue, 1):
            if i <= 10:
                embed.add_field(
                    name=f"{i}. {song['title']}",
                    value="\u200b",
                    inline=False
                )
                
        if len(queue) > 10:
            embed.set_footer(text=f"And {len(queue) - 10} more songs...")
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))