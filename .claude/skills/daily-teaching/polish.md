# The Polish version

Every teaching goes out in two languages. The English is written first and is the record
the lore, the checks and the brief are kept against. The Polish is written straight after,
from it, in the same run and the same commit.

## A retelling, not a translation

Write the Polish as a Polish writer of this Church would have written the same teaching. It
must say the same thing, but it doesn't have to say it the same way.

- **Funny and clear beat faithful.** If a joke rests on English (a pun, an idiom, a very
  British detail), replace it with one that lands in Polish, or cut it and let the sentence
  do something else. A line that is correct but flat has failed. A line that has drifted but
  lands has not.
- **Keep the substance.** The ruling, the practice, what is decided, which witness said what,
  any lore planted or touched. A reader of either version should come away holding the same
  teaching. The Polish doesn't add lore, and doesn't drop any.
- **Keep the shape.** The same components in the same order, the same number of verses and
  litany lines, the same image. Sentence boundaries inside paragraphs are yours.
- **The register is Polish church officialese, played straight about absurd things:**
  parish notices, curial decrees, commission minutes, the proceedings of a diocesan synod.
  Polish has a rich stock of it: *orzeczono*, *postanowiono*, *przyjmuje się do
  wiadomości*, *w sprawie*, *na tle*, *odwołanie oddalone*, *wniebowstąpienie*, *czuwanie*,
  *schola*, *naczynie wybrane*, *okres zwykły*. When it fits naturally, a double meaning with
  liturgical Polish is the best joke available.
- **The voice is still self-deprecating and never smug.** The same rules as `style.md`
  (*Never*, *Practice and advice*) apply to the Polish exactly.

## Conventions

- **He, Him, His** → capitalised, as in Polish devotional writing: *On, Jego, Jemu, Mu,
  Niego, Nim, Go*. He is never quoted, in Polish either.
- **Brothers and sisters.** In running text write *brat Callum* and *siostra Aniela*. Use
  *br.* and *s.* in attributions and signatures (*— br. Tomasz*). Names stay as they are.
- **Numbers.** Four-digit numbers take no separator (*№ 4102*); larger ones take a space
  (*12 405*). Polish dates are written *2 października*.
- **Quotation marks.** Use „…” and nest ‚…’ inside them. The em dash — spaced — stays.
- **Forms of address.** Readers are *ty*, informal — but never gendered: no past-tense or
  conditional verb that assumes the reader is a man or a woman (*szukałeś*, *byś chciał*,
  *zapomniałaś*). Write around it: *czegokolwiek tu szukano*, *niż by się chciało*, *co
  inaczej wyleciałoby ci z głowy*. The Church speaks of itself as *Kościół*, and its royal
  *My* is used as sparingly as the English *We*.
- **The Book.** The record the teachings are entered in is *Księga*, capitalised, like the
  seal *Wpisano do Księgi*.
- **Words to use:** teaching → **kazanie** (*kazania*, *kazań*); sighting → **objawienie** (as in
  an apparition — *objawienia*, *objawień*; never *widzenie*);
  sacred image → **święty obraz**; the wall → **ściana**; the Prophet → **Prorok**; the
  Church → **Kościół**; the book → **księga**; the archive → **archiwum**; mount →
  **wierzchowiec**; the bread hat → **chlebowa czapka**; garlic sauce → **sos czosnkowy**;
  ring road → **obwodnica**; the Eternal Orbit → **Wieczna Orbita**; imprimatur → stays
  *imprimatur*.
- **Feasts** go by their names in `data/l10n/pl/calendar.toml`. The brief prints today's.

## Proofreading

The Polish is proofread every day, as its own pass, after it is written — slowly, sentence
by sentence, as a native editor would, not as a translator checking meaning. These are the
mistakes that have actually been made here; look for each one:

- **Case government.** Check the case every verb and preposition takes: *nauczać czegoś*
  (so *Czego nauczał*, never *Co nauczał*), *pokazywać palcem **na** coś*, *dotyczyć
  czegoś*, *zależeć od*, *brakować czegoś*. Negation takes the genitive (*nie ma chleba*).
- **Agreement.** A subject and its verbs and participles agree in gender and number all the
  way through a sentence. A sentence that starts with *jedno kazanie* doesn't end with
  *gdy są niewygodne*. With numerals of five and above the subject takes the genitive:
  *wszystkich pięć kazań*, *pięć kazań czeka*.
- **Impersonal forms need no subject; participles do.** *Spisano bez poprawek* can't go on
  to *tak jak zostało objawione*. Use *Spisane bez poprawek, tak jak zostało objawione*.
- **Commas.** There is no comma before a single *i*, *oraz*, *lub* or *albo* joining two
  clauses, unless it closes an insertion or the conjunction is repeated (*i nie spieszył
  się, i nie spóźnił*). There is always a comma before *że*, *który*, *gdy*, *żeby*, *bo*,
  *a* and *ale*. An address takes an exclamation mark or a comma, never a colon
  (*Czcigodni Bracia i Siostry!*).
- **Mixed lists.** Don't mix *albo … czy …* in one list. After *nie jest*, a list of things
  something isn't runs *ani …, ani …, ani …*.
- **Calques.** English word order, English idioms taken literally (*powiedz jedną miłą rzecz
  w dół*), and nouns where Polish would use a verb. If a sentence could only have come from
  English, rewrite it.
- **Ambiguity.** A Polish word that means something else too: *objaw* as an imperative
  reads as *symptom*. Pick another word unless the double meaning is the joke.
- **Titles.** The title has to carry the English title's idea *and* sound like a Polish
  title. Where it can, echo Polish biblical or liturgical phrasing (*Tu rozpoczyna się
  Księga*).

If you can start a subagent, have it do this pass with fresh eyes. Give it the Polish file,
the English original and this section, and ask for corrections as "before → after". Run it
in the foreground and wait for its answer — the run must not move on, or end, while it is
still working. Then apply the ones you agree with. If it fails or returns nothing, or you
cannot start one, do the pass yourself, after writing everything else, and read each
sentence twice.

## Front matter

`content/teachings/YYYY-MM-DD-<slug>.pl.md`, beside the English file:

| Field | Polish version |
|---|---|
| `slug`, `date`, `draft`, `form`, `image`, `tags` | **copied exactly from the English.** Polish URLs mirror the English, and `teaching.py check` fails if any of these differ |
| `title`, `summary`, `standfirst`, `caption`, `note`, `signoff` | written in Polish |
| `seal` | Polish, 24 characters or fewer, like the English |
| `feast` | the Polish name of the same observance (from the brief); left out when the English leaves it out |

The summary still has to work on its own in 150 characters.

## Links

Markdown links from the root go to the Polish site: `/pl/images/`, `/pl/faith/`, `/pl/`,
`/pl/teachings/YYYY-MM-DD/<slug>/`. `teaching.py check` fails on any root link outside
`/pl/`.

## The slips and the calendar

- `content/_index.pl.md` has the same three panels as `content/_index.md`, and every panel
  you rewrite in English is rewritten in Polish the same day, with the same `updated`.
- **The litany** is written for Polish, not translated: call and response in the shape of a
  Polish litany (*Kocie na kebabie — jedź przed nami*). Keep the number of lines and what
  they draw on.
- **The calendar slip** names the same days in the same order, bold where the English is
  bold. The leads are Polish abbreviations: **Pn Wt Śr Cz Pt Sb Nd**. Use the `short` names
  from `data/l10n/pl/calendar.toml`. A lesser observance that exists only on the slip gets a
  Polish name of your own.
- **Signs & Wonders** covers the same sightings, each written the way it would be reported in
  Polish.
- The handwritten `note` is lowercase and casual. When the English note changes, give the
  Polish one its own line instead of a translation.
- **Whatever you add to `data/calendar.toml`** (a `dated` observance, or rarely a change to
  `weekly`) gets its Polish `name`, `short` and, for `weekly`, `when` in
  `data/l10n/pl/calendar.toml` in the same commit. Weekly entries are keyed by `day`,
  `[weekly.Fri]`. Dated entries are keyed by date, `[dated."2026-10-04"]`.
- `data/l10n/pl/images.toml` is kept by hand, like the English catalogue. Never edit it.
