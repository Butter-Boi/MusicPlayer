import yt_dlp

def get_first_youtube_link(query):
    search = f"ytsearch1:{query}"  # Only grab 1 result
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info and len(info['entries']) > 0:
            video = info['entries'][0]
            title = video['title']
            return f"https://www.youtube.com/watch?v={video['id']}", title
        else:
            return None, None

# Example usage

def search(query):
    link, title = get_first_youtube_link(query)

    if link:
        print("Top video:", title)
        return link, title
    else:
        print("No results found.")
        return None