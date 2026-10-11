#!/usr/bin/env python3
"""
BIT Announcement Tracker - Notification Scraper and Document Generator
Scrapes all available notifications from BIT sources (Main Website WP REST API & RSS,
Project VLE, and existing SQLite Database records), updates the database,
and exports a comprehensive Markdown documentation file.
"""

import os
import sys
import html
import logging
import sqlite3
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("doc_scraper")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bit_tracker.db")
OUTPUT_MD_PATH = os.path.join(BASE_DIR, "BIT_Announcements_Documentation.md")

WP_API_URL = "https://www.bit.lk/wp-json/wp/v2/posts?per_page=100"
FEED_URL = "https://www.bit.lk/index.php/feed/?paged={page}"
PROJECT_VLE_URL = "https://project.vle.bit.lk/"

def html_to_markdown(html_content):
    """Converts HTML content into clean, readable Markdown text."""
    if not html_content:
        return ""
    
    html_content = html.unescape(html_content)
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style tags
    for tag in soup(["script", "style"]):
        tag.decompose()
        
    # Replace line breaks
    for br in soup.find_all("br"):
        br.replace_with("\n")
        
    # Format links
    for a in soup.find_all("a"):
        text = a.get_text().strip()
        href = a.get("href", "").strip()
        if href and text and text != href:
            a.replace_with(f"[{text}]({href})")
        elif href:
            a.replace_with(f"<{href}>")
            
    # Format list items
    for li in soup.find_all("li"):
        li.insert(0, "- ")
        li.append("\n")
        
    # Format headings
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            h_text = h.get_text().strip()
            h.replace_with(f"\n\n{'#' * (level + 2)} {h_text}\n\n")
            
    # Format paragraphs and block containers
    for tag in soup.find_all(["p", "div", "blockquote"]):
        tag.append("\n\n")
        
    text = soup.get_text()
    
    # Normalize excessive newlines
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_blank = False
        elif not prev_blank:
            cleaned_lines.append("")
            prev_blank = True
            
    return html.unescape("\n".join(cleaned_lines).strip())

def parse_date_to_sortable(date_str):
    """Converts various date formats into a sortable tuple/string (YYYY-MM-DD HH:MM)."""
    if not date_str:
        return ("0000-00-00", "Unknown")
        
    cleaned = date_str.strip()
    
    # Try ISO format
    try:
        dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        return (dt.strftime("%Y-%m-%d %H:%M"), dt.strftime("%Y-%m-%d %H:%M"))
    except Exception:
        pass
        
    # Try common formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return (dt.strftime("%Y-%m-%d %H:%M"), dt.strftime("%Y-%m-%d"))
        except Exception:
            pass
            
    return ("1900-01-01", cleaned)

def scrape_wp_posts():
    """Scrapes all posts from WordPress REST API (full articles with HTML)."""
    logger.info("Fetching posts from BIT WordPress REST API...")
    announcements = []
    try:
        response = requests.get(WP_API_URL, timeout=20)
        if response.status_code == 200:
            posts = response.json()
            logger.info(f"Retrieved {len(posts)} posts from WP REST API.")
            for post in posts:
                raw_title = post.get("title", {}).get("rendered", "Untitled")
                clean_title = html.unescape(raw_title).strip()
                link = post.get("link", "")
                guid = post.get("guid", {}).get("rendered", link)
                raw_date = post.get("date", "")
                sort_key, display_date = parse_date_to_sortable(raw_date)
                
                content_html = post.get("content", {}).get("rendered", "")
                excerpt_html = post.get("excerpt", {}).get("rendered", "")
                
                content_md = html_to_markdown(content_html) if content_html else html_to_markdown(excerpt_html)
                
                announcements.append({
                    "id": guid,
                    "title": clean_title,
                    "link": link,
                    "raw_date": raw_date,
                    "display_date": display_date,
                    "sort_key": sort_key,
                    "source": "Main Site",
                    "content": content_md
                })
        else:
            logger.warning(f"WP REST API returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching from WP REST API: {e}")
        
    return announcements

def scrape_rss_feed_pages():
    """Paginates through the RSS feed to catch any extra or older posts."""
    logger.info("Checking RSS feed pages...")
    announcements = []
    page = 1
    while True:
        url = FEED_URL.format(page=page)
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                break
            feed = feedparser.parse(response.content)
            if not feed.entries:
                break
                
            for entry in feed.entries:
                guid = entry.get("id", entry.get("link"))
                raw_title = entry.get("title", "Untitled")
                clean_title = html.unescape(raw_title).strip()
                link = entry.get("link", "")
                pub_date = entry.get("published", "")
                sort_key, display_date = parse_date_to_sortable(pub_date)
                
                # Check for content in RSS
                content_html = ""
                if "content" in entry and entry.content:
                    content_html = entry.content[0].get("value", "")
                elif "summary" in entry:
                    content_html = entry.get("summary", "")
                    
                content_md = html_to_markdown(content_html)
                
                announcements.append({
                    "id": guid,
                    "title": clean_title,
                    "link": link,
                    "raw_date": pub_date,
                    "display_date": display_date,
                    "sort_key": sort_key,
                    "source": "Main Site",
                    "content": content_md
                })
            page += 1
        except Exception as e:
            logger.warning(f"Stopped RSS pagination at page {page}: {e}")
            break
            
    logger.info(f"Retrieved {len(announcements)} entries from RSS feed across {page-1} pages.")
    return announcements

def scrape_project_vle():
    """Scrapes announcements and discussion threads from Project VLE."""
    logger.info("Fetching notices from Project VLE...")
    announcements = []
    try:
        response = requests.get(PROJECT_VLE_URL, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            h3_tags = soup.find_all("h3")
            
            for h3 in h3_tags:
                title = h3.get_text(strip=True)
                next_link = h3.find_next("a", href=True)
                while next_link and "forum/discuss.php" not in next_link["href"]:
                    next_link = next_link.find_next("a", href=True)
                    
                link = next_link["href"] if next_link else PROJECT_VLE_URL
                guid = link
                
                # Fetch full discussion post content if available
                content_md = ""
                display_date = "Project VLE Notice"
                sort_key = "2025-10-01 00:00"
                
                if "discuss.php" in link:
                    try:
                        post_resp = requests.get(link, timeout=10)
                        if post_resp.status_code == 200:
                            post_soup = BeautifulSoup(post_resp.content, "html.parser")
                            article = post_soup.find("article") or post_soup.find("div", class_="forumpost")
                            if article:
                                # Extract post date if present
                                time_tag = article.find("time")
                                if time_tag and time_tag.get("datetime"):
                                    sort_key, display_date = parse_date_to_sortable(time_tag["datetime"])
                                content_md = html_to_markdown(str(article))
                    except Exception as e:
                        logger.warning(f"Could not fetch full post from {link}: {e}")
                        
                announcements.append({
                    "id": guid,
                    "title": title,
                    "link": link,
                    "raw_date": display_date,
                    "display_date": display_date,
                    "sort_key": sort_key,
                    "source": "Project VLE",
                    "content": content_md
                })
        logger.info(f"Retrieved {len(announcements)} notices from Project VLE.")
    except Exception as e:
        logger.error(f"Error scraping Project VLE: {e}")
        
    return announcements

def load_from_database():
    """Loads existing announcement records from SQLite database."""
    if not os.path.exists(DB_PATH):
        logger.info("Database file not found, skipping DB load.")
        return []
        
    logger.info("Loading existing records from SQLite database...")
    announcements = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, title, link, pub_date, source, discovered_at FROM announcements")
        rows = c.fetchall()
        for row in rows:
            sort_key, display_date = parse_date_to_sortable(row["pub_date"])
            announcements.append({
                "id": row["id"],
                "title": row["title"],
                "link": row["link"],
                "raw_date": row["pub_date"],
                "display_date": display_date,
                "sort_key": sort_key,
                "source": row["source"],
                "content": ""
            })
        conn.close()
        logger.info(f"Loaded {len(announcements)} records from SQLite database.")
    except Exception as e:
        logger.error(f"Error loading from database: {e}")
        
    return announcements

def sync_to_database(announcements):
    """Syncs any newly discovered announcements to the SQLite database."""
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            pub_date TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'Main'
        )
    ''')
    
    new_count = 0
    for ann in announcements:
        try:
            c.execute(
                "INSERT INTO announcements (id, title, link, pub_date, source) VALUES (?, ?, ?, ?, ?)",
                (ann["id"], ann["title"], ann["link"], ann["raw_date"], ann["source"])
            )
            new_count += 1
        except sqlite3.IntegrityError:
            pass  # Already exists
        except Exception as e:
            logger.warning(f"Error saving announcement to DB: {e}")
            
    conn.commit()
    conn.close()
    if new_count > 0:
        logger.info(f"Added {new_count} new announcements to SQLite database.")

def generate_markdown_doc(announcements):
    """Generates the comprehensive Markdown documentation file."""
    logger.info(f"Generating documentation file: {OUTPUT_MD_PATH}...")
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources_count = {}
    for a in announcements:
        sources_count[a["source"]] = sources_count.get(a["source"], 0) + 1
        
    sources_summary = ", ".join([f"**{src}**: {count}" for src, count in sources_count.items()])
    
    lines = []
    lines.append("# 📢 UCSC BIT Announcement Archive & Documentation")
    lines.append("")
    lines.append("> Comprehensive archive of all official notices and announcements from the Bachelor of Information Technology (BIT) program, University of Colombo School of Computing (UCSC).")
    lines.append("")
    lines.append("## 📌 Overview & Metadata")
    lines.append("")
    lines.append(f"- **Generated At:** `{now_str}`")
    lines.append(f"- **Total Notifications Scraped:** `{len(announcements)}`")
    lines.append(f"- **Breakdown by Source:** {sources_summary}")
    lines.append(f"- **Primary Portals Monitored:**")
    lines.append("  - Main BIT Portal: [https://www.bit.lk](https://www.bit.lk)")
    lines.append("  - Main VLE Portal: [https://vle.bit.lk](https://vle.bit.lk)")
    lines.append("  - Project VLE Portal: [https://project.vle.bit.lk](https://project.vle.bit.lk)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Quick Index Table
    lines.append("## 📋 Quick Reference Index")
    lines.append("")
    lines.append("| # | Date | Source | Title | Direct Link |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for idx, a in enumerate(announcements, 1):
        clean_title = a["title"].replace("|", "-").strip()
        link_str = f"[Open Link ↗]({a['link']})" if a['link'] else "N/A"
        anchor = f"announcement-{idx}"
        title_anchor = f"[{clean_title}](#{anchor})"
        lines.append(f"| {idx} | {a['display_date']} | `{a['source']}` | {title_anchor} | {link_str} |")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Detailed Announcements Section
    lines.append("## 📑 Detailed Announcements Archive")
    lines.append("")
    
    for idx, a in enumerate(announcements, 1):
        anchor = f"announcement-{idx}"
        lines.append(f'<a id="{anchor}"></a>')
        lines.append(f"### {idx}. {a['title']}")
        lines.append("")
        lines.append(f"- 📅 **Published Date:** `{a['display_date']}`")
        lines.append(f"- 🏷️ **Source:** `{a['source']}`")
        if a["link"]:
            lines.append(f"- 🔗 **Original Link:** [{a['link']}]({a['link']})")
        lines.append("")
        
        content = a.get("content", "").strip()
        if content:
            lines.append("#### Content & Details")
            lines.append("")
            lines.append(content)
        else:
            lines.append("*(No extended body content available in feed/record. Please visit the original link above for full details.)*")
            
        lines.append("")
        lines.append("---")
        lines.append("")
        
    # Write to file
    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    logger.info(f"Successfully generated documentation: {OUTPUT_MD_PATH}")

def main():
    print("==========================================================")
    print("  UCSC BIT Announcements - Master Scraper & Doc Generator")
    print("==========================================================")
    
    # Collect announcements from all available sources
    all_items = []
    
    # 1. WordPress REST API (Full contents)
    wp_items = scrape_wp_posts()
    all_items.extend(wp_items)
    
    # 2. RSS Feed (Pages 1..N)
    rss_items = scrape_rss_feed_pages()
    all_items.extend(rss_items)
    
    # 3. Project VLE Forum discussions
    pvle_items = scrape_project_vle()
    all_items.extend(pvle_items)
    
    # 4. Existing Database records (Historical VLE & past syncs)
    db_items = load_from_database()
    all_items.extend(db_items)
    
    # Merge and deduplicate
    # Prioritize items with content over items without content
    import re
    def normalize_title(t):
        if not t:
            return ""
        return re.sub(r'[^a-zA-Z0-9]', '', t.lower())

    unique_map = {}
    
    for item in all_items:
        src = item.get("source", "Main Site")
        if src in ("Main", "Main Site"):
            src = "Main Site"
        item["source"] = src
        
        norm_t = normalize_title(item.get("title", ""))
        if not norm_t:
            continue
            
        key = f"{src}::{norm_t}"
        
        if key not in unique_map:
            unique_map[key] = item
        else:
            existing = unique_map[key]
            # Prioritize fuller content
            if not existing.get("content") and item.get("content"):
                existing["content"] = item["content"]
            # Prioritize clean canonical permalinks over index.php date archives
            if "index.php" in existing.get("link", "") and "index.php" not in item.get("link", ""):
                existing["link"] = item["link"]
            # Prioritize more specific timestamps
            if len(item.get("display_date", "")) > len(existing.get("display_date", "")):
                existing["display_date"] = item["display_date"]
                existing["sort_key"] = item["sort_key"]
                
    merged_list = list(unique_map.values())
    
    # Sort chronologically (newest first)
    merged_list.sort(key=lambda x: str(x.get("sort_key") or ""), reverse=True)
    
    print(f"\n[+] Total unique announcements consolidated: {len(merged_list)}")
    
    # Sync new announcements to SQLite
    sync_to_database(merged_list)
    
    # Generate Markdown Documentation
    generate_markdown_doc(merged_list)
    
    print(f"[+] Master documentation created at: {OUTPUT_MD_PATH}")
    print("==========================================================")

if __name__ == "__main__":
    main()
