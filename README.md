# Gumbit Stitch Shop

A click-to-sew embroidery simulator built from the Gumbit patch by PJ O'Rourke II.

Pick a thread off the rack, click a part of the patch, and a needle stitches it in.
Every section follows an outline in the original design.

**Live page:** https://feldtdesign-ship-it.github.io/gumbit-stitch-shop/

## How it works

Open `index.html`. Nothing to install, no build step, no dependencies.
The patch photo and the region map are baked into the file as base64, so it runs
from a local file or from any static host.

- 23 parts: border, lettering, twill, face, two eye sockets, two eyes, upper and
  lower lip, seven separate teeth, neck, two collar halves, tie knot, two jacket halves.
- 17 thread colors plus "As drawn" and a mix-your-own picker.
- Clicks queue, so you can line up several parts and watch them run.
- Seam ripper unpicks a part. Sew it as drawn, Surprise me, and Rip it all out run the whole patch.
- Speed dial, machine sound, stitch and thread counters.

Shading comes from the real photo: each pixel keeps its brightness relative to the
median of its own region, so a new thread color picks up the original stitch texture
and sheen instead of going flat.

## Repo

    index.html                  the whole thing
    tools/seg.py                first pass, splits the patch into coarse regions
    tools/seg3.py               second pass, snaps sections to the stitched outlines
    tools/tpl.html              page source before the images are inlined
    tools/patch-source.jpg      the patch photo at 720px
    tools/regions.png           the region map, one palette index per part

To rebuild `index.html` after editing `tools/tpl.html`, base64 the two images in
`tools/` and substitute them for the `__SRC__` and `__LAB__` placeholders.

## Credit

Patch artwork by PJ O'Rourke II. Built by Feldt Design.
