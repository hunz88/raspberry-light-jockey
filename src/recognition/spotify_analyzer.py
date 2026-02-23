"""
Spotify Audio Analyzer
Recupera la struttura delle canzoni (sezioni, verse, chorus, drop...)
usando le Spotify Web API con Client Credentials (no login utente).
"""

import requests
import base64
import time


class SpotifyAnalyzer:
    """Analisi strutturale delle canzoni via Spotify"""

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expiry = 0
        print("🎧 Spotify Analyzer initialized (section mapping attivo)")

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _get_token(self):
        """Ottieni/rinnova access token con Client Credentials flow"""
        if self._token and time.time() < self._token_expiry - 60:
            return self._token

        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        resp = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={'Authorization': f'Basic {credentials}'},
            data={'grant_type': 'client_credentials'},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            self._token = data['access_token']
            self._token_expiry = time.time() + data['expires_in']
            return self._token
        else:
            raise Exception(f"Spotify token error {resp.status_code}: {resp.text}")

    # ------------------------------------------------------------------
    # Track search
    # ------------------------------------------------------------------

    def search_track(self, artist, title):
        """Cerca traccia su Spotify. Restituisce (track_id, duration_sec) o (None, None)."""
        token = self._get_token()
        query = f"artist:{artist} track:{title}"
        resp = requests.get(
            'https://api.spotify.com/v1/search',
            headers={'Authorization': f'Bearer {token}'},
            params={'q': query, 'type': 'track', 'limit': 1},
            timeout=10
        )
        if resp.status_code == 200:
            items = resp.json().get('tracks', {}).get('items', [])
            if items:
                track = items[0]
                return track['id'], track['duration_ms'] / 1000.0
        return None, None

    # ------------------------------------------------------------------
    # Audio analysis
    # ------------------------------------------------------------------

    def get_audio_analysis(self, track_id):
        """Scarica l'analisi audio completa di una traccia."""
        token = self._get_token()
        resp = requests.get(
            f'https://api.spotify.com/v1/audio-analysis/{track_id}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_song_sections(self, artist, title):
        """
        Restituisce la lista di sezioni etichettate per la canzone.
        Ogni sezione: {'start': float, 'duration': float, 'type': str, 'loudness': float}
        Ritorna None se la canzone non viene trovata.
        """
        try:
            track_id, _ = self.search_track(artist, title)
            if not track_id:
                print(f"   🔍 Spotify: traccia non trovata — {artist} / {title}")
                return None

            analysis = self.get_audio_analysis(track_id)
            if not analysis:
                return None

            raw_sections = analysis.get('sections', [])
            if not raw_sections:
                return None

            labeled = self._label_sections(raw_sections)
            print(f"   🗺️  Spotify: {len(labeled)} sezioni per '{title}'")
            for s in labeled:
                print(f"      {s['type']:12s} @ {s['start']:5.0f}s  ({s['loudness']:.1f}dB)")
            return labeled

        except Exception as e:
            print(f"   ❌ Spotify error: {e}")
            return None

    # ------------------------------------------------------------------
    # Section labeling
    # ------------------------------------------------------------------

    def _label_sections(self, raw_sections):
        """
        Etichetta le sezioni Spotify come intro/verse/chorus/drop/break/buildup/transition
        usando loudness relativa e posizione nella canzone.
        """
        if not raw_sections:
            return []

        loudnesses = [s['loudness'] for s in raw_sections]
        median_loud = sorted(loudnesses)[len(loudnesses) // 2]
        max_loud = max(loudnesses)

        labeled = []
        for i, s in enumerate(raw_sections):
            loud = s['loudness']
            loud_rel = loud - median_loud   # positivo = più forte della media

            # Prima sezione quieta → intro
            if i == 0 and loud_rel < 1.0:
                section_type = 'intro'

            # Sezione più forte in assoluto → drop
            elif loud == max_loud:
                section_type = 'drop'

            # Molto più forte della media → chorus
            elif loud_rel > 3.0:
                section_type = 'chorus'

            # Molto più quieta della media → break
            elif loud_rel < -4.0:
                section_type = 'break'

            # Più forte della sezione precedente → buildup
            elif i > 0 and loud > raw_sections[i - 1]['loudness'] + 2.0:
                section_type = 'buildup'

            # Leggermente sotto la media → verse
            elif loud_rel < -1.0:
                section_type = 'verse'

            else:
                section_type = 'verse'

            labeled.append({
                'start': s['start'],
                'duration': s['duration'],
                'type': section_type,
                'loudness': loud,
            })

        return labeled
