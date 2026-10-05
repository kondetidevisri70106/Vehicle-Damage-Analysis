from collections import Counter

VIEW_WEIGHTS = {"front": 1.0, "rear": 1.0, "left": 0.9,
                "right": 0.9, "closeup": 1.2}


def fuse_views(view_results):
    fused = []
    class_counter = Counter()
    weighted_sev = 0.0
    total_weight = 0.0

    for view, res in view_results.items():
        w = VIEW_WEIGHTS.get(view, 1.0)
        for d in res.get("detections", []):
            class_counter[d["class"]] += 1
            fused.append({**d, "view": view, "weight": w})
        weighted_sev += res.get("severity", {}).get("score", 0.0) * w
        total_weight += w

    avg_severity = weighted_sev / total_weight if total_weight else 0.0
    dominant = class_counter.most_common(1)[0][0] if class_counter else "none"

    return {
        "fused_detections": fused,
        "dominant_damage": dominant,
        "class_distribution": dict(class_counter),
        "fused_severity_score": round(avg_severity, 3),
        "num_views": len(view_results),
    }