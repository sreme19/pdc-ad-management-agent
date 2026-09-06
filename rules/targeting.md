# Targeting rules

Source: `master_Riteangle__marketing_requirement.docx` ("Audience Personas," "Market Map," India
evidence) and Sree's Jul 30 / Aug 5 / Aug 7 logs. `ad-setup-loop` picks one persona (or a named
combination) per ad set — never a generic "everyone" audience.

## The provider-energy distinction — read this before anything else here

Women in the casual segment (18–24/18–22 in the notes) genuinely respond to "provider energy" — a
partner who is well-networked, can plan and fund an experience, is financially capable. That is a real
preference the matching backend is allowed to weigh. **It must never appear in ad copy, implied or
otherwise** (see `compliance.md` rule #1). The resolution the marketing knowledge base itself proposes
(an explicitly open hypothesis, H2): sell the *verified lifestyle / social-currency* signal instead —
travel history, being into cars/gadgets/tech, an established career — never money itself. "Someone who
has traveled to 30 countries" is fine; "someone who can afford to fly you anywhere" is not.

## Core audience bands

- **Women 18–30, Men 25–38** — the priority band per the Aug 7 playbook, currently live in ad sets.
- Two age-differentiated creative treatments for women specifically (Aug 5 note):
  - **18–22**: ads should telegraph wild experiences — partying, travel, adventure, social energy.
    "Stop scrolling through guys who just want attention" — hard-hitting, feminist-coded copy tests
    well here (Aug 9 note).
  - **25–30**: ads should telegraph security, safety, and loyalty instead.
- Men 30–40 with a financial/career signal ("they will have money → get very good signups" — Sree's
  Jul 30 note) convert well as a segment, but **the ad copy selling to men never says this about
  themselves either** — it's a targeting/interest-list signal (career, tech, travel history, gadgets,
  cars as *interest categories* Snap/Meta can target on), not a line of ad copy.

## Personas (pick one per ad set, name it in the ad-set naming slug)

1. **The Invisible Man** (`INVISIBLE-MAN`) — 28–38, career/education-focused, not skilled at
   photo-gaming, months of near-zero matches ("like the Martian on Mars"), wants real choice. Language
   cues: "I'm done with this," "nothing happens," "only the good-looking guys get replies."
2. **The Flooded Woman** (`FLOODED-WOMAN`) — 25–35, romance/marriage-minded, 100–200 matches in 30
   minutes with no practical filter beyond photos, wants a shortlist that actually means something.
   Language cues: "Everyone is the same," "I closed the tab," "I'm exhausted."
3. **The Second-Chapter Person** (`SECOND-CHAPTER`) — post-divorce or late-30s+, wants seriousness
   without family-mediated matchmaking, distrusts both casual apps and traditional matrimony sites.
4. **The Casual but Selective Woman** (`CASUAL-SELECTIVE`) — 18–28 (see age split above), wants
   physical + verified lifestyle/social-currency signal without labels, needs efficient filtering
   without reading 200 profiles. This is the persona where the provider-energy distinction above
   matters most.

## Geography

**Bangalore first**, then Delhi/Hyderabad — this is where the platform's own membership already
concentrates (Bangalore leads by a wide margin per first-party data; Delhi, Hyderabad, Rudrapur follow).
An Indonesian cohort exists too (Kota Malang, Kota Bandung) but is not the current ad-spend priority.
Open question the source docs flag and leave unresolved (Sree's Jul 30 note): whether to concentrate
further in already-penetrated metros or test a Tier-2 city (e.g. Indore) — treat this as a live
hypothesis for `ad-ideation`, not a settled call.

**A new country is a budget question before it is a targeting question.** Inventory price is not
constant across markets and the difference is not marginal: the first Thailand test bought
impressions at a **₹348 CPM against India's ₹6.50–₹12.85**, so the standing ₹300/day default bought
772 impressions and 3 swipes — a non-answer that reads like a creative failure. Before proposing an
ad set in a market this account has not run in, go to `budget.md`'s "A market's price is a budget
input" section and size the budget against that market's own CPM. Thailand is currently **untested,
not rejected** (`lrn-2026-09-07-snap-thailand-cpm-is-27x-india`).

## Other targeting parameters

- Separate ad sets by gender — never a mixed-gender ad set. The gender goes in the ad-set name as a
  whole token (`WOMEN_18-22_CASUAL_LPV`) — `ad-agent propose` reads it from there to run the
  destination gate, so a name without one is rejected.
- **The destination has an audience too.** A page written in the second person to a man does not
  become a women's landing page because a women's ad points at it. `rules/destinations.yaml` records
  whose POV each page occupies and `propose` enforces the match — see that file for why (98% of
  lead-form submissions and 100% of `/get` store taps were men).
- Lifestyle interest categories that map to the personas: Dating & Relationships, Travel, Lifestyle,
  Career/Tech, Nightlife.
- Android-heavy device targeting where the platform allows it (the Play Store listing is the primary
  install destination; iOS is TestFlight open testing).
- Because the current objective is traffic to a web landing page (not app install), **broader
  audiences often outperform narrow ones early** — let the platform's own delivery algorithm find who
  actually swipes up and stays on the page rather than over-constraining the audience up front.

## Focus: dating funnel, evolving toward matrimony framing

Aug 14 note: "Current focus: Dating → matrimony" — campaigns today sell the dating/casual-to-relationship
funnel; matrimony-framed creative is a direction to grow into, not the current default.
