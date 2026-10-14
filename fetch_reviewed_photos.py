#!/usr/bin/env python3
"""Download ONLY manually reviewed Wikimedia files, verify metadata, convert to WebP."""
import csv, io, json, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
entries=[
 ('seed0','Egyptian food Koshary.jpg','Dina Said','CC BY-SA 4.0'),
 ('seed3','Ful medames.jpg','Zachbe','CC BY-SA 3.0'),
 ('seed1','Molokhia.JPG','Showshow777','CC BY-SA 4.0'),
]
out=ROOT/'assets/photos';out.mkdir(exist_ok=True,parents=True)
credits=ROOT/'PHOTO-CREDITS.csv'
rows=[]
for recipe,title,expected_author,expected_license in entries:
    api='https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url%7Cextmetadata&titles='+urllib.parse.quote('File:'+title)
    req=urllib.request.Request(api,headers={'User-Agent':'BilHanaRecipePhotoResearch/1.0 (contact: https://github.com/3bHussein)'})
    try:
        with urllib.request.urlopen(req,timeout=20) as response: data=json.load(response)
        page=next(iter(data['query']['pages'].values()))
        info=page['imageinfo'][0];meta=info['extmetadata']
        author=meta.get('Artist',{}).get('value','')
        license_name=meta.get('LicenseShortName',{}).get('value','')
        if expected_author.lower() not in author.lower() or license_name!=expected_license:
            print('REVIEW REQUIRED: attribution/license mismatch',recipe,author,license_name);continue
        with urllib.request.urlopen(urllib.request.Request(info['url'],headers={'User-Agent':'BilHanaRecipePhotoResearch/1.0'}),timeout=35) as response: content=response.read()
        im=Image.open(io.BytesIO(content));im.verify()
        im=Image.open(io.BytesIO(content)).convert('RGB');im.thumbnail((1200,1200))
        dest=out/(recipe+'.webp');im.save(dest,'WEBP',quality=82,method=6)
        rows.append([recipe,dest.name,expected_author,'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title.replace(' ','_')),expected_license,'yes'])
        print('SAVED',dest)
    except Exception as e: print('NOT DOWNLOADED',recipe,str(e))
if rows:
    with credits.open('a',newline='',encoding='utf-8') as f:csv.writer(f).writerows(rows)
    import subprocess,sys
    subprocess.run([sys.executable,str(ROOT/'bundle_photos.py')],check=True)
print('New verified photographs:',len(rows))
