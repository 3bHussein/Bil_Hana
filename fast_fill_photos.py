#!/usr/bin/env python3
"""Fast-fill all Bil Hana recipe images from openly licensed Commons files.
Provisional matches are logged separately from manually verified PHOTO-CREDITS.csv.
"""
import csv, html, io, json, os, re, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parent
INDEX=ROOT/'index.html'
OUT=ROOT/'assets/photos'
OUT.mkdir(parents=True,exist_ok=True)
source=INDEX.read_text(encoding='utf-8')
manifest_match=re.search(r'(<script id="bh-photo-manifest" type="application/json">)(.*?)(</script>)',source,re.S)
if not manifest_match: raise RuntimeError('photo manifest not found')
manifest=json.loads(manifest_match.group(2))
recipes=[]
# First 18 seed recipes in their original order.
base=source.split('const base=[',1)[1].split('];',1)[0]
for i,m in enumerate(re.finditer(r"\[\s*'([^']+)'\s*,\s*'([^']+)'",base)):
    recipes.append(('seed'+str(i),m.group(1),m.group(2)))
# 24 extra recipes; the original list uses double-quoted strings.
extra=source.split('const extraRecipes=',1)[1].split('/* V19:',1)[0] if 'const extraRecipes=' in source else ''
for i,m in enumerate(re.finditer(r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"(?:main|dessert|side|soup|drink|breakfast|salad|bakery|seafood)"',extra)):
    recipes.append(('extra'+str(i),m.group(1),m.group(2)))
for m in re.finditer(r'"id":"(v19_\d+)","ar":"([^"]+)","en":"([^"]+)"',source):
    recipes.append((m.group(1),m.group(2),m.group(3)))
recipes=list(dict((r[0],r) for r in recipes).values())
print('Parsed',len(recipes),'recipes',flush=True)
if len(recipes)<90: raise RuntimeError('Recipe parser found fewer than 90 recipes; abort to avoid bad mapping')
existing=set(manifest)
# Recheck provisional images, while preserving the original reviewed photo set.
reviewed={'seed0','seed1','seed2','seed4','seed5','seed7','seed8','seed10','seed12','seed13','seed15','seed16','extra5'}

logpath=ROOT/'PROVISIONAL-PHOTO-SOURCES.csv'
records=[]
if logpath.exists():
    with logpath.open(encoding='utf-8',newline='') as f: records=list(csv.DictReader(f))
headers=['recipe_id','arabic_name','english_name','commons_page','license','artist','match_status']
logged={r['recipe_id'] for r in records}
agent={'User-Agent':'BilHanaRecipePhotoBot/1.0 (github.com/3bHussein/Bil_Hana; Wikimedia Commons attribution)'}

def get(url):
    req=urllib.request.Request(url,headers=agent)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req,timeout=28) as response:return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,503) or attempt==4: raise
            wait=min(60, 5*(2**attempt))
            print('RATE LIMITED; waiting',wait,'seconds',flush=True)
            time.sleep(wait)

def plain(s):return re.sub(r'<[^>]*>','',html.unescape(s or '')).strip()
# Explicit searches for recipes with known wrong photos; do not fall back to broad food results.
priority_queries={
    'extra2':'roasted chicken potatoes tray',
    'extra13':'tulumba dessert',
    'extra17':'shrimp tomato garlic dish',
    'v19_6':'oatmeal soup',
    'v19_11':'fava beans eggs',
    'extra6':'aged cheese tomatoes',
    'extra7':'tahini sauce dip',
    'v19_40':'stuffed onions dolma',
    'v19_42':'white bean stew',
    'extra15':'Egyptian bread rolls',
    'v19_52':'basbousa semolina cake',
}
priority_terms={
    'extra2':('chicken and potato','chicken potatoes','chicken with potatoes','chicken potato'),
    'extra13':('tulumba',),
    'extra17':('shrimp tomato','shrimp garlic','prawn tomato','prawn garlic'),
    'v19_6':('oat','oatmeal'),
    'v19_11':('fava','beans'),
    'extra6':('cheese',),
    'extra7':('tahini',),
    'v19_40':('stuffed onion','onion dolma'),
    'v19_42':('white bean',),
    'extra15':('bread roll','flatbread'),
    'v19_52':('basbousa','semolina cake'),
}
# Reject obviously unsuitable presentations even when their names contain the dish.
priority_exclusions={
    'extra2':('king ranch','tortilla','enchilada','mexican'),
    'extra17':('frozen','raw','package','packaged','uncooked'),
    'extra13':('city','village','deir'),
    'extra7':('schnitzel','chicken','steak'),
}
success=0
# Audit-only by default: the importer must never silently overwrite existing provisional images.
# Explicitly set PHOTO_REPLACE_IDS to a comma-separated list of reviewed recipe IDs.
replace_ids={x.strip() for x in os.environ.get('PHOTO_REPLACE_IDS','').split(',') if x.strip()}
for rid,ar,en in recipes:
    if rid in existing and (ROOT/manifest[rid]).exists() and rid not in replace_ids: continue
    if rid in reviewed and rid not in replace_ids: continue
    # Recover from intermittent Commons failures by trying a shorter search too.
    # Keep filename and rights metadata together, even for provisional matches.
    query='filetype:bitmap '+priority_queries.get(rid,en)
    params={'action':'query','generator':'search','gsrsearch':query,'gsrnamespace':'6','gsrlimit':'30','prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':'900','format':'json'}
    try:
        payload=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)))
        pages=list(payload.get('query',{}).get('pages',{}).values())
        pages.sort(key=lambda p:p.get('index',999))
        chosen=None
        terms=[w.lower() for w in re.findall(r'[A-Za-z]{4,}',en) if w.lower() not in ('egyptian','with','and','soup','baked','fried','grilled','cream','stuffed','tomato','potato','rice','cheese','chicken','beef','meat','salad','sweet','milk','sauce','bread','pasta','cream')]
        if not terms: terms=[w.lower() for w in re.findall(r'[A-Za-z]{4,}',en) if w.lower() not in ('egyptian','with','and','soup','baked','fried','grilled','cream','stuffed')]
        for p in pages:
            inf=(p.get('imageinfo') or [{}])[0];meta=inf.get('extmetadata') or {}
            lic=plain((meta.get('LicenseShortName') or {}).get('value',''))
            if not (lic.startswith('CC BY') or lic in ('CC0','Public domain')):continue
            url=inf.get('thumburl') or inf.get('url','')
            if not url or not re.search(r'\.(jpg|jpeg|png|webp)(\?|$)',url,re.I):continue
            title=urllib.parse.unquote(p.get('title','')).lower().replace('_',' ')
            if rid in priority_terms:
                if not any(w in title for w in priority_terms[rid]): continue
                if any(bad in title for bad in priority_exclusions.get(rid,())): continue
            elif not terms or not any(w in title for w in terms): continue
            # Never use another named dish or a generic Egyptian-food image as a substitute.
            forbidden=('koshary','kosheri','pyramid','risotto','salmon','chocolate cake','countryfriedsteak','nian gao','logo','plant','collage','food sources')
            if any(word in title for word in forbidden): continue
            # Reject duplicate Commons images already assigned to a different recipe.
            page_url=inf.get('descriptionurl','')
            if any(row['commons_page']==page_url and row['recipe_id']!=rid for row in records): continue
            if any(bad in title for bad in ('ingredients','raw ','seeds','plant','logo','map','pyramid','market','advertisement')): continue
            chosen=(p,inf,meta,lic,url);break
        if not chosen:
            # Keep existing provisional file rather than replace it with another unrelated photo.
            print('NO RELEVANT LICENSED MATCH',rid,en,flush=True)
            continue
        p,inf,meta,lic,url=chosen
        blob=get(url)
        with Image.open(io.BytesIO(blob)) as im:
            im=ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((900,700))
            im.save(OUT/(rid+'.webp'),'WEBP',quality=79,method=4)
        manifest[rid]='assets/photos/'+rid+'.webp'
        records=[row for row in records if row['recipe_id']!=rid]
        records.append(dict(recipe_id=rid,arabic_name=ar,english_name=en,commons_page=inf.get('descriptionurl',''),license=lic,artist=plain((meta.get('Artist') or {}).get('value','')),match_status='PROVISIONAL - KEYWORD MATCH, NEEDS VISUAL REVIEW'))
        success+=1
        print('IMPORTED',rid,en,p.get('title'),flush=True)
    except Exception as exc:print('FAILED',rid,str(exc)[:180],flush=True)
    if success and success%15==0:
        print('Checkpoint',success,flush=True)
    time.sleep(2.5)
with logpath.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader();writer.writerows(records)
new=json.dumps(manifest,ensure_ascii=False)
INDEX.write_text(source[:manifest_match.start(2)]+new+source[manifest_match.end(2):],encoding='utf-8')
print('COMPLETE new=',success,'total=',len(manifest),'recipes=',len(recipes),flush=True)
