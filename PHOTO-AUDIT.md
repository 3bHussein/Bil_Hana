# Bil Hana — photo accuracy audit

Updated: 2026-10-15. All 100 image files exist. Keyword matches are NOT visual approval. 87 provisional photos require human visual verification.

## High-priority wrong or misleading photos

| ID | Recipe | Problem |
| --- | --- | --- |
| extra2 | بطاطس صينية بالفراخ | Living chicken at bird park, not cooked traybake |
| extra13 | بلح الشام | Deir al-Balah geographic place, not dessert |
| extra17 | جمبري إسكندراني | Senna plant, not shrimp |
| v19_6 | شوربة شوفان | Magnesium foods collage, not soup |
| v19_11 | فول بالبيض | Magnesium foods collage, not beans and eggs |
| extra6 | جبنة قديمة بالطماطم | Crab risotto, not aged cheese |
| extra7 | سلطة طحينة | Schnitzel main course with tahini side, not tahini salad |
| v19_40 | محشي بصل | Raw onions and other food, not stuffed onions |
| v19_42 | فاصوليا بيضاء | Red kidney bean stew, not white bean stew |
| extra15 | قرص فلاحي | Documentary bakery scene, not reliably country bread rolls |
| v19_52 | هريسة سميد | Geographic place Harissa, Lebanon, not semolina dessert |

## Rules

- Preserve source, author, and license for replacements.
- A keyword match is NOT verified; visually inspect finished cooked dishes.
- Avoid raw ingredients, restaurants, geographic places, and similar-sounding unrelated dishes.
- Keep the current 100-photo manifest intact until each replacement is ready.

## Recheck after photo import run 38646786915

Latest source register has 54 keyword candidates and 33 old review-required candidates; these counts are not a measure of visually approved photos.

| ID | Latest source | Assessment from filename/source metadata |
| --- | --- | --- |
| extra2 | King Ranch chicken casserole | **Still incorrect**: Mexican-style casserole, not Egyptian chicken-and-potato traybake |
| extra17 | Frozen cooked shrimp | **Still incorrect**: frozen shrimp, not a prepared Alexandrian shrimp dish |
| extra13 | Tulumba | **Plausible replacement** for بلح الشام; visual inspection still needed |
| extra7 | Tahini Sauce | **Plausible replacement** for سلطة طحينة; visual inspection still needed |
| v19_52 | Vegan Basbousa | **Related dessert, not exact** Egyptian semolina harissa; verify before approving |
| v19_6 | Magnesium-rich foods collage | **Still incorrect**: not oat soup |
| v19_11 | Magnesium-rich foods collage | **Still incorrect**: not fava beans with eggs |
| extra6 | Crab risotto | **Still incorrect**: not aged cheese with tomato |
| v19_40 | Raw onions and other foods | **Still incorrect**: not stuffed onions |
| v19_42 | Red kidney bean stew | **Still incorrect**: not white bean stew |
| extra15 | Bakery documentary scene | **Not verified** as a plated country bread roll |

Importer safety: existing photos are now protected from silent overwrite. Replacements require explicitly supplied `PHOTO_REPLACE_IDS`; never mark keyword-matched candidates visually approved without inspection.
