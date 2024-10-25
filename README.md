![SenpaiSounds banner](/photos/SenpaiSounds_banner.png)

# SenpaiSounds

*SenpaiSounds* is an innovative Discord music bot designed to enhance server experience by seamlessly streaming music from YouTube.

Build using the `discord.py` library and leveraging `yt-dlp` for video downloading, *SenpaiSounds* offers a user-friendly interface for music playback directly within your Discord server.

The bot allows users to effortlessly queue songs, manage playlists, and control playback (all through simple commands). Whether you're looking to create a lively atmosphere for gaming sessions or provide a chill background vibe for social interactions, *SenpaiSounds* aims to meet your music needs.


## Key Features
- ***Stream from YouTube:*** Easily play music from your favorite YouTube videos and playlists, making it simple to share tunes with friends.

- ***Playlist Management:***  Queue up multiple tracks with ease, ensuring your music flows without interruption.

- ***Dynamic Media Control:*** Users can enjoy intuitive controls for play, pause, skip, and more, all while engaging with the bot's friendly responses.

- ***Giphy Integration:*** Enjoy animated GIFs related to your interactions between friends for an enhanced entertainment experience.

- ***Doggo Knowledge:*** Fetch fun dog facts and images, adding an element of joy and surprise.


## Future Enhancements
While *SenpaiSounds* is currently a work in progress, plans for future updates include:

- ***Expanded Audio Features:*** Adding sound effect options to enrich the vibe of your social interactions.

- ***Lyrics Integration:*** Displaying lyrics to songs , providing users with a complete sing-along experience. 

- ***Saving Playlists:*** Storing or using already-created playlist to never let music stop.

- ***Visual Improvements:*** Enhance current button aesthetics, making them more intuitive by using emojis


## APIs Used

- [Discord Developer](https://discord.com/developers/docs/intro) - Used for integrating everything with Discord

- [Youtube Data API](https://developers.google.com/youtube/v3) - Used for fetching data from YouTube videos

- [GIPHY Developers](https://developers.giphy.com/) - Used for sea rching specific category of GIFs

- [TheDogAPI](https://thedogapi.com/) - Used for displaying dog knowledge and pictures

## To run locally
1. Install the dependencies listed in `requirements.txt`. You may use the following command.

        pip install -r requirements.txt

2. Create your own API keys that is required for this project. You will need to follow the guides on the websites in this [section](#apis-used).

3. Put all your API keys into `.env_example` and rename it to `.env`.

4. Run `bot.py` to get the bot online.


## Contribution
*SenpaiSounds* is currently an individual project but contributions are welcome! Whether you want to suggest features, report bugs, or help improve the bot, your input can help shape the future of this project.


## License
This project is licensed under the MIT Lisense - see the [LICENSE](LICENSE) file for details.


## Acknowledgments
This project make use of [FFmepg](https://www.ffmpeg.org/), a free, powerful, open-source software licensed under the [LGPL or GPL](https://ffmpeg.org/legal.html) multimedia framework that allows the handling of video, audio, and other media streams. Without FFmpeg, the audio processing and streaming functionalities of *SenpaiSounds* would not be possible.
