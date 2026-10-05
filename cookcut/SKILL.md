---
name: cookcut
description: CookCut turns a reference image of a finished result plus a step-by-step source (recipe, assembly guide, manual, craft tutorial) into segmented AI-video prompts sized to the chosen video model's real clip-length limit (Seedance 2.0 / 2.5, Google Flow / Veo, Kling, Runway, etc.), then either sends them to a connected video-model tool or outputs copy-paste scripts. Use this whenever the user types /cookcut, or asks to turn a recipe, cooking steps, DIY or assembly instructions, or a tutorial into an AI-generated video, a "how it's made" clip, a short-form cooking reel, or video-model prompts — even if they don't name the skill.
---

# CookCut

CookCut converts **"here's what it should look like" + "here's how it's made"** into a ready-to-generate, multi-clip AI video script. The core problem it solves: video models cap each generation at a fixed length (e.g. 8s or 15s), so a 30s video has to be planned as several clips that cut together cleanly, with the same dish, hands, surfaces and lighting in every one.

The reference doesn't have to be food. A finished bookshelf, a knitted hat, an assembled LEGO set — "dish" below means "the finished result".

## Step 1 — Collect the five inputs

Look at what the user already gave you, and only ask for what's missing. When `AskUserQuestion` is available, ask the missing items in one round (it takes up to 4 questions; put the first two inputs in a plain-text request if they're missing, since they're uploads/pastes, not choices).

1. **Reference image** of the finished dish/result. Required — it is the visual anchor for every clip. If missing, ask for it. If they truly have none, offer to proceed from a written description and flag that consistency will be weaker.
2. **Step-by-step source** — recipe, assembly guide, manual, craft tutorial, a URL, a PDF, or pasted text. If it's a URL, fetch it. If it's a file, read it.
3. **Target video length** in seconds (e.g. 10s, 30s, 60s). Suggested options: 10s, 15s, 30s, 60s.
4. **Video model** — e.g. Seedance 2.0, Seedance 2.5, Google Flow (Veo 3.1), Kling, Runway, Sora. Accept whatever they name.
5. **Delivery mode** — ask explicitly:
   - "Send to the video model directly" through a connected connector / MCP tool, or
   - "Just give me the scripts" for copy-paste.

Also worth asking in the same round if unclear (but default sensibly rather than blocking): aspect ratio (default 9:16 for social reels), whether to include audio/voiceover (default: ambient kitchen/workshop SFX, no voiceover), and on-screen text language.

## Step 2 — Check the model's current limits online

Model specs change every few months (Seedance went 15s → 30s between 2.0 and 2.5; Veo is 8s per clip). Don't trust memory. Search before planning:

- `WebSearch` for "<model name> max video duration per generation" and "<model name> duration options". Prefer the vendor's own docs or API reference; reseller pages (Runway, Artlist, fal, Replicate) are fine as a second source, but note that a reseller can cap below the model's native limit — if the user named a platform, use **that platform's** limit.
- Record, for this run:
  - **max seconds per generation**
  - **allowed durations** — some models accept only fixed values (e.g. Veo: 4/6/8; Seedance 2.0 API: 4–15 with some platforms restricting to 4,5,6,8,10,12,15). Use the exact list if found.
  - **image-to-video / reference-image support**, and first/last-frame control
  - **extend / continue** support (Flow's Extend, Seedance multi-round extension)
  - **timestamp-level prompting** support (Seedance 2.5 accepts per-timestamp instructions)
  - **native audio** support
  - known content restrictions (e.g. Seedance restricts realistic human faces in reference images → keep shots hands-only)
- Tell the user the limit in one line with the source, e.g. "Seedance 2.0 caps at 15s per clip (Runway docs), so 30s = 2 clips."

If search fails or is unavailable, fall back to `references/models.md` (a dated snapshot) and say clearly that the limit is unverified.

## Step 3 — Plan the segments

Run the bundled planner so the split is exact and respects the model's allowed durations:

```bash
python scripts/plan_segments.py --total 30 --max 8 --allowed 4,6,8
python scripts/plan_segments.py --total 30 --max 15            # any integer 1..max allowed
python scripts/plan_segments.py --total 30 --max 15 --min 4    # continuous range 4..15
```

It returns the fewest clips that reach the target, as even as possible, and reports any over/under-shoot (e.g. 30s on Veo → 8+8+8+6). If the target is under the model's max, it's one clip — say so, don't split for the sake of it.

If the model supports **extend** and the user prefers it, you can plan one base clip plus extensions instead of independent clips; the planner's numbers still tell you how many passes.

## Step 4 — Read the reference image and build a continuity bible

Study the image closely and write a short **continuity bible** — the facts every clip must repeat word-for-word so the model renders the same scene each time:

- The finished dish: components, colors, textures, garnish, sauce, portion, how it's arranged
- Vessel / plate / board: material, color, shape
- Surface & background: countertop, cloth, props
- Lighting: direction, warmth, time of day
- Camera language: overhead vs 45° vs eye-level, lens feel (macro, shallow DOF)
- Hands: if shown, skin tone, sleeves, nails/rings — or "hands only, no faces"
- Style: e.g. "bright natural-light food reel", "moody dark-wood cinematic"

Copying this block into every prompt is the single biggest lever for cross-clip consistency, so keep it tight (40–80 words) and concrete.

## Step 5 — Condense the steps into visual beats

Video models show actions, not instructions. Turn the source into **visual beats** — moments that look different on screen.

- Drop non-visual steps (preheat the oven, wait 2 hours, read safety notes) or compress them into a visual cue (oven light on, a quick timer close-up).
- Merge near-identical steps (chop onion, chop garlic → "chopping aromatics").
- Compress time: simmering for 40 min becomes one 2-second shot of a bubbling pot.
- Budget roughly **2–4 seconds per beat**; a 15s clip holds 3–5 beats, an 8s clip 2–3.
- **The final clip always ends on the hero shot that matches the reference image** — that's the payoff. If there's room, open clip 1 with a 1–2s teaser of the finished result too (common in food reels).
- If the source has more beats than the length can hold, keep the most visually distinctive and tell the user what you cut.

Distribute beats across the planned segments so each clip has a clear mini-arc and **ends on a handoff frame** — a stable, describable composition the next clip opens on (e.g. "pan of golden onions, wooden spoon resting at right, overhead").

## Step 6 — Write the scripts

Read `references/prompt-formats.md` for the model-specific prompt shape (Seedance, Veo/Flow, generic). Every segment gets:

```
CLIP n/N — Xs — [model] — [aspect ratio] — [audio on/off]
Input: [text-to-video | image-to-video with reference image | first frame = last frame of clip n-1]

Continuity: <the continuity bible, verbatim>

Shots:
0–3s  — <shot type> · <action> · <camera move>
3–6s  — ...
...

Ends on: <handoff frame description>
Audio: <SFX / ambient / voiceover line, if enabled>
Avoid: <faces, text artifacts, extra hands, utensils changing, morphing food, etc.>
```

Writing guidance:
- Describe **physical action with verbs and objects** ("knife slices a tomato into thin rounds") rather than intent ("prepare the tomato").
- One camera move per shot. Name it: slow push-in, overhead static, top-down pour, macro rack-focus.
- Keep subjects the model struggles with simple: two hands max, no reflections in knives, no readable text on packaging.
- For image-to-video models, say which image to attach: the reference image for the hero clip; for earlier clips, either the reference image as a style reference or the previous clip's last frame as the first frame.
- Write prompts in English unless the model or user prefers otherwise; put any on-screen captions (e.g. Traditional Chinese step labels) in a separate "Captions" line for adding in an editor, since models garble on-screen text.

## Step 7 — Deliver

### Mode A: send to the video model directly

1. Look for a tool that can generate video with the chosen model: check the tools you already have, then `ToolSearch` (keywords: the model name, "video generation", "seedance", "veo", "flow", "kling", "runway", "fal", "replicate"), then `SearchMcpRegistry` with the same keywords. If a registry match exists but isn't connected, show it with `SuggestConnectors`.
2. If nothing connected can reach that model, say so plainly in one line and fall back to Mode B — don't block the user.
3. Video generation costs credits. Before the first call, show the plan (N clips, durations, model, resolution) and get a clear yes. One approval can cover the whole batch if the user says so.
4. Generate clips **in order**. When the tool supports a first-frame/image input, pass the previous clip's last frame (or the reference image for the hero clip). Pass the continuity bible every time.
5. Collect the returned files or links, send them to the user, and note any clip that drifted (wrong plate, changed garnish) with a suggested re-roll prompt tweak.

### Mode B: copy-paste scripts

- Output each clip in its **own fenced code block** so it copies cleanly, preceded by a one-line settings header (duration, aspect, input image).
- If the user will keep or share the scripts, also save them as a document (the session's docs type if available, otherwise a markdown file) so they aren't lost in chat.

### Always include (both modes)

- **Assembly notes**: clip order, where to trim overlaps (usually 0.2–0.5s at each cut), and that captions/music go on in the editor (CapCut, Premiere, etc.).
- A one-line summary: target length, actual length, clips × durations, model limit and where it came from.

## Edge cases

- **Target shorter than the model's minimum** (e.g. 3s on a 4s-min model): generate the minimum and tell the user to trim.
- **Very long target** (e.g. 2 minutes on an 8s model = 15 clips): flag the consistency risk, suggest an extend-capable model (Seedance 2.5, Flow Extend) or a shorter cut, then proceed if they confirm.
- **Source with dangerous steps** (deep-frying, blowtorches, power tools): fine to depict, but don't invent unsafe shortcuts the source didn't include.
- **People in the reference image**: keep generated shots hands-only unless the user explicitly wants a person on camera and the model allows it.
- **Model the user named doesn't exist / is ambiguous** ("Seedance 3", "Flow"): search; if it resolves (Flow → Veo 3.1), say what it resolved to; if not, ask.
