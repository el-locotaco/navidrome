import os
import re
import time
import requests

USERNAME = os.getenv("LISTENBRAINZ_USERNAME", "YOUR_LISTENBRAINZ_USERNAME_HERE")
MUSIC_DIR = "/music"
PLAYLIST_DIR = "/playlists"
LIDARR_URL = os.getenv("LIDARR_URL", "http://lidarr:8686")
LIDARR_API_KEY = os.getenv("LIDARR_API_KEY", "YOUR_LIDARR_API_KEY_HERE")

def get_lidarr_defaults(headers):
    q_id, m_id = 1, 1
    try:
        q_res = requests.get(f"{LIDARR_URL}/api/v1/qualityprofile", headers=headers, timeout=10)
        if q_res.status_code == 200 and q_res.json():
            q_id = q_res.json()[0]["id"]
            
        m_res = requests.get(f"{LIDARR_URL}/api/v1/metadataprofile", headers=headers, timeout=10)
        if m_res.status_code == 200 and m_res.json():
            m_id = m_res.json()[0]["id"]
    except Exception as e:
        print(f"  [Lidarr Profile Warning]: {e}")
    return q_id, m_id

def search_lidarr_and_download(artist_name, track_title, processed_artists):
    if not LIDARR_API_KEY or artist_name in processed_artists:
        return
    
    headers = {"X-Api-Key": LIDARR_API_KEY}
    
    try:
        q_id, m_id = get_lidarr_defaults(headers)
        
        # Search artist on Lidarr
        res = requests.get(f"{LIDARR_URL}/api/v1/artist/lookup", params={"term": artist_name}, headers=headers, timeout=10)
        time.sleep(1) # Throttle
        
        if res.status_code == 200 and res.json():
            artist_data = res.json()[0]
            artist_mbid = artist_data.get("foreignArtistId")
            
            existing = requests.get(f"{LIDARR_URL}/api/v1/artist", headers=headers, timeout=10).json()
            time.sleep(1)
            
            artist_entry = next((a for a in existing if a.get("foreignArtistId") == artist_mbid), None)
            
            if not artist_entry:
                payload = {
                    "artistName": artist_data["artistName"],
                    "foreignArtistId": artist_mbid,
                    "qualityProfileId": q_id,
                    "metadataProfileId": m_id,
                    "rootFolderPath": MUSIC_DIR,
                    "monitored": True,
                    "addOptions": {
                        "monitor": "all",
                        "searchForMissingAlbums": True
                    }
                }
                add_res = requests.post(f"{LIDARR_URL}/api/v1/artist", json=payload, headers=headers, timeout=10)
                time.sleep(2)
                
                if add_res.status_code in (200, 201):
                    artist_entry = add_res.json()
                    print(f"  [Lidarr] Added artist: {artist_data['artistName']}")
                else:
                    return

            if artist_entry:
                cmd_payload = {
                    "name": "ArtistSearch",
                    "artistId": artist_entry["id"]
                }
                requests.post(f"{LIDARR_URL}/api/v1/command", json=cmd_payload, headers=headers, timeout=10)
                print(f"  [Lidarr] Search queued for: {artist_name}")
                processed_artists.add(artist_name)
                time.sleep(2)

    except Exception as e:
        print(f"  [Lidarr Exception]: {e}")

def find_local_file(artist, title):
    artist_clean = re.sub(r'[^\w\s]', '', artist.lower())
    title_clean = re.sub(r'[^\w\s]', '', title.lower())
    
    for root, _, files in os.walk(MUSIC_DIR):
        for file in files:
            if file.endswith(('.mp3', '.flac', '.m4a', '.ogg', '.wav')):
                file_clean = re.sub(r'[^\w\s]', '', file.lower())
                if title_clean in file_clean and (artist_clean in file_clean or artist_clean in root.lower()):
                    return os.path.relpath(os.path.join(root, file), MUSIC_DIR)
    return None

def fetch_and_build_playlists():
    print(f"Fetching playlists for ListenBrainz user: {USERNAME}")
    url = f"https://api.listenbrainz.org/1/user/{USERNAME}/playlists/createdfor"
    processed_artists = set()
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            print(f"ListenBrainz API Error: HTTP {res.status_code}")
            return
            
        playlists = res.json().get("playlists", [])
        os.makedirs(PLAYLIST_DIR, exist_ok=True)

        for item in playlists:
            pl_info = item.get("playlist", {})
            title = pl_info.get("title", "ListenBrainz Playlist")
            mbid = pl_info.get("identifier", "").split("/")[-1]
            if not mbid:
                continue

            pl_res = requests.get(f"https://api.listenbrainz.org/1/playlist/{mbid}", timeout=15)
            if pl_res.status_code != 200:
                continue

            tracks = pl_res.json().get("playlist", {}).get("track", [])
            m3u_lines = ["#EXTM3U", f"#PLAYLIST:{title}"]
            matched = 0

            for track in tracks:
                track_title = track.get("title", "")
                artist = track.get("creator", "")
                local_path = find_local_file(artist, track_title)
                if local_path:
                    m3u_lines.append(f"../{local_path}")
                    matched += 1
                else:
                    search_lidarr_and_download(artist, track_title, processed_artists)

            safe_filename = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_") + ".m3u"
            out_path = os.path.join(PLAYLIST_DIR, safe_filename)
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(m3u_lines) + "\n")

            print(f"Written: {safe_filename} ({matched}/{len(tracks)} local tracks matched)")

    except Exception as e:
        print(f"Sync error: {e}")

if __name__ == "__main__":
    while True:
        print("\n=== Starting ListenBrainz Playlist Sync ===")
        fetch_and_build_playlists()
        print("=== Sync Complete. Sleeping for 6 hours... ===\n")
        time.sleep(21600)
