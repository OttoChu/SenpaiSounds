import asyncio
import discord
from discord.ext import commands
import yt_dlp
from youtubesearchpython import VideosSearch
from utils.embedded_list import PaginationView


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

    # Helper function to search for a video on YouTube
    def search_youtube(self, query: str) -> tuple:
        '''
        Search for a video on YouTube and return the title and URL of the first result

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

    # Helper function to get voice channel
    async def get_voice_client(self, ctx: commands.Context) -> discord.VoiceClient:
        '''
        Get the voice client of the bot

        Parameters:
        ctx (commands.Context): The context of the command

        Returns:
        voice_client (discord.VoiceClient): The voice client of the bot
        '''
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention}, you need to be in a voice channel to use this command!")
            return None
        if not ctx.guild.voice_client:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()
        else:
            voice_client = ctx.guild.voice_client
        return voice_client

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

    def after_playing(self, error: Exception) -> None:
        '''
        Callback function that is called after the audio is done playing

        Parameters:
        error (Exception): The error that occurred while playing the audio
        '''
        if error:
            print(f"An error occurred: {error}")
        if self.playlist:
            self.playlist.pop(0)
            if self.playlist:
                title, yt_url, audio_url, requester = self.playlist[0]
                self.current_song = (title, yt_url, audio_url, requester)
                asyncio.run_coroutine_threadsafe(
                    self.play_sound(self.current_voice_client, audio_url),
                    self.bot.loop
                )
                asyncio.run_coroutine_threadsafe(
                    self.send_play_message(self.current_ctx),
                    self.bot.loop
                )
        else:
            asyncio.run_coroutine_threadsafe(
                self.current_ctx.send("Reached the end of the playlist!"),
                self.bot.loop
            )

    # Command to play music from YouTube
    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        voice_client = await self.get_voice_client(ctx)
        self.current_voice_client = voice_client
        self.current_ctx = ctx
        if not voice_client:
            return

        # Extract audio stream URL without downloading
        wait_message = await ctx.send("Please wait while I fetch the audio...")
        title, yt_url = self.search_youtube(query)
        if not title or not yt_url:
            await wait_message.delete()
            await ctx.send(f"No results found!\n{ctx.author.mention}, please try another query.")
            return
        info = self.ytdlp.extract_info(yt_url, download=False)
        audio_url = info['url']

        self.playlist.append((title, yt_url, audio_url, ctx.author.mention))
        await wait_message.delete()

        if not voice_client.is_playing():

            title, yt_url, audio_url, requester = self.playlist.pop()
            self.current_song = (title, yt_url, audio_url, requester)
            await self.play_sound(voice_client, audio_url)
            await self.send_play_message(ctx)
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
            emb.description = "Add some songs using the `!play` command!"
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

    # Command to show the current song
    @commands.command()
    async def playing(self, ctx: commands.Context) -> None:
        if not self.current_song:
            await ctx.send("Nothing is playing!")
            return

        await self.send_play_message(ctx)


async def setup(bot):
    await bot.add_cog(Youtube_Player(bot))