import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
import json
from collections import deque
import hashlib

SEEDS = ['https://docs.python.org/3/','https://realpython.com/','https://wiki.python.org/moin/']
MAX_PAGES = 500
DELAY = 2.0

visited = set()
to_visit = deque(SEEDS)
pages_data = []
domain_last_visit = {}
robot_parsers = {}

def get_robot_parser(url):
    # load or cache robot parser for a domain
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    if domain not in robot_parsers:
        rp = RobotFileParser()
        rp.set_url(urljoin(domain, '/robots.txt'))
        try:
            rp.read()
        except:
            pass
        robot_parsers[domain] = rp
    return robot_parsers[domain]

def can_fetch(url):
    # check robots.txt allowance
    try:
        return get_robot_parser(url).can_fetch("*", url)
    except:
        return True

def respect_politeness(url):
    # enforce delay between requests to same domain
    domain = urlparse(url).netloc
    if domain in domain_last_visit:
        elapsed = time.time() - domain_last_visit[domain]
        if elapsed < DELAY:
            time.sleep(DELAY - elapsed)
    domain_last_visit[domain] = time.time()

def fetch_page(url):
    try:
        # ignore common non html file types
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip',
                            '.tar', '.gz', '.mp3', '.mp4', '.avi', '.doc', '.docx']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return None, None
        
        headers = {'User-Agent': 'MyCrawlerBot'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # ensure the response is html
        content_type = response.headers.get('Content-Type', '').lower()
        if 'html' not in content_type:
            return None, None
        
        return response.text, response.url
    except:
        return None, None

def extract_links(html, base_url):
    # collect http or https links from page
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        absolute_url = urljoin(base_url, link['href'])
        parsed = urlparse(absolute_url)
        if parsed.scheme in ['http', 'https']:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            links.append(clean_url)
    return links

def extract_text(html):
    # extract page title and visible text
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(['script', 'style', 'meta', 'link']):
            script.decompose()
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ''
        text = soup.get_text(separator=' ', strip=True)
        return title_text, text
    except:
        return '', ''

def crawl():
    print(f"Starting crawl: {MAX_PAGES} pages, {DELAY}s delay")
    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.popleft()
        if url in visited or not can_fetch(url):
            continue
        
        respect_politeness(url)
        print(f"[{len(visited)+1}/{MAX_PAGES}] {url}")
        html, final_url = fetch_page(url)
        
        if html:
            visited.add(url)
            title, text = extract_text(html)
            outlinks = extract_links(html, final_url or url)
            
            pages_data.append({
                'doc_id': hashlib.md5(url.encode()).hexdigest(),
                'url': url,
                'title': title,
                'text': text,
                'outlinks': outlinks
            })
            
            # enqueue outlinks for future crawling
            for link in outlinks:
                if link not in visited:
                    to_visit.append(link)
    
    with open('data/pages.json', 'w') as f:
        json.dump(pages_data, f, ensure_ascii=False)
    print(f"Done! Crawled {len(visited)} pages")

if __name__ == '__main__':
    crawl()
