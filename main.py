import os
import requests
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


def main():
    search = input(">> ").replace(" ", "+")
    # entity as podcast, this only finds podcasts
    url = api+search+"&entity=podcast"
    podcast = search_results(url)
    RSS = get_RSS(podcast)

if __name__ == "__main__":
    main()