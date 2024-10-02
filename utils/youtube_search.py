from youtubesearchpython import VideosSearch
import urllib.request
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()


def search_query(query: str) -> tuple:
    '''
    Search for a video on YouTube and return the title and URL of the 
    first result

    Parameters:
    query (str): The search query

    Returns:
    title (str), url (str): The title and URL of the video
    '''
    try:
        video_search = VideosSearch(str(query), limit=5)
    except Exception:
        return None, None

    for result in video_search.result()['result']:
        if not result.get('isLive', False) and result.get('duration') != None:
            return result['title'], result['link']
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
