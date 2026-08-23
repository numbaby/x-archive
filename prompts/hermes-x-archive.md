# X Archive Collection Task

You are the X Archive automation agent.

Your mission is to collect new posts from the configured X accounts and archive them into the GitHub repository.

Repository:

/home/azureuser/x-archive/

Do NOT directly invent or modify historical archive entries.

---

## STEP 1 — Collect

Get X account profiles from https://github.com/numbaby/profile_list_on_x/blob/main/profiles.json

Collect new posts from each above extracted X profile.

RSS service like fxtwitter-rss is preferred over X API call. 

For every post extract:

- X post ID
- username
- publication timestamp
- exact original text
- original X URL
- media URLs
- media type

Preserve the original post text exactly.

Do not translate it.

Do not summarize it.

Do not rewrite it.

Normalize timestamps to UTC ISO-8601:

YYYY-MM-DDTHH:mm:ssZ

---

## STEP 2 — Prepare JSON

Create a temporary JSON file containing the newly discovered posts.

Use:


/home/azureuser/x-archive/incoming/

The JSON must follow:

schema/post.schema.json

---

## STEP 3 — Archive

Run:

cd /home/azureuser/x-archive 

source .venv/bin/activate

python scripts/archive.py incoming/<FILE>.json

Do not manually append records to JSONL.

Do not manually modify data/index.json.

The Python script is the source of truth for:

- validation
- deduplication
- JSONL storage
- media download
- index management

---

## STEP 4 — Render Markdown

After archive.py completes successfully:

python scripts/render_markdown.py --all

Do not manually format archive Markdown.

---

## STEP 5 — Validate

Run:

python scripts/archive.py --help

Then inspect:

git diff --check

Check:

git status

The repository must not contain:

- GitHub access tokens
- API keys
- passwords
- OAuth secrets
- session cookies

---

## STEP 6 — Review changes

Run:

git diff --stat

git diff -- data archive

Make sure:

- only expected files changed
- no historical post was deleted
- no existing post ID was modified
- no unexpected file was added
- images correspond to the new posts

---

## STEP 7 — Git

Before committing:

git pull --rebase origin main

Then check:

git status

If there are no changes:

DO NOT create a commit.

If there are changes:

git add data archive assets

Commit using:

archive: add @USERNAME YYYY-MM-DD posts

Example:

archive: add @elonmusk 2026-08-21 posts

Then:

git push origin main

---

## STEP 8 — Report

Return:

Posts discovered:
New posts:
Duplicates skipped:
Images downloaded:
Image failures:
Markdown files updated:
Git commit:

If there are no new posts:

Report that nothing new was archived.

Do not create an empty commit.

---

## Error handling

If any of the following occurs:

- Git conflict
- authentication failure
- schema validation failure
- media download failure
- malformed X data
- unexpected repository modification

STOP.

Do not delete files.

Do not reset the repository.

Do not force push.

Report the exact error.
