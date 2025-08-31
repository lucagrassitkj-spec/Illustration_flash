import feedparser
import yaml
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- RACCOLTA DA RSS ---
def fetch_rss(feed_url, max_articles):
    feed = feedparser.parse(feed_url)
    results = []
    for entry in feed.entries[:max_articles]:
        results.append(f"**{entry.title}**\n{entry.link}")
    return results

# --- RACCOLTA DA HTML (senza RSS) ---
def fetch_html(site_url, max_articles):
    results = []
    resp = requests.get(site_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Caso specifico: Illustration.lol
    # Gli articoli sono dentro <a class="block">
    articles = soup.select("a.block")[:max_articles]
    for a in articles:
        title = a.get_text(strip=True)
        link = a["href"]
        # Se i link sono relativi, li completiamo
        if link.startswith("/"):
            link = site_url.rstrip("/") + link
        results.append(f"**{title}**\n{link}")

    return results

# --- MAIN ---
def main():
    config = load_config()
    all_text = []

    for site in config["sites"]:
        try:
            if site["type"] == "rss":
                summaries = fetch_rss(site["url"], config.get("max_per_site", 2))
            elif site["type"] == "html":
                summaries = fetch_html(site["url"], config.get("max_per_site", 2))
            else:
                summaries = []

            if summaries:
                all_text.append(f"## {site['name']}")
                all_text.extend(summaries)
        except Exception as e:
            all_text.append(f"(Errore con {site['name']}: {e})")

    os.makedirs("output", exist_ok=True)
    fname = f"output/illustrazione_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))
    print("DEBUG: file salvato", fname)

if __name__ == "__main__":
    main()
