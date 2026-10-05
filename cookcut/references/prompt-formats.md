# Prompt formats by model

Use the shape that matches the chosen model. Every format still carries the continuity bible verbatim and ends on a described handoff frame.

## Seedance 2.0

Seedance follows structured, specific prompts. Order: **shot type → subject → action → environment → lighting → style**. It handles multi-shot within one clip, so list shots in order with rough timing.

```
[Reference: attach reference image as style/consistency reference]
Continuity: <bible>

Multi-shot, <N>s, 9:16.
Shot 1 (0–4s): Overhead close-up. Two hands crack an egg into a white ceramic bowl. Static camera.
Shot 2 (4–8s): 45° macro. Whisk beats eggs to a pale froth. Slow push-in.
Shot 3 (8–12s): ...
Ends on: <handoff frame>.
Audio: crisp whisking, soft kitchen ambience. No music, no speech.
Avoid: faces, readable text, extra hands, utensils changing shape.
```

- Keep humans hands-only — Seedance restricts realistic faces in reference inputs.
- For a later clip, attach the previous clip's last frame as the first frame when the platform allows it.

## Seedance 2.5

Same as 2.0, but use **timestamp-level instructions** — 2.5 follows per-timestamp direction precisely, which is the cleanest way to place beats inside a long (up to 30s) clip.

```
Continuity: <bible>

[0–3s] Overhead. Hands lay dough on floured walnut board. Static.
[3–7s] 45°. Rolling pin flattens dough into a disc. Slow pan left.
[7–10s] ...
[27–30s] Hero: <matches reference image exactly>. Slow push-in, hold.
Audio: [0–10s] rolling, flour dust; [10–30s] sizzle...
Avoid: ...
```

- If chaining with multi-round extension, write each extension as its own timestamped block starting at 0s, and open with "Continue from previous frame:" plus the handoff description.

## Google Flow / Veo 3.1

Veo clips are short (4/6/8s), so **one to three shots per clip**. Veo responds well to cinematic, sentence-style description with the camera move stated up front. Audio cues go in the prompt in plain language.

```
Continuity: <bible>

A 45-degree slow push-in on a cast-iron pan as hands drop sliced garlic into shimmering olive oil; the garlic sizzles and turns pale gold. Warm side light from the left, shallow depth of field.
The clip ends on the pan of golden garlic with a wooden spoon resting at the right edge.
Audio: loud sizzle, faint kitchen ambience, no music, no dialogue.
```

- Use **Frames** mode (first/last frame) when you want a clean handoff: set clip n's first frame to clip n-1's last frame; set the final clip's last frame to the reference image.
- If using **Extend** instead of separate clips: each extension prompt describes only what happens next (~7s), repeats the continuity bible, and can't take new reference images.
- Choose duration from 4, 6, 8 only.

## Generic (Kling, Runway, Sora, Hailuo, Wan, others)

When no model-specific format applies:

```
Continuity: <bible>
Duration: <X>s · Aspect: <ratio> · Input: <text | image + which image>
Shot list:
1. (0–Xs) <shot type> — <action> — <camera move>
2. ...
Ends on: <handoff frame>
Audio: <if supported>
Negative: <faces, morphing, extra hands, text>
```

Search the model's prompting guide in Step 2 if time allows and adapt; some (e.g. Kling) also take a separate negative-prompt field.
