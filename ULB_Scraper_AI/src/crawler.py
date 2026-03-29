import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import time

class ULBDeepScraper:
    def __init__(self, base_url="https://www.ulbsibiu.ro/", max_pages=1000):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.data = []
        self.max_pages = max_pages
        
        # Extensii de documente și imagini
        self.file_extensions = ('.pdf', '.docx', '.doc', '.xlsx', '.xls', '.jpg', '.png')
        
        # Foldere de stocare
        self.db_path = "data/database/files_index.csv"
        self.download_dir = "data/raw"
        os.makedirs(self.download_dir, exist_ok=True)

    def is_valid_url(self, url):
        parsed = urlparse(url)
        # Permitem orice subdomeniu care aparține de ulbsibiu.ro
        return "ulbsibiu.ro" in parsed.netloc and url not in self.visited_urls

    def download_file(self, url):
        """Descarcă fișierul și returnează calea locală."""
        try:
            parsed_url = urlparse(url)
            # Creăm o structură de foldere bazată pe extensie
            ext = url.split('.')[-1].lower()[:4]
            save_folder = os.path.join(self.download_dir, ext)
            os.makedirs(save_folder, exist_ok=True)
            
            file_name = os.path.basename(parsed_url.path)
            if not file_name:
                file_name = f"file_{int(time.time())}.{ext}"
            
            local_path = os.path.join(save_folder, file_name)
            
            # Descarcă doar dacă nu există deja
            if not os.path.exists(local_path):
                resp = requests.get(url, timeout=15, stream=True)
                if resp.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
            return local_path
        except:
            return "Error-Download"

    def scrape_page(self, url):
        if len(self.visited_urls) >= self.max_pages:
            return
        
        try:
            self.visited_urls.add(url)
            print(f"🔍 [{len(self.visited_urls)}/{self.max_pages}] Explorăm: {url}")
            
            response = requests.get(url, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                
                # Cazul 1: Este un fișier?
                if full_url.lower().endswith(self.file_extensions):
                    if not any(d['url'] == full_url for d in self.data):
                        print(f"   💾 Fișier găsit! Descărcăm...")
                        local_file = self.download_file(full_url)
                        
                        self.data.append({
                            'url': full_url,
                            'type': full_url.split('.')[-1].lower()[:4],
                            'local_path': local_file,
                            'source_page': url
                        })
                
                # Cazul 2: Este o pagină nouă de explorat?
                elif self.is_valid_url(full_url):
                    # Verificăm să nu fie un link de tip anchor (#) sau mailto
                    if urlparse(full_url).scheme in ['http', 'https']:
                        self.scrape_page(full_url)

        except Exception as e:
            print(f"⚠️ Eroare la {url}: {e}")

    def run(self):
        print(f"🚀 START Deep Scraper pe {self.base_url}")
        self.scrape_page(self.base_url)
        self.save_data()

    def save_data(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        df = pd.DataFrame(self.data)
        df.to_csv(self.db_path, index=False)
        print(f"\n✅ Colectare terminată! {len(df)} fișiere salvate în {self.db_path}")