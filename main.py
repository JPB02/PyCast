import os
import requests
import urllib.request
import feedparser

# itune's search api
api = "https://itunes.apple.com/search?term="

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

def get_RSS(selected_podcast):
    return selected_podcast['feedUrl']

def parse_RSS(rss):
    parsed_url = feedparser.parse(rss)
    return parsed_url

def get_episode_number(rss):
    episodeList = rss['entries'] 
    episode_number = len(episodeList)
    return episode_number

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

def get_podcast_title(feed):
    if "title" in feed.feed:
        return feed.feed.title
    else:
        return "No title found"

def download_mp3(feed, episode):
    episode_number = get_episode_number(feed)
    podcast_title = get_podcast_title(feed)
    if not os.path.isdir(podcast_title):
        os.makedirs(podcast_title)

    entry = feed.entries[episode_number-int(episode)]

    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if enclosure.type == 'audio/mpeg':
                mp3_url = enclosure.href
                episode_title = (entry.title) + ".mp3"
                file_path = os.path.join(podcast_title, episode_title)
                    
                # Download the MP3 and save it to the file path
                response = requests.get(mp3_url)

                with open(file_path, mode="wb") as file:
                    file.write(response.content)
                    print(f"Downloaded: {file_path}, Title:")

def main():
    search = input(">> Search Podcast: ").replace(" ", "+")
    # entity as podcast, this only finds podcasts
    url = api+search+"&entity=podcast"
    podcast = search_results(url)
    RSS = get_RSS(podcast)
    podcast_title = podcast['trackName']
    parsed_rss = parse_RSS(RSS)
    episode = choose_episode_from_list(parsed_rss)    
    download_mp3(parsed_rss ,episode)

if __name__ == "__main__":
    main()