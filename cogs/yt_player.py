import asyncio
import discord
from discord.ext import commands
import yt_dlp
from youtubesearchpython import VideosSearch
from utils.embedded_list import PaginationView
import random


class Youtube_Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playlist = []
        self.current_song = None
        self.current_voice_client = None
        self.current_ctx = None
        # YouTube downloader settings
        yt_dlp_format_options = {
            'format': 'bestaudio/best', 'noplaylist': True,
            'default_search': 'ytsearch', 'quiet': True
        }
        self.ytdlp = yt_dlp.YoutubeDL(yt_dlp_format_options)
    
    # Helper function to reset the player
    def reset(self) -> None:
        '''
        Reset the player
        '''
        self.playlist = []
        self.current_song = None
        self.current_voice_client = None
        self.current_ctx = None

    # Helper function to search for a video on YouTube
    def search_youtube(self, query: str) -> tuple:
        '''
        Search for a video on YouTube and return the title and URL of the 
        first result

        Parameters:
        query (str): The search query

        Returns:
        title (str): The title of the video
        url (str): The URL of the video
        '''
        video_search = VideosSearch(query, limit=10)
        for result in video_search.result()['result']:
            if not result.get('isLive', False):
                return result['title'], result['link']
        return None, None

    # Helper function to play sound from a URL
    async def play_sound(self, voice_client: discord.VoiceClient, url: str) -> None:
        '''
        Play audio from a URL in the voice channel

        Parameters:
        ctx (commands.Context): The context of the command
        voice_client (discord.VoiceClient): The voice client of the bot
        url (str): The URL of the audio stream
        '''
        # FFmpeg options to stream audio from the URL
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'  # -vn tells ffmpeg that this is an audio-only stream,
        }

        # Stream audio using discord's built-in support for audio URLs
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                url, executable="utils/ffmpeg/bin/ffmpeg.exe", **ffmpeg_options)
        )
        voice_client.play(source, after=self.after_playing)

    # Helper function to send not in voice channel message
    async def send_not_in_voice_channel_message(self, ctx: commands.Context) -> None:
        '''
        Send a message to the channel that the bot is not in a voice channel

        Parameters:
        ctx (commands.Context): The context of the command
        '''
        emb = discord.Embed(title="Not in a voice channel", color=0xff0000)
        emb.description = "Use the `!play song_name` command to play music!"
        await ctx.send(embed=emb)

    # Helper function to send play message
    async def send_play_message(self, ctx: commands.Context) -> None:
        '''
        Send a message to the channel that the bot is playing a song

        Parameters:
        ctx (commands.Context): The context of the command
        '''
        title, yt_url, _, requester = self.current_song

        emb = discord.Embed(title="Playing", color=0x00ff00)
        emb.add_field(name="** **", value=f"[{title}]({yt_url})", inline=False)
        emb.add_field(name="Requested by", value=requester, inline=False)

        await ctx.send(embed=emb)

    # Callback function that is called after the audio is done playing
    def after_playing(self, error: Exception) -> None:
        '''
        Callback function that is called after the audio is done playing

        Parameters:
        error (Exception): The error that occurred while playing the audio
        '''
        if error:
            print(f"An error occurred: {error}")

        # Continue playing the playlist if there are more songs
        if len(self.playlist) > 0:
            self.current_song = self.playlist[0]
            asyncio.run_coroutine_threadsafe(
                self.play_sound(self.current_voice_client,
                                self.current_song[2]),
                self.bot.loop
            )
            asyncio.run_coroutine_threadsafe(
                self.send_play_message(self.current_ctx),
                self.bot.loop
            )
            self.playlist.pop(0)
        else:
            self.current_song = None
            asyncio.run_coroutine_threadsafe(
                self.auto_disconnect(),
                self.bot.loop
            )

    # Helper function to auto-disconnect after 3 seconds if no music is playing
    async def auto_disconnect(self) -> None:
        '''
        Disconnect the bot from the voice channel if no music is playing
        after 5 minutes
        '''
        await asyncio.sleep(300)
        if (not self.current_voice_client.is_playing() 
            and not self.current_song 
            and self.current_voice_client):
            await self.current_voice_client.disconnect()
            emb = discord.Embed(title=f"Disconnected form {self.current_voice_client.channel.name}", color=0xff0000)
            emb.description = f"Call me back with the `!play song_name` command!"
            await self.current_ctx.send(embed=emb)
            self.reset()

    # Command to play music from YouTube
    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        # User must be in a voice channel to use this command
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention}, you need to be in a voice channel to use this command!")
            return
        # Join the voice channel if the bot is not already connected
        if not ctx.guild.voice_client:
            voice_channel = ctx.author.voice.channel
            self.current_voice_client = await voice_channel.connect()
            self.current_ctx = ctx

        # Extract audio stream URL without downloading
        wait_message = await ctx.send("Please wait while I fetch the audio...")

        # Check if the query is a YouTube URL
        if "https://www.youtube.com/watch?v=" in query:
            try:
                info = self.ytdlp.extract_info(query, download=False)
                audio_url = info['url']
                title = info['title']
                yt_url = query

            # Video not available on YouTube
            except Exception as e:
                await wait_message.delete()
                if e == yt_dlp.utils.DownloadError:
                    await ctx.send(f"Video not available on YouTube!\n{ctx.author.mention}, please try another query.")
                else:
                    await ctx.send(f"The URL maybe invalid or truncated!\n{ctx.author.mention}, please try another query.")
                return
            
        else:
            title, yt_url = self.search_youtube(query)
            await wait_message.delete()
            if not title or not yt_url:
                await ctx.send(f"No results found!\n{ctx.author.mention}, please try another query.")
                return
            info = self.ytdlp.extract_info(yt_url, download=False)
            audio_url = info['url']

        # Add the song to the playlist
        self.playlist.append((title, yt_url, audio_url, ctx.author.mention))

        # Play the song if nothing is playing
        if not self.current_voice_client.is_playing():
            self.current_song = self.playlist.pop(0)
            await self.play_sound(self.current_voice_client, self.current_song[2])
            await self.send_play_message(ctx)

        # Add the song to the playlist if something is playing
        else:
            emb = discord.Embed(title="Added to Playlist", color=0x00ff00)
            emb.add_field(
                name="** **", value=f"[{title}]({yt_url})", inline=False)
            emb.add_field(name="Requested by",
                          value=ctx.author.mention, inline=False)
            await ctx.send(embed=emb)

    # Command to show the current playlist
    @commands.command()
    async def playlist(self, ctx: commands.Context) -> None:
        if not self.playlist:
            emb = discord.Embed(title="Nothing else is in the playlist",
                                color=0x00ff00)
            emb.description = "Use the `!play song_name` command to add more songs!"
            await ctx.send(embed=emb)
            return

        requesters = [song[3] for song in self.playlist]
        song_names = [f"[{song[0]}]({song[1]})" for song in self.playlist]
        song_with_requester = [f"{i}. {requester} - {song}"
                               for i, (song, requester) in
                               enumerate(zip(song_names, requesters), start=1)]

        title, yt_url, _, requester = self.current_song
        description = f"**Currently playing:**\n[{title}]({yt_url})\nRequested by {requester}"

        view = PaginationView(song_with_requester, item_id=None, title="**Playlist**",
                              list_description=description, items_per_page=5)
        emb = view.create_embed()
        await ctx.send(embed=emb, view=view)

    # Command to clear the playlist
    @commands.command()
    async def clear(self, ctx: commands.Context) -> None:
        self.playlist = []
        emb = discord.Embed(title="Playlist cleared", color=0x00ff00)
        emb.description = "Add new songs with the `!play song_name` command!"
        await ctx.send(embed=emb)

    # Command to shuffle the playlist
    @commands.command()
    async def shuffle(self, ctx: commands.Context) -> None:
        if not self.playlist:
            emb = discord.Embed(title="Nothing to shuffle", color=0xff0000)
            emb.description = "Add songs with the `!play song_name` command!"
            await ctx.send(embed=emb)
            return

        random.shuffle(self.playlist)
        emb = discord.Embed(title="Playlist shuffled", color=0x00ff00)
        emb.description = "Use the `!playlist` command to see the new order!"
        await ctx.send(embed=emb)

    # Command to show the current song
    @commands.command()
    async def playing(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if not self.current_song:
            emb = discord.Embed(title="Nothing is playing", color=0xff0000)
            emb.description = "Play something with the `!play song_name` command!"
            await ctx.send(embed=emb)
            return

        await self.send_play_message(ctx)

    # Command to skip the current song
    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return

        self.current_voice_client.stop()
        if len(self.playlist) > 0:
            await self.play_sound(self.current_voice_client, self.playlist[0][2])
        else:
            emb = discord.Embed(title="No more songs in the playlist", color=0xff0000)
            emb.description = "Add more songs with the `!play song_name` command!"
            await ctx.send(embed=emb)

    # Command to stop the music
    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return

        self.current_voice_client.stop()
        self.playlist = []
        self.current_song = None
        emb = discord.Embed(title="Stopped", color=0xff0000)
        emb.description = "Everything has been stopped!\nUse the `!play song_name` command to play music!"
        await ctx.send(embed=emb)

    # Command to pause the music
    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if self.current_song is None:
            emb = discord.Embed(title="Nothing is playing", color=0xff0000)
            emb.description = "Play something with the `!play song_name` command!"
            await ctx.send(embed=emb)
            return

        self.current_voice_client.pause()
        emb = discord.Embed(title="Paused", color=0x00ff00)
        emb.description = "Use the `!resume` command to resume the music!"
        await ctx.send(embed=emb)

    # Command to resume the music
    @commands.command()
    async def resume(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if self.current_song is None:
            emb = discord.Embed(title="Nothing is playing", color=0xff0000)
            emb.description = "Play something with the `!play song_name` command!"
            await ctx.send(embed=emb)
            return

        self.current_voice_client.resume()
        await self.send_play_message(ctx)

    # Command to disconnect the bot from the voice channel
    @commands.command()
    async def disconnect(self, ctx: commands.Context) -> None:
        if self.current_voice_client is None:
            await self.send_not_in_voice_channel_message(ctx)
            return
        
        # Flags to stop the player sending messages before disconnecting
        self.playlist = []
        self.current_song = None
        await self.current_voice_client.disconnect()
        emb = discord.Embed(title=f"Disconnected form {self.current_voice_client.channel.name}", color=0xff0000)
        emb.description = f"Call me back with the `!play song_name` command!"
        await ctx.send(embed=emb)
        self.reset()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Youtube_Player(bot))
