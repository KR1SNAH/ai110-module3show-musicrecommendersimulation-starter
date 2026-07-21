import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    genre_preferences: Dict[str, float]
    mood_preferences: Dict[str, float]
    target_energy: float
    target_valence: float
    target_danceability: float
    likes_acoustic: bool
    discovery_bias: float

def _score_song(
    genre_preferences: Dict[str, float],
    mood_preferences: Dict[str, float],
    target_energy: float,
    target_valence: float,
    target_danceability: float,
    likes_acoustic: bool,
    discovery_bias: float,
    song: Song,
) -> Tuple[float, List[str]]:
    """Shared scoring rule used by both the OOP Recommender and the functional score_song()/recommend_songs() path."""
    reasons = []
    score = 0.0

    genre_weight = genre_preferences.get(song.genre, 0.0)
    score += genre_weight * 25
    if genre_weight > 0:
        reasons.append(f"'{song.genre}' genre matches your taste ({genre_weight:.2f} affinity)")

    mood_weight = mood_preferences.get(song.mood, 0.0)
    score += mood_weight * 20
    if mood_weight > 0:
        reasons.append(f"'{song.mood}' mood matches your taste ({mood_weight:.2f} affinity)")

    energy_gap = abs(target_energy - song.energy)
    score += max(0.0, 1 - energy_gap) * 20
    if energy_gap <= 0.15:
        reasons.append(f"energy ({song.energy:.2f}) close to your target ({target_energy:.2f})")

    valence_gap = abs(target_valence - song.valence)
    score += max(0.0, 1 - valence_gap) * 15
    if valence_gap <= 0.15:
        reasons.append(f"valence ({song.valence:.2f}) close to your target ({target_valence:.2f})")

    dance_gap = abs(target_danceability - song.danceability)
    score += max(0.0, 1 - dance_gap) * 10
    if dance_gap <= 0.15:
        reasons.append(f"danceability ({song.danceability:.2f}) close to your target ({target_danceability:.2f})")

    is_acoustic = song.acousticness > 0.5
    if likes_acoustic == is_acoustic:
        score += 5
        reasons.append("acoustic style matches your preference" if is_acoustic else "non-acoustic style matches your preference")
    else:
        score -= 5

    popularity_norm = song.popularity / 100
    blended_popularity = (1 - discovery_bias) * popularity_norm + discovery_bias * (1 - popularity_norm)
    score += blended_popularity * 5
    if discovery_bias >= 0.5 and popularity_norm < 0.5:
        reasons.append("under-the-radar pick, matching your discovery preference")
    elif discovery_bias < 0.5 and popularity_norm >= 0.5:
        reasons.append("popular pick, matching your mainstream preference")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one song against the user's profile, returning (score, reasons)."""
        return _score_song(
            user.genre_preferences,
            user.mood_preferences,
            user.target_energy,
            user.target_valence,
            user.target_danceability,
            user.likes_acoustic,
            user.discovery_bias,
            song,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for the user, ranked by score descending."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Builds a human-readable explanation from the reasons collected during scoring."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "General fit based on your taste profile."

def load_songs(csv_path: str) -> List[Song]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(Song(
                id=int(row["id"]),
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
                popularity=int(row["popularity"]),
            ))
    return songs

def score_song(user_prefs: Dict, song: Song) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    return _score_song(
        user_prefs.get("genre_preferences", {}),
        user_prefs.get("mood_preferences", {}),
        user_prefs["target_energy"],
        user_prefs["target_valence"],
        user_prefs["target_danceability"],
        user_prefs["likes_acoustic"],
        user_prefs.get("discovery_bias", 0.0),
        song,
    )

def recommend_songs(user_prefs: Dict, songs: List[Song], k: int = 5) -> List[Tuple[Song, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "General fit based on your taste profile."
        scored.append((song, score, explanation))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
