# MP Build — RoloTech Kodi Repository

A self-hosted Kodi add-on repository and one-click build, served from
GitHub Pages at `https://markpugh.github.io/MP/`.

The headline product is the **MP Build**: run one installer add-on and it
sets up a complete, pre-configured streaming system — a discovery UI, a
debrid playback engine, the MP skin, and all the supporting modules — then
walks you through authorizing Real Debrid / AllDebrid / Trakt.

---

## What's in the repo

**The build**

| Add-on | ID | Version | Role |
|---|---|---|---|
| MP Build | `script.mpbuild` | 1.10.17 | One-click installer + configurator. Run this first. |
| MP SuperSearch | `plugin.video.mpsupersearch` | 1.8.2 | Discovery UI (granular TMDB filtering). The home screen. |
| MP SuperLite | `plugin.video.mpsuperlite` | 0.9.1 | Debrid playback engine — scrape, rank, resolve, play, scrobble. |
| MP skin | `skin.mp` | 1.1.9 | The build's own comic-book skin; boots straight into SuperSearch. |
| TMDb Helper | `plugin.video.themoviedb.helper` | 6.15.6 | Metadata + episode browsing. |
| MP Trailer Finder | `script.mp.trailerfinder` | 0.2.2 | Trailers. |

**Supporting modules** (installed automatically by MP Build)

CocoScrapers `1.0.32`, ResolveURL `5.1.198`, Up Next `1.1.9`,
a4kSubtitles `3.24.2`, InfoTagger `0.0.8`, jurialmunkey `0.2.35`,
Addon Signals `0.0.6`, qrcode `6.1.0`, plus the Studio Icons and Weather
Icons resource packs.

**Repository add-on**

`repository.rolotech` `1.0.0` — the repo itself (has the GitHub Pages URLs
baked into its `addon.xml`).

---

## Install on Kodi (Xbox, desktop, anything — Kodi 21 Omega or newer)

1. **Settings → System → Add-ons → Unknown sources → ON**
2. **Settings → File Manager → Add source**, paste
   `https://markpugh.github.io/MP/` and name it `rolotech`.
3. **Add-ons → Install from zip file → rolotech → `repository.rolotech/` →
   `repository.rolotech-1.0.0.zip`**
4. **Add-ons → Install from repository → RoloTech Repository → Program
   add-ons → MP Build → Install.**
5. Open **MP Build** and run it. It installs everything above, then walks
   you through Real Debrid / AllDebrid / Trakt authorization (QR code, web
   page, or skip for each).

When it finishes you land on the MP skin, booting straight into SuperSearch.
Kodi polls the repo automatically and offers updates whenever a version is
bumped and pushed.

---

## How the repo works

Each add-on lives in a top-level folder named after its ID, containing a
**mirror `addon.xml`** (a copy of the latest version's manifest) and the
matching **`<id>-<version>.zip`**. The real source lives only inside the zip
— the folders are publishing stubs.

`_repo_generator.py` reads every folder's `addon.xml`, rebuilds the
top-level `addons.xml` + `addons.xml.md5`, extracts icons, and writes the
browsable `index.html` pages. Kodi reads `addons.xml` to learn what versions
exist and downloads the zips on demand.

The MP Build installer pins exact versions in its `INSTALL_ORDER`, so a
pinned version **must** match the zip present in that add-on's folder, or a
clean install will 404. Audit the pins after any version bump.

---

## Shipping a new version

Example: bumping MP SuperLite `0.9.1 → 0.9.2`.

1. Bump `version="0.9.2"` in the add-on's source `addon.xml`.
2. Build the zip. Either drop the source folder in here and let the
   generator pack it:
   ```bash
   python _repo_generator.py --pack plugin.video.mpsuperlite
   ```
   or build it yourself and place it at
   `plugin.video.mpsuperlite/plugin.video.mpsuperlite-0.9.2.zip` with a
   matching mirror `addon.xml`. The zip's internal root folder must be the
   add-on ID (`plugin.video.mpsuperlite/...`).
3. If MP Build pins this add-on, bump the pin in
   `script.mpbuild` → `resources/lib/installer.py` (`INSTALL_ORDER`) and
   ship a new MP Build version too.
4. Rebuild metadata (if you didn't use `--pack`, which runs it for you):
   ```bash
   python _repo_generator.py
   ```
5. Remove the superseded zip, then commit and push:
   ```bash
   git add -A && git commit -m "MP SuperLite 0.9.2" && git push
   ```

Force a Kodi check on any installed device with
**Add-ons → My add-ons → <add-on> → Check for updates**, or restart Kodi.

### Adding a brand-new add-on

Create a top-level folder named after the add-on ID, drop its `addon.xml`
and a versioned zip inside, run `python _repo_generator.py`, commit, push.
The generator picks up any subdirectory containing an `addon.xml`.

---

## GitHub Pages

Served from the `main` branch root:
**Settings → Pages → Source: Deploy from a branch → Branch `main` → Folder
`/ (root)`**.

After a push, confirm `https://markpugh.github.io/MP/addons.xml` loads in a
browser — if it does, Kodi can reach it too.

---

## Layout

```
MP/                                        <-- this repo (markpugh/MP)
├── _repo_generator.py
├── README.md
├── addons.xml                             <-- generated, committed
├── addons.xml.md5                         <-- generated, committed
├── index.html                             <-- generated (browsable listing)
├── repository.rolotech/                   <-- the repo add-on
│   ├── addon.xml
│   ├── icon.png
│   └── repository.rolotech-1.0.0.zip
├── script.mpbuild/                        <-- the installer
│   ├── addon.xml                          <-- mirror of latest version
│   └── script.mpbuild-1.10.17.zip
├── plugin.video.mpsupersearch/
├── plugin.video.mpsuperlite/
├── skin.mp/
├── plugin.video.themoviedb.helper/
├── script.mp.trailerfinder/
└── … supporting modules, one folder each
```

Every add-on folder follows the same `addon.xml` + `<id>-<version>.zip`
shape shown for `repository.rolotech` and `script.mpbuild`.

---

## Troubleshooting

**"Could not connect to repository":** GitHub Pages can lag a minute on a
fresh deploy. Open `https://markpugh.github.io/MP/addons.xml` in a browser;
if it 404s, Pages isn't live yet — wait and retry.

**A clean install 404s on one add-on:** its MP Build pin doesn't match a zip
in the repo. Confirm `<id>/<id>-<version>.zip` exists for the exact version
pinned in `installer.py`'s `INSTALL_ORDER`, fix whichever is wrong, re-run
the generator, push.

**Update not showing after a version bump:** force it with **Add-ons → My
add-ons → <add-on> → Check for updates**, or restart Kodi. If still missing,
open the live `addons.xml` in a browser and confirm the new version is
actually listed — if not, the push didn't include the regenerated metadata.

**Renaming the repo later:** if `MP` is ever renamed on GitHub, update the
URL lines + `<source>` tag in `repository.rolotech/addon.xml`, re-run
`python _repo_generator.py --pack repository.rolotech`, and push.

---

Add-ons retain their own upstream licenses; repository tooling is MIT.
