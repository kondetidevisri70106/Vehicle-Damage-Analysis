from collections import Counter


def fuse_frames(frame_detections):
    class_counter = Counter()
    all_dets = []
    sev_scores = []
    for fd in frame_detections:
        for d in fd.get("detections", []):
            class_counter[d["class"]] += 1
            all_dets.append(d)
        sev_scores.append(fd.get("severity_score", 0.0))
    sorted_sev = sorted(sev_scores)
    median = sorted_sev[len(sorted_sev) // 2] if sorted_sev else 0.0
    dominant = class_counter.most_common(1)[0][0] if class_counter else "none"
    return {
        "frame_count": len(frame_detections),
        "dominant_damage": dominant,
        "class_distribution": dict(class_counter),
        "temporal_severity": round(median, 3),
        "total_detections": len(all_dets),
        "frames": frame_detections,
    }