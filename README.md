# ATAK Air Guardian API 🛩️

A secure REST API that tracks aircraft over Finland in real-time using OpenSky Network data with mTLS authentication.

## What It Does

Fetches live aircraft data from OpenSky Network every 30 seconds, filters for Finnish airspace, transforms coordinates to MGRS (Military Grid Reference System), and serves the data via a secure API.

## How It Works

```
OpenSky API → Celery Worker → Filter Finland → Transform to MGRS → Redis → FastAPI → Client
   (OAuth2)      (every 30s)    (59.5-70°N)      (classifications)  (cache)  (mTLS)
```

1. **Celery Beat** triggers data fetch every 30 seconds
2. **Celery Worker** gets data from OpenSky API (OAuth2 auth)
3. **Filter** keeps only aircraft over Finland (59.5-70°N, 19.5-31.5°E)
4. **Transform** converts GPS to MGRS + classifies altitude/speed in Finnish
5. **Redis** stores processed data with SSL/TLS
6. **FastAPI** serves data via mTLS-secured HTTPS

---

## 🚀 Quick Start - Docker (Recommended)

### Prerequisites
- Docker & Docker Compose
- OpenSky Network account (get credentials at https://opensky-network.org)

### Installation

## 1. Clone repository
```bash
git clone <repo-url>
cd atak-airguardian-api
```

## 2. Configure environment
cp .env.example .env.docker
nano .env.docker
# Add your OpenSky credentials:
# OPENSKY_CLIENT_ID=your-client-id
# OPENSKY_CLIENT_SECRET=your-client-secret

## 3. Poetry install
```bash
curl -sSL https://install.python-poetry.org/ | python3 -
or
```
```bash
echo 'export PATH="/home/user/.local/bin:$PATH"' >> ~/.zshrc
```

```bash
poetry install
poetry lock
```

## 4. Generate certificates
```bash
./setup.sh
```



## 5. Start services
### Rebuild
```bash
docker compose up -d --build
```

### Stop services
```bash
docker compose down
```

### Restart service
```bash
docker compose restart celery-worker
```

## 6. Test
curl --cacert certs/ca.crt \
     --cert certs/client.crt \
     --key certs/client.key \
     https://localhost:8002/radar/aircraft

---

## 💻 Local Development - Poetry

### Prerequisites
- Python 3.12+
- Poetry
- Redis 7.0+
- OpenSky credentials

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd atak-airguardian-api

# 2. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. Install dependencies
poetry install --no-root

# 4. Install Redis
sudo apt-get install -y redis-server

# 5. Configure environment
cp .env.example .env
nano .env
# Update:
# REDIS_HOST=localhost
# OPENSKY_CLIENT_ID=your-client-id
# OPENSKY_CLIENT_SECRET=your-client-secret

# 6. Generate certificates
chmod +x setup.sh
./setup.sh
```

### Running Locally (4 terminals)

**Terminal 1 - Redis:**
```bash
redis-server --port 0 --tls-port 6381 \
  --tls-cert-file certs/redis.crt \
  --tls-key-file certs/redis.key \
  --tls-ca-cert-file certs/ca.crt \
  --tls-auth-clients no
```

**Terminal 2 - Celery Worker:**
```bash
poetry run celery -A app.celery_app worker --loglevel=info --concurrency=4
```

**Terminal 3 - Celery Beat:**
```bash
poetry run celery -A app.celery_app beat --loglevel=info
```

**Terminal 4 - API:**
```bash
poetry run python -m app.main
```

**Test:**
```bash
curl --cacert certs/ca.crt \
     --cert certs/client.crt \
     --key certs/client.key \
     https://localhost:8002/radar/aircraft
```

---

## 📊 Data Format

### Transformed Endpoint: `/radar/aircraft`

```json
{
  "aircraft_count": 15,
  "timestamp": "03.11.2025 10:30:45",
  "aircraft": [
    {
      "icao24": "4aca8d",
      "callsign": "FIN123",
      "origin_country": "Finland",
      "time_position": "03.11.2025 10:30:43",
      "last_contact": "03.11.2025 10:30:44",
      "position": "35VML26",
      "altitude": "korkealla",
      "velocity": "nopea",
      "true_track": 253.3,
      "on_ground": false
    }
  ]
}
```

### Raw Endpoint: `/radar/aircraft/raw`

```json
{
  "aircraft_count": 15,
  "timestamp": 1730628645,
  "aircraft": [
    {
      "icao24": "4aca8d",
      "callsign": "FIN123",
      "origin_country": "Finland",
      "time_position": 1730628643,
      "last_contact": 1730628644,
      "longitude": 24.9384,
      "latitude": 60.1699,
      "baro_altitude": 10668,
      "velocity": 231.5,
      "true_track": 253.3,
      "on_ground": false
    }
  ]
}
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

## 🔧 Configuration

### Required Environment Variables

```bash
# Redis Configuration
#####################################
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_DB=your_redis_db

# Celery Configuration
#####################################
CELERY_BROKER_URL=your_celery_broker_url
CELERY_RESULT_BACKEND=your_celery_result_backend

# OpenSky API Configuration
#####################################
OPENSKY_API_URL=your_opensky_api_url
OPENSKY_TOKEN_URL=your_opensky_token_url
OPENSKY_CLIENT_ID=your_opensky_client_id
OPENSKY_CLIENT_SECRET=your_opensky_client_secret

# Finland Bounding Box
#####################################
FINLAND_LAT_MIN=59.5
FINLAND_LAT_MAX=70.0
FINLAND_LON_MIN=19.5
FINLAND_LON_MAX=31.5

# API Server Configuration
#####################################
API_HOST=your_api_host
API_PORT=your_api_port

# mTLS Configuration
#####################################
MTLS_ENABLED=your_mtls_enabled
MTLS_CA_CERT=your_mtls_ca_cert_path
MTLS_SERVER_CERT=your_mtls_server_cert_path
MTLS_SERVER_KEY=your_mtls_server_key_path
MTLS_CLIENT_CERT=your_mtls_client_cert_path
MTLS_CLIENT_KEY=your_mtls_client_key_path
```

---

## 🔌 API Usage

### cURL
```bash
curl --cacert certs/ca.crt \
     --cert certs/client.crt \
     --key certs/client.key \
     https://localhost:8002/radar/aircraft
```

### Python
```python
import httpx

response = httpx.get(
    'https://localhost:8002/radar/aircraft',
    verify='certs/ca.crt',
    cert=('certs/client.crt', 'certs/client.key')
)
print(response.json())
```

### Postman
1. Settings → Certificates → Add Certificate
2. Host: `localhost:8002`
3. PFX file: `certs/client.p12`
4. Passphrase: `atak2024`

---

## 🛠️ Troubleshooting

### Empty Aircraft Data
```bash
# Wait 30 seconds for first fetch, or manually trigger:
docker compose exec celery-worker celery -A app.celery_app call app.tasks.radar_task.fetch_aircraft_data

# Check worker logs:
docker compose logs celery-worker
```

### Certificate Errors
```bash
# Regenerate certificates:
rm -rf certs
./setup.sh
docker compose down
docker compose up --build
```

### Redis Connection Issues
```bash
# Check Redis:
docker compose ps redis
docker compose logs redis

# Test connection:
docker compose exec redis redis-cli --tls --cacert /certs/ca.crt -p 6381 ping
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f celery-worker
```

---

## 🔐 Security

- **mTLS**: Client + server certificate authentication
- **Redis SSL/TLS**: Encrypted connections
- **OAuth2**: Secure OpenSky API access
- Keep `credentials.json` and `.env` files private

---
