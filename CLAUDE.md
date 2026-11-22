# Midway Ventures LLC site: rules for editing

- Edit `site-config.json`, `src/site.css` or `tools/build_site.py`, never the files in `public/` by hand
  (except `public/.htaccess` and `public/assets/js/site.js`). Rebuild and run `tools/verify.py` before committing.
- Never edit live files on Hostinger directly. Always go through this repo.
- Only claim what the owner confirmed: heated, private bathroom, private office, 36 x 45 x 16 ft. Never claim
  climate-controlled, gated, cameras, lighting, door size, power or access hours until confirmed.
- Never draw the bathroom or office in the shop drawing until the layout is known.
- No aggregateRating or Review schema. Reviews only word for word from real customers.
- Town names (Lovell, Cowley, Byron, Powell, Cody, Greybull, Basin) appear only on the town pages, the FAQ
  town list, the footer town links and schema. Lovell also appears where it is the street address.
- Town pages must share under 25% of their 5-word phrases (verify.py checks this).
- The header logo animation (M drives in leaving the green bands, then the name slides out) must stay
  CSS-only and respect prefers-reduced-motion. It plays once per visit (sessionStorage key `mvLogo`).
- Rent buttons go to the CCStorage rental page in `rentUrl`. Show base rent before card or ACH fees.
