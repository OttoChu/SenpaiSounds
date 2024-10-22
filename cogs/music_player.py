import asyncio
from concurrent.futures import ThreadPoolExecutor
import discord
from discord.ext import commands
import yt_dlp
from utils.embedded_list import PaginationView
from utils.youtube_search import *
import random
import datetime


class Youtube_Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.MAX_ADD_PLAYLIST_SIZE = 20
        self.bot = bot
        self.playlist = []
        self.current_song = None
        self.current_voice_client = None
        self.current_ctx = None
        self.loop_current = [False, None]
        self.start_time = 0
        self.time_passed = 0
        self.disconnect_timer_task = None
        self.executor = ThreadPoolExecutor(max_workers=8)

        # YouTube downloader settings
        yt_dlp_format_options = {
            'format': 'bestaudio/best',  # Choose the best audio format
            'default_search': 'ytsearch',  # Use ytsearch for search queries
            'quiet': True,  # Suppress console output
            'audioformat': 'mp3',  # Use mp3 format for audio
            'is_live': False, 'live-from-start': False,  # Skip live streams
            'extractor-args': 'youtube:skip=bypass',  # Skip age-gate
            'skip_download': True,  # Ensures no download happens
            'nocheckcertificate': True,  # In case SSL slows down the process
            'force_generic_extractor': False,  # Use generic to speed up for playlists
            'extract_flat': 'in_playlist',  # Extract all videos in the playlist
            'youtube_include_dash_manifest': False  # Skip DASH manifest
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
        self.start_time = 0
        self.time_passed = 0
        self.disconnect_timer_task = None

    # Helper function to run blocking code in an executor
    async def run_in_executor(self, func, *args) -> any:
        '''
        Helper method to run blocking code in an executor

        Parameters:
        func (function): The function to run
        *args: The arguments to pass to the function

        Returns:
        Any: The result of the function
        '''
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

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

        def play_audio():
            # Stream audio using discord's built-in support for audio URLs
            source = discord.FFmpegPCMAudio(url, executable="utils/ffmpeg/bin/ffmpeg.exe",
                                            **ffmpeg_options)
            self.current_voice_client.play(source, after=self.after_playing)

        await self.run_in_executor(play_audio)
        # Track the time the song started playing
        self.start_time = datetime.datetime.now().timestamp()
        self.time_passed = 0

    # Helper function to return loop status
    def get_loop_status(self) -> str:
        '''
        Get the loop status of the current song

        Returns:
        str: The loop status
        '''
        if self.loop_current[0]:
            return f"*This song is looped by {self.loop_current[1]}*"
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

    # Helper function to add a song to the playlist
    async def add_single_to_playlist(self, ctx: commands.Context, entry: dict) -> None:
        '''
        Add a song to the playlist

        Parameters:
        ctx (commands.Context): The context of the command
        entry (dict): The dictionary containing the song information

        Returns:
        bool: True if the song was added to the playlist, False otherwise
        '''
        audio_url = entry['url']
        title = entry['title']
        yt_url = entry['webpage_url']
        duration = entry.get('duration')

        if duration == None:
            await ctx.send(f"Livestreams are not supported!\n{ctx.author.mention}, please try another query.")
            return False

        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.playlist.append(
            (title, yt_url, audio_url, duration, ctx.author.mention, time))
        return True

    # Helper function to add multiple songs to the playlist
    async def add_multi_to_playlist(self, ctx: commands.Context, entry: dict) -> None:
        '''
        Add multiple songs to the playlist

        Parameters:
        ctx (commands.Context): The context of the command
        entry (dict): The dictionary containing the song information
        '''

        title = entry['title']
        yt_url = entry['url']
        duration = entry.get('duration')

        if duration == None:
            await ctx.send(f"Livestreams are not supported!\n{ctx.author.mention}, please try another query.")
            return False

        info = await self.run_in_executor(self.ytdlp.extract_info, yt_url, False)
        audio_url = info.get('url')

        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.playlist.append(
            (title, yt_url, audio_url, duration, ctx.author.mention, time))
        return True

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

        if self.current_voice_client.is_playing():
            self.time_passed = datetime.datetime.now().timestamp() - \
                self.start_time + self.time_passed
            self.start_time = datetime.datetime.now().timestamp()
            current_timestamp = self.get_formatted_time(self.time_passed)
        else:
            current_timestamp = self.get_formatted_time(self.time_passed)

        progress = int((self.time_passed / duration) * 30)
        duration = self.get_formatted_time(duration)

        emb = discord.Embed(title=f"Playing", color=0x00ff00)
        emb.add_field(
            name="** **", value=f"[{title}]({yt_url})", inline=False)
        emb.add_field(
            name="** **", value=f"{'▓' * progress}{'░' * (30 - progress)} ({current_timestamp}/{duration})", inline=False)

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
            emb = discord.Embed(title="An error occurred", color=0xff0000)
            emb.description = "An error occurred that the developer didn't account for.\nPlease contact the developer with the error message below and the command you ran."
            emb.add_field(name="** **", value=error)
            asyncio.run_coroutine_threadsafe(
                self.current_ctx.send(embed=emb),
                self.bot.loop
            )
            return

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
        after 5 minutes
        '''
        # only one timer task should be running at a time
        if self.disconnect_timer_task:
            return

        async def disconnect_after_timeout():
            await asyncio.sleep(300)
            if (not self.current_voice_client.is_playing()
                and self.current_song is None
                    and self.current_voice_client is not None):
                await self.current_voice_client.disconnect()
                emb = discord.Embed(
                    title=f"Disconnected due to inactivity", color=0xff0000)
                emb.description = f"Call me back with the `!play song_name` command!"
                await self.current_ctx.send(embed=emb)
                self.reset()

        self.disconnect_timer_task = self.bot.loop.create_task(
            disconnect_after_timeout())

    # Command to play music from YouTube
    @commands.command(help="Play music from YouTube", usage="!play\n!play <song name / YouTube URL>", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str = None) -> None:
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

        wait_message = discord.Embed(
            title="Please wait while I fetch the audio...", color=0x00ff00)
        wait_message.add_field(
            name="** **", value="This may take a few seconds!")
        wait_message = await ctx.send(embed=wait_message)
        add_playlist = False

        #  Adding a random trending song from YouTube
        if not query:
            while True:
                title, yt_url = await (search_random())
                info = await self.run_in_executor(self.ytdlp.extract_info, yt_url, False)
                audio_url = info['url']
                duration = info.get('duration')
                if title and yt_url and audio_url and duration:
                    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.playlist.append(
                        (title, yt_url, audio_url, duration, ctx.author.mention, time))
                    break

        # Adding songs with YouTube URLs
        elif "https://www.youtube.com/watch?v=" in query:
            # Adding Youtube playlist
            if "list=" in query:
                add_playlist = True
                play_list_len = get_playlist_length(query)
                new_songs = get_playlist_song_urls(
                    query, self.MAX_ADD_PLAYLIST_SIZE)

                # Limit the number of songs added by one command
                if play_list_len > self.MAX_ADD_PLAYLIST_SIZE:
                    too_long_message = discord.Embed(
                        title="Playlist too long", color=0xff0000)
                    too_long_message.description = f"Only the first {self.MAX_ADD_PLAYLIST_SIZE} songs will be added to the playlist!"
                    await ctx.send(embed=too_long_message)

                # Adding the first song to the playlist, the rest will be added later
                info = await self.run_in_executor(self.ytdlp.extract_info, new_songs.pop(0), False)
                if not await self.add_single_to_playlist(ctx, info):
                    await wait_message.delete()
                    await ctx.send(f"Song not added to the playlist!")
                    return
            # Adding a single song with a YouTube URL
            else:
                try:
                    info = await self.run_in_executor(self.ytdlp.extract_info, query, False)
                    if not await self.add_single_to_playlist(ctx, info):
                        await wait_message.delete()
                        await ctx.send(f"Song not added to the playlist!")
                        return

                # Video not available on YouTube
                except Exception as e:
                    await wait_message.delete()
                    if e == yt_dlp.utils.DownloadError:
                        await ctx.send(f"Video not available on YouTube!\n{ctx.author.mention}, please try another query.")
                    else:
                        await ctx.send(f"The URL maybe invalid or truncated!\n{ctx.author.mention}, please try another query.")
                    return

        # Search for a song with the query
        else:
            title, yt_url = await search_query(ctx, query)
            if not title or not yt_url:
                await wait_message.delete()
                await ctx.send(f"No results found!\n{ctx.author.mention}, please try another query.")
                return

            info = await self.run_in_executor(self.ytdlp.extract_info, yt_url, False)
            if not await self.add_single_to_playlist(ctx, info):
                await wait_message.delete()
                return

        # Play the song if nothing is playing
        await wait_message.delete()
        if not self.current_voice_client.is_playing():
            self.current_song = self.playlist.pop(0)
            await self.play_sound(self.current_song[2])
            await self.send_play_message(ctx)

        else:
            # Add single song to the playlist if something is playing
            if not add_playlist:
                title, yt_url, audio_url, duration, requester, time = self.playlist[-1]
                duration = self.get_formatted_time(duration)
                emb = discord.Embed(title="Added to Playlist", color=0x00ff00)
                emb.add_field(
                    name="** **", value=f"[{title}]({yt_url}) ({duration})", inline=False)
                emb.add_field(name="Requested by",
                              value=f"{requester} at {time}", inline=False)
                # await wait_message.delete()
                await ctx.send(embed=emb)

        if add_playlist:
            # Adding the rest of the playlist if a playlist was added
            async def add_rest_of_playlist():
                failed_songs = []
                while len(new_songs) > 0:
                    try:
                        info = await self.run_in_executor(self.ytdlp.extract_info, new_songs.pop(0), False)
                        if not await self.add_single_to_playlist(ctx, info):
                            await wait_message.delete()
                            continue
                    except Exception as e:
                        e = str(e).split("[0;31mERROR:[0m ")[1].split(":")[1].strip()
                        failed_songs.append((info['title'], info['webpage_url'], e))
                        continue

                    # Update the wait message
                    new_wait_message = discord.Embed(
                        title="Adding the playlist...", color=0x00ff00)
                    new_wait_message.description = "Please wait while the rest of the playlist is added!"
                    new_wait_message.add_field(
                        name="** **", value=f"{len(new_songs)} songs left to add!")
                    await wait_message.edit(embed=new_wait_message)

                # Reached the end of the new playlist
                await wait_message.delete()
                emb = discord.Embed(
                    title="New songs added!", color=0x00ff00)
                emb.description = "Use the `!playlist` command to see the new playlist!"
                if failed_songs:
                    emb.add_field(name="Failed to add the following songs",
                                  value="\n".join([f"[{title}]({url})\n{error}\n" for title, url, error in failed_songs]))
                await ctx.send(embed=emb)

            # await wait_message.delete()
            wait_message = discord.Embed(
                title="Adding the playlist...", color=0x00ff00)
            wait_message.description = "Please wait while the rest of the playlist is added!"
            wait_message.add_field(
                name="** **", value=f"{len(new_songs)} songs left to add!")
            wait_message = await ctx.send(embed=wait_message)
            asyncio.create_task(add_rest_of_playlist())

    # Command to show the current playlist
    @commands.command(help="Show the current playlist", usage="!playlist", aliases=["pl"])
    async def playlist(self, ctx: commands.Context) -> None:
        if not self.playlist:
            emb = discord.Embed(title="Nothing else is in the playlist",
                                color=0x00ff00)
            emb.description = "Use the `!play song_name` command to add more songs!"
            await ctx.send(embed=emb)
            return

        self.time_passed = datetime.datetime.now().timestamp() - \
            self.start_time + self.time_passed
        self.start_time = datetime.datetime.now().timestamp()
        time_left = self.current_song[3] - self.time_passed
        total_time = self.get_formatted_time(
            sum([song[3] for song in self.playlist]) + time_left)

        requesters = [song[4] for song in self.playlist]
        song_names = [f"[{song[0]}]({song[1]})" for song in self.playlist]

        durations = [self.get_formatted_time(
            song[3]) for song in self.playlist]

        formatted_song = [f"{i}. {requester} - {song} ({duration})\n"
                          for i, (song, duration, requester) in
                          enumerate(zip(song_names, durations, requesters), start=1)]

        # duration of the current song is not accurate if it is looped
        if self.loop_current[0]:
            loop_message = "*(Not accurate as the current song is looped)*"
        else:
            loop_message = ""

        description = f"Songs in playlist: **{len(self.playlist)}**\nPlaylist duration: **{total_time}** {loop_message}"

        view = PaginationView(formatted_song, item_id=None, title="Playlist",
                              list_description=description, items_per_page=5)
        emb = view.create_embed()
        await ctx.send(embed=emb, view=view)

    # Command to move a song in the playlist
    @commands.command(help="Move a song in the playlist", usage="!move <song_position> <new_position>", aliases=["m"])
    async def move(self, ctx: commands.Context, old_position: int, new_position: int) -> None:
        if len(self.playlist) == 0:
            emb = discord.Embed(
                title="Nothing in the playlist", color=0xff0000)
            emb.description = "There are no songs in the playlist to move!"
            await ctx.send(embed=emb)
            return

        if old_position < 1 or old_position > len(self.playlist) or new_position < 1 or new_position > len(self.playlist):
            emb = discord.Embed(title="Invalid song position",
                                color=0xff0000)
            emb.description = "Please check the song position and try again!"
            await ctx.send(embed=emb)
            return

        song = self.playlist.pop(old_position - 1)
        self.playlist.insert(new_position - 1, song)
        emb = discord.Embed(title="Song moved", color=0x00ff00)
        emb.description = f"Song moved from position {old_position} to position {new_position}!"
        await ctx.send(embed=emb)

    # Command to remove a song from the playlist
    @commands.command(help="Remove a song from the playlist", usage="!remove <song_position>")
    async def remove(self, ctx: commands.Context, position: int) -> None:
        if position < 1 or position > len(self.playlist):
            emb = discord.Embed(title="Invalid song position", color=0xff0000)
            emb.description = "Please check the song position and try again!"
            await ctx.send(embed=emb)
            return

        song = self.playlist.pop(position - 1)
        emb = discord.Embed(title="Song removed", color=0x00ff00)
        emb.description = f"Removed [{song[0]}]({song[1]}) from the playlist!"
        await ctx.send(embed=emb)

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

        voice_client = self.current_voice_client
        ctx = self.current_ctx
        self.reset()
        self.current_voice_client = voice_client
        self.current_ctx = ctx

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
        self.time_passed = datetime.datetime.now().timestamp() - self.start_time
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
        self.start_time = datetime.datetime.now().timestamp()
        await self.send_play_message(ctx)

    # Command to disconnect the bot from the voice channel
    @commands.command(help="Disconnect the bot from the voice channel", usage="!disconnect", aliases=["dc"])
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

    # Commands to play rickroll
    @commands.command(help="Play a rickroll", usage="!rick")
    async def rick(self, ctx: commands.Context) -> None:
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention}, you need to be in a voice channel to use this command!")
            return
        if not ctx.guild.voice_client:
            voice_channel = ctx.author.voice.channel
            self.current_voice_client = await voice_channel.connect()
            self.current_ctx = ctx

        def play_audio():
            # Stream audio using discord's built-in support for audio URLs
            ffmpeg_options = {'options': '-vn'}
            source = discord.FFmpegPCMAudio("data/music.mp3", executable="utils/ffmpeg/bin/ffmpeg.exe",
                                            **ffmpeg_options)
            self.current_voice_client.play(source, after=self.after_playing)

        play_audio()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Youtube_Player(bot))
