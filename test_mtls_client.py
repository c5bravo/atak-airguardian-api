# test_mtls_client.py
import httpx
from app.config import settings


def test_mtls_connection():
    """Test mTLS connection to the API"""

    if not settings.mtls_enabled:
        print("⚠️  mTLS is not enabled in settings")
        return

    url = f"https://{settings.api_host}:{settings.api_port}/radar/aircraft"

    try:
        with httpx.Client(
            verify=settings.mtls_ca_cert,
            cert=(settings.mtls_client_cert, settings.mtls_client_key),
            timeout=10.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            print("✅ mTLS connection successful!")
            print(f"Response: {response.json()}")
    except httpx.RequestError as e:
        print(f"❌ Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_mtls_connection()
