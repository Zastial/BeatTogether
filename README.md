# 🎵 Spotify Textual Player

Une application de lecteur Spotify construite avec le framework Textual de Python.

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

## 📁 Configuration

L'application utilise des variables d'environnement pour la configuration Spotify :

| Variable | Description | Valeur par défaut |
|----------|-------------|------------------|
| `SPOTIPY_CLIENT_ID` | ID client Spotify | Requis |
| `SPOTIPY_CLIENT_SECRET` | Secret client Spotify | Requis |
| `REDIRECT_URL` | URL de redirection OAuth | `http://localhost:8888/callback` |

### Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet :

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id_here
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret_here
REDIRECT_URL=http://localhost:8888/callback
```

## 🎮 Contrôles

### Clavier
- `Q` : Quitter
- `Espace` : Rechercher un son

### Interface
- **🎵 Musique en cours** : Affiche la piste actuellement jouée avec durée et barre de progression
- **📋 Liste d'attente** : Montre les pistes en attente
- **🔍 Ajouter un son** : Accède à l'écran de recherche dédié

## 🔧 Fonctionnalités

- ✅ Affichage de la musique en cours avec durée en temps réel
- ✅ Barre de progression visuelle
- ✅ Liste d'attente mise à jour automatiquement
- ✅ Recherche et ajout de pistes via un écran dédié
- ✅ Navigation fluide entre écrans
- ✅ Synchronisation automatique avec Spotify
- ✅ Évite les clignotements lors des mises à jour

## 🎵 Recherche de musiques

1. Cliquer sur "🔍 Ajouter un son" pour accéder� à l'écran de recherche
2. Saisir le nom d'une chanson ou artiστε 
3. Cliquer sur une piste pour l'ajouter à la liste d'attente
4. Retour automatique à l'écran principal après ajout

## 📝 Notes

L'application est optimisée pour une expérience fluide avec mise à jour automatique toutes les secondes pour la piste en cours et toutes les 3 secondes pour la queue.