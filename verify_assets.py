from pathlib import Path
import re,sys
root=Path(__file__).parent
html=(root/'index.html').read_text(encoding='utf-8')
images=list((root/'assets/images').glob('*.svg'))
errors=[str(p) for p in images if '<svg' not in p.read_text(encoding='utf-8') or '</svg>' not in p.read_text(encoding='utf-8')]
if len(images)<100:errors.append(f'Only {len(images)} local SVGs')
if 'assets/images/' not in html:errors.append('Image asset reference missing')
print(f'Found {len(images)} local SVG illustrations')
if errors:print('\n'.join(errors));sys.exit(1)
print('Asset checks passed (not a browser or photo-license test)')
