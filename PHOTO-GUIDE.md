# Real food photos / الصور الحقيقية

The website **does not yet include licensed food photographs**. Its existing 370 SVG illustrations are bundled and work offline.

To include actual photos in GitHub Pages:
1. Obtain photographs you own or have permission to redistribute. Confirm each photo matches the recipe.
2. Put each photo in `assets/photos/` named by recipe ID, e.g. `seed0.webp`, `seed1.webp`, `extra0.webp`.
3. Record attribution, license and original URL in `PHOTO-CREDITS.csv` (if required by the license).
4. Run `python bundle_photos.py` and upload the entire project including `assets/`.

The bundler only includes present files, preventing broken requests. Personal browser uploads are not automatically published to GitHub. Do not use copyrighted photos without permission.
