"""Build a complete edition from CNA's public Singapore and World RSS feeds."""
from datetime import datetime, timezone, timedelta
from html import unescape
from pathlib import Path
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FEEDS = {'singapore': '10416', 'world': '6311'}

def clean(value):
    return ' '.join(unescape(re.sub(r'<[^>]*>', ' ', value or '')).split())

def fetch_stories(category):
    url = f'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category={category}'
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'EverydayCompass/1.0 RSS reader'})
            with urllib.request.urlopen(request, timeout=40) as response:
                tree = ET.fromstring(response.read())
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    stories, seen = [], set()
    # Retain the publisher's feed ordering; do not invent editorial rankings.
    for item in tree.findall('./channel/item'):
        title, link = clean(item.findtext('title')), (item.findtext('link') or '').strip()
        if not title or not link.startswith('https://www.channelnewsasia.com/') or link in seen:
            continue
        seen.add(link)
        stories.append({'title': title, 'url': link,
                        'summary': clean(item.findtext('description'))[:500],
                        'source': 'CNA', 'published': clean(item.findtext('pubDate'))})
        if len(stories) == 15:
            return stories
    raise ValueError(f'Feed {category} has only {len(stories)} usable stories; preserving previous edition')

def main():
    edition = {key: fetch_stories(value) for key, value in FEEDS.items()}
    edition['generated_at'] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    edition['test_mode'] = False
    target = ROOT / 'data/daily-news.json'
    target.parent.mkdir(exist_ok=True)
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(edition, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(target)
    print(f"Generated {edition['generated_at']}: 15 Singapore + 15 World stories")

if __name__ == '__main__':
    main()
