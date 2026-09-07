# Creative style rules

Source: `master_Riteangle__marketing_requirement.docx` (tone of voice, ad-ready threads, visual
identity, product-data supplement, objection handling, production note). Everything here is subject to
`compliance.md` first — a strong line that trips a compliance rule doesn't ship.

## Tone of voice

**Do:** confident, precise, empathetic without softness, human, direct. Speak to lived frustration,
then offer the clear alternative. Translate anything technical into felt experience before it reaches
the ad — "the emotional heavy lifting is handled," not "we close the effort gap."

**Don't:** hype, salesy urgency, technical jargon (data gap / effort gap / vectors / game theory — these
are internal architecture language, never ad copy), money/provider language, ranking people,
"high-earning" claims, purchase language.

## Taglines

Primary: **"Meet who you actually want — in minutes, not months."**

Site-native alternatives (pick to match the specific hook, don't reuse the same one across every ad in
a set):
- No swipes. Ever. Just matches. *(also good trimmed to just "No Swipes. Ever." — see below)*
- We do the matching. You skip the work.
- Proven, not just claimed.
- A shortlist that means something — instead of a flood or a desert.
- Proof, never stored. Verified, then deleted.
- You finally have real choice. *(men)*
- You finally have a shortlist that means something. *(women)*
- The AI does the searching. You do the meeting.

**Retired 2026-09-07: "Verified, not vibes."** The app owner's call, made while cutting
`creatives/30secondsparks-founder-pitch`. Do not reach for it in new work. It is left listed nowhere
above on purpose — a retired line that stays in the list gets used.

What replaced it on that asset was **"No Swipes. Ever."**, which is not a new line: it is the
existing site-native "No swipes. Ever. Just matches." trimmed to its first half. Worth knowing
before anyone treats the trim as an invention needing approval.

**It was verified against the product before use, and that check is repeatable.** "No swipes" is an
absolute claim about behaviour, so it was checked rather than assumed: `SwipeCard.svelte` exists in
`pocket-dating-coach` but is never mounted anywhere, and the only other hit is an e2e test whose
body is `expect(true).toBe(true)`. The live Discover feed uses buttons — Admire, Notice me, like,
`Next`. If a swipe mechanic is ever shipped, this line dies with it.

**Two shipped build scripts still emit the retired line and have deliberately NOT been changed:**
`creatives/moveon-swagger-video/typeset_video.py` (FOOT_TAGLINE / END_TAGLINE) and
`creatives/moveon-properly-w2530/typeset.py`. Their assets are already live with it, and rewriting a
shipped creative's source so it no longer matches the asset in Ads Manager trades one problem for a
worse one. The consequence to know: **re-running either script re-emits a retired tagline.** Change
the constant at that point, not before. Campaign records and QA docs that quote the line are records
of what shipped and must not be edited at all.

## Ad-ready emotional threads (the strongest available hooks)

**This list is the `[HOOK]` vocabulary** that `naming.md` requires every ad name to draw from, so each
thread carries its slug. A hook that isn't here has no name yet — add the thread first, then name the
ad. Slugs are uppercase, hyphenated, no underscores (the ad name is underscore-delimited).

- **`CAMERA-JUDGE`** — the camera as a judge nobody appointed. "Don't judge a book by its cover," and
  yet the biggest decision of your life got handed to the camera.
- **`DESOLATE-MAN`** — months of silence, "like the Martian stranded on Mars," then one or two options
  that feel like being cornered rather than choosing.
- **`FOURTEEN-SUITORS`** — the flooded woman who closes the tab: fourteen suitors, no order, tab
  closed. An ordered shortlist is the product. *(Standing caveat as of 2026-08-27: the competitor scan
  suggests this persona may be inverted — the complaint observed is quality of what reaches her, not
  volume. See `research/questions/q-2026-08-27-is-the-riteangle-woman-flooded.md`. The thread is still
  ad-ready; the persona behind it is under review.)*
- **`VERIFIED-DELETED`** — proof that's verified, then deleted. He doesn't get points for saying it, he
  gets points for proving it, and she never sees the document.
- **`MONOTONIC-PROGRESS`** — progress that never slides backward. His standing is absolute and
  monotonic; he is never quietly losing to men he cannot see.
- **`MOVE-ON-PROPER`** — the breakup re-entry, in her register: moving on is not in question, *how* is.
  "Move on toh karna hai — par dhang se." Not crying, not partying — the deliberate middle that
  Tinder's breakup campaigns skip. The exit moment, where every thread above is an entry moment.
  *(Added 2026-08-27 — derived in-session, not from the source docx. Origin:
  `ideas/idea-2026-08-27-breakup-reentry-second-chapter.md`, approved by Sree after reviewing Tinder's
  Move On Salon creatives; learnings `lrn-2026-08-27-tinder-sells-the-breakup` and
  `lrn-2026-08-27-hinglish-is-shaadis-hook-mechanic`. Carries an unresolved risk: no comment-moderation
  policy exists for the hostility a breakup hook attracts — surface it again before anything is
  enabled.)*
- **`KNOW-YOUR-WORTH`** — the self-worth clapback: every label she's been handed ("too sensitive",
  "high-maintenance", "gaon ki ladki") flipped sarcastically into a statement of her value, refrain
  "Tumse na ho paayega." Worth is RECOGNIZED, never provided — the currency is standards, self-respect,
  freedom, ambition; never money (compliance rule #1 rebased this thread from a "you can't afford me"
  draft, see `creatives/girlboss-moodboard-w1830/text-treatment.md`). Distinct from MOVE-ON-PROPER (the
  exit moment) and BUILD-YOURSELF-FIRST: this is the identity moment — who she is, not what she left.
  *(Added 2026-09-01 — derived in a live session with Sree from a girlboss mood board; first asset is
  the "Tumse Na Ho Paayega" 28s video, `creatives/girlboss-moodboard-w1830/`. Same unresolved
  comment-moderation risk as MOVE-ON-PROPER: a sarcastic clapback hook invites hostile replies.)*
- **`BUILD-YOURSELF-FIRST`** — the MOVE-ON-PROPER "how" argument sharpened to one line: you can't
  change him, you can build yourself. Four women, four bad experiences, one shared turn, then six
  beats of self-development. Deliberately not "this happened because you weren't focused on
  yourself" — that reads as blaming her for being catfished. *(Added 2026-08-30, registering a slug
  that was already in production use: `VID_BUILD-YOURSELF-FIRST_A_20260830` shipped under this name
  before the thread was written down here, which is the gap this entry closes. Origin:
  `creatives/buildyourself-lead-w1830/brief.md`; QA `pass` on the shipped video recorded in that
  creative's `qa.md`.)*

## Quotable first-party stats — use these, not invented or industry-borrowed numbers

Measured from the live platform. **Quote rates and medians, never totals** — the platform is early, and
a median is true at any size; a total ("48 users") reads as small in a way a rate doesn't.

- Median time from signup to first match, for men: **12 minutes**. Fastest under three. 16 of 27
  matched men were matched inside the first hour. "Minutes, not months" is a measurement here, not a
  slogan.
- Median woman has **14 suitors** (busiest has 20) — this is the literal source of the "fourteen
  suitors, no order, tab closed" line above; it's first-party fact, not a borrowed industry claim.
- **54% of all messages sent on the platform were sent by an AI companion on someone's behalf** (737 of
  1,375) — the cleanest available way to quantify "the emotional heavy lifting is handled."
  matches came from the matchmaker (147), a Notice Me (27), or an invite (12) — matching, not swiping,
  is what actually produces relationships here.
- Membership runs **31 men : 17 women** (under 2:1) against Indian dating apps reported at 70–93% male
  — "gender-balanced community" is a claim this product can back with a number; most competitors
  cannot.
- 17 anonymous "Tips" (honest profile feedback) have already been left and used — this channel is live,
  not a roadmap item.

## Objection handling (for ad copy and comment replies)

| Objection | Response |
|---|---|
| "Another dating app?" | "No swipes. Ever. Just matches that mean something." |
| "AI will feel cold." | "The emotional heavy lifting is handled so you stay in control without the mental load." |
| "Why would men verify?" | The shortlist is ordered by verified fit, not by who gamed the photo. Verification is how you rise. |
| "Is this only for rich people?" | Identity-verified and established professionals. Money is never an attraction signal. |
| "What if the shortlist is still bad?" | Real match guaranteed. If a match goes quiet, we replace it. |

## Visual identity

- **Primary palette**: brand pink `#FF3B6B`, pink deep `#E11D54`, coral `#FF7A4D`, coral deep `#C2410C`.
- **Grounds/ink**: cream `#FFF3F0`, surface `#FBEEE9`, hairline `#EFDED7`, ink `#1B1020` for text.
- **The palette is light, on purpose** — every major rival ships a dark UI; in a feed of dark dating
  creative, cream reads as the differentiator before a single word. Don't default to a dark ad
  background out of habit.
- **Status colours are functional, not decorative**: amber `#F59E0B` = "worth a second look," red
  `#EF4444` = "red flag." Never use either as a plain accent colour.
- **Networking season** (a platonic-mode pause on dating) uses a calm teal instead of pink — any
  creative aimed at that audience/mode should be teal, not pink.
- Typeface: **Gabarito** throughout. Wordmark: lowercase **"riteangle"**, always — the lowercase and the
  "rite" spelling are what carry the pun; never capitalize it in creative.

## Production constraint — six seconds is short

This product's best moments are conversations (an AI vetting a man on her behalf, a coaching card, an
ordered shortlist) — they read beautifully as a still and are hard to convey in six seconds of Snap
motion without deliberately staging them. Plan for **purpose-built, scripted conversation assets**, not
generic lifestyle stock footage, with the emotional beat landing in the first two seconds. Build around
the emotional threads above.

## Turn a continuity break into an intended transformation

When a multi-scene cut can't hold one variable perfectly across every frame, don't fight it — **make
the change the story**. On the "Tumse Na Ho Paayega" cut (2026-08-30), two unavoidable breaks became
the arc:

- **Hair arc** — dark hair in the origin scenes, caramel in the travel/payoff scenes. Read as a
  glow-up, not a continuity error. Once it's deliberate, lock which scenes sit on each side of the turn.
- **Geography arc** — Indian-origin scenes → international-travel payoff, sold as *her* adventure (she's
  out in the world), never *someone took her there*. This keeps the "bigger life" promise clear of
  `compliance.md` rule #1: travel is her own journey, not being kept. Foreign tourists in the background
  sell "out in the world" without a provider cue.

The rule of thumb: a break the viewer would read as a mistake becomes an asset the moment the cut
*commits* to it as a before/after. Decide the turn point, then let every scene declare which side it's
on.

## Assets that already exist — brief from these, don't invent from a blank page

The product's own interface renders that already exist and can be used as creative reference: the
persistent AI status bar (on / taken-over states), the man's AI-conversation view, the hand-off banner,
the woman's ranked shortlist, the man's four-stage progress bar, the Date/Network mode toggle side by
side. Check with whoever holds the design mockups before commissioning new illustration for something
the product already shows.

## Competitive landscape (for `ad-ideation` / `ad-intake` reference)

- **Tinder** — volume + casual, playful/FOMO tone.
- **Bumble** — women-first, "make the first move," equality/kindness framing.
- **Hinge** — "designed to be deleted," prompts, quality over quantity.
- **Shaadi.com / Jeevansathi / BharatMatrimony** — marriage-first, family involvement, trust language
  undercut in practice by verification failures and scams (a real, sourced weakness to contrast against
  — see `compliance.md` before making any direct comparative claim).
- **Aisle** — "nothing casual about this dating app," high-intent premium positioning.
- **TrulyMadly / QuackQuack** — India-built, "photo-verified / no fake profiles" as the core claim,
  performance-heavy Meta spend.

Where to actually look at their live creative: Meta Ads Library (facebook.com/ads/library, filter to
India + active), Snap's public ads library/topic pages, Google Ads Transparency Center.
