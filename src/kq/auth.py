"""Authentication for Azure Data Explorer."""

import os
import sys
from datetime import datetime

from azure.identity import (
    AzureCliCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    TokenCachePersistenceOptions,
)


def get_persistent_cache():
    """Get token cache for 90-day refresh token persistence."""
    return TokenCachePersistenceOptions(
        name="kq-cache",
        allow_unencrypted_storage=True  # Required on Linux without keyring
    )


def get_credential(use_device_code=False, quiet=False):
    """
    Get Azure credential in priority order:
    1. Service Principal (for automation)
    2. Azure CLI (for users who ran 'az login')
    3. Device code (for WSL/headless)
    """
    # 1. Service Principal (automation)
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    if all([client_id, client_secret, tenant_id]):
        if not quiet:
            print("Using service principal authentication", file=sys.stderr)
        return ClientSecretCredential(tenant_id, client_id, client_secret)

    # 2. Azure CLI
    if not use_device_code:
        try:
            cred = AzureCliCredential()
            cred.get_token("https://kusto.kusto.windows.net/.default")
            if not quiet:
                print("Using Azure CLI authentication", file=sys.stderr)
            return cred
        except Exception:
            pass

    # 3. Device code (with persistent cache)
    def prompt_callback(url, code, expires_on):
        print(f"\n  To sign in, open: {url}")
        print(f"  Enter the code:   {code}")
        print(f"  (expires: {expires_on})\n", flush=True)

    if not quiet:
        print("Using device code authentication", file=sys.stderr)

    return DeviceCodeCredential(
        cache_persistence_options=get_persistent_cache(),
        prompt_callback=prompt_callback
    )


def login(cluster_url: str, device_code=False):
    """Authenticate to ADX and cache tokens."""
    print(f"Authenticating to {cluster_url}...")

    try:
        credential = get_credential(use_device_code=device_code, quiet=True)
        token = credential.get_token("https://kusto.kusto.windows.net/.default")

        # Normalize expiry (could be datetime or int timestamp)
        if hasattr(token.expires_on, "isoformat"):
            expires = token.expires_on.isoformat()
        elif isinstance(token.expires_on, int):
            expires = datetime.fromtimestamp(token.expires_on).isoformat()
        else:
            expires = str(token.expires_on)

        print(f"\nAuthentication successful!")
        print(f"  Expires: {expires}")
        print(f"  Tokens cached for ~90 days")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}", file=sys.stderr)
        return False


def status(cluster_url: str = None):
    """Check authentication status."""
    if cluster_url:
        print(f"Cluster: {cluster_url}")

    try:
        credential = get_credential(quiet=True)
        credential.get_token("https://kusto.kusto.windows.net/.default")
        print("Status: Authenticated")
        return True
    except Exception:
        print("Status: Not authenticated")
        print("Run: kq auth login")
        return False
