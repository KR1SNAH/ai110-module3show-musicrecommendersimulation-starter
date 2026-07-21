"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: weighted affinities (not just one favorite) so scoring can
    # differentiate degrees of match across genres/moods, plus broader audio
    # targets and a discovery bias (0 = mainstream, 1 = niche/undiscovered).
    user_prefs = {
        "genre_preferences": {
            "indie pop": 0.95,
            "pop": 0.8,
            "synthwave": 0.6,
            "house": 0.5,
            "lofi": 0.3,
        },
        "mood_preferences": {
            "happy": 0.9,
            "euphoric": 0.6,
            "playful": 0.5,
        },
        "target_energy": 0.75,
        "target_valence": 0.7,
        "target_danceability": 0.75,
        "likes_acoustic": False,
        "discovery_bias": 0.4,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song.title} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
