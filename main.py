import os
import requests

# itune's search api
api = "https://itunes.apple.com/search?term="

def search_results(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        selection = 1 # keep track of choice

        # fetch and print podcast results
        for item in data['results']:
            print(f"Selection: {selection}")
            print(f"Name: {item['trackName']}")
            print(f"Artist: {item['artistName']}")
            print("-"*40)
            selection+=1

    else:
        print("API Failure...")

    podcast_choice = input(">> Choose Podcast by ID: ")
    selected = data['results'][int(podcast_choice)-1]
    print(selected['trackName'])
    return selected

def main():
    search = input(">> ").replace(" ", "+")
    # entity as podcast, this only finds podcasts
    url = api+search+"&entity=podcast"
    search_results(url)

if __name__ == "__main__":
    main()