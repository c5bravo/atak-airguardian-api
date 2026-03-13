# ATAK Air&Marine Proxy

A secure REST API that tracks aircraft in real-time using Practice tool API and OpenSky Network data.

## What It Does

Fetches live aircraft data from Practice tool and OpenSky Network, the user filters for airspace, transforms coordinates to MGRS (Military Grid Reference System), and serves the data via secure API.

## How It Works

```
Data API  →  Filter "Finland" → Transform to MGRS  → FastAPI
(OAuth2)       (59.5-70°N)     (classifications)
```

1. **Task** gets data from Data API (OAuth2 auth)
2. **Filter** keeps only aircrafts over Finland (59.5-70°N, 19.5-31.5°E)
3. **Transform** converts GPS to MGRS + classifies altitude/speed in Finnish
4. **FastAPI** serves data via mTLS-secured HTTPS

---

## Quick Start - Docker (Recommended)

### Prerequisites

- Docker & Docker Compose
- OpenSky Network account (get credentials at https://opensky-network.org)

### Installation

#### 1. Clone repository

```bash
git clone <repo-url>
cd atak-airguardian-api
```

#### 2. Configure environment

```bash
cp .env.example .env.docker
nano .env.docker
```

###### Add your OpenSky credentials:

##### OPENSKY_CLIENT_SECRET=your-client-secret


### 3. Start services

##### Rebuild

```bash
docker compose up -d --build
```

##### Stop services

```bash
docker compose down
```

## Local Development - Poetry

##### pre-commit

Ensures quality by enabling pre-commit hooks

```console
pre-commit install --install-hooks
pre-commit run --all-files
```

##### Prerequisites

- Python 3.12+
- Poetry
- OpenSky credentials

##### Running Locally

**Terminal - API:**

```bash
poetry run python -m app.main
```

**Test:**

```bash
curl https://localhost:8002/radar/aircraft
```

---

## Data Format

### Transformed Endpoint: `/radar/aircraft`

```json
[
    {
        "aircraftId": "BNOK",
        "position": "34WDC65",
        "altitude": "high",
        "speed": "slow",
        "direction": 268,
        "details": "This aircraft[BNOK] from [Finland] and it is civilian aircraft.",
        "is_exit": false
    }
]
```

### MGRS Position Format

**Example:** `"35VML26"`

- `35V` = Grid Zone (UTM zone + latitude band)
- `ML` = 100km Square Identifier
- `26` = 10km precision (first 2 digits of easting)

### Classifications (Finnish)

**Altitude:**
| Finnish | Range | English |
|---------|-------|---------|
| `pinnassa` | < 300m | At surface |
| `matalalla` | 300-3000m | Low altitude |
| `korkealla` | > 3000m | High altitude |

**Velocity:**
| Finnish | Range | English |
|---------|-------|---------|
| `hidas` | < 140 m/s | Slow |
| `nopea` | 140-280 m/s | Fast |
| `erittäin nopea` | > 280 m/s | Very fast |

---

## Configuration

### Required Environment Variables

```bash
# DATA API Configuration

DATA_API_URL=

or

# OpenSky API Configuration

OPENSKY_API_URL=your_opensky_api_url
OPENSKY_TOKEN_URL=your_opensky_token_url

OPENSKY_CLIENT_ID=your_opensky_client_id
OPENSKY_CLIENT_SECRET=your_opensky_client_secret

# Finland Bounding Box for Example

LAT_MIN=59.5
LAT_MAX=70.0
LON_MIN=19.5
LON_MAX=31.5

# API Server Configuration

API_HOST=your_api_host
API_PORT=your_api_port
```
---

### Certificate Errors

```bash
docker compose down

docker compose up --build
```

### View Logs

```bash
# All services
docker compose logs -f

```
---

## Security

- **OAuth2**: Secure API access
- Keep `credentials.json` and `.env` files private

---
