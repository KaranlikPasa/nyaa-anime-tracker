"""
Nyaa.si RSS Fetcher and Parser using Requests
"""
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import requests

NYAA_BASE_URL = "https://nyaa.si"
NYAA_RSS_URL = f"{NYAA_BASE_URL}/?page=rss"

# Standard BitTorrent trackers for generated magnet links
DEFAULT_TRACKERS = [
    "http://nyaa.tracker.wf:7777/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce"
]

class NyaaClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        })

    def build_magnet(self, info_hash: str, title: str) -> str:
        if not info_hash:
            return ""
        params = [f"xt=urn:btih:{info_hash.strip().lower()}"]
        if title:
            params.append(f"dn={urllib.parse.quote(title)}")
        for tr in DEFAULT_TRACKERS:
            params.append(f"tr={urllib.parse.quote(tr)}")
        return "magnet:?" + "&".join(params)

    def fetch_feed(self, category: str = "1_0", query: str = "", english_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Fetches the RSS feed from nyaa.si.
        category: "1_0" (All Anime), "1_2" (Anime - English), "1_4" (Anime - Raw), "0_0" (All Categories)
        query: Optional search keyword
        """
        # Backward compatibility with boolean english_only
        if english_only is not None:
            cat = "1_2" if english_only else "1_0"
        else:
            cat = category or "1_0"

        params = {"page": "rss"}
        if cat and cat != "all":
            params["c"] = cat
            
        if query and query.strip():
            params["q"] = query.strip()
            
        url = f"{NYAA_BASE_URL}/?{urllib.parse.urlencode(params)}"
        
        try:
            resp = self.session.get(url, timeout=12)
            if resp.status_code != 200:
                print(f"[NyaaClient] HTTP {resp.status_code} from {url}")
                return []
            return self._parse_rss(resp.content)
        except Exception as e:
            print(f"[NyaaClient] Request error: {e}")
            return []

    def _parse_rss(self, xml_bytes: bytes) -> List[Dict[str, Any]]:
        results = []
        try:
            root = ET.fromstring(xml_bytes)
            channel = root.find("channel")
            if channel is None:
                return results

            for item in channel.findall("item"):
                title_elem = item.find("title")
                title = title_elem.text if title_elem is not None and title_elem.text else ""

                link_elem = item.find("link")
                link = link_elem.text if link_elem is not None and link_elem.text else ""

                guid_elem = item.find("guid")
                guid = guid_elem.text if guid_elem is not None and guid_elem.text else link

                pub_date_elem = item.find("pubDate")
                pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ""

                # Namespaced fields
                seeders_elem = item.find("{https://nyaa.si/xmlns/nyaa}seeders")
                seeders = seeders_elem.text if seeders_elem is not None and seeders_elem.text else "0"

                leechers_elem = item.find("{https://nyaa.si/xmlns/nyaa}leechers")
                leechers = leechers_elem.text if leechers_elem is not None and leechers_elem.text else "0"

                size_elem = item.find("{https://nyaa.si/xmlns/nyaa}size")
                size = size_elem.text if size_elem is not None and size_elem.text else ""

                category_elem = item.find("{https://nyaa.si/xmlns/nyaa}category")
                category = category_elem.text if category_elem is not None and category_elem.text else ""

                hash_elem = item.find("{https://nyaa.si/xmlns/nyaa}infoHash")
                info_hash = hash_elem.text if hash_elem is not None and hash_elem.text else ""

                magnet = self.build_magnet(info_hash, title)

                results.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "guid": guid.strip(),
                    "pubDate": pub_date.strip(),
                    "seeders": seeders.strip(),
                    "leechers": leechers.strip(),
                    "size": size.strip(),
                    "category": category.strip(),
                    "infoHash": info_hash.strip(),
                    "magnet": magnet
                })

        except Exception as e:
            print(f"[NyaaClient] XML parse error: {e}")

        return results

nyaa_client = NyaaClient()
