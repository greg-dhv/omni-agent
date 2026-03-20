"""
One-time script to get Google OAuth refresh token for Ads + Search Console.

Usage:
1. Fill in your CLIENT_ID and CLIENT_SECRET below
2. Run: python get_refresh_token.py
3. Browser opens, authorize both Google Ads AND Search Console access
4. Copy the refresh_token to your .env file
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# Fill these in from Google Cloud Console
CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# Scopes for both Google Ads and Search Console
SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

def main():
    # Create OAuth flow
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    # Run local server to handle OAuth callback
    credentials = flow.run_local_server(
        port=8080,
        prompt="consent",
        access_type="offline"  # This ensures we get a refresh token
    )

    print("\n" + "=" * 60)
    print("SUCCESS! Add these to your .env file:")
    print("=" * 60)
    print(f"\n# This token works for BOTH Google Ads and Search Console")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"GSC_REFRESH_TOKEN={credentials.refresh_token}")
    print("\n# Also add your Search Console site URL:")
    print("GSC_SITE_URL=sc-domain:yourdomain.com")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
