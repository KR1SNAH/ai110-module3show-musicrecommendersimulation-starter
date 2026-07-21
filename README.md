# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

**`Song` fields:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness, popularity.

**`UserProfile` fields:** instead of a single favorite genre/mood, the profile stores weighted affinities so scoring can tell degrees of preference apart, plus a few audio targets:

- `genre_preferences` / `mood_preferences` — dicts mapping a genre or mood to an affinity from 0 to 1 (e.g. `{"pop": 0.8, "lofi": 0.3}`)
- `target_energy`, `target_valence`, `target_danceability` — the ideal value (0-1) for each audio trait
- `likes_acoustic` — whether the user prefers acoustic (`acousticness > 0.5`) or non-acoustic songs
- `discovery_bias` — 0 means favor mainstream/popular songs, 1 means favor under-the-radar songs

**Scoring (`_score_song` in `recommender.py`, ~0-100 points):**

| Signal | Points | How it's scored |
|---|---|---|
| Genre match | up to 25 | `genre_preferences.get(song.genre, 0) * 25` — weighted, not just hit/miss |
| Mood match | up to 20 | `mood_preferences.get(song.mood, 0) * 20` |
| Energy fit | up to 20 | `max(0, 1 - |target_energy - song.energy|) * 20` — rewards being *close*, not just exact |
| Valence fit | up to 15 | same distance formula against `target_valence` |
| Danceability fit | up to 10 | same distance formula against `target_danceability` |
| Acoustic fit | ±5 | +5 if `likes_acoustic` agrees with `acousticness > 0.5`, else -5 |
| Discovery bias | up to 5 | blends reward for popular vs. niche songs based on `discovery_bias` |

Popularity is never scored on its own outside of `discovery_bias` — otherwise the system would just recommend whatever's already popular regardless of fit.

**Choosing recommendations:** every song in the catalog is scored against the user's profile, sorted descending by score, and the top `k` are returned. `explain_recommendation` / `recommend_songs` reuse the same reasons collected during scoring (e.g. "'pop' genre matches your taste (0.80 affinity)") to build a human-readable explanation for each pick.

The recommendation systems like the one used in Spotify use multiple signals to recommend songs. They use similarity scores between the songs based on their attributes, similarity between users, what time of day it is, which device they're listening on, which songs they usually skip, replay rate, as well as Deep Learning and some other metrics.

The recommendation systems like the one used in Spotify use multiple signals to recommend songs. They use similarity scores between the songs based on their attributes, similarity between users, what time of day it is, which device they're listening on, which songs they usually skip, replay rate, as well as Deep Learning and some other metrics.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



