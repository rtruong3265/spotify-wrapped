import base64
import json
import requests
import urllib.parse
from .config import CLIENT_ID, CLIENT_SECRET


class SpotifyAPI:
    def __init__(self):
        # Client information
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/userauth"
        self.scope = ("user-library-read playlist-read-private user-top-read "
                      "playlist-read-collaborative user-read-playback-position "
                      "user-top-read user-read-recently-played")
        self.refresh_token = None  # Set your refresh token if you already have one
        self.access_token = None
        self.auth_string = f"{self.client_id}:{self.client_secret}"
        self.auth_base64 = base64.b64encode(self.auth_string.encode()).decode()

    def get_auth_url(self):
        """Generate and print the Spotify authorization URL."""
        url = "https://accounts.spotify.com/authorize"
        query = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        auth_url = f"{url}?{urllib.parse.urlencode(query)}"
        print("Go to the following URL to authorize:")
        print(auth_url)

    def get_access_token(self, auth_code):
        """Exchange authorization code for access token and refresh token."""
        url = "https://accounts.spotify.com/api/token"
        headers = {
            'Authorization': 'Basic ' + self.auth_base64,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response.status_code == 200:
            self.access_token = response_data.get("access_token")
            self.refresh_token = response_data.get("refresh_token")  # Ensure this is saved
            print("Tokens successfully retrieved!")
            return self.access_token
        else:
            print(f"Error: {response_data.get('error_description', 'Unknown error')}")
            if response_data.get("error") == "invalid_grant":
                print("Authorization code expired. Please reauthorize.")
            return None

    def get_auth_header(self):
        """Return authorization header."""
        if not self.access_token:
            print("No access token. Please authenticate first.")
            return None
        return {"Authorization": "Bearer " + self.access_token}

    def is_token_expired(self):
        """Ensure the access token is valid by refreshing it if necessary."""
        # Simulating token expiration behavior for testing
        if not self.access_token:
            print("Access token expired or missing. Refreshing...")
            self.refresh_access_token()

    def refresh_access_token(self):
        """Use the refresh token to get a new access token."""
        if not self.refresh_token:
            print("No refresh token available. Reauthorize the application.")
            self.get_auth_url()  # Prompt the user to reauthorize
            return None

        url = "https://accounts.spotify.com/api/token"
        headers = {
            'Authorization': 'Basic ' + self.auth_base64,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response.status_code == 200:
            self.access_token = response_data.get("access_token")
            print("Access token refreshed successfully!")
            return self.access_token
        else:
            print(f"Error refreshing token: {response_data.get('error_description', 'Unknown error')}")
            if response_data.get("error") == "invalid_grant":
                print("Refresh token expired. Please reauthorize.")
            return None

    @staticmethod
    def ms_to_min_sec(ms):
        """Helper function to convert milliseconds to minutes and seconds."""
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes} min {seconds} sec"

    def search_for_artist(self, artist_name):
        """Search for an artist by name."""
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"q={artist_name}&type=artist&limit=1"
        query_url = f"{url}?{query}"
        result = requests.get(query_url, headers=headers)
        json_result = result.json()["artists"]["items"]

        if len(json_result) == 0:
            #print("No artist with this name exists...")
            return None

        artist_info = json_result[0]
        return {
            "name": artist_info["name"],
            "id": artist_info["id"],
            "popularity": str(artist_info["popularity"]) + "/100",
            "followers": artist_info["followers"]["total"]
        }

    def search_for_song(self, song_name):
        """Search for a song by name."""
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"q={song_name}&type=track&limit=10"
        query_url = f"{url}?{query}"
        result = requests.get(query_url, headers=headers)
        json_result = result.json()["tracks"]["items"]

        if len(json_result) == 0:
            #print("No song with this name exists...")
            return None

        songs = []
        for track in json_result:
            track_info = {
                "name": track["name"],
                "album": track["album"]["name"],
                "artist": track["artists"][0]["name"],
                "release_date": track["album"]["release_date"],
                "duration": self.ms_to_min_sec(track["duration_ms"]),
                "popularity": str(track["popularity"]) + "/100",
                "preview_url": track["preview_url"] if track["preview_url"] else "No preview available"
            }
            songs.append(track_info)

        return songs

    def get_top_tracks_by_artist(self, artist_id):
        """Get top tracks by artist."""
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        headers = self.get_auth_header()
        params = {"market": "US"}
        result = requests.get(url, headers=headers, params=params)

        if result.status_code != 200:
            #print(f"Failed to get tracks: {result.status_code} - {result.text}")
            return []

        json_result = result.json()["tracks"]
        top_tracks = []

        for track in json_result:
            track_name = track.get("name", "Unknown Track")
            duration = self.ms_to_min_sec(track["duration_ms"])
            popularity = str(track["popularity"]) + "/100"
            preview_url = track.get("preview_url") if track.get("preview_url") else "No preview available"

            top_tracks.append({
                "name": track_name,
                "duration": duration,
                "popularity": popularity,
                "preview_url": preview_url
            })

        return top_tracks

    def get_user_playlists(self):
        """Get the user's playlists."""
        url = "https://api.spotify.com/v1/me/playlists"
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            #print(f"Failed to get playlists: {response.status_code} - {response.text}")
            return []

        playlists = response.json().get("items", [])
        return playlists
        #for playlist in playlists:
            #print(f"Playlist Name: {playlist['name']}, Tracks: {playlist['tracks']['total']}")

    def get_top_items(self, item_type, time_range, limit=50):
        """Fetch top items (tracks/artists) for a specified time range, including song previews."""
        url = f"https://api.spotify.com/v1/me/top/{item_type}"
        headers = self.get_auth_header()
        params = {
            "time_range": time_range,
            "limit": limit
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            #print(f"Failed to get top {item_type}: {response.status_code} - {response.text}")
            return []

        items = response.json().get("items", [])
        formatted_items = []

        for item in items:
            if item_type == "tracks":
                track_info = {
                    "name": item["name"],
                    "artist": item["artists"][0]["name"],
                    "album": item["album"]["name"],
                    "duration_ms": item["duration_ms"],  # Include raw duration for calculations
                    "duration": self.ms_to_min_sec(item["duration_ms"]),
                    "popularity": str(item["popularity"]) + "/100",
                    "preview_url": item.get("preview_url", "No preview available")
                }
                formatted_items.append(track_info)
            elif item_type == "artists":
                artist_info = {
                    "name": item["name"],
                    "popularity": str(item["popularity"]) + "/100",
                    "genres": item.get("genres", [])
                }
                formatted_items.append(artist_info)

        return formatted_items

    def get_total_time_listened(self, time_range):
        """Calculate total time listened from top tracks."""
        top_tracks = self.get_top_items("tracks", time_range)
        total_time_ms = sum(track["duration_ms"] for track in top_tracks)
        total_time_minutes = total_time_ms // 60000
        hours = total_time_minutes // 60
        minutes = total_time_minutes % 60
        #print(f"Total time listened over {time_range.replace('_', ' ')}: {hours} hours {minutes} minutes")
        return hours, minutes

    def get_favorite_genres(self, time_range):
        """Determine the top 3 favorite genres based on top artists."""
        top_artists = self.get_top_items("artists", time_range)
        genre_count = {}

        for artist in top_artists:
            for genre in artist.get("genres", []):
                genre_count[genre] = genre_count.get(genre, 0) + 1

        # Sort genres by frequency in descending order
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        top_3_genres = [genre for genre, count in sorted_genres[:3]]

        if top_3_genres:
            #print(f"Top 3 genres over {time_range.replace('_', ' ')}: {', '.join(top_3_genres)}")
            return top_3_genres
        else:
            #print(f"No genre data available for {time_range.replace('_', ' ')}")
            return []

# def get_refresh_token(self, auth_code):
#     """Exchange authorization code for access token and refresh token."""
#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         'Authorization': 'Basic ' + self.auth_base64,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     data = {
#         'grant_type': 'authorization_code',
#         'code': auth_code,
#         'redirect_uri': self.redirect_uri
#     }
#
#     response = requests.post(url, headers=headers, data=data)
#     response_data = response.json()
#
#     if response.status_code == 200:
#         refresh_token = response_data.get("refresh_token")
#         print("Refresh Token:")
#         print(refresh_token)
#         return refresh_token
#     else:
#         print(f"Error: {response_data.get('error_description', 'Unknown error')}")
#         return None


# Usage example
# spotify = SpotifyAPI()
# spotify.get_auth_url()  # Get the authorization URL
# Once you have the auth code, you can get the access token
# auth_code = input("Enter the authorization code: ")
# user_token = spotify.get_access_token(auth_code)

# if user_token:
#    print("Successfully retrieved user token!")
     # Test retrieving user-specific data
#    print("\nTesting access to user playlists:")
#    print("\nUser's Playlists:")
#    spotify.get_user_playlists()

    # Testing retrieval of top tracks for the last 4 weeks
#    print("\nTop Tracks (Last 4 Weeks):")
#    top_tracks = spotify.get_top_items("tracks", "short_term", 10)
#    print(top_tracks)
#    for idx, track in enumerate(top_tracks, 1):
#        print(f"{idx}. {track['name']} by {track['artist']}")
#        print(f"   Preview: {track['preview_url']}")

    # Getting total time listened over the past 6 months
#    print("\nTotal Time Listened (Last 6 Months):")
#    spotify.get_total_time_listened("medium_term")

    # Getting the favorite genre over the last month
#    print("\nFavorite Genre (Last 4 Weeks):")
#    spotify.get_favorite_genre("short_term")

