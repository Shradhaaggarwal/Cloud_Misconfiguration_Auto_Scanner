# scanner/inventory_extensions.py
"""
Inventory helpers for additional Azure resource types.

This file provides:
- list_key_vaults(azure_credentials=None) -> List[dict]
- list_app_services(azure_credentials=None) -> List[dict]

Behavior:
- If the Azure SDK (and credentials) are available, it will attempt to use the
  Azure management clients to list real resources and return them as plain dicts
  (so the checks can read .get('properties') etc like your other inventory functions).
- If the SDK is not available or an error occurs, it returns an empty list so
  the scanner remains safe to run in mock/test mode.
"""

from typing import List, Dict
import os
import traceback

# Try to import Azure SDK. If not available, will fallback to mock-empty implementation.
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.keyvault import KeyVaultManagementClient
    from azure.mgmt.web import WebSiteManagementClient
    AZURE_SDK_AVAILABLE = True
except Exception:
    AZURE_SDK_AVAILABLE = False


def _to_dict(obj):
    """Simple helper: convert SDK objects to dict if needed; try .as_dict() then __dict__ fallback."""
    try:
        return obj.as_dict()
    except Exception:
        try:
            return dict(obj.__dict__)
        except Exception:
            return {}


def list_key_vaults(azure_credentials: Dict = None) -> List[Dict]:
    """
    Return a list of Key Vault resource dicts.

    azure_credentials: optional dict if you want to pass custom credential info.
    If None, DefaultAzureCredential() is used.

    Returned shape mirrors azure SDK .as_dict() output; the checks look at:
      item.get('properties', {}).get('enableSoftDelete') etc.
    """
    if not AZURE_SDK_AVAILABLE:
        # SDK missing: safe fallback for local/mock testing
        return []

    try:
        cred = None
        if azure_credentials and isinstance(azure_credentials, dict):
            # Note: For most flows DefaultAzureCredential is recommended. This branch
            # is left for custom credential wiring (client id/secret) if desired.
            cred = DefaultAzureCredential()
        else:
            cred = DefaultAzureCredential()

        subscription_id = azure_credentials.get("subscription_id") if azure_credentials else os.environ.get("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            # If subscription id is missing, return empty so code remains safe.
            return []

        client = KeyVaultManagementClient(credential=cred, subscription_id=subscription_id)

        items = []
        for v in client.vaults.list_by_subscription():
            items.append(_to_dict(v))
        return items

    except Exception:
        # Very important: don't raise here; return empty list so run_scan stays robust.
        traceback.print_exc()
        return []


def list_app_services(azure_credentials: Dict = None) -> List[Dict]:
    """
    Return a list of App Services (web apps + function apps) resource dicts.

    The checks expect to find settings under:
      app.get('properties', {}).get('siteConfig', {}).get('appSettings') 
    or similar shapes — this function returns the SDK objects converted to dicts.
    """
    if not AZURE_SDK_AVAILABLE:
        return []

    try:
        cred = DefaultAzureCredential()
        subscription_id = azure_credentials.get("subscription_id") if azure_credentials else os.environ.get("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            return []

        web_client = WebSiteManagementClient(credential=cred, subscription_id=subscription_id)

        # enumerate by subscription: this returns top-level Web Apps (includes Function Apps)
        items = []
        for site in web_client.web_apps.list():
            # fetch full site config including app settings if available
            try:
                site_dict = _to_dict(site)
                # attempt to get app settings: list_application_settings returns object
                app_settings = web_client.web_apps.list_application_settings(site.resource_group, site.name)
                site_dict.setdefault('properties', {})['siteConfig'] = site_dict.get('properties', {}).get('siteConfig', {}) or {}
                # app_settings is a SiteConfigResourceEnvelope-like object, convert to dict
                try:
                    settings_dict = app_settings.properties or app_settings.as_dict().get('properties')
                except Exception:
                    settings_dict = app_settings.as_dict() if hasattr(app_settings, "as_dict") else {}
                # Normalize app settings to shape your checks expect:
                # some code expects list of {'name':..., 'value':...}, some expects dict
                if isinstance(settings_dict, dict) and settings_dict.get('app_settings') is None:
                    # The azure SDK 'list_application_settings' returns a dict of key->value under properties.properties
                    # We keep it as a dict here so checks cope with either dict or list.
                    site_dict['properties']['siteConfig']['appSettings'] = settings_dict.get('properties') or settings_dict
                else:
                    site_dict['properties']['siteConfig']['appSettings'] = settings_dict
            except Exception:
                # If fetching app settings fails, still return site with minimal info
                pass
            items.append(site_dict)
        return items

    except Exception:
        traceback.print_exc()
        return []


# Optional helper to support easy local mocking for unit tests
def list_key_vaults_mock() -> List[Dict]:
    """Return a couple of mock Key Vault dicts for quick testing."""
    return [
        {
            "id": "/subscriptions/0000/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/kv1",
            "name": "kv1",
            "properties": {
                "enableSoftDelete": False,
                "enablePurgeProtection": False,
                "accessPolicies": [
                    {"displayName": "AllUsers", "tenantId": "xxxx", "objectId": "all"}
                ],
            },
        }
    ]


def list_app_services_mock() -> List[Dict]:
    """Return a couple of mock App Service dicts for quick testing of secret detection."""
    return [
        {
            "id": "/subscriptions/0000/resourceGroups/rg1/providers/Microsoft.Web/sites/app1",
            "name": "app1",
            "properties": {
                "siteConfig": {
                    "appSettings": [
                        {"name": "DATABASE_PASSWORD", "value": "s3cr3t_pass_here"},
                        {"name": "SOME_FLAG", "value": "true"},
                    ]
                }
            },
        }
    ]
