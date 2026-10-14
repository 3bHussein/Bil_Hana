#!/usr/bin/env python3
"""Research up to 20 missing recipes; output candidates for human review only."""
import csv
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
batch_size = int(os.getenv("PHOTO_BATCH_SIZE", "20"))
if batch_size not in (10, 20):
    raise SystemExit("Batch must be 10 or 20")

with (root / "PHOTO-CREDITS.csv").open(encoding="utf-8-sig", newline="") as stream:
    done = {row["recipe_id"] for row in csv.DictReader(stream)}
with (root / "RECIPE-PHOTO-QUEUE.csv").open(encoding="utf-8-sig", newline="") as stream:
    missing = [row for row in csv.DictReader(stream) if row["id"] not in done]

fields = ["recipe_id", "recipe_ar", "commons_file", "source_url", "photographer", "license", "review_status"]
results = []
for recipe in missing[:batch_size]:
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": recipe["en"] + " food", "gsrnamespace": 6, "gsrlimit": 5,
        "prop": "imageinfo", "iiprop": "url|extmetadata"
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "BilHanaPhotoResearch/1.0 (https://github.com/3bHussein/Bil_Hana)"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        for page in payload.get("query", {}).get("pages", {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            metadata = info.get("extmetadata", {})
            license_name = metadata.get("LicenseShortName", {}).get("value", "")
            if not (license_name.startswith("CC BY") or license_name in ("CC0", "Public Domain")):
                continue
            results.append([recipe["id"], recipe["ar"], page["title"], info.get("descriptionurl", ""),
                            metadata.get("Artist", {}).get("value", ""), license_name, "PENDING VISUAL REVIEW"])
    except Exception as error:
        print("Search failed:", recipe["id"], str(error))

with (root / "PHOTO-RESEARCH-NEXT.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(fields)
    writer.writerows(results)
print("Candidates:", len(results), "Recipes searched:", min(batch_size, len(missing)))
