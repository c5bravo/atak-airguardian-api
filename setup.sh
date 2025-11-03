#!/bin/bash
# setup.sh - Setup script for ATAK Air Guardian API

set -e

echo "🚀 ATAK Air Guardian API - Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Run ./install_docker_ubuntu.sh first"
    exit 1
fi

echo "✅ Docker is installed"

# Check .env.docker
if [ ! -f ".env.docker" ]; then
    echo "⚠️  .env.docker file not found!"
    echo "Please create .env.docker file with your configuration"
    exit 1
fi

echo "✅ .env.docker file found"

# Generate certs
if [ ! -d "certs" ] || [ ! -f "certs/ca.crt" ]; then
    echo ""
    echo "📜 Generating mTLS certificates..."
    mkdir -p certs

    # Root CA
    echo "  → Generating Root CA..."
    openssl req -x509 -new -nodes -keyout certs/ca.key -out certs/ca.crt -days 365 \
      -subj "/C=FI/ST=Uusimaa/L=Helsinki/O=ATAKAirGuardian/CN=ATAKAirGuardianCA" 2>/dev/null

    # Server certificate (for API)
    echo "  → Generating Server Certificate..."
    cat > certs/server.cnf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = FI
ST = Uusimaa
L = Helsinki
O = ATAKAirGuardian
CN = api

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = api
DNS.2 = localhost
DNS.3 = atak-api
IP.1 = 127.0.0.1
EOF

    openssl genrsa -out certs/server.key 2048 2>/dev/null
    openssl req -new -key certs/server.key -out certs/server.csr -config certs/server.cnf 2>/dev/null
    openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key \
      -CAcreateserial -out certs/server.crt -days 365 -extensions v3_req -extfile certs/server.cnf 2>/dev/null

    # Client certificate
    echo "  → Generating Client Certificate..."
    openssl genrsa -out certs/client.key 2048 2>/dev/null
    openssl req -new -key certs/client.key -out certs/client.csr \
      -subj "/C=FI/ST=Uusimaa/L=Helsinki/O=ATAKAirGuardian/CN=atak-client" 2>/dev/null
    openssl x509 -req -in certs/client.csr -CA certs/ca.crt -CAkey certs/ca.key \
      -CAcreateserial -out certs/client.crt -days 365 2>/dev/null

    # Redis certificate (with proper SAN)
    echo "  → Generating Redis Certificate..."
    cat > certs/redis.cnf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = FI
ST = Uusimaa
L = Helsinki
O = ATAKAirGuardian
CN = redis

[v3_req]
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = redis
DNS.2 = localhost
DNS.3 = atak-redis
IP.1 = 127.0.0.1
EOF

    openssl genrsa -out certs/redis.key 2048 2>/dev/null
    openssl req -new -key certs/redis.key -out certs/redis.csr -config certs/redis.cnf 2>/dev/null
    openssl x509 -req -in certs/redis.csr -CA certs/ca.crt -CAkey certs/ca.key \
      -CAcreateserial -out certs/redis.crt -days 365 -extensions v3_req -extfile certs/redis.cnf 2>/dev/null

    # Create PKCS12 for Postman
    echo "  → Creating PKCS12 certificate for Postman..."
    openssl pkcs12 -export -out certs/client.p12 \
      -inkey certs/client.key \
      -in certs/client.crt \
      -certfile certs/ca.crt \
      -password pass:atak2024 2>/dev/null

    # Cleanup
    rm -f certs/*.csr certs/*.srl certs/*.cnf

    # Set proper permissions
    chmod 644 certs/*.crt certs/*.p12
    chmod 600 certs/*.key

    echo "✅ Certificates generated successfully"
else
    echo "✅ Certificates already exist"
fi

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Review .env.docker configuration"
echo "  2. Start services: docker compose up -d --build"
echo "  3. View logs: docker compose logs -f"
echo "  4. Check status: docker compose ps"
echo ""
echo "Test the API:"
echo "  curl --cacert certs/ca.crt \\"
echo "       --cert certs/client.crt \\"
echo "       --key certs/client.key \\"
echo "       https://localhost:8002/radar/aircraft"
echo ""
echo "For Postman:"
echo "  - Import certificate: certs/client.p12"
echo "  - Password: atak2024"
echo ""