#!/usr/bin/env python3
"""Import up to 10 or 20 individually reviewed Commons photos; never auto-approve search hits."""
import csv, io, json, os, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
LIMIT=int(os.getenv("PHOTO_BATCH_SIZE","10"))
if LIMIT not in (10,20): raise SystemExit("PHOTO_BATCH_SIZE must be 10 or 20")
candidates=list(csv.DictReader((ROOT/"REVIEWED-CANDIDATES.csv").open(encoding="utf-8-sig",newline="")))
credits=ROOT/"PHOTO-CREDITS.csv"
with credits.open(encoding="utf-8-sig",newline="") as fh: existing=list(csv.DictReader(fh))
by_recipe={r["recipe_id"]:r for r in existing}
out=ROOT/"assets/photos"
out.mkdir(parents=True,exist_ok=True)
count=0
for row in candidates:
    if count>=LIMIT: break
    recipe=row["recipe_id"]
    if recipe in by_recipe or "REJECTED" in row["review_note"].upper(): continue
    url=row["file_page"]
    if not url.startswith("https://commons.wikimedia.org/wiki/File:"): continue
    title=urllib.parse.unquote(url.split("/wiki/",1)[1]).replace("_"," ")
    api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":title})
    try:
        req=urllib.request.Request(api,headers={"User-Agent":"BilHanaPhotoImporter/1.0 (https://github.com/3bHussein/Bil_Hana)"})
        with urllib.request.urlopen(req,timeout=25) as response: data=json.load(response)
        page=next(iter(data["query"]["pages"].values()))
        info=page["imageinfo"][0]
        meta=info["extmetadata"]
        artist=re.sub(r"<[^>]*>"," ",meta.get("Artist",{}).get("value",""))
        license_name=meta.get("LicenseShortName",{}).get("value","")
        if row["photographer"].lower() not in artist.lower() or row["license"]!=license_name:
            print("SKIPPED metadata mismatch",recipe);continue
        if meta.get("NonFree",{}).get("value","false").lower()=="true":
            print("SKIPPED nonfree",recipe);continue
        with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"BilHanaPhotoImporter/1.0"}),timeout=35) as response: raw=response.read()
        im=Image.open(io.BytesIO(raw));im.verify()
        im=Image.open(io.BytesIO(raw)).convert("RGB");im.thumbnail((1200,1200))
        filename=recipe+".webp"
        im.save(out/filename,"WEBP",quality=82)
        by_recipe[recipe]={"recipe_id":recipe,"filename":filename,"photographer":row["photographer"],"source_url":url,"license":license_name,"attribution_required":"yes"}
        count+=1
        print("IMPORTED",recipe)
    except Exception as exc:
        print("SKIPPED",recipe,str(exc))
if count:
    fields=["recipe_id","filename","photographer","source_url","license","attribution_required"]
    with credits.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader();writer.writerows(by_recipe.values())
    import subprocess,sys
    subprocess.run([sys.executable,str(ROOT/"bundle_photos.py")],check=True)
print("Imported in this batch:",count,"of maximum",LIMIT)
