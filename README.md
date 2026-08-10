```markdown
# Media & Automation Stack

This Docker Compose setup deploys a self-hosted media server and automation pipeline for music management, indexing, downloading, tagging, deduplication, AI features, and playlist synchronization.

---

## Architecture Overview


```

```
                  ┌─────────────────────────────────┐
                  │    /mnt/music_ssd/Music         │
                  └────────────────┬────────────────┘
                                   │
 ┌───────────────────┬─────────────┼─────────────┬───────────────────┐
 ▼                   ▼             ▼             ▼                   ▼

```

┌───────────┐      ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐
│ Navidrome │      │  Lidarr   │  │qBittorrent│  │   slskd   │  │ ListenBrainz Sync │
└─────┬─────┘      └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └───────────────────┘
│                  │              │              │
▼                  ▼              │              │
┌───────────┐      ┌───────────┐        │              │
│ AudioMuse │      │ Prowlarr  │◄───────┴──────────────┘
└───────────┘      └─────┬─────┘
│
▼
┌───────────┐
│FlareSolve │
└───────────┘

```

---

## Services & Ports

| Container | Service | Host Port | Internal Port | Description |
| :--- | :--- | :--- | :--- | :--- |
| `navidrome` | Navidrome | `4533` | `4533` | Music server & Subsonic API |
| `lidarr` | Lidarr | `8686` | `8686` | Music management & automation |
| `prowlarr` | Prowlarr | `9696` | `9696` | Indexer manager for Arrs |
| `qbittorrent` | qBittorrent | `8080`, `6881` | `8080`, `6881` | Torrent client (Web UI & BitTorrent) |
| `flaresolverr` | FlareSolverr | `8191` | `8191` | Cloudflare bypass proxy for indexers |
| `slskd` | slskd | `5030`, `5031`, `2242` | `5030`, `5031`, `2242` | Soulseek daemon & Web UI |
| `picard` | MusicBrainz Picard | `5800` | `5800` | GUI music tagger (Web UI via VNC) |
| `czkawka` | Czkawka | `5801` | `5800` | Duplicate file finder (Web UI via VNC) |
| `audiomuse-ai-flask` | AudioMuse AI | `8000` | `8000` | AI-driven music analysis API |
| `audiomuse-ai-worker` | AudioMuse Worker | N/A | N/A | Background processing for AudioMuse |
| `audiomuse-redis` | Redis | Dynamic | `6379` | Queue broker for AudioMuse |
| `audiomuse-postgres` | PostgreSQL | Dynamic | `5432` | Database for AudioMuse |
| `listenbrainz-sync` | LB Sync | N/A | N/A | Synchronizes ListenBrainz to M3U |

---

## Shared Volumes & Storage Layout

All applications operate on a shared host volume (`/mnt/music_ssd/Music`) to prevent cross-filesystem copies and facilitate hardlinking across services.


```

/mnt/music_ssd/Music/
├── Playlists/          # Exported M3U/M3U8 playlists
├── blackhole/          # Drop directory for automatic import
└── [Artist]/[Album]/   # Main structured music directory

```

---

## Prerequisites & Installation

### 1. Create Local Directory Structure

Run the following command to ensure all bound host paths exist before starting containers:

```bash
mkdir -p /mnt/music_ssd/Music/blackhole /mnt/music_ssd/Music/Playlists \
         data plugins lidarr-config prowlarr-config qbittorrent-config \
         slskd-config picard-config czkawka-config \
         audiomuse-redis-data audiomuse-postgres-data \
         audiomuse-temp-flask audiomuse-plugins-flask \
         audiomuse-temp-worker audiomuse-plugins-worker \
         lb-m3u-sync

```

### 2. Configure Environment Variables (`.env`)

Create a `.env` file in the same directory as `docker-compose.yml`:

```ini
# --- Navidrome ---
ND_LASTFM_APIKEY=1e201a94ea849c63137452060d954703
ND_LASTFM_SECRET=e03aa0e2c7dd85663a35d364abaeecd1

# --- slskd ---
SLSKD_USERNAME=pedram
SLSKD_PASSWORD=@BlackeyeS1
SLSKD_SLSK_USERNAME=pedram
SLSKD_SLSK_PASSWORD=@BlackeyeS1

# --- AudioMuse PostgreSQL ---
POSTGRES_USER=audiomuse
POSTGRES_PASSWORD=audiomusepassword
POSTGRES_DB=audiomusedb

# --- ListenBrainz Sync ---
LISTENBRAINZ_USERNAME=pedramibiza
LIDARR_API_KEY=e8cde872088441bf9286b8f5923e5967

```

---

## Operational Commands

### Launch the Stack

Build custom images (like `listenbrainz-sync`) and launch all containers in background mode:

```bash
docker compose up -d --build

```

### View Logs

Monitor logs across all services:

```bash
docker compose logs -f

```

Monitor logs for a specific service:

```bash
docker compose logs -f navidrome

```

### Restart a Service

```bash
docker compose restart lidarr

```

### Tear Down the Stack

Stop containers without destroying persistent volumes:

```bash
docker compose down

```

---

## Service Configuration Details

* **Navidrome**: Set to scan `/music` every hour (`1h`). Transcoding configuration enabled. Plugins enabled via `/data/plugins`.
* **slskd**: Pre-configured to output downloads directly into `/mnt/music_ssd/Music` and watch the `blackhole` folder.
* **ListenBrainz Sync**: Containerized python utility targeting local Lidarr and Navidrome APIs for automated playlist generation from ListenBrainz user data (`pedramibiza`).

```

```
