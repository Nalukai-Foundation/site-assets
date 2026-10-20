# site-assets

Images and source for the Past Programs page on nalukai.org.

- `img/` – thumbnails and photos used by the page. Served via jsDelivr:
  `https://cdn.jsdelivr.net/gh/Nalukai-Foundation/site-assets@main/img/<file>.jpg`
- `page/past-programs.source.html` – editable source (program data lives in the `PROGRAMS` array).
- `page/past-programs-squarespace.html` – paste-ready output for a Squarespace Code block (images load from the CDN above).
- `page/build_squarespace.py` – turns the source into the Squarespace version (`python3 page/build_squarespace.py`).

Note: jsDelivr caches files. When replacing an image, use a new filename.
