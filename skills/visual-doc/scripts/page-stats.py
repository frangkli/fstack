#!/usr/bin/env python3
"""Measure a visual-doc page against the skill's limits, and print what breaks them.

Usage: page-stats.py <page.html>. Exits 1 when anything is flagged.
Visible text is what a reader sees without opening anything: closed <details> bodies, tab panels
after the first, scripts, styles and Mermaid source are left out.
"""
import re
import sys
from collections import Counter
from html.parser import HTMLParser

BUDGET, PARAGRAPH, BARE_SECTION = 1500, 50, 100
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
UNITS = {"p", "li", "dd", "td", "th"}
# A figure by the element or class that starts it; the first match on an element wins.
FIGURES = [("mermaid", "pre", "mermaid"), ("terms", "dl", "terms"), ("table", "table", None), ("cards", None, "arch"),
           ("findings", None, "findings"), ("bars", None, "bars"), ("stack", None, "stack"), ("stack", None, "stack-row"),
           ("timeline", "ol", "timeline"), ("phases", None, "phases"),
           ("scale", None, "scale"), ("tabs", None, "tabs"), ("metrics", None, "metrics"), ("flow", None, "flow"),
           ("diagram", None, "diagram"), ("decisions", "ol", "decisions"), ("code", "pre", None)]
LIMITS = {"phases": 1, "decisions": 1}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, hidden, figure, unit words list or None)
        self.words = 0
        self.long = []
        self.sections = [{"title": "(before the first h2)", "prose": 0, "figures": []}]
        self.figures = Counter()
        self.heading = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        parent = self.stack[-1] if self.stack else (None, False, None, None, False, None)
        hidden = parent[1] or tag in ("script", "style") or ("mermaid" in classes)
        if parent[0] == "details" and parent[4] and tag != "summary":
            hidden = True
        if parent[0] == "div" and parent[5] and tag == "section":
            hidden = hidden or parent[5][0] > 0
            parent[5][0] += 1
        figure = parent[2]
        if not figure:
            for name, t, c in FIGURES:
                if (t is None or t == tag) and (c is None or c in classes):
                    figure = name
                    # Several .stack-rows side by side are one figure, so a row right after another counts once.
                    if "stack-row" in classes and self.sections[-1]["figures"][-1:] == ["stack"]:
                        break
                    if not parent[1] and not (name == "table" and self.sections[-1]["title"].startswith("Decided")):
                        self.figures[name] += 1
                        self.sections[-1]["figures"].append(name)
                    break
        closed = tag == "details" and "open" not in a
        tabs = [0] if tag == "div" and "tabs" in classes else None
        unit = [] if tag in UNITS else None
        if tag == "h2" and not hidden:
            self.heading = []
        if tag not in VOID:
            self.stack.append((tag, hidden, figure, unit, closed, tabs))

    def handle_endtag(self, tag):
        if not any(e[0] == tag for e in self.stack):
            return
        while self.stack:
            e = self.stack.pop()
            if e[3] is not None and not e[1] and len(e[3]) > PARAGRAPH:
                self.long.append((len(e[3]), " ".join(e[3][:8])))
            if e[0] == "h2" and self.heading is not None:
                self.sections.append({"title": " ".join(self.heading), "prose": 0, "figures": []})
                self.heading = None
            if e[0] == tag:
                break

    def handle_data(self, data):
        if not self.stack or self.stack[-1][1]:
            return
        words = data.split()
        if not words:
            return
        self.words += len(words)
        if self.heading is not None:
            self.heading += words
            return
        unit = next((e[3] for e in reversed(self.stack) if e[3] is not None), None)
        if unit is not None:
            unit += words
        if not self.stack[-1][2]:
            self.sections[-1]["prose"] += len(words)


def main(path):
    page = Page()
    page.feed(re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S))
    flags = []
    print(f"visible words: {page.words} (budget about {BUDGET})")
    if page.words > BUDGET * 1.1:
        flags.append(f"over the word budget by {page.words - BUDGET}")
    print("figures, a Decided section's table aside: " + (", ".join(f"{k} ×{v}" for k, v in page.figures.most_common()) or "none"))
    for name, n in page.figures.items():
        if n > LIMITS.get(name, 2):
            flags.append(f"{name} used {n} times in the visible page (limit {LIMITS.get(name, 2)})")
    for n, start in page.long:
        flags.append(f"{n}-word paragraph or item (limit {PARAGRAPH}): \"{start} …\"")
    for s in page.sections[1:]:
        if s["prose"] > BARE_SECTION and not s["figures"] and not s["title"].startswith("Decided"):
            flags.append(f"section \"{s['title']}\" has {s['prose']} words of prose and no figure")
    for f in flags:
        print("FLAG " + f)
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
