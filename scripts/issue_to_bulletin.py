#!/usr/bin/env python3
"""Turn a bulletin issue-form submission into a bulletins.json entry.

Reads ISSUE_TITLE, ISSUE_BODY, ISSUE_CREATED from the environment
(never interpolated into a shell command, so issue text cannot inject code).
"""
import json, os, pathlib, re

body = os.environ["ISSUE_BODY"]
fields = {}
for m in re.finditer(r"^### (.+?)\s*\n+(.*?)(?=^### |\Z)", body, re.S | re.M):
    v = m.group(2).strip()
    fields[m.group(1).strip()] = "" if v == "_No response_" else v

title = re.sub(r"^\[Bulletin\]\s*", "", os.environ["ISSUE_TITLE"]).strip()
entry = {
    "date": os.environ["ISSUE_CREATED"],
    "title": title,
    "summary": fields.get("Summary", ""),
    "category": fields.get("Category", "News") or "News",
}
if fields.get("Details"): entry["body"] = fields["Details"]
if re.match(r"https?://\S+$", fields.get("Link", "")): entry["link"] = fields["Link"]
flags = fields.get("Flags", "").lower()
if "[x] breaking" in flags: entry["breaking"] = True
if "[x] headline" in flags: entry["headline"] = True

f = pathlib.Path("bulletins.json")
data = json.loads(f.read_text())
data["bulletins"].insert(0, entry)
f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("Added:", title)
