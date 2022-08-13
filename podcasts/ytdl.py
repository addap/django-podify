import yt_dlp


def get_playlist_info(playlist_url):
    ydl_opts = {'extract_flat': 'in_playlist'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        # info = ydl.sanitize_info(info)
    return info


def get_episode_info(episode_url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(episode_url, download=False)
        # info = ydl.sanitize_info(info)

    del info['automatic_captions']
    return info
