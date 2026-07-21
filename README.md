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

### Adversarial and edge-case profile testing

To see whether the scoring logic (`_score_song` in `recommender.py`) could be tricked or would produce unexpected results, I ran the real `data/songs.csv` catalog through `recommend_songs()` with a baseline profile (values within the documented ranges) plus 7 adversarial/edge-case profiles. Raw terminal output for each is below.

**Baseline (documented-range) profile** — the profile shipped in `src/main.py`, used as a control:

```
Top recommendations:

Rooftop Lights (indie pop/happy) - Score: 91.86
Because: 'indie pop' genre matches your taste (0.95 affinity); 'happy' mood matches your taste (0.90 affinity); energy (0.76) close to your target (0.75); valence (0.81) close to your target (0.70); danceability (0.82) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Sunrise City (pop/happy) - Score: 86.88
Because: 'pop' genre matches your taste (0.80 affinity); 'happy' mood matches your taste (0.90 affinity); energy (0.82) close to your target (0.75); valence (0.84) close to your target (0.70); danceability (0.79) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Neon Cathedral (house/euphoric) - Score: 70.04
Because: 'house' genre matches your taste (0.50 affinity); 'euphoric' mood matches your taste (0.60 affinity); energy (0.88) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Gym Hero (pop/intense) - Score: 66.86
Because: 'pop' genre matches your taste (0.80 affinity); valence (0.77) close to your target (0.70); danceability (0.88) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Night Drive Loop (synthwave/moody) - Score: 64.23
Because: 'synthwave' genre matches your taste (0.60 affinity); energy (0.75) close to your target (0.75); danceability (0.73) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference
```

**Unbounded genre weight (`genre_preferences={"pop": 100.0}`)** — `genre_preferences` is documented as a 0-1 affinity multiplied by 25, but nothing clamps it. A single weight of 100 should be rejected, not accepted:

```
Top recommendations:

Sunrise City (pop/happy) - Score: 2514.88
Because: 'pop' genre matches your taste (100.00 affinity); popular pick, matching your mainstream preference

Gym Hero (pop/intense) - Score: 2512.86
Because: 'pop' genre matches your taste (100.00 affinity); popular pick, matching your mainstream preference

Paper Boats (classical/melancholic) - Score: 50.32
Because: energy (0.22) close to your target (0.20); valence (0.30) close to your target (0.20); danceability (0.20) close to your target (0.20); acoustic style matches your preference

Blue Hour Static (blues/anxious) - Score: 42.80
Because: acoustic style matches your preference

Spacewalk Thoughts (ambient/chill) - Score: 41.84
Because: energy (0.28) close to your target (0.20); acoustic style matches your preference
```

**Finding:** a single out-of-range weight produces a score over 2500 on a system documented as "~0-100 points" and completely overrides every audio-fit signal — the top 2 picks are pop songs with mediocre energy/valence/danceability fit for a user who otherwise wanted low-energy, acoustic songs (`target_energy=0.2`, `likes_acoustic=True`). The scoring rule trusts `genre_preferences`/`mood_preferences` values without validating they're in `[0, 1]`.

**Negative genre weight (`genre_preferences={"lofi": -1.0}`)** — targets tuned to match lofi tracks well, testing whether a negative affinity is silently accepted:

```
Top recommendations:

Spacewalk Thoughts (ambient/chill) - Score: 67.03
Because: 'chill' mood matches your taste (1.00 affinity); energy (0.28) close to your target (0.40); valence (0.65) close to your target (0.60); acoustic style matches your preference

Golden Hour Vows (folk/nostalgic) - Score: 49.70
Because: energy (0.45) close to your target (0.40); valence (0.62) close to your target (0.60); danceability (0.48) close to your target (0.60); acoustic style matches your preference

Coffee Shop Stories (jazz/relaxed) - Score: 49.47
Because: energy (0.37) close to your target (0.40); valence (0.71) close to your target (0.60); danceability (0.54) close to your target (0.60); acoustic style matches your preference

Harvest Moon Waltz (country/peaceful) - Score: 47.76
Because: energy (0.33) close to your target (0.40); valence (0.68) close to your target (0.60); acoustic style matches your preference

Blue Hour Static (blues/anxious) - Score: 47.60
Because: energy (0.40) close to your target (0.40); danceability (0.45) close to your target (0.60); acoustic style matches your preference
```

**Finding:** both lofi tracks in the catalog (Midnight Coding, Focus Flow) got pushed out of the top 5 entirely by the -25 point genre penalty, but neither the score-driving reason nor any negative signal appears in any explanation shown above — `_score_song` only calls `reasons.append(...)` for genre/mood when the weight is `> 0`, so a penalty of any size is applied silently. A user (or grader) reading only the explanations would have no way to know genre affinity was involved at all.

**Out-of-range discovery_bias (`discovery_bias=-20.0`)** — documented as 0 (mainstream) to 1 (niche), worth "up to 5" points:

```
Top recommendations:

Copper Skyline (hip hop/playful) - Score: 108.90
Because: non-acoustic style matches your preference; popular pick, matching your mainstream preference

Gym Hero (pop/intense) - Score: 99.60
Because: non-acoustic style matches your preference; popular pick, matching your mainstream preference

Sunrise City (pop/happy) - Score: 95.50
Because: non-acoustic style matches your preference; popular pick, matching your mainstream preference

Neon Cathedral (house/euphoric) - Score: 84.00
Because: non-acoustic style matches your preference; popular pick, matching your mainstream preference

Rooftop Lights (indie pop/happy) - Score: 72.25
Because: non-acoustic style matches your preference; popular pick, matching your mainstream preference
```

**Finding:** with no genre/mood preferences and neutral audio targets, this profile should produce fairly flat scores across the catalog — instead it ranks purely by raw popularity, with scores up to ~108 on a "~0-100 point" scale, because `blended_popularity` is never clamped to `[0, 1]` before being scaled by 5.

**NaN target_energy (`target_energy=float('nan')`)** — simulates a corrupted upstream value (e.g. a division-by-zero elsewhere in a real pipeline):

```
Top recommendations:

Rooftop Lights (indie pop/happy) - Score: 70.81
Because: 'indie pop' genre matches your taste (0.90 affinity); 'happy' mood matches your taste (0.90 affinity); valence (0.81) close to your target (0.70); danceability (0.82) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Sunrise City (pop/happy) - Score: 68.28
Because: 'pop' genre matches your taste (0.80 affinity); 'happy' mood matches your taste (0.90 affinity); valence (0.84) close to your target (0.70); danceability (0.79) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Gym Hero (pop/intense) - Score: 50.46
Because: 'pop' genre matches your taste (0.80 affinity); valence (0.77) close to your target (0.70); danceability (0.88) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Velvet Confession (r&b/romantic) - Score: 31.60
Because: valence (0.70) close to your target (0.70); danceability (0.65) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Salt and Sirens (reggae/dreamy) - Score: 31.34
Because: valence (0.66) close to your target (0.70); danceability (0.70) close to your target (0.75); non-acoustic style matches your preference
```

**Finding:** no crash and no `nan` in any score — none of the songs mention energy at all in their explanation, because Python's `max(0.0, 1 - nan)` evaluates to `0.0` (NaN comparisons are always `False`), so the entire energy dimension is silently disabled rather than raising an error or propagating the NaN. Compare to the baseline profile above (same genre/mood/valence/dance targets): the ranking is nearly identical minus every energy-related reason, with no indication anything went wrong.

**Acoustic boundary (target matches `acousticness == 0.5` exactly)** — `is_acoustic = acousticness > 0.5` is a strict comparison, and song #18 "Salt and Sirens" has `acousticness` exactly `0.50`:

```
Top recommendations:

Salt and Sirens (reggae/dreamy) - Score: 87.38
Because: 'reggae' genre matches your taste (1.00 affinity); 'dreamy' mood matches your taste (1.00 affinity); energy (0.48) close to your target (0.48); valence (0.66) close to your target (0.66); danceability (0.70) close to your target (0.70)

Midnight Coding (lofi/chill) - Score: 48.90
Because: energy (0.42) close to your target (0.48); valence (0.56) close to your target (0.66); danceability (0.62) close to your target (0.70); acoustic style matches your preference

Golden Hour Vows (folk/nostalgic) - Score: 48.80
Because: energy (0.45) close to your target (0.48); valence (0.62) close to your target (0.66); acoustic style matches your preference

Focus Flow (lofi/focused) - Score: 48.79
Because: energy (0.40) close to your target (0.48); valence (0.59) close to your target (0.66); danceability (0.60) close to your target (0.70); acoustic style matches your preference

Coffee Shop Stories (jazz/relaxed) - Score: 47.77
Because: energy (0.37) close to your target (0.48); valence (0.71) close to your target (0.66); acoustic style matches your preference
```

**Finding:** even for the top pick, a perfect genre/mood/energy/valence/danceability match, `likes_acoustic=True` against a song at exactly `acousticness=0.5` gets none of the "acoustic style matches your preference" bonus and no mention of the mismatch either — same silent-penalty pattern as the negative-weight case, just triggered by a boundary value instead of an out-of-range one.

**Empty/degenerate profile (`genre_preferences={}`, `mood_preferences={}`)** — sanity check: does the system degrade gracefully with no genre/mood signal at all?

```
Top recommendations:

Velvet Confession (r&b/romantic) - Score: 48.00
Because: energy (0.50) close to your target (0.50); non-acoustic style matches your preference

Salt and Sirens (reggae/dreamy) - Score: 47.70
Because: energy (0.48) close to your target (0.50); non-acoustic style matches your preference; under-the-radar pick, matching your discovery preference

Night Drive Loop (synthwave/moody) - Score: 45.05
Because: valence (0.49) close to your target (0.50); non-acoustic style matches your preference

Storm Runner (rock/intense) - Score: 42.40
Because: valence (0.48) close to your target (0.50); non-acoustic style matches your preference

Iron Choir (metal/triumphant) - Score: 41.35
Because: valence (0.55) close to your target (0.50); danceability (0.60) close to your target (0.50); non-acoustic style matches your preference
```

**Finding:** no crash — this is the one edge case that behaves exactly as it should. With no genre/mood weights, the system degrades cleanly to ranking by audio-target closeness.

**Out-of-range target_energy (`target_energy=5.0`)** — same genre/mood/valence/danceability targets as the baseline profile, but `target_energy` set to 5.0 instead of 0.75:

```
Top recommendations:

Rooftop Lights (indie pop/happy) - Score: 72.06
Because: 'indie pop' genre matches your taste (0.95 affinity); 'happy' mood matches your taste (0.90 affinity); valence (0.81) close to your target (0.70); danceability (0.82) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Sunrise City (pop/happy) - Score: 68.28
Because: 'pop' genre matches your taste (0.80 affinity); 'happy' mood matches your taste (0.90 affinity); valence (0.84) close to your target (0.70); danceability (0.79) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Neon Cathedral (house/euphoric) - Score: 52.64
Because: 'house' genre matches your taste (0.50 affinity); 'euphoric' mood matches your taste (0.60 affinity); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Gym Hero (pop/intense) - Score: 50.46
Because: 'pop' genre matches your taste (0.80 affinity); valence (0.77) close to your target (0.70); danceability (0.88) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference

Night Drive Loop (synthwave/moody) - Score: 44.23
Because: 'synthwave' genre matches your taste (0.60 affinity); danceability (0.73) close to your target (0.75); non-acoustic style matches your preference; popular pick, matching your mainstream preference
```

**Finding:** compared to the baseline run, every score drops by exactly 20 points (Rooftop Lights: 91.86 → 72.06, Sunrise City: 86.88 → 68.28, Gym Hero: 66.86 → 50.46) and no song's explanation mentions energy anywhere — `energy_gap` saturates at ≥ 4 for every song (since real energies are 0-1), so `max(0, 1 - gap)` floors to 0 across the entire catalog at once. A single bad input silently zeroes out one-fifth of the scoring budget for every recommendation, with no error or indication that the target was invalid.

### Summary

The scoring function (`_score_song`) has no input validation anywhere — `genre_preferences`/`mood_preferences` weights, `discovery_bias`, and the `target_*` fields are all trusted to be within their documented `[0, 1]` ranges. When they aren't, the system doesn't fail loudly: it either produces scores far outside the documented "~0-100" scale (unbounded genre weight, out-of-range discovery bias) or silently disables a scoring dimension for the whole catalog (NaN/out-of-range targets) or for a single song (negative weights, boundary acousticness) without ever mentioning it in the explanation text. The one genuinely adversarial-looking case that behaved correctly was the fully empty preference profile, which degraded gracefully to ranking by audio-target closeness.

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



