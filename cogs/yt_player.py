import asyncio
import discord
from discord.ext import commands
import yt_dlp
from youtubesearchpython import VideosSearch
from utils.embedded_list import PaginationView
import random
import datetime


class Youtube_Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playlist = []
        self.current_song = None
        self.current_voice_client = None
        self.current_ctx = None
        self.loop_current = [False, None]
        # YouTube downloader settings
        yt_dlp_format_options = {
            'format': 'bestaudio/best', 'noplaylist': True,
            'default_search': 'ytsearch', 'quiet': True,
            'audioformat': 'mp3', 'is_live': False,
            'live-from-start': False
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
        self.loop_current = [False, None]

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
        try:
            video_search = VideosSearch(str(query), limit=5)
        except Exception:
            return None, None

        for result in video_search.result()['result']:
            if not result.get('isLive', False) and result.get('duration') != None:
                return result['title'], result['link']
        return None, None

    # Helper function to play sound from a URL
    async def play_sound(self, url: str) -> None:
        '''
        Play audio from a URL in the voice channel

        Parameters:
        url (str): The URL of the audio stream
        '''
        # FFmpeg options to stream audio from the URL
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'  # -vn tells ffmpeg that this is an audio-only stream,
        }

        # Troll feature
        # 1% chance to play a rickroll instead of the requested song
        # The chance can be adjusted to any value between 0 and 1
        if random.random() < 0.01:
            url = "data/music.mp3"
            ffmpeg_options = {'options': '-vn'}

        # Stream audio using discord's built-in support for audio URLs
        source = discord.FFmpegPCMAudio(url, executable="utils/ffmpeg/bin/ffmpeg.exe",
                                        **ffmpeg_options)

        self.current_voice_client.play(source, after=self.after_playing)

    # Helper function to return loop status
    def get_loop_status(self) -> str:
        '''
        Get the loop status of the current song

        Returns:
        str: The loop status
        '''
        if self.loop_current[0]:
            return f"*This looped by {self.loop_current[1]}*"
        return ""

    # Helper function to return formatted time from seconds
    def get_formatted_time(self, seconds: int) -> str:
        '''
        Get the formatted time from seconds

        Parameters:
        seconds (int): The time in seconds

        Returns:
        str: The formatted time in HH:MM:SS format (MM:SS if less than an hour)
        '''
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds // 60) % 60
        secs = seconds % 60

        return f"{hours:02}:{minutes:02}:{secs:02}" if hours > 0 else f"{minutes:02}:{secs:02}"

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
        title, yt_url, _, duration, requester, time = self.current_song
        duration = self.get_formatted_time(duration)

        emb = discord.Embed(title=f"Playing", color=0x00ff00)
        emb.add_field(
            name="** **", value=f"[{title}]({yt_url}) ({duration})", inline=False)
        emb.add_field(name="Requested by",
                      value=f"{requester} at {time}", inline=False)
        if self.loop_current[0]:
            emb.add_field(
                name="** **", value=f"{self.get_loop_status()}", inline=False)
        await ctx.send(embed=emb)

    # Helper function to send nothing is playing message
    async def send_nothing_is_playing_message(self, ctx: commands.Context) -> None:
        '''
        Send a message to the channel that nothing is playing

        Parameters:
        ctx (commands.Context): The context of the command
        '''
        emb = discord.Embed(title="Nothing is playing", color=0xff0000)
        emb.description = "Play something with the `!play song_name` command!"
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

        # Loop the current song if the loop flag is set
        if self.loop_current[0]:
            self.playlist.insert(0, self.current_song)

        # Continue playing the playlist if there are more songs
        if len(self.playlist) > 0:
            self.current_song = self.playlist[0]
            asyncio.run_coroutine_threadsafe(
                self.play_sound(self.current_song[2]),
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
        after 10 minutes
        '''
        await asyncio.sleep(600)
        if (not self.current_voice_client.is_playing()
            and not self.current_song
                and not self.current_voice_client):
            await self.current_voice_client.disconnect()
            emb = discord.Embed(
                title=f"Disconnected form {self.current_voice_client.channel.name}", color=0xff0000)
            emb.description = f"Call me back with the `!play song_name` command!"
            await self.current_ctx.send(embed=emb)
            self.reset()

    # Command to play music from YouTube
    @commands.command(help="Play music from YouTube", usage="!play <song name / YouTube URL>")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        # User must be in a voice channel to use this command
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention}, you need to be in a voice channel to use this command!")
            return
        # Join the voice channel if the bot is not already connected
        if not ctx.guild.voice_client:
            wait_message = await ctx.send("Joining the voice channel...")
            voice_channel = ctx.author.voice.channel
            self.current_voice_client = await voice_channel.connect()
            self.current_ctx = ctx
            await wait_message.delete()

        # Extract audio stream URL without downloading
        wait_message = await ctx.send("Fetching the audio...")

        # Check if the query is a YouTube URL
        if "https://www.youtube.com/watch?v=" in query:
            try:
                info = self.ytdlp.extract_info(query, download=False)
                audio_url = info['url']
                title = info['title']
                yt_url = query
                duration = info.get('duration')
                if duration == None:
                    await ctx.send(f"Livestreams are not supported!\n{ctx.author.mention}, please try another query.")
                    return

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
            if not title or not yt_url:
                await ctx.send(f"No results found!\n{ctx.author.mention}, please try another query.")
                return

            info = self.ytdlp.extract_info(yt_url, download=False)
            audio_url = info['url']
            duration = info['duration']

        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the song to the playlist
        self.playlist.append(
            (title, yt_url, audio_url, duration, ctx.author.mention, time))
        await wait_message.delete()

        # Play the song if nothing is playing
        if not self.current_voice_client.is_playing():
            self.current_song = self.playlist.pop(0)
            await self.play_sound(self.current_song[2])
            await self.send_play_message(ctx)

        # Add the song to the playlist if something is playing
        else:
            duration = self.get_formatted_time(duration)
            emb = discord.Embed(title="Added to Playlist", color=0x00ff00)
            emb.add_field(
                name="** **", value=f"[{title}]({yt_url}) ({duration})", inline=False)
            emb.add_field(name="Requested by",
                          value=f"{ctx.author.mention} at {time}", inline=False)
            await ctx.send(embed=emb)

    # Command to show the current playlist
    @commands.command(help="Show the current playlist", usage="!playlist")
    async def playlist(self, ctx: commands.Context) -> None:
        if not self.playlist:
            emb = discord.Embed(title="Nothing else is in the playlist",
                                color=0x00ff00)
            emb.description = "Use the `!play song_name` command to add more songs!"
            await ctx.send(embed=emb)
            return

        requesters = [song[4] for song in self.playlist]
        song_names = [f"[{song[0]}]({song[1]})" for song in self.playlist]
        durations = [self.get_formatted_time(
            song[3]) for song in self.playlist]

        formatted_song = [f"{i}. {requester} - {song} ({duration})\n"
                          for i, (song, duration, requester) in
                          enumerate(zip(song_names, durations, requesters), start=1)]

        description = f"Songs in playlist: {len(self.playlist)}\nPlaylist duration: {self.get_formatted_time(sum([song[3] for song in self.playlist]))}"

        view = PaginationView(formatted_song, item_id=None, title="Playlist",
                              list_description=description, items_per_page=5)
        emb = view.create_embed()
        await ctx.send(embed=emb, view=view)

    # Command to clear the playlist
    @commands.command(help="Clear the current playlist", usage="!clear")
    async def clear(self, ctx: commands.Context) -> None:
        self.playlist = []
        emb = discord.Embed(title="Playlist cleared", color=0x00ff00)
        emb.description = "Add new songs with the `!play song_name` command!"
        await ctx.send(embed=emb)

    # Command to shuffle the playlist
    @commands.command(help="Shuffle the current playlist", usage="!shuffle")
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
    @commands.command(help="Show the current song", usage="!playing")
    async def playing(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if not self.current_song:
            await self.send_nothing_is_playing_message(ctx)
            return

        await self.send_play_message(ctx)

    # Command to loop the current song
    @commands.command(help="Loop the current song", usage="!loop")
    async def loop(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if not self.current_song:
            await self.send_nothing_is_playing_message(ctx)
            return

        self.loop_current[0] = not self.loop_current[0]

        if self.loop_current[0]:
            self.loop_current[1] = ctx.author.mention
            emb = discord.Embed(
                title="Looping the current song", color=0x00ff00)
            emb.description = f"[{self.current_song[0]}]({self.current_song[1]}) will be looped!"
            emb.add_field(
                name="** **", value="Use the `!loop` command again to stop looping!")
        else:
            emb = discord.Embed(
                title="Stopped looping the current song", color=0xff0000)
            emb.description = "Use the `!loop` command again to loop the song!"
        await ctx.send(embed=emb)

    # Command to skip the current song
    @commands.command(help="Skip the current song", usage="!skip")
    async def skip(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return

        self.current_voice_client.stop()

        # Loop the current song if the loop flag is set
        if self.loop_current[0]:
            emb = discord.Embed(
                title="The current song is being looped", color=0x00ff00)
            emb.description = "Use the `!loop` command to stop looping before skipping!"
            await ctx.send(embed=emb)
            await self.play_sound(self.current_song[2])
            return

        # Continue playing the playlist if there are more songs
        if len(self.playlist) > 0:
            await self.play_sound(self.playlist[0][2])
        else:
            emb = discord.Embed(
                title="No more songs in the playlist", color=0xff0000)
            emb.description = "Add more songs with the `!play song_name` command!"
            await ctx.send(embed=emb)

    # Command to stop the music
    @commands.command(help="Stop the music", usage="!stop")
    async def stop(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return

        self.current_voice_client.stop()
        self.playlist = []
        self.current_song = None
        self.loop_current = [False, None]
        emb = discord.Embed(title="Stopped", color=0xff0000)
        emb.description = "Everything has been stopped!\nUse the `!play song_name` command to play music!"
        await ctx.send(embed=emb)

    # Command to pause the music
    @commands.command(help="Pause the music", usage="!pause")
    async def pause(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if self.current_song is None:
            self.send_nothing_is_playing_message(ctx)
            return

        self.current_voice_client.pause()
        emb = discord.Embed(title="Paused", color=0x00ff00)
        emb.description = "Use the `!resume` command to resume the music!"
        await ctx.send(embed=emb)

    # Command to resume the music
    @commands.command(help="Resume the music", usage="!resume")
    async def resume(self, ctx: commands.Context) -> None:
        if not self.current_voice_client:
            await self.send_not_in_voice_channel_message(ctx)
            return
        if self.current_song is None:
            self.send_nothing_is_playing_message(ctx)
            return

        self.current_voice_client.resume()
        await self.send_play_message(ctx)

    # Command to disconnect the bot from the voice channel
    @commands.command(help="Disconnect the bot from the voice channel", usage="!disconnect")
    async def disconnect(self, ctx: commands.Context) -> None:
        if self.current_voice_client is None:
            await self.send_not_in_voice_channel_message(ctx)
            return

        # Flags to stop the player sending messages before disconnecting
        self.playlist = []
        self.current_song = None
        await self.current_voice_client.disconnect()
        emb = discord.Embed(
            title=f"Disconnected form {self.current_voice_client.channel.name}", color=0xff0000)
        emb.description = f"Call me back with the `!play song_name` command!"
        await ctx.send(embed=emb)
        self.reset()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Youtube_Player(bot))
