#!/usr/bin/env python3
"""Add a bulletin to bulletins.json.

  python3 scripts/post.py "Headline" -s "One-line summary" -c Events [-b] [-l URL] [--push]
"""
import argparse, json, subprocess, pathlib, datetime

p = argparse.ArgumentParser()
p.add_argument("title")
p.add_argument("-s", "--summary", default="")
p.add_argument("-c", "--category", default="News")
p.add_argument("-l", "--link")
p.add_argument("-b", "--breaking", action="store_true", help="show in the breaking-news ticker")
p.add_argument("--headline", action="store_true", help="make this a lead-story candidate without the ticker")
p.add_argument("--push", action="store_true", help="commit and push straight away")
a = p.parse_args()

f = pathlib.Path(__file__).resolve().parent.parent / "bulletins.json"
data = json.loads(f.read_text())
entry = {"date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "title": a.title, "summary": a.summary, "category": a.category}
if a.link: entry["link"] = a.link
if a.breaking: entry["breaking"] = True
if a.headline: entry["headline"] = True
data["bulletins"].insert(0, entry)
f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("Added:", a.title)
if a.push:
    subprocess.run(["git", "add", str(f)], check=True)
    subprocess.run(["git", "commit", "-m", f"Bulletin: {a.title}"], check=True)
    subprocess.run(["git", "push"], check=True)
