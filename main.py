#!/usr/bin/env python3
"""
Application Textual pour afficher la musique Spotify en cours,
la liste d'attente et permettre d'ajouter des sons.
"""

import asyncio
import requests
from io import BytesIO
from datetime import datetime
from typing import List, Optional, Dict
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Button, Input, ListView, ListItem, Label,
    ProgressBar, TextArea
)
from textual_image.renderable import Image
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message

# Import des fonctions Spotify
from spotify import (
    getCurrentPlayingTrack, getQueue, SearchSong, AddtoQueue, 
    DeletefromQueue, playTrack, pausePlayback, resumePlayback, 
    nextTrack, previousTrack
)


class Track:
    """Représente une piste musicale"""
    def __init__(self, track_data: Dict = None, title: str = None, artist: str = None, album: str = None, track_id: str = None):
        if track_data:
            # Création à partir des données Spotify
            self.id = track_data.get('id', '')
            self.title = track_data.get('name', '') or track_data.get('title', '')
            self.artist = track_data.get('artist', '')
            self.album = track_data.get('album', '')
            self.is_playing = track_data.get('is_playing', False)
            self.progress_ms = track_data.get('progress_ms', 0)
            self.duration_ms = track_data.get('duration_ms', 0)
            self.image_url = track_data.get('image_url', '')
        else:
            # Création manuelle (pour compatibilité)
            self.id = track_id or ''
            self.title = title or ''
            self.artist = artist or ''
            self.album = album or ''
            self.is_playing = False
            self.progress_ms = 0
            self.duration_ms = 0
            self.image_url = ''
        
        self.added_at = datetime.now()

    def __str__(self):
        return f"{self.title} - {self.artist}"


class SpotifyManager:
    """Gestionnaire pour l'API Spotify"""
    
    def __init__(self):
        self.local_queue = []  # Queue locale pour compenser les limitations de l'API
        self.is_playing = False

    def get_current_track(self) -> Optional[Track]:
        """Récupère la piste actuellement en cours"""
        track_data = getCurrentPlayingTrack()
        if track_data:
            print(f"Debug - Données reçues: {track_data}")  # Debug
            track = Track(track_data=track_data)
            print(f"Debug - Track créé: title='{track.title}', artist='{track.artist}'")  # Debug
            return track
        return None

    def get_queue(self) -> List[Track]:
        """Récupère la liste d'attente (queue locale + API)"""
        # Récupérer la queue depuis l'API Spotify
        api_queue = getQueue()
        tracks = []
        
        # Convertir les dictionnaires en objets Track
        for track_data in api_queue:
            tracks.append(Track(track_data=track_data))
        
        # Si pas de queue API, utiliser la queue locale
        if not tracks:
            tracks = self.local_queue
            
        return tracks

    def add_to_queue(self, track: Track):
        """Ajoute une piste à la queue"""
        if track.id:
            # Ajouter via l'API Spotify
            success = AddtoQueue(track.id)
            if success:
                self.local_queue.append(track)
                return True
        else:
            # Ajouter à la queue locale seulement
            self.local_queue.append(track)
            return True
        return False

    def search_tracks(self, query: str) -> List[Track]:
        """Recherche des pistes sur Spotify"""
        results = SearchSong(query, limit=10)
        tracks = []
        for track_data in results:
            tracks.append(Track(track_data=track_data))
        return tracks

    def play_pause(self):
        """Toggle play/pause"""
        current_track = self.get_current_track()
        if current_track and current_track.is_playing:
            self.is_playing = pausePlayback()
        else:
            self.is_playing = resumePlayback()

    def next_track(self):
        """Passe à la piste suivante"""
        success = nextTrack()
        if success and self.local_queue:
            # Retirer la première piste de notre queue locale
            self.local_queue.pop(0)
        return success

    def previous_track(self):
        """Revient à la piste précédente"""
        return previousTrack()

    def play_track(self, track: Track):
        """Joue une piste spécifique"""
        if track.id:
            return playTrack(track.id)
        return False

    def remove_from_queue(self, track: Track):
        """Supprime une piste de la queue locale"""
        if track in self.local_queue:
            self.local_queue.remove(track)
            return True
        return False


class TrackItem(ListItem):
    """Widget pour afficher une piste dans la liste"""
    
    def __init__(self, track: Track):
        super().__init__()
        self.track = track

    def compose(self):
        url = self.track.image_url if self.track.image_url else "https://picsum.photos/200"
        response = requests.get(url)
        image_data = BytesIO(response.content)

        yield Horizontal(
            Image(image_data),
            Vertical(
                Label(f"[bold]{self.track.title}[/bold]"),
                Label(f"{self.track.artist}"),
            ),
            id="track-container"
        )


class CurrentTrackWidget(Static):
    """Widget pour afficher la piste en cours"""
    
    track = reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track = None

    def compose(self):
        url = "https://picsum.photos/200"
        response = requests.get(url)
        image_data = BytesIO(response.content)

        yield Label("🎵 Musique en cours", classes="title")
        yield Horizontal(
            Image(image_data),
            Vertical(
                Static("Aucune musique en cours", id="current-track-info"),
                Static("", id="current-track-details"),
                Static("", id="current-track-duration"),
            ),
            id="current-track-container"
        )
        yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="progress-bar")

    def on_mount(self):
        """Initialisation après le montage du widget"""
        # Initialiser avec la piste actuelle si elle existe
        if self.track:
            self.update_track_display(self.track)

    def watch_track(self, track: Optional[Track]):
        """Mise à jour réactive de la piste"""
        self.update_track_display(track)

    def update_track_display(self, track: Optional[Track]):
        """Met à jour l'affichage de la piste"""
        try:
            if track:
                self.query_one("#current-track-info").update(f"🎵 {track.title}")
                self.query_one("#current-track-details").update(
                    f"👤 {track.artist}"
                )
                # Afficher la durée en temps réel
                duration_text = self.get_duration_display(track)
                self.query_one("#current-track-duration").update(duration_text)
                
                # Afficher l'image de l'album
                if track.image_url:
                    self.query_one("#current-track-image", Image).src = track.image_url
                else:
                    self.query_one("#current-track-image", Image).src = ""
                
                # Mettre à jour la barre de progression
                self.update_progress_bar(track)
            else:
                self.query_one("#current-track-info").update("Aucune musique en cours")
                self.query_one("#current-track-details").update("")
                self.query_one("#current-track-duration").update("")
                self.query_one("#current-track-image", Image).src = ""
                # Réinitialiser la barre de progression
                progress_bar = self.query_one("#progress-bar", ProgressBar)
                progress_bar.progress = 0
        except Exception:
            # Les widgets ne sont pas encore montés, on ignore l'erreur
            pass

    def get_duration_display(self, track: Track) -> str:
        """Retourne l'affichage de la durée en temps réel"""
        if hasattr(track, 'progress_ms') and hasattr(track, 'duration_ms'):
            if track.progress_ms and track.duration_ms:
                progress_seconds = track.progress_ms // 1000
                duration_seconds = track.duration_ms // 1000
                
                progress_min = progress_seconds // 60
                progress_sec = progress_seconds % 60
                duration_min = duration_seconds // 60
                duration_sec = duration_seconds % 60
                
                return f"⏱️ {progress_min:02d}:{progress_sec:02d} / {duration_min:02d}:{duration_sec:02d}"
        
        return "⏱️ --:-- / --:--"

    def update_progress_bar(self, track: Track):
        """Met à jour la barre de progression"""
        try:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            
            if hasattr(track, 'progress_ms') and hasattr(track, 'duration_ms'):
                if track.progress_ms and track.duration_ms and track.duration_ms > 0:
                    # Calculer le pourcentage de progression
                    progress_percentage = (track.progress_ms / track.duration_ms) * 100
                    progress_bar.progress = progress_percentage
                else:
                    progress_bar.progress = 0
            else:
                progress_bar.progress = 0
        except Exception:
            # Les widgets ne sont pas encore montés, on ignore l'erreur
            pass


class QueueWidget(Static):
    """Widget pour afficher la liste d'attente"""
    
    tracks = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self):
        yield Label("📋 Liste d'attente", classes="title")
        yield ListView(id="queue-list")

    def watch_tracks(self, tracks: List[Track]):
        queue_list = self.query_one("#queue-list", ListView)
        queue_list.clear()
        for track in tracks:
            queue_list.append(TrackItem(track))


class SearchWidget(Static):
    """Widget pour rechercher et ajouter des pistes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self):
        yield Label("🔍 Rechercher des musiques", classes="title")
        yield Input(placeholder="Tapez le nom d'une chanson ou d'un artiste...", id="search-input")
        yield Button("🔍 Rechercher", id="search-btn")
        yield ListView(id="search-results")

    def clear_search_results(self):
        self.query_one("#search-results", ListView).clear()


class SpotifyApp(App):
    """Application principale Spotify avec Textual"""
    
    CSS = """
    .title {
        color: $primary;
        margin-bottom: 1;
    }
    
    .controls {
        margin-top: 1;
        height: 3;
    }
    
    .controls Button {
        margin: 0 1;
    }
    
    #current-track-info {
        text-style: bold;
        margin: 1 0;
    }
    
    #current-track-details {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #progress-bar {
        margin: 1 0;
    }
    
    #search-results {
        height: 10;
        border: solid $primary;
        margin-top: 1;
    }
    
    #queue-list {
        height: 15;
        border: solid $primary;
    }
    
    #queue-list ListItem {
        padding: 1;
    }
    
    #current-track-image, #track-image {
        width: 10;
        height: 10;
        text-align: center;
    }
    
    #current-track-container, #track-container {
        height: auto;
    }
    
    Horizontal {
        height: auto;
    }
    
    Vertical {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quitter"),
    ]

    def __init__(self):
        super().__init__()
        self.spotify = SpotifyManager()
        self.search_results = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                CurrentTrackWidget(id="current-track"),
                Horizontal(
                    QueueWidget(id="queue"),
                    SearchWidget(id="search"),
                ),
            ),
            id="main-container"
        )
        yield Footer()

    def on_mount(self):
        """Initialisation de l'application"""
        self.update_current_track()
        self.update_queue()
        self.title = "🎵 Spotify Textual Player"
        
        # Mise à jour automatique de la piste en cours toutes les secondes
        self.set_interval(1.0, self.update_current_track)

    def update_current_track(self):
        """Met à jour l'affichage de la piste en cours"""
        current_widget = self.query_one("#current-track", CurrentTrackWidget)
        current_widget.track = self.spotify.get_current_track()

    def update_queue(self):
        """Met à jour la liste d'attente"""
        queue_widget = self.query_one("#queue", QueueWidget)
        queue_widget.tracks = self.spotify.get_queue()

    def on_button_pressed(self, event: Button.Pressed):
        """Gestion des clics sur les boutons"""
        if event.button.id == "search-btn":
            self.search_tracks()

    def on_input_submitted(self, event: Input.Submitted):
        """Gestion de la soumission du champ de recherche"""
        if event.input.id == "search-input":
            self.search_tracks()

    def search_tracks(self):
        """Recherche des pistes"""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()
        
        if not query:
            return

        # Mock de la recherche
        self.search_results = self.spotify.search_tracks(query)
        
        # Affichage des résultats
        search_results_list = self.query_one("#search-results", ListView)
        search_results_list.clear()
        
        for track in self.search_results:
            item = TrackItem(track)
            item.add_class("search-result")
            search_results_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected):
        """Gestion de la sélection d'un élément de liste"""
        if event.list_view.id == "search-results":
            # Ajouter la piste sélectionnée à la queue
            selected_item = event.item
            if hasattr(selected_item, 'track'):
                success = self.spotify.add_to_queue(selected_item.track)
                if success:
                    self.update_queue()
                    
                    # Nettoyer les résultats de recherche
                    search_input = self.query_one("#search-input", Input)
                    search_input.value = ""
                    self.query_one("#search-results", ListView).clear()
                    
                    self.notify(f"✅ '{selected_item.track.title}' ajoutée à la liste d'attente!")
                else:
                    self.notify(f"❌ Erreur lors de l'ajout de '{selected_item.track.title}'")


    def action_quit(self):
        """Action quitter"""
        self.exit()


def main():
    """Point d'entrée de l'application"""
    app = SpotifyApp()
    app.run()


if __name__ == "__main__":
    main()
