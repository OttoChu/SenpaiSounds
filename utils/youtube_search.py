from youtubesearchpython import VideosSearch
import discord
import urllib.request
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()


async def search_query(ctx: discord.ext.commands.Context, query: str) -> tuple:
    '''
    Search for a video on YouTube and return the title and URL of the
    first result. It doesn't return any live videos or videos without a duration

    Parameters:
    ctx (discord.ext.commands.Context): The context of the command
    query (str): The search query

    Returns:
    title (str), url (str): The title and URL of the video
    '''
    query = query.replace(' ', '+')
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&maxResults=5&type=video&key={os.getenv('YOUTUBE_API_KEY')}"
    try:
        # Primary search method
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read())
                for item in data['items']:
                    # Ignore live videos and videos without a duration
                    if item['snippet']['liveBroadcastContent'] == 'live' or item.get('id', {}).get('videoId') == None:
                        continue
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_title = item['snippet']['title']
                    return video_title, video_url
            elif response.status == 403:
                await ctx.send("API key quota exceeded")

        emb = discord.Embed(title="Using the secondary search method",
                            description="The primary search method failed to find a suitable video. This method is slower and may not always return the best results.")
        emb.add_field(name="** **", value="Please wait a moment...")
        await ctx.send(embed=emb)

        # Secondary search method
        video_search = VideosSearch(str(query), limit=5)
        for result in video_search.result()['result']:
            # Ignore live videos and videos without a duration
            if not result.get('isLive', False) and result.get('duration') != None:
                return result['title'], result['link']
        return None, None

    except Exception as e:
        print(f"Failed to fetch video: {e}")
        return None, None


async def search_random() -> tuple:
    '''
    Search for a random trending music video on YouTube

    Returns:
    title (str), url (str): The title and URL of the video
    '''
    # Search for a random trending music video
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&videoCategoryId=10&maxResults=20&key={os.getenv('YOUTUBE_API_KEY')}"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read())

                videos = data.get('items', [])
                if not videos:
                    return None, None

                random_video = random.choice(videos)
                title = random_video['snippet']['title']
                video_id = random_video['id']
                url = f"https://www.youtube.com/watch?v={video_id}"
                return title, url

            elif response.status == 403:
                print("API key quota exceeded")
                return None, None
            return None, None

    except Exception as e:
        print(f"Failed to fetch random video: {e}")
        return None, None


def get_playlist_length(playlist_url: str, limit: int = 50) -> int:
    '''
    Get the length of a playlist

    Parameters:
    playlist_url (str): The URL of the playlist

    Returns:
    length (int): The number of videos in the playlist
    '''
    playlist_id = playlist_url.split('list=')[1]
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={limit}&key={os.getenv('YOUTUBE_API_KEY')}"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read())
                return data['pageInfo']['totalResults']
            elif response.status == 403:
                print("API key quota exceeded")
                return 0
            return 0
    except Exception as e:
        print(f"Failed to fetch playlist length: {e}")
        return 0


def get_playlist_song_urls(playlist_url: str, limit: int) -> list:
    '''
    Get the URLs of all the songs in a playlist

    Parameters:
    playlist_url (str): The URL of the playlist
    limit (int): The maximum number of songs to fetch

    Returns:
    urls (list): A list of URLs of the songs in the playlist
    '''
    playlist_id = playlist_url.split('list=')[1]
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={limit+1}&key={os.getenv('YOUTUBE_API_KEY')}"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read())
                urls = []
                for item in data['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    urls.append(f"https://www.youtube.com/watch?v={video_id}")
                return urls
            elif response.status == 403:
                print("API key quota exceeded")
                return []
            return []
    except Exception as e:
        print(f"Failed to fetch playlist song URLs: {e}")
        return []
