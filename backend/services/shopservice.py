"""Nearby repair shops via OpenStreetMap Overpass API."""
import math
import time
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RADIUS_M = 15000  # 15 km
CACHE_TTL = 3600
_cache = {}


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_query(lat, lon, radius, vehicle_type):
    tags = [
        '"shop"="car_repair"',
        '"amenity"="car_repair"',
        '"shop"="motorcycle_repair"',
        '"shop"="bicycle"',
        '"shop"="tyres"',
        '"shop"="car_parts"',
        '"shop"="motorcycle"',
        '"shop"="auto_repair"',
        '"shop"="vehicle_repair"',
    ]
    parts = []
    for t in tags:
        parts.append(f'node[{t}](around:{radius},{lat},{lon});')
        parts.append(f'way[{t}](around:{radius},{lat},{lon});')
    return f"[out:json][timeout:25];({' '.join(parts)});out center tags;"


def find_nearby_shops(lat, lon, vehicle_type="car_sedan", radius=RADIUS_M):
    cache_key = (round(lat, 3), round(lon, 3), vehicle_type)
    now = time.time()
    if cache_key in _cache:
        cached_time, cached = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached

    query = _build_query(lat, lon, radius, vehicle_type)
    try:
        res = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=25,
            headers={"User-Agent": "DamageGenX/1.0"},
        )
        res.raise_for_status()
        elements = res.json().get("elements", [])
    except Exception as e:
        print(f"[shops] Overpass error: {e}")
        return []

    shops = []
    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name")
        if not name:
            continue
        el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
        el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if el_lat is None or el_lon is None:
            continue
        shops.append({
            "name": name,
            "lat": el_lat,
            "lon": el_lon,
            "address": ", ".join(filter(None, [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:city"),
            ])) or tags.get("addr:full", "Address not listed"),
            "phone": tags.get("phone", ""),
            "website": tags.get("website", ""),
            "opening_hours": tags.get("opening_hours", ""),
            "distance_km": round(_haversine_km(lat, lon, el_lat, el_lon), 2),
        })

    shops.sort(key=lambda s: s["distance_km"])
    shops = shops[:8]
    _cache[cache_key] = (now, shops)
    return shops