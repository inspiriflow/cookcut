# Video model limits — fallback snapshot

**Snapshot date: 2026-10-05.** Use this only when a live search in Step 2 fails. Always tell the user these numbers are from a snapshot and may be out of date. Platforms that resell a model may cap it lower than the native limit.

| Model | Max per generation | Allowed durations | Image input | Extend / chain | Notes |
|---|---|---|---|---|---|
| Seedance 2.0 (ByteDance) | 15s | 4–15s on most platforms; some APIs only accept 4, 5, 6, 8, 10, 12, 15; also "auto" | Text, image (first/last frame), up to 9 reference images + video + audio refs | Video extension supported | Native audio. Restricts realistic human faces in reference inputs. Fast / Mini variants exist with lower resolution caps (Mini: 5s on some platforms). |
| Seedance 2.5 (ByteDance, Jul 2026) | 30s | Check platform | Text, image | Multi-round extension to multi-minute | Accepts timestamp-level instructions (what happens at 0–3s, 3–5s, etc.) |
| Google Flow / Veo 3.1 | 8s | 4, 6, 8 | Image-to-video; first/last frame ("Frames") mode | Flow "Extend" adds ~7s per pass, up to ~148s total; Veo 3.1 and 3.1 Fast only, not Lite | Native audio. Extension locks reference images — continuity comes from prompt + last frames. |

Models not listed (Kling, Runway Gen-4.x, Sora, Hailuo, Wan, Pika, etc.): always search; don't guess.
