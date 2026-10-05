#!/usr/bin/env python3
"""Split a target video length into the fewest clips a video model can generate.

Examples:
  python plan_segments.py --total 30 --max 8 --allowed 4,6,8     # Veo: 8+8+8+6
  python plan_segments.py --total 30 --max 15                    # Seedance 2.0: 15+15
  python plan_segments.py --total 45 --max 15 --min 4            # 15+15+15
  python plan_segments.py --total 10 --max 15 --allowed 4,5,6,8,10,12,15
"""
import argparse
import itertools
import json


def allowed_values(max_s, min_s, allowed):
    if allowed:
        vals = sorted({int(v) for v in allowed.split(",") if v.strip()})
        return [v for v in vals if v <= max_s]
    return list(range(max(1, min_s), max_s + 1))


def plan(total, vals):
    """Fewest clips; then smallest |actual-total| (prefer shortfall-free); then most even."""
    if not vals:
        raise SystemExit("No allowed durations.")
    best = None
    max_clips = -(-total // vals[0]) + 1  # ceil(total/min)+1 safety bound
    for n in range(1, max_clips + 1):
        cands = []
        for combo in itertools.combinations_with_replacement(sorted(vals, reverse=True), n):
            actual = sum(combo)
            diff = actual - total
            cands.append((abs(diff), diff < 0, max(combo) - min(combo), combo, actual))
        # Accept this clip count only if something reaches the target (>= total) or hits it exactly.
        reachable = [c for c in cands if c[4] >= total]
        if reachable:
            best = min(reachable, key=lambda c: (c[0], c[2]))
            # Also consider an exact/near-under plan at same n if strictly closer
            near = min(cands, key=lambda c: (c[0], c[1], c[2]))
            if near[0] < best[0] and near[0] <= 1:
                best = near
            break
    _, _, _, combo, actual = best
    return list(combo), actual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, required=True, help="target video length in seconds")
    ap.add_argument("--max", type=int, required=True, help="max seconds per generation")
    ap.add_argument("--min", type=int, default=1, help="min seconds per generation")
    ap.add_argument("--allowed", default="", help="comma list of exact allowed durations")
    a = ap.parse_args()

    vals = allowed_values(a.max, a.min, a.allowed)
    if a.total <= vals[0]:
        clips, actual = [vals[0]], vals[0]
    elif not a.allowed:
        # Continuous range: fewest clips, split as evenly as possible.
        n = -(-a.total // a.max)
        base, extra = divmod(a.total, n)
        clips = [base + 1] * extra + [base] * (n - extra)
        if min(clips) < vals[0]:  # can't go below the model minimum
            clips = [max(c, vals[0]) for c in clips]
        actual = sum(clips)
    else:
        clips, actual = plan(a.total, vals)

    timeline, t = [], 0
    for i, d in enumerate(clips, 1):
        timeline.append({"clip": i, "seconds": d, "start": t, "end": t + d})
        t += d

    out = {
        "target_seconds": a.total,
        "actual_seconds": actual,
        "difference": actual - a.total,
        "clip_count": len(clips),
        "clips": timeline,
        "note": (
            "Exact match." if actual == a.total else
            f"Over by {actual - a.total}s — trim in the editor." if actual > a.total else
            f"Short by {a.total - actual}s — closest the allowed durations allow."
        ),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
