import os
import requests
from pathlib import Path
import re
from PIL import Image
import imagehash
import time
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
IMG_BASE_URL = "https://image.tmdb.org/t/p/original"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# === MCU TITLE LIST BY CATEGORY ===
titles_by_phase = {
    "phase_1": [
        "Iron Man", "The Incredible Hulk", "Iron Man 2", "Thor",
        "Captain America: The First Avenger", "The Avengers"
    ],
    "phase_2": [
        "Iron Man 3", "Thor: The Dark World", "Captain America: The Winter Soldier",
        "Guardians of the Galaxy", "Avengers: Age of Ultron", "Ant-Man"
    ],
    "phase_3": [
        "Captain America: Civil War", "Doctor Strange", "Guardians of the Galaxy Vol. 2",
        "Spider-Man: Homecoming", "Thor: Ragnarok", "Black Panther",
        "Avengers: Infinity War", "Ant-Man and the Wasp", "Captain Marvel",
        "Avengers: Endgame", "Spider-Man: Far From Home"
    ],
    "phase_4": [
        "Black Widow", "Shang-Chi and the Legend of the Ten Rings", "Eternals",
        "Spider-Man: No Way Home", "Doctor Strange in the Multiverse of Madness",
        "Thor: Love and Thunder", "Black Panther: Wakanda Forever"
    ],
    "phase_5": [
        "Ant-Man and the Wasp: Quantumania", "Guardians of the Galaxy Vol. 3",
        "The Marvels", "Deadpool 3"
    ],
    "disney_plus": [
        "WandaVision", "The Falcon and the Winter Soldier", "Loki",
        "What If...?", "Hawkeye", "Moon Knight", "Ms. Marvel",
        "She-Hulk: Attorney at Law", "Werewolf by Night", "Secret Invasion", "Echo"
    ],
    "upcoming": [
        "Captain America: Brave New World", "Thunderbolts", "Blade",
        "Fantastic Four", "Agatha All Along", "Daredevil: Born Again", "Blade: Trinity"
    ]
}

# === FUNCTIONS ===
def get_tmdb_id(title):
    search_url = "https://api.themoviedb.org/3/search/multi"
    params = {"query": title, "include_adult": False, "language": "en-US", "api_key": API_KEY}
    response = requests.get(search_url, params=params)
    results = response.json().get("results", [])
    if results:
        return results[0]["id"], results[0]["media_type"]
    return None, None

def is_duplicate(new_img_path, existing_img_paths, threshold=5):
    new_hash = imagehash.average_hash(Image.open(new_img_path))
    for path in existing_img_paths:
        existing_hash = imagehash.average_hash(Image.open(path))
        if new_hash - existing_hash <= threshold:
            return True
    return False

def download_posters(title, tmdb_id, media_type, folder_path):
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    posters = response.json().get("posters", [])

    filtered_posters = [
        p for p in posters
        if p.get("iso_639_1") == "en" and p.get("vote_average", 0) >= 5 and p.get("width", 0) >= 1000
    ]

    existing_imgs = list(folder_path.glob("*.jpg"))

    count = 0
    for i, poster in enumerate(filtered_posters):
        if count >= 10:
            break
        poster_url = f"{IMG_BASE_URL}{poster['file_path']}"
        safe_title = re.sub(r'[\\/*?:"<>|]', '', title.lower().replace(' ', '_'))
        temp_filename = folder_path / f"temp_{safe_title}_{i+1}.jpg"

        try:
            response = requests.get(poster_url, timeout=10)
            response.raise_for_status()
            img_data = response.content
            with open(temp_filename, 'wb') as f:
                f.write(img_data)
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"  [!] Failed to download {poster_url} - {e}")
            continue

        if not is_duplicate(temp_filename, existing_imgs):
            final_filename = folder_path / f"{safe_title}_{count+1}.jpg"
            temp_filename.rename(final_filename)
            existing_imgs.append(final_filename)
            count += 1
            print(f"Downloaded: {final_filename}")
        else:
            temp_filename.unlink()

# === MAIN LOOP ===
base_dir = Path("../marvel_posters")
base_dir.mkdir(exist_ok=True)

for phase, titles in titles_by_phase.items():
    folder = base_dir / phase
    folder.mkdir(parents=True, exist_ok=True)

    for title in titles:
        print(f"Searching for: {title}")
        tmdb_id, media_type = get_tmdb_id(title)
        if tmdb_id:
            download_posters(title, tmdb_id, media_type, folder)
        else:
            print(f"  [!] Could not find TMDB ID for: {title}")
