import os
import requests
import feedparser
from pydub import AudioSegment
import simpleaudio as sa
import io
from tqdm import tqdm 



# Itune's search api
api = "https://itunes.apple.com/search?term="

# Print the results of itunes search and returns selected podcast's data
def search_results(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        selection = 1 # keep track of choice

        # fetch and print podcast results
        for item in data['results']:
            print(f"Selection ID: {selection}")
            print(f"Name: {item['trackName']}")
            print(f"Artist: {item['artistName']}")
            print("-"*40)
            selection+=1

    else:
        print("API Failure...")

    podcast_choice = input(">> Choose Podcast by ID: ")
    selected = data['results'][int(podcast_choice)-1]
    print(f"Selected Podcast: {selected['trackName']}")
    return selected

# Returns the podcast rss
def get_RSS(selected_podcast):
    return selected_podcast['feedUrl']

# Simple parse of the rss 
def parse_RSS(rss):
    parsed_url = feedparser.parse(rss)
    return parsed_url

# Get the total number of episodes available
def get_episode_number(rss):
    episodeList = rss['entries'] 
    episode_number = len(episodeList)
    return episode_number

# Return choice of podcast episode, after printing all episodes
def choose_episode_from_list(podcast_RSS):
    episodeList = podcast_RSS['entries'] 
    episode_number = len(episodeList)
    for entry in episodeList:
        print(f"{episode_number}.{entry['title']}")
        episode_number-=1

    choice = input(">> ID: ")
    chosen = episodeList[len(episodeList)-int(choice)]['title']
    print(f"Chosen Episode: {chosen}")
    return choice

# Returns podcast title(if it exists)
def get_podcast_title(feed):
    if "title" in feed.feed:
        return feed.feed.title
    else:
        return "No title found"

# Function that streams episode
def stream_episode(episode_url):
    print(f"Streaming episode from: {episode_url}")
    
    # Download the MP3 stream
    response = requests.get(episode_url, stream=True)
    
    if response.status_code == 200:
        audio_data = response.content
        
        # Load the audio into pydub using io.BytesIO
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        
        # Play the audio using simpleaudio
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        play_obj.wait_done()  # Wait for playback to finish
    else:
        print("Failed to stream the episode.")

# Filenames must be correct, otherwise it won't save correctly
def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()

# Download Episode as .mp3 file
def download_mp3(episode, feed):
    podcast_title = get_podcast_title(feed)
    mp3_url, title = episode

    # Ensure podcast directory exists
    if not os.path.isdir(podcast_title):
        os.makedirs(podcast_title)

    # Create a sanitized file name
    episode_title = sanitize_filename(title) + ".mp3"
    file_path = os.path.join(podcast_title, episode_title)

    # Begin downloading the MP3 with a progress bar
    response = requests.get(mp3_url, stream=True)

    if response.status_code == 200:
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB chunks

        # Use tqdm to show the download progress
        with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=episode_title) as progress_bar:
            with open(file_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        print(f"Downloaded: {file_path}, Title: {title}")
    else:
        print("Download failed.")

# Returns a tuple with mp3_url and episode title
def get_episode_url(feed, episode):
    episode_number = get_episode_number(feed)

    entry = feed.entries[episode_number-int(episode)]

    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if enclosure.type == 'audio/mpeg':
                mp3_url = enclosure.href
                return (mp3_url, entry.title)

# Main function
def main():
    search = input(">> Search Podcast: ").replace(" ", "+")
    # entity as podcast, this only finds podcasts
    url = api+search+"&entity=podcast"
    podcast = search_results(url)
    RSS = get_RSS(podcast)
    podcast_title = podcast['trackName']
    parsed_rss = parse_RSS(RSS)
    episode = choose_episode_from_list(parsed_rss)    
    episode_url = get_episode_url(parsed_rss, episode)
    

    # Ask the user whether to stream or download
    action = input(">> Would you like to (S)tream or (D)ownload the episode? ").lower()

    if action == 's':
        # Stream the episode
        stream_episode(episode_url[0])  # The first item in the tuple is the mp3 URL
    elif action == 'd':
        # Download the episode
        download_mp3(episode_url, parsed_rss)
    else:
        print("Invalid choice, please choose either 'S' for stream or 'D' for download.")


if __name__ == "__main__":
    main()