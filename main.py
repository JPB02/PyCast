import os
import requests
import feedparser
from pydub import AudioSegment
import simpleaudio as sa
import io
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, messagebox

# iTunes search API
api = "https://itunes.apple.com/search?term="

class PodcastApp:
    def __init__(self, master):
        self.master = master
        self.master.title("PyCast")

        # Search Frame
        self.search_frame = ttk.LabelFrame(master, text="Search for Podcasts")
        self.search_frame.grid(row=0, padx=10, pady=10, sticky="ew")

        self.search_label = ttk.Label(self.search_frame, text="Enter podcast name:")
        self.search_label.grid(row=0, column=0, padx=5, pady=5)

        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_podcasts)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        # Results Frame
        self.results_frame = ttk.LabelFrame(master, text="Search Results")
        self.results_frame.grid(row=1, padx=10, pady=10, sticky="ew")

        self.results_listbox = tk.Listbox(self.results_frame, width=50, height=10)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=5)

        self.select_button = ttk.Button(self.results_frame, text="Select Podcast", command=self.select_podcast)
        self.select_button.grid(row=1, column=0, padx=5, pady=5)

        # Episode Frame
        self.episode_frame = ttk.LabelFrame(master, text="Episodes")
        self.episode_frame.grid(row=2, padx=10, pady=10, sticky="ew")

        self.episode_listbox = tk.Listbox(self.episode_frame, width=50, height=10)
        self.episode_listbox.grid(row=0, column=0, padx=5, pady=5)

        self.action_button = ttk.Button(self.episode_frame, text="Download", command=self.download)
        self.action_button.grid(row=1, column=0, padx=5, pady=5)

        self.podcast_data = None
        self.parsed_rss = None

    def search_podcasts(self):
        search_term = self.search_entry.get().replace(" ", "+")
        url = f"{api}{search_term}&entity=podcast"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.results_listbox.delete(0, tk.END)  # Clear previous results
            self.podcast_data = data['results']  # Store podcast data for later use
            for index, item in enumerate(self.podcast_data):
                self.results_listbox.insert(tk.END, f" {item['trackName']} by {item['artistName']}")
        else:
            messagebox.showerror("Error", "API Failure...")

    def select_podcast(self):
        try:
            selected_index = self.results_listbox.curselection()[0]
            selected_podcast = self.podcast_data[selected_index]
            rss_url = selected_podcast['feedUrl']
            self.parsed_rss = self.parse_RSS(rss_url)
            self.episode_listbox.delete(0, tk.END)  # Clear previous episodes

            for index, entry in enumerate(self.parsed_rss.entries):
                self.episode_listbox.insert(tk.END, f" {entry.title}")
        except IndexError:
            messagebox.showwarning("Warning", "Please select a podcast first.")

    def parse_RSS(self, rss):
        return feedparser.parse(rss)

    def download(self):
        try:
            selected_index = self.episode_listbox.curselection()[0]
            chosen_episode = self.parsed_rss.entries[selected_index]
            mp3_url = next(enclosure.href for enclosure in chosen_episode.enclosures if enclosure.type == 'audio/mpeg')

            self.download_mp3(chosen_episode.title, mp3_url)
        except IndexError:
            messagebox.showwarning("Warning", "Please select an episode first.")

    def download_mp3(self, title, mp3_url):
        # Ensure podcast directory exists
        podcast_title = "Downloaded Podcasts"
        if not os.path.isdir(podcast_title):
            os.makedirs(podcast_title)

        episode_title = self.sanitize_filename(title) + ".mp3"
        file_path = os.path.join(podcast_title, episode_title)

        # Begin downloading the MP3 with a progress bar
        response = requests.get(mp3_url, stream=True)

        if response.status_code == 200:
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB chunks

            with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=episode_title) as progress_bar:
                with open(file_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)

            messagebox.showinfo("Success", f"Downloaded: {file_path}")
        else:
            messagebox.showerror("Error", "Download failed.")

    def sanitize_filename(self, filename):
        return "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()


if __name__ == "__main__":
    root = tk.Tk()
    app = PodcastApp(root)
    root.mainloop()
