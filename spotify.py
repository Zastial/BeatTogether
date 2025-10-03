import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Optional

# Configuration Spotify
SPOTIPY_CLIENT_ID = '610313e73c6d4333bf2831d16208d75f'
SPOTIPY_CLIENT_SECRET = '81527ba3f7844a8bb7c9ada01528dc74'
REDIRECT_URL = 'http://localhost:8888/callback'

# Initialisation du client Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played",
        redirect_uri=REDIRECT_URL,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
    )
)

sp.user = "s7df1bggy7vp04apvg6dglu0t" #C'est moi wesh


def getCurrentPlayingTrack() -> Optional[Dict]:
    """
    Récupère la piste actuellement en cours de lecture
    
    Returns:
        Dict contenant les informations de la piste ou None si aucune piste n'est en cours
    """
    try:
        current_track = sp.current_user_playing_track()
        
        if current_track is None or current_track['item'] is None:
            return None
            
        track = current_track['item']
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'is_playing': current_track['is_playing'],
            'progress_ms': current_track['progress_ms'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
        }
    except Exception as e:
        print(f"Erreur lors de la récupération de la piste en cours: {e}")
        return None


def getQueue() -> List[Dict]:
    """
    Récupère la liste d'attente actuelle
    
    Returns:
        Liste des pistes en attente
    """
    try:
        # Note: L'API Spotify ne permet pas de récupérer directement la queue
        # Cette fonction retourne une liste vide pour l'instant
        # Dans une vraie implémentation, il faudrait maintenir une queue locale

        results = sp.queue()

        tracks = []
        for item in results['queue']:
            print(item.keys())
            tracks.append({
                'id': item['id'],
                'title': item['name'],
                'artist': ', '.join([artist['name'] for artist in item['artists']]),
                'album': item['album']['name'],
            })

        return tracks
    except Exception as e:
        print(f"Erreur lors de la récupération de la queue: {e}")
        return []


print(getQueue())



def SearchSong(query: str, limit: int = 10) -> List[Dict]:
    """
    Recherche des pistes sur Spotify
    
    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats (défaut: 10)
    
    Returns:
        Liste des pistes trouvées
    """
    try:
        results = sp.search(q=query, type='track', limit=limit)
        tracks = []
        
        for track in results['tracks']['items']:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url'],
                'external_urls': track['external_urls'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
            })
        
        return tracks
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        return []


def AddtoQueue(track_id: str) -> bool:
    """
    Ajoute une piste à la queue
    
    Args:
        track_id: ID de la piste à ajouter
    
    Returns:
        True si l'ajout a réussi, False sinon
    """
    try:
        sp.add_to_queue(track_id)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout à la queue: {e}")
        return False


def DeletefromQueue(track_id: str) -> bool:
    """
    Supprime une piste de la queue
    
    Args:
        track_id: ID de la piste à supprimer
    
    Returns:
        True si la suppression a réussi, False sinon
    
    Note:
        L'API Spotify ne permet pas de supprimer directement de la queue
        Cette fonction est un placeholder pour une future implémentation
    """
    try:
        # L'API Spotify ne permet pas de supprimer directement de la queue
        # Il faudrait maintenir une queue locale et la gérer manuellement
        print(f"Suppression de la piste {track_id} de la queue (non implémentée)")
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression de la queue: {e}")
        return False


# Fonctions utilitaires supplémentaires
def playTrack(track_id: str) -> bool:
    """
    Lance la lecture d'une piste
    
    Args:
        track_id: ID de la piste à jouer
    
    Returns:
        True si la lecture a démarré, False sinon
    """
    try:
        sp.start_playback(uris=[f"spotify:track:{track_id}"])
        return True
    except Exception as e:
        print(f"Erreur lors de la lecture: {e}")
        return False


def pausePlayback() -> bool:
    """
    Met en pause la lecture
    
    Returns:
        True si la pause a réussi, False sinon
    """
    try:
        sp.pause_playback()
        return True
    except Exception as e:
        print(f"Erreur lors de la pause: {e}")
        return False


def resumePlayback() -> bool:
    """
    Reprend la lecture
    
    Returns:
        True si la reprise a réussi, False sinon
    """
    try:
        sp.start_playback()
        return True
    except Exception as e:
        print(f"Erreur lors de la reprise: {e}")
        return False


def nextTrack() -> bool:
    """
    Passe à la piste suivante
    
    Returns:
        True si le changement a réussi, False sinon
    """
    try:
        sp.next_track()
        return True
    except Exception as e:
        print(f"Erreur lors du passage à la piste suivante: {e}")
        return False


def previousTrack() -> bool:
    """
    Revient à la piste précédente
    
    Returns:
        True si le changement a réussi, False sinon
    """
    try:
        sp.previous_track()
        return True
    except Exception as e:
        print(f"Erreur lors du retour à la piste précédente: {e}")
        return False
