"""
Metadata Fetcher Module
Fetches lyrics and additional metadata from free APIs
"""

import requests
import json
from urllib.parse import quote


class MetadataFetcher:
    """Fetch lyrics and metadata from free sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RaspberryPi-LightJockey/1.0'
        })
        
        print("📚 Metadata fetcher initialized")
    
    def get_lyrics(self, artist, title):
        """
        Get song lyrics from lyrics.ovh (FREE!)
        
        Args:
            artist: artist name
            title: song title
            
        Returns:
            lyrics string or None
        """
        try:
            # Clean up artist and title
            artist = artist.strip()
            title = title.strip()
            
            # lyrics.ovh API
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            
            print(f"📝 Fetching lyrics for: {title} - {artist}")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('lyrics', '')
                
                if lyrics:
                    print(f"✅ Lyrics found ({len(lyrics)} characters)")
                    return lyrics
                else:
                    print("❌ No lyrics found")
                    return None
            else:
                print(f"❌ Lyrics API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching lyrics: {e}")
            return None
    
    def get_lyrics_snippet(self, artist, title, max_lines=8):
        """
        Get a snippet of lyrics (first few lines)
        
        Args:
            artist: artist name
            title: song title
            max_lines: maximum number of lines to return
            
        Returns:
            lyrics snippet or None
        """
        full_lyrics = self.get_lyrics(artist, title)
        
        if not full_lyrics:
            return None
        
        # Split into lines and get first few
        lines = full_lyrics.split('\n')
        snippet_lines = []
        
        for line in lines[:max_lines * 2]:  # Get a bit extra to filter
            line = line.strip()
            if line and len(snippet_lines) < max_lines:
                snippet_lines.append(line)
        
        return '\n'.join(snippet_lines)
    
    def search_musicbrainz(self, artist, title):
        """
        Search MusicBrainz for additional metadata (FREE!)
        
        Args:
            artist: artist name
            title: song title
            
        Returns:
            metadata dict or None
        """
        try:
            # MusicBrainz search
            query = f'artist:"{artist}" AND recording:"{title}"'
            url = "https://musicbrainz.org/ws/2/recording/"
            
            params = {
                'query': query,
                'fmt': 'json',
                'limit': 1
            }
            
            print(f"🔍 Searching MusicBrainz for: {title} - {artist}")
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                
                if recordings:
                    recording = recordings[0]
                    
                    metadata = {
                        'mbid': recording.get('id', ''),
                        'title': recording.get('title', ''),
                        'length': recording.get('length', 0),  # milliseconds
                        'tags': []
                    }
                    
                    # Extract tags (genres, moods, etc.)
                    tags = recording.get('tags', [])
                    for tag in tags:
                        tag_name = tag.get('name', '')
                        if tag_name:
                            metadata['tags'].append(tag_name)
                    
                    # Get release info if available
                    releases = recording.get('releases', [])
                    if releases:
                        release = releases[0]
                        metadata['release_date'] = release.get('date', '')
                        metadata['country'] = release.get('country', '')
                    
                    print(f"✅ MusicBrainz metadata found")
                    return metadata
                else:
                    print("❌ No results from MusicBrainz")
                    return None
            else:
                print(f"❌ MusicBrainz API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error searching MusicBrainz: {e}")
            return None
    
    def get_complete_metadata(self, artist, title):
        """
        Get complete metadata: lyrics + MusicBrainz data
        
        Args:
            artist: artist name
            title: song title
            
        Returns:
            complete metadata dict
        """
        metadata = {
            'artist': artist,
            'title': title,
            'lyrics': None,
            'lyrics_snippet': None,
            'mb_data': None,
            'tags': [],
            'genres': []
        }
        
        # Get lyrics snippet (not full lyrics to save time)
        lyrics_snippet = self.get_lyrics_snippet(artist, title)
        if lyrics_snippet:
            metadata['lyrics_snippet'] = lyrics_snippet
        
        # Get MusicBrainz data
        mb_data = self.search_musicbrainz(artist, title)
        if mb_data:
            metadata['mb_data'] = mb_data
            metadata['tags'] = mb_data.get('tags', [])
            
            # Extract genres from tags
            genre_keywords = ['rock', 'pop', 'jazz', 'blues', 'metal', 'electronic', 
                            'hip hop', 'rap', 'classical', 'country', 'folk', 'reggae']
            
            for tag in metadata['tags']:
                tag_lower = tag.lower()
                for genre_kw in genre_keywords:
                    if genre_kw in tag_lower:
                        if genre_kw not in metadata['genres']:
                            metadata['genres'].append(genre_kw)
        
        return metadata
    
    def analyze_lyrics_themes(self, lyrics):
        """
        Simple keyword-based theme analysis of lyrics
        
        Args:
            lyrics: lyrics text
            
        Returns:
            dict with detected themes and keywords
        """
        if not lyrics:
            return {'themes': [], 'keywords': []}
        
        lyrics_lower = lyrics.lower()
        
        # Define theme keywords
        themes_map = {
            'ocean/water': ['ocean', 'sea', 'water', 'wave', 'tide', 'beach', 'shore', 
                           'blue', 'deep', 'swim', 'drown', 'sail', 'ship'],
            'love': ['love', 'heart', 'kiss', 'romance', 'baby', 'darling', 'sweet',
                    'together', 'forever', 'feeling'],
            'night': ['night', 'dark', 'moon', 'star', 'midnight', 'dream', 'sleep'],
            'fire': ['fire', 'burn', 'flame', 'hot', 'heat', 'smoke', 'ash'],
            'nature': ['tree', 'forest', 'flower', 'rain', 'sun', 'sky', 'green',
                      'wind', 'mountain', 'river'],
            'sadness': ['sad', 'cry', 'tear', 'pain', 'hurt', 'broken', 'alone',
                       'lonely', 'goodbye', 'lost'],
            'happiness': ['happy', 'joy', 'smile', 'laugh', 'dance', 'celebrate',
                         'party', 'fun', 'bright'],
            'party': ['party', 'dance', 'club', 'music', 'beat', 'rhythm', 'dj',
                     'night', 'wild', 'crazy']
        }
        
        detected_themes = {}
        all_keywords = []
        
        # Count keywords for each theme
        for theme, keywords in themes_map.items():
            count = 0
            found_words = []
            
            for keyword in keywords:
                if keyword in lyrics_lower:
                    count += lyrics_lower.count(keyword)
                    found_words.append(keyword)
            
            if count > 0:
                detected_themes[theme] = {
                    'count': count,
                    'keywords': found_words
                }
                all_keywords.extend(found_words)
        
        # Sort themes by count
        sorted_themes = sorted(detected_themes.items(), 
                             key=lambda x: x[1]['count'], 
                             reverse=True)
        
        return {
            'themes': [theme for theme, _ in sorted_themes],
            'theme_details': dict(sorted_themes),
            'keywords': list(set(all_keywords))
        }
