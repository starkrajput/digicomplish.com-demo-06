"""Report internal links that point to a missing page. Usage: python tools/check_links.py"""
import collections
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site"))
bad = collections.defaultdict(set)
for dp, dn, fn in os.walk(ROOT):
    if "wp-content" in dp or "wp-includes" in dp:
        continue
    for f in fn:
        if not f.endswith(".html") or f.startswith("_"):
            continue
        p = os.path.join(dp, f)
        s = open(p, encoding="utf-8").read()
        for h in re.findall(r'<a\b[^>]*\shref="([^"]+)"', s):
            if h.startswith(("http", "mailto:", "tel:", "#", "javascript", "?")):
                continue
            u = h.split("#")[0].split("?")[0]
            if not u.startswith("/"):
                u = "/" + os.path.relpath(os.path.join(dp, u), ROOT).replace(os.sep, "/")
            t = os.path.join(ROOT, u.lstrip("/"))
            if u == "/" or os.path.isfile(t) or os.path.isfile(os.path.join(t, "index.html")):
                continue
            bad[u].add(os.path.relpath(p, ROOT))
for u, ps in sorted(bad.items()):
    print(u, len(ps), sorted(ps)[:3])
print("missing targets:", len(bad))
