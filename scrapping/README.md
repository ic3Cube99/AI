# Metacritic Critic Review Scraper

`reviews.py` downloads critic reviews from the configured Metacritic movie page,
stores them in a local SQLite database, and provides interactive search, update,
and delete operations.

The current target is *E.T. the Extra-Terrestrial*:

`https://www.metacritic.com/movie/et-the-extra-terrestrial/critic-reviews`

## Requirements

- Python 3.10 or later
- `requests`
- `beautifulsoup4`

Install the third-party packages with:

```bash
python -m pip install requests beautifulsoup4
```

## Run

From this directory, run:

```bash
python reviews.py
```

The script creates `reviews.db` in the current working directory. It creates a
`ReviewData` table if needed, fetches the page, inserts the scraped reviews, and
prints all stored rows plus up to three highlighted quotes.

After scraping, the script prompts you to optionally:

1. Search for a reviewer by the exact reviewer name.
2. Replace the review text for a reviewer.
3. Delete a reviewer's rows by entering `YES` at the confirmation prompt.

Press Enter at a prompt to skip that operation. Reviewer updates and deletions
apply to every matching row.

## Data and behavior

- Each row contains an auto-incremented `ReviewID`, `Reviewer`, and `Review`.
- New rows are appended on every successful run; existing reviews are not
  deduplicated.
- Non-ASCII characters are removed from reviewer names and review text.
- If the request fails, the script prints the download error and exits. If no
  review cards are found, it prints a notice and continues with an empty result.
- The scraper depends on Metacritic's current page structure and may need updates
  if the site changes its HTML.

Use the scraper responsibly and follow the website's terms and applicable
rules for automated access.
