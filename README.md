# Raspberry Pi Navidrome & Automated Music Stack

A full-featured, containerized music server ecosystem optimized for a Raspberry Pi or single-board computer running Docker. This stack automates music streaming, downloading, metadata management, AI recommendation enrichment, and playlist synchronization.

---

## Features & Included Services

* **[Navidrome](https://www.navidrome.org/)** (`:4533`): Lightweight, high-performance music server and streamer compatible with Subsonic apps.
* **[Lidarr](https://lidarr.audio/)** (`:8686`): Automated music library manager and downloader.
* **[Prowlarr](https://prowlarr.com/)** (`:9696`): Indexer proxy and manager for the *Arr stack.
* **[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)** (`:8191`): Cloudflare bypass proxy for web scraping and indexers.
* **[slskd](https://github.com/slskd/slskd)** (`:5030`): Web-based Soulseek client for direct P2P music downloads.
* **[MusicBrainz Picard](https://picard.musicbrainz.org/)** (`:5800`): Web GUI for manual and automated audio tagging.
* **[Czkawka](https://github.com/qarmin/czkawka)** (`:5801`): Web UI tool to scan and remove duplicate audio files.
* **AudioMuse-AI Stack** (`:8000`): Self-hosted AI music discovery/recommendation engine backed by PostgreSQL and Redis.
* **ListenBrainz Sync**: Custom daemon script that syncs user "Created For" playlists from ListenBrainz into local `.m3u` format and automatically requests missing artists via Lidarr.

---

## Directory Structure

Ensure the following local structure exists or update the paths in `docker-compose.yml` to match your storage setup:

```text
.
├── docker-compose.yml
├── lb-m3u-sync/
│   ├── Dockerfile
│   └── sync.py
├── data/                  # Navidrome database & cache
├── plugins/               # Navidrome plugins
├── lidarr-config/         # Lidarr configuration
├── prowlarr-config/       # Prowlarr configuration
├── slskd-config/          # slskd appdata
├── picard-config/         # Picard configuration
├── czkawka-config/        # Czkawka configuration
├── audiomuse-redis-data/  # Redis database files
└── audiomuse-postgres-data/ # Postgres database files

```

External storage mounts (e.g., SSD mounted at `/mnt/music_ssd`):

* `/mnt/music_ssd/Music`: Primary music library.
* `/mnt/music_ssd/Music/Playlists`: Generated `.m3u` playlists.
* `/mnt/music_ssd/Music/blackhole`: Watch folder for automated downloads.

---

## Prerequisites

* **OS:** Raspberry Pi OS 64-bit, Ubuntu, or any Debian-based distribution.
* **Docker & Docker Compose v2:** Installed and running.
* **Storage:** External SSD formatted as `ext4` or `exFAT` recommended for library storage.

---

## Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

```


2. **Configure Environment Variables:**
Open `docker-compose.yml` and update all placeholders matching `YOUR_*_HERE`:
* `ND_LASTFM_APIKEY` / `ND_LASTFM_SECRET`: Last.fm API keys for artist metadata.
* `SLSKD_USERNAME` / `SLSKD_PASSWORD`: Admin login for slskd web interface.
* `SLSKD_SLSK_USERNAME` / `SLSKD_SLSK_PASSWORD`: Soulseek network account credentials.
* `POSTGRES_USER` / `POSTGRES_PASSWORD`: Database credentials for AudioMuse-AI.
* `LISTENBRAINZ_USERNAME`: ListenBrainz profile handle to pull playlists from.
* `LIDARR_API_KEY`: API key generated inside Lidarr (*Settings -> General -> API Key*).


3. **Set permissions:**
Ensure user ID `1000:1000` owns the mounted directories:
```bash
sudo chown -R 1000:1000 /mnt/music_ssd/Music ./data ./plugins

```


4. **Build and start containers:**
```bash
docker compose up -d --build

```



---

## Port Map Summary

| Service | Port | Description |
| --- | --- | --- |
| **Navidrome** | `4533` | Music Web Interface & Subsonic API |
| **Lidarr** | `8686` | Music Automation & Monitoring |
| **Prowlarr** | `9696` | Torrent/Usenet Indexer Manager |
| **FlareSolverr** | `8191` | Cloudflare Bypass Service |
| **slskd** | `5030` | Soulseek Web Client |
| **MusicBrainz Picard** | `5800` | Browser GUI for Music Tagging |
| **Czkawka** | `5801` | Browser GUI for Duplicate Cleaning |
| **AudioMuse-AI** | `8000` | AI Recommendation Service |

---

## ListenBrainz Sync Service (`lb-m3u-sync`)

The included sync container runs a loop every 6 hours:

1. Fetches personalized "Created For" playlists from the ListenBrainz API.
2. Checks local storage for matching track files.
3. Generates relative `.m3u` files in `/playlists` for Navidrome to load.
4. If a track is missing locally, it pushes the artist to **Lidarr** via REST API to search and download automatically.

---

## Troubleshooting & Maintenance

* **Check Logs:**
```bash
docker compose logs -f [service_name]

```


* **Force Navidrome Rescan:**
Log into Navidrome, navigate to **Settings**, and trigger a **Quick Scan** or **Full Scan**.
* **Lidarr API Key Location:**
Retrieve or regenerate via `http://<PI_IP>:8686` -> *Settings* -> *General* -> *API Key*.
