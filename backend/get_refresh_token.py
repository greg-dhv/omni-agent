"""
One-time script to get Google Ads OAuth refresh token.

Usage:
1. Fill in your CLIENT_ID and CLIENT_SECRET below
2. Run: python get_refresh_token.py
3. Open the URL in browser, authorize, paste the code
4. Copy the refresh_token to your .env file
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# Fill these in from Google Cloud Console
CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# Google Ads API scope
SCOPES = ["https://www.googleapis.com/auth/adwords"]

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

    print("\n" + "=" * 50)
    print("SUCCESS! Copy this refresh token to your .env file:")
    print("=" * 50)
    print(f"\nGOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
