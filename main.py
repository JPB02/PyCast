import os
import requests

# itune's search api
api = "https://itunes.apple.com/search?term="

def search_results(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        # fetch and print podcast results
        for item in data['results']:
            print(f"Track Name: {item['trackName']}")
            print("-"*40)

    else:
        print("API Failure...")


def main():
    search = input(">> ").replace(" ", "+")
    # entity as podcast, this only finds podcasts
    url = api+search+"&entity=podcast"
    search_results(url)

if __name__ == "__main__":
    main()