"""Authentication for Azure Data Explorer."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Suppress noisy azure-identity credential chain warnings
logging.getLogger("azure.identity").setLevel(logging.ERROR)

from azure.identity import (
    AzureCliCredential,
    AuthenticationRecord,
    ClientSecretCredential,
    DeviceCodeCredential,
    TokenCachePersistenceOptions,
)

# Kusto scope
KUSTO_SCOPE = "https://kusto.kusto.windows.net/.default"

# Persistent auth record path — allows silent token refresh without re-prompting
AUTH_RECORD_PATH = Path.home() / ".config" / "kq" / "auth_record.json"


def get_persistent_cache():
    """Get token cache for 90-day refresh token persistence."""
    return TokenCachePersistenceOptions(
        name="kq-cache",
        allow_unencrypted_storage=True  # Required on Linux without keyring
    )


def _load_auth_record():
    """Load saved authentication record if it exists."""
    if AUTH_RECORD_PATH.exists():
        try:
            return AuthenticationRecord.deserialize(AUTH_RECORD_PATH.read_text())
        except Exception:
            pass
    return None


def _save_auth_record(record):
    """Save authentication record for future silent auth."""
    AUTH_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_RECORD_PATH.write_text(record.serialize())


def get_credential(use_device_code=False, quiet=False):
    """
    Get Azure credential in priority order:
    1. Service Principal (for automation)
    2. Azure CLI (for users who ran 'az login')
    3. Device code with cached auth record (for WSL/headless)
    """
    # 1. Service Principal (automation)
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    if all([client_id, client_secret, tenant_id]):
        if not quiet:
            print("Using service principal authentication", file=sys.stderr)
        return ClientSecretCredential(tenant_id, client_id, client_secret)

    # 2. Azure CLI (skip entirely if az not on PATH)
    if not use_device_code:
        import shutil
        if shutil.which("az"):
            try:
                cred = AzureCliCredential()
                cred.get_token(KUSTO_SCOPE)
                if not quiet:
                    print("Using Azure CLI authentication", file=sys.stderr)
                return cred
            except Exception:
                pass

    # 3. Device code with persistent cache and auth record
    cache = get_persistent_cache()
    auth_record = _load_auth_record()

    if auth_record:
        # Have a saved auth record — create credential that can silently refresh
        if not quiet:
            print("Using cached authentication", file=sys.stderr)
        return DeviceCodeCredential(
            authentication_record=auth_record,
            cache_persistence_options=cache,
            disable_automatic_authentication=True,
        )
    else:
        # No auth record — need interactive device code flow
        def prompt_callback(url, code, expires_on):
            print(f"\n  To sign in, open: {url}")
            print(f"  Enter the code:   {code}")
            print(f"  (expires: {expires_on})\n", flush=True)

        if not quiet:
            print("Device code authentication required", file=sys.stderr)

        return DeviceCodeCredential(
            cache_persistence_options=cache,
            prompt_callback=prompt_callback,
        )


def login(cluster_url: str, device_code=False):
    """Authenticate to ADX and cache tokens."""
    print(f"Authenticating to {cluster_url}...")

    def prompt_callback(url, code, expires_on):
        print(f"\n  To sign in, open: {url}")
        print(f"  Enter the code:   {code}")
        print(f"  (expires: {expires_on})\n", flush=True)

    cache = get_persistent_cache()
    credential = DeviceCodeCredential(
        cache_persistence_options=cache,
        prompt_callback=prompt_callback,
    )

    try:
        record = credential.authenticate(scopes=[KUSTO_SCOPE])
        _save_auth_record(record)

        token = credential.get_token(KUSTO_SCOPE)

        if hasattr(token.expires_on, "isoformat"):
            expires = token.expires_on.isoformat()
        elif isinstance(token.expires_on, int):
            expires = datetime.fromtimestamp(token.expires_on).isoformat()
        else:
            expires = str(token.expires_on)

        print(f"\nAuthentication successful!")
        print(f"  Expires: {expires}")
        print(f"  Auth record saved to {AUTH_RECORD_PATH}")
        print(f"  Subsequent queries will authenticate silently")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}", file=sys.stderr)
        return False


def status(cluster_url: str = None):
    """Check authentication status."""
    if cluster_url:
        print(f"Cluster: {cluster_url}")

    auth_record = _load_auth_record()
    if auth_record:
        print(f"Auth record: {AUTH_RECORD_PATH}")
        print(f"  Username: {auth_record.username}")
    else:
        print("No auth record found. Run: kq auth login")
        return False

    try:
        credential = get_credential(quiet=True)
        credential.get_token(KUSTO_SCOPE)
        print("Status: Authenticated (token valid)")
        return True
    except Exception:
        print("Status: Token expired. Run: kq auth login")
        return False
