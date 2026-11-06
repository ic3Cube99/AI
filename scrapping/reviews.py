"""
Simple Rotten Tomatoes review scraper with an in-memory SQLite store.

This script downloads reviews for a movie page, stores them in SQLite, and
offers simple search, update, and delete interactions. It intentionally
preserves ASCII-cleaning behavior from the original sample.
"""

from __future__ import annotations
import sqlite3
from typing import Iterable, List, Tuple
import requests
from bs4 import BeautifulSoup


# Configuration
# Switch to Metacritic critic reviews: static HTML with stable data-testid attributes
URL = "https://www.metacritic.com/movie/et-the-extra-terrestrial/critic-reviews"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}
DB_PATH = "reviews.db"


def fetch_soup(url: str, *, timeout: float = 20.0) -> BeautifulSoup | None:
    """Fetch a page and return a BeautifulSoup parser, or None on error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print("Error downloading webpage:", exc)
        return None


def ascii_clean(text: str) -> str:
    """Replicate the original ASCII-cleaning approach."""
    return text.encode("ascii", "ignore").decode("utf-8")


def scrape_reviews(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """Extract (reviewer, review_text) tuples from Metacritic critic reviews."""
    results: List[Tuple[str, str]] = []

    cards = soup.select('[data-testid="review-card"]')
    if not cards:
        print("No review cards found. The website structure may have changed.")
        return results

    for card in cards:
        pub = card.select_one('[data-testid="review-card-header"]')
        quote = card.select_one('[data-testid="review-quote-text"]')
        author = card.select_one('[data-testid="review-author"]')

        # Build a reviewer label like: "Kenneth Turan (Los Angeles Times)"
        pub_text = pub.get_text(strip=True) if pub else ""
        # Publication text starts with a numeric score, strip leading digits and spaces
        while pub_text and pub_text[0].isdigit():
            pub_text = pub_text[1:]
        pub_text = pub_text.strip()

        author_text = author.get_text(strip=True) if author else ""
        if author_text.lower().startswith("by "):
            author_text = author_text[3:].strip()

        reviewer = author_text or pub_text or "Unknown"
        if author_text and pub_text and author_text != pub_text:
            reviewer = f"{author_text} ({pub_text})"

        review_text = quote.get_text(strip=True) if quote else ""

        if reviewer and review_text:
            results.append((ascii_clean(reviewer), ascii_clean(review_text)))

    return results


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ReviewData (
            ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
            Reviewer  TEXT,
            Review    TEXT
        )
        """
    )


def insert_reviews(conn: sqlite3.Connection, reviews: Iterable[Tuple[str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO ReviewData (Reviewer, Review)
        VALUES (?, ?)
        """,
        list(reviews),
    )
    conn.commit()


def print_all_reviews(conn: sqlite3.Connection, title: str) -> None:
    print(f"\n--- {title} ---")
    cur = conn.execute(
        """
        SELECT ReviewID, Reviewer, Review
        FROM ReviewData
        """
    )
    for row in cur.fetchall():
        print(row)


def print_highlighted_quotes(conn: sqlite3.Connection, count: int = 3) -> None:
    """Print a small selection of highlighted review quotes."""
    print("\n=== HIGHLIGHTED QUOTES ===")
    cur = conn.execute(
        """
        SELECT Review
        FROM ReviewData
        ORDER BY ReviewID
        LIMIT ?
        """,
        (count,),
    )
    rows = cur.fetchall()
    if not rows:
        print("No quotes available.")
        return
    for idx, (quote,) in enumerate(rows, start=1):
        print(f"{idx}. \"{quote}\"")


def main() -> None:
    # File-backed DB for external inspection via SQLite Browser
    with sqlite3.connect(DB_PATH) as conn:
        # Allow concurrent GUI reads while script is open
        conn.execute("PRAGMA journal_mode=WAL;")
        soup = fetch_soup(URL)
        if soup is None:
            return

        reviews = scrape_reviews(soup)
        print(f"Number of reviews scraped: {len(reviews)}")

        init_db(conn)
        if reviews:
            insert_reviews(conn, reviews)

        # Show all stored
        print_all_reviews(conn, "ALL STORED REVIEWS")

        # Highlight a few quotes
        print_highlighted_quotes(conn, 3)

        # Search for a reviewer
        search_name = input(
            "\nEnter a reviewer name to search, or press Enter to skip: "
        ).strip()
        if search_name:
            cur = conn.execute(
                """
                SELECT ReviewID, Reviewer, Review
                FROM ReviewData
                WHERE Reviewer = ?
                """,
                (search_name,),
            )
            for row in cur.fetchall():
                print(row)

        # Update a review
        update_name = input(
            "\nEnter the reviewer name whose review you want to update, or press Enter to skip: "
        ).strip()
        if update_name:
            new_review = input("Enter the new review text: ").strip()
            conn.execute(
                """
                UPDATE ReviewData
                SET Review = ?
                WHERE Reviewer = ?
                """,
                (new_review, update_name),
            )
            conn.commit()
            updated = conn.execute("SELECT changes()").fetchone()[0]
            print("Number of reviews updated:", updated)

        # Delete a user's movie reviews
        delete_name = input(
            "\nEnter a reviewer name whose reviews you want to delete, or press Enter to skip: "
        ).strip()
        if delete_name:
            confirm = input("Are you sure? Type YES to delete: ").strip()
            if confirm == "YES":
                conn.execute(
                    """
                    DELETE FROM ReviewData
                    WHERE Reviewer = ?
                    """,
                    (delete_name,),
                )
                conn.commit()
                deleted = conn.execute("SELECT changes()").fetchone()[0]
                print("Number of reviews deleted:", deleted)
            else:
                print("Deletion cancelled.")

        # Final display
        print_all_reviews(conn, "FINAL REVIEW DATA")


if __name__ == "__main__":
    main()
