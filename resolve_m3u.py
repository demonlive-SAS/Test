#!/usr/bin/env python3
"""
resolve_m3u.py - Resolve the final (real) URL behind a .ts / stream link
and write the result to an M3U playlist.

Usage:
    python resolve_m3u.py "http://example.com/live/stream.ts"
    python resolve_m3u.py url1 url2 url3 -o playlist.m3u
    python resolve_m3u.py -f links.txt -o playlist.m3u

links.txt format (one per line, optional name after a comma):
    http://example.com/a.ts,Channel A
    http://example.com/b.ts

Requires: pip install requests
"""

import argparse
import sys
from urllib.parse import urlparse

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StreamResolver/1.0)"}
TIMEOUT = 15


def resolve(url: str):
    """Follow redirects and return (final_url, redirect_chain)."""
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # HEAD is cheap; some servers reject it, so fall back to a streamed GET
        r = session.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code >= 400 or r.status_code == 405:
            raise requests.RequestException("HEAD rejected")
    except requests.RequestException:
        # stream=True avoids downloading the video body
        r = session.get(url, allow_redirects=True, timeout=TIMEOUT, stream=True)
        r.close()

    chain = [resp.url for resp in r.history] + [r.url]
    return r.url, chain


def default_name(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    return path.split("/")[-1] or urlparse(url).netloc


def read_links(args):
    items = []  # (url, name)
    for u in args.urls:
        items.append((u.strip(), None))
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                url, _, name = line.partition(",")
                items.append((url.strip(), name.strip() or None))
    return items


def main():
    p = argparse.ArgumentParser(description="Resolve stream links into an M3U playlist.")
    p.add_argument("urls", nargs="*", help="One or more stream URLs")
    p.add_argument("-f", "--file", help="Text file with URLs (optionally 'url,name')")
    p.add_argument("-o", "--output", default="playlist.m3u", help="Output playlist path")
    args = p.parse_args()

    items = read_links(args)
    if not items:
        p.error("Provide at least one URL or use -f links.txt")

    entries = []
    for url, name in items:
        try:
            final, chain = resolve(url)
        except requests.RequestException as e:
            print(f"[FAIL] {url}\n       {e}", file=sys.stderr)
            continue

        print(f"[OK]   {url}")
        for hop in chain[:-1]:
            print(f"       -> {hop}")
        print(f"       FINAL: {final}\n")
        entries.append((name or default_name(final), final))

    if not entries:
        sys.exit("No links resolved; playlist not written.")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, final in entries:
            f.write(f"#EXTINF:-1,{name}\n{final}\n")

    print(f"Wrote {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} to {args.output}")


if __name__ == "__main__":
    main()
