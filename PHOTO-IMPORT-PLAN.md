# Bil Hana V23 — photo import plan

The website must use real, correctly matched, reuse-licensed photographs wherever available. Store approved images under `assets/photos/` as optimized WebP and maintain `PHOTO-CREDITS.csv` (recipe ID, title, filename, source URL, photographer, license, attribution URL).

Do not present third-party thumbnails or search links as downloaded assets. Do not ship unverified or mislabeled images. Fall back to existing local SVG illustrations where an approved photograph is not available.

## Current baseline

The repository's `main` currently only contains README.md. Website assets from the locally supplied V23 ZIP have **not yet been pushed**. The photo import count in that package was **0**.

## Deployment checklist

- [ ] Upload `index.html` and original `assets/images/` from the V23 package to the repository
- [ ] Validate 100 recipe IDs and images used in list/detail views
- [ ] Research and check candidate images and permissions
- [ ] Convert verified files to WebP and record credits
- [ ] Confirm all local paths and test on GitHub Pages
