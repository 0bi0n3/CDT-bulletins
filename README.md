# The CDT Bulletin

A classic-newspaper style bulletin board for the Centre for Doctoral Training in AI for Digital Media Inclusion, University of Surrey. Static site: no build step.

## Posting a story

Every story is an entry in `bulletins.json`. Commit to `main` and the site redeploys in about a minute.

- **Fastest (web/phone):** open `bulletins.json` on GitHub, press the pencil, paste a new object at the top of `bulletins`, commit.
- **Command line:** `python3 scripts/post.py "Headline" -s "Summary" -c Events -b --push` (`-b` puts it in the red breaking ticker).

Fields: `date` (ISO, UTC), `title`, `summary`, `category` (becomes a section tab), `author`, and optionally `body` (blank line = new paragraph), `link`, `breaking: true`. The newest story becomes the lead.

- **Issue form:** Issues → New issue → *Post a bulletin*. When a maintainer (owner, member or collaborator) opens it, a workflow adds the story to `bulletins.json`, redeploys and closes the issue. Issues from anyone else are ignored.

## Feed, story pages and archive

On every deploy `scripts/build.py` generates `feed.xml` (RSS 2.0, latest 50 stories), a permalink page per story under `story/`, and `archive.html` (all stories by month). Headlines on the front page link to their story pages. These exist only in the deployed site (`_site/`, not committed). To preview them locally: `python3 scripts/build.py && cd _site && python3 -m http.server`.

## Enabling hosting (once)

Repo **Settings → Pages → Source: GitHub Actions**. Site appears at `https://<user>.github.io/<repo>/`.

## Local preview

For the bare front page: `python3 -m http.server` then open http://localhost:8000 (opening the file directly will not work, because the page fetches `bulletins.json`).
