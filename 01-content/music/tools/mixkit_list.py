#!/usr/bin/env python3
"""List Mixkit free music tracks from mood/tag pages. Usage: mixkit_list.py OUT.json PAGE_PATH..."""
import html, json, re, sys, time, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def parse(page, source):
    items = []
    for block in page.split('data-test-id="audio-player"')[1:]:
        mid = re.search(r'data-audio-player-item-id-value="(\d+)"', block)
        mp3 = re.search(r'data-audio-player-preview-url-value="([^"]+\.mp3)"', block)
        title = re.search(r'item-grid-card__title">\s*([^<]+?)\s*</h2>', block)
        author = re.search(r'item-grid-music-preview__author">\s*by\s*([^<]+?)\s*</p>', block)
        dur = re.search(r'data-test-id="duration">\s*([\d:]+)', block)
        tags = re.findall(r'meta-links__link"[^>]*href="/free-stock-music/([^"]+)/">([^<]+)<', block)
        if mid and mp3:
            items.append({"id": int(mid.group(1)), "title": html.unescape(title.group(1)) if title else "",
                          "artist": html.unescape(author.group(1)) if author else "",
                          "duration": dur.group(1) if dur else "", "mp3": mp3.group(1),
                          "tags": [html.unescape(t[1]) for t in tags], "found_on": [source]})
    return items

out, paths = sys.argv[1], sys.argv[2:]
seen = {}
for p in paths:
    for item in parse(get("https://mixkit.co/free-stock-music/" + p.strip("/") + "/"), p):
        if item["id"] in seen:
            seen[item["id"]]["found_on"] += item["found_on"]
        else:
            seen[item["id"]] = item
    time.sleep(1)
json.dump(sorted(seen.values(), key=lambda x: -len(x["found_on"])), open(out, "w"), indent=1)
print(len(seen), "tracks")
