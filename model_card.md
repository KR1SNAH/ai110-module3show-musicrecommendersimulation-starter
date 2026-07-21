# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

I named my model VibeMatcher.

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

Generates a ranked top-5 list of songs from a small fixed catalog by comparing a user's stated taste profile (favorite genres/moods, target energy/valence/danceability, acoustic preference, mainstream-vs-niche bias) against each song's attributes. It assumes the user can honestly state numeric preferences up front. It has no listening history, skips, or feedback loop. This is a classroom simulation, not a production system: the catalog is tiny (20 songs) and hand-labeled.



## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Every song has a genre, mood, and a few 0–1 audio traits (energy, valence, danceability, acousticness) plus a popularity score. A user's profile lists how much they like different genres and moods (not just one favorite), plus their ideal energy/valence/danceability and whether they want mainstream or under-the-radar picks. For each song, the model adds up points for: genre match, mood match, how close the song's energy/valence/danceability are to the user's targets, whether its acoustic style fits, and whether its popularity fits the user's mainstream/niche preference. Songs are sorted by total score and the top 5 are returned with a plain-English explanation built from whichever signals matched.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

20 songs, 17 different genres (lofi appears 3 times, pop twice, everything else once), 16 different moods. I didn't add or remove any songs — all testing used the existing data/songs.csv as-is. Missing from the dataset: no lyrics/language, no tempo actually used in scoring (it's loaded but never scored on), no listening-history or skip data, no world-music/non-English genres beyond reggae, and no way to represent a song that blends multiple moods or a playlist-level "arc" (e.g., building energy over a set).

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

Works best for users whose favorite genre/mood already has good representation in the catalog and whose energy/valence/danceability targets line up with what's actually popular (e.g., the baseline "happy, upbeat pop fan" profile produced picks that matched intuition well). The weighted-affinity design (rather than a single favorite genre) reasonably captures "I like X most, Y a little" rather than an all-or-nothing filter. The explanation text is genuinely traceable back to the math, which is a real strength for transparency, when it isn't hiding a mismatch (see Limitations).

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One weakness I found while testing adversarial profiles is that `discovery_bias` and `target_energy` are not actually independent signals, because in this catalog energy and popularity are strongly correlated (Pearson r ≈ 0.80: the calmest songs, like the classical and ambient tracks, are also the least popular, while the highest-energy songs are the most popular). I tested a "calm but mainstream" profile (`target_energy=0.3`, `discovery_bias=0.0`) against a "high-energy mainstream" profile (`target_energy=0.9`, `discovery_bias=0.0`) and found that the high-energy user's top picks were genuinely close to their target energy, but not a single song in the calm user's top 5 was close enough to trigger the "energy close to your target" reason at all. The genuinely calm songs in the catalog (classical, ambient, country) never surfaced for that user because their low popularity dragged their score down below higher-energy songs with a better popularity match. In other words, the system can satisfy "energetic and popular" or "calm and niche," but "calm and mainstream" is a user type it structurally cannot serve well with this catalog, even though nothing about that combination of preferences is unreasonable. This isn't a bug in any single line of scoring code — it's an emergent bias from two independently-reasonable signals interacting with a skewed catalog.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Here's a simple way to think about the whole evaluation: imagine explaining to a friend why "Gym Hero," a high-energy pop workout track, keeps showing up for someone who told the app they just want "Happy Pop." The app doesn't require a song to match everything you asked for - it hands out partial credit for each thing it *does* match (genre, mood, energy, valence, danceability, acoustic style, popularity) and just adds it all up. "Gym Hero" is pop (a genre match) and has energy/danceability close to what a typical pop fan wants, and it's popular, so it racks up a big score even though its mood is labeled "intense," not "happy," and gets zero credit for mood. A song that actually felt "happy" but was a weaker genre/energy match could easily lose to it. That single idea - the system rewards *whichever* signals happen to line up, not all of them together - explains a lot of what showed up in testing below.

I tested the recommender with a baseline "normal" profile (the one shipped in `src/main.py` - a happy, upbeat pop/indie-pop fan who leans mainstream) plus several deliberately unusual or extreme profiles, to see whether the scoring logic could be tricked or would quietly do something weird: an unbounded genre weight (100 instead of the expected 0-1), a negative genre weight, an out-of-range discovery bias, a NaN energy target, a target that landed exactly on the acoustic/non-acoustic boundary, a completely empty preference profile, an out-of-range energy target, and a few "opposite" pairs designed to isolate one variable at a time (calm-vs-energetic, niche-vs-mainstream, eclectic-vs-monolithic taste).

What surprised me most was that the system rarely crashes or does anything obviously broken - it just quietly reallocates points in ways a user would never notice from the explanation text alone. The comparisons below each isolate one changed variable so the "why" is clear.

**Baseline (happy pop, mainstream) vs. unbounded genre weight (pop set to 100 instead of 1.0):** Cranking one genre weight from a normal value up to 100 took two only-okay-fit pop songs and rocketed them to scores over 2,500, burying every other song in the catalog no matter how well it matched everything else. This makes sense once you know genre affinity is just multiplied straight through with no upper limit - but it means one confident typo (100 instead of 1.0) can completely take over the recommendations.

**Baseline vs. out-of-range energy target (5.0 instead of 0.75):** Every single song's score dropped by exactly 20 points, and not one explanation mentioned energy anymore. Real songs only go up to about 1.0 on the energy scale, so a target of 5.0 can never be "close" to anything - the entire energy portion of the score quietly zeroed out for the whole catalog at once. It's logical given the math, but a user would have no way to know a fifth of the scoring just vanished.

**Negative genre weight (dislikes lofi) vs. a neutral profile with no opinion on lofi at all:** Both profiles produce explanations that never say the word "lofi" - but one is secretly subtracting 25 points from every lofi song, while the other is just giving it zero. Reading the explanation alone, you can't tell "the app knows you dislike this" apart from "the app has no idea what you think of this." That's consistent with how the code only writes down *positive* matches, but it hides real information a user would probably want to see.

**Calm + mainstream listener (energy target 0.3, wants popular songs) vs. energetic + mainstream listener (energy target 0.9, wants popular songs):** Changing only the energy target flipped everything. The energetic listener's top picks (Storm Runner, Iron Choir, Crimson Static) were genuinely close to their target energy and popular at the same time - the two goals reinforced each other. The calm listener's top five never once earned the "close to your target energy" credit, because in this catalog the calmest songs (classical, ambient) also happen to be the least popular, so they got outranked by mid-energy songs that were more popular. It makes sense once you see how this particular set of 20 songs happens to be built, but it means "I want something calm and popular" is a request this system just can't satisfy well here, even though it's a perfectly reasonable thing to want.

**Eclectic taste (seven genres liked at 0.4 each) vs. monolithic taste (one genre liked at 1.0):** Scored against the exact same song, a perfect match on every other measure, the eclectic profile came out 15 points lower (62.66 vs. 77.66) than the monolithic one - purely because it spread its enthusiasm across many genres instead of picking one favorite at full strength. This is expected given the math (weaker numbers earn weaker credit), but it means two people who both genuinely love a song can get very different scores just because of how they chose to rate their other, unrelated interests.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

Clamp/validate all inputs (genre weights, discovery_bias, targets) to their documented 0–1 ranges.
Let users specify a range or "don't care" for energy/valence/danceability instead of one exact target.
Add a diversity step (e.g., MMR) so the top-5 doesn't cluster so tightly on the same audio profile.
Normalize genre/mood weights so spreading affinity across many genres isn't penalized versus picking one favorite.
Surface negative/mismatched reasons in the explanation, not just positive matches.

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
