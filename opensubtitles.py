import requests

class OpenSubtitlesError(Exception):
    pass

class OpenSubtitles:
    def __init__(self, api_key, username=None, password=None):
        self.api_url = "https://api.opensubtitles.com/api/v1"
        self.api_key = api_key
        self.username = username
        self.password = password
        self.token = None

    def _ensure_token(self):
        if self.token:
            return

        if self.username and self.password:
            url = f"{self.api_url}/login"
            headers = {"Content-Type": "application/json", "Api-Key": self.api_key}
            data = {"username": self.username, "password": self.password}
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                self.token = response.json().get("token")
            except requests.exceptions.RequestException as e:
                raise OpenSubtitlesError(f"Error logging in: {e}")

    def search_subtitles(self, query, language):
        self._ensure_token()

        url = f"{self.api_url}/subtitles"
        headers = {"Content-Type": "application/json", "Api-Key": self.api_key}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        params = {"query": query, "languages": language}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as e:
            raise OpenSubtitlesError(f"Error searching subtitles: {e}")

    def download_subtitle(self, file_id):
        self._ensure_token()

        url = f"{self.api_url}/download"
        headers = {"Content-Type": "application/json", "Api-Key": self.api_key}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        data = {"file_id": file_id}
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            download_url = response.json().get("link")

            # Download the actual subtitle file
            subtitle_response = requests.get(download_url)
            subtitle_response.raise_for_status()
            return subtitle_response.text
        except requests.exceptions.RequestException as e:
            raise OpenSubtitlesError(f"Error downloading subtitle: {e}")
