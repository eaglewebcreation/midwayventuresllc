# Midway Ventures LLC website

Static site for Midway Ventures LLC: one heated 36 x 45 ft shop for rent on US-310 just west of Lovell, WY.
Built by Eagle Web Creation. Plain HTML/CSS/JS, deployed to Hostinger from Git.

## Branches
- `main`: source plus the production build in `public/`.
- `preview`: only the noindexed preview build, deployed to https://midwayventures.eaglewebcreation.com

## Edit and rebuild
1. Owner facts live in `site-config.json`. Anything still `null` under `CONFIRM` shows on the site as
   "[waiting on owner confirmation]" (or an HTML TODO comment).
2. `python3 tools/build_site.py` writes `public/`. `python3 tools/verify.py` checks it.
3. Preview build: `SITE_URL=https://midwayventures.eaglewebcreation.com python3 tools/build_site.py`, then copy
   `public/` to the `preview` branch.
4. Logo, favicons and link-preview image: `python3 tools/build_images.py` (needs Pillow and cairosvg).

## Availability
`.github/workflows/sync-availability.yml` reads the CCStorage rental page every hour (minute 41). If the
shop flips between Rent Now and Join Waiting List it updates `site-config.json`, rebuilds and pushes both
branches. If the page can't be read, nothing changes.

## Going live
Set `prodHost` in `site-config.json` to the real domain, change the noindex rule in `public/.htaccess` to
match it, rebuild, and point Hostinger at `main`'s `public/` build. Nothing goes live until Talon approves.
