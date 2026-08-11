import os
import urllib.request
import time

# Create images directory if it doesn't exist
os.makedirs("images", exist_ok=True)

# A sample list of licensed-free images from Wikimedia Commons using Special:FilePath
# Organized by category to test our mismatch guard (foxes vs wolves vs dogs)
IMAGE_URLS = {
    "red_fox_1": "https://commons.wikimedia.org/wiki/Special:FilePath/Fox_-_Flickr_-_Richard_Bartz_16.jpg?width=800",
    "red_fox_2": "https://commons.wikimedia.org/wiki/Special:FilePath/Vulpes_vulpes_ssp_fulvus.jpg?width=800",
    "red_fox_3": "https://commons.wikimedia.org/wiki/Special:FilePath/Fox_study_6.jpg?width=800",
    "wolf_1": "https://commons.wikimedia.org/wiki/Special:FilePath/Canis_lupus_standing_in_snow.jpg?width=800",
    "wolf_2": "https://commons.wikimedia.org/wiki/Special:FilePath/Canis_lupus_laying.jpg?width=800",
    "wolf_3": "https://commons.wikimedia.org/wiki/Special:FilePath/Eurasian_wolf_2.jpg?width=800",
    "dog_1": "https://commons.wikimedia.org/wiki/Special:FilePath/Collared_Brown_and_White_Dog.jpg?width=800",
    "dog_2": "https://commons.wikimedia.org/wiki/Special:FilePath/Cute_dog.jpg?width=800",
    "bear_1": "https://commons.wikimedia.org/wiki/Special:FilePath/2010-kodiak-bear-1.jpg?width=800",
    "bear_2": "https://commons.wikimedia.org/wiki/Special:FilePath/Ours_brun_parc_des_felins.jpg?width=800"
}

def download_images():
    print("Downloading seed images...")
    for name, url in IMAGE_URLS.items():
        filepath = os.path.join("images", f"{name}.jpg")
        if not os.path.exists(filepath):
            print(f"Downloading {name}...")
            try:
                # Adding a generic User-Agent to avoid 403 Forbidden errors
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
                time.sleep(1) # Be polite to the server
            except Exception as e:
                print(f"Failed to download {name}: {e}")
        else:
            print(f"{name} already exists. Skipping.")
    print("\nDownload complete! Check the 'images' folder.")

if __name__ == "__main__":
    download_images()
