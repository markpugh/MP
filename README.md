# RoloTech Kodi Repository

Self-hosted Kodi addon repository served from GitHub Pages at
`https://markpugh.github.io/MP/`.

Currently ships:

- `repository.rolotech` 1.0.0 — the repository addon itself
- `plugin.video.mpsupersearch` 1.0.6 — MP SuperSearch (granular TMDB filter UI)

---

## First-time push

This skeleton is already wired up with your GitHub user (`markpugh`)
and repo name (`MP`). The repo addon zip and metadata files have
already been built. You just need to push.

```bash
cd MP                  # this folder
git init
git remote add origin https://github.com/markpugh/MP.git
git branch -M main
git add -A
git commit -m "Initial RoloTech repository"
git push -u origin main
```

If GitHub rejects the push because the remote already has commits
(e.g., an auto-created README), pull and rebase first:

```bash
git pull --rebase origin main
git push -u origin main
```

## Enable GitHub Pages

In the GitHub web UI:

**Settings → Pages → Source: Deploy from a branch → Branch: `main` →
Folder: `/ (root)` → Save**

Wait ~30 seconds, then confirm `https://markpugh.github.io/MP/addons.xml`
loads in a browser. If it does, Kodi will be able to reach it too.

## Install on Kodi (Xbox, desktop, anything)

1. **Settings → System → Add-ons → Unknown sources → ON**
2. **Settings → File Manager → Add source**, paste:
   `https://markpugh.github.io/MP/`
   Name it `rolotech`.
3. **Add-ons → Install from zip file → rolotech →
   `repository.rolotech/` → `repository.rolotech-1.0.0.zip`**
4. **Add-ons → Install from repository → RoloTech Repository → Video
   add-ons → MP SuperSearch → Install**

Done. Kodi polls the repo automatically and offers updates whenever
you bump a version and push.

---

## Ongoing: shipping a new MP SuperSearch version

When you bump 1.0.6 → 1.0.7:

1. Update `version="1.0.7"` in the addon's source `addon.xml`.
2. Build the new zip (or drop the source folder in here and use
   `--pack`).
3. Place the new zip at:
   `plugin.video.mpsupersearch/plugin.video.mpsupersearch-1.0.7.zip`
4. Replace `plugin.video.mpsupersearch/addon.xml` with the new
   version's manifest. (Automatic if you used `--pack`.)
5. Rebuild metadata:
   ```bash
   python _repo_generator.py
   ```
6. `git add -A && git commit -m "MP SuperSearch 1.0.7" && git push`

Force a Kodi check on any installed device with **Add-ons → Check for
updates**.

## Adding a brand-new addon to the repo

1. Create a top-level folder named after the addon ID
   (e.g. `script.rolotech.dashboard/`).
2. Place the addon's `addon.xml` and a versioned zip inside it.
3. Run `python _repo_generator.py`.
4. Commit and push.

The generator picks up any subdirectory containing an `addon.xml`.

---

## Layout

```
MP/                                      <-- this repo (markpugh/MP)
├── _repo_generator.py
├── README.md
├── addons.xml                           <-- generated, committed
├── addons.xml.md5                       <-- generated, committed
├── repository.rolotech/
│   ├── addon.xml                        <-- has GitHub Pages URLs baked in
│   ├── icon.png
│   └── repository.rolotech-1.0.0.zip
└── plugin.video.mpsupersearch/
    ├── addon.xml                        <-- mirror of latest version
    └── plugin.video.mpsupersearch-1.0.6.zip
```

---

## Troubleshooting

**"Could not connect to repository":** GitHub Pages can take a minute
on first deploy. Open `https://markpugh.github.io/MP/addons.xml` in
a browser; if it 404s, Pages isn't live yet — wait, retry.

**Repo installs but MP SuperSearch isn't visible in the repo:** Open
the live `addons.xml` in a browser and confirm both addons are
listed. If only the repo addon appears, the generator missed the
plugin folder — confirm `plugin.video.mpsupersearch/addon.xml`
exists, re-run the generator, push.

**Update not showing after a version bump:** Force it with
**Add-ons → My add-ons → MP SuperSearch → Check for updates**, or
restart Kodi. If still missing, open the live `addons.xml` in a
browser and confirm the new version number is actually there. If not,
your push didn't include the regenerated metadata.

**Renaming the repo later:** If you ever rename `MP` to something
else on GitHub, update the three URL lines + `<source>` tag in
`repository.rolotech/addon.xml`, re-run `--pack repository.rolotech`,
push.

---

MIT licensed.
