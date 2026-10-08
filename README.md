# The CDT Bulletin

A classic-newspaper style bulletin board for the Centre for Doctoral Training in AI for Digital Media Inclusion, University of Surrey. Static site: no build step.

## Posting a story

Every story is an entry in `bulletins.json`. Commit to `main` and the site redeploys in about a minute.

- **Fastest (web/phone):** open `bulletins.json` on GitHub, press the pencil, paste a new object at the top of `bulletins`, commit.
- **Command line:** `python3 scripts/post.py "Headline" -s "Summary" -c Events -b --push` (`-b` puts it in the red breaking ticker).

Fields: `date` (ISO, UTC), `title`, `summary`, `category` (becomes a section tab), `author`, and optionally `body` (blank line = new paragraph), `link`, `breaking: true`. The newest story becomes the lead.

## Enabling hosting (once)

Repo **Settings → Pages → Source: GitHub Actions**. Site appears at `https://<user>.github.io/<repo>/`.

## Local preview

`python3 -m http.server` then open http://localhost:8000 (opening the file directly will not work, because the page fetches `bulletins.json`).
