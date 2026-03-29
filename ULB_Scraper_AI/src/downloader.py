import os
import requests
from tqdm import tqdm

class ULBDownloader:
    def __init__(self, base_data_path="data/raw"):
        self.base_path = base_data_path
        # Mapăm tipul de fișier la folderul corect
        self.folders = {
            'pdf': os.path.join(self.base_path, 'pdf'),
            'word': os.path.join(self.base_path, 'word'),
            'image': os.path.join(self.base_path, 'images')
        }
        self._create_folders()

    def _create_folders(self):
        """Asigură existența folderelor de destinație."""
        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)

    def download_file(self, file_info):
        """
        Descarcă un singur fișier.
        file_info: dicționar {'url': ..., 'type': ...}
        """
        url = file_info['url']
        file_type = file_info['type']
        
        # Extragem numele fișierului din URL
        file_name = url.split('/')[-1]
        if not file_name:
            file_name = "unnamed_file"
            
        save_path = os.path.join(self.folders[file_type], file_name)

        try:
            # Stream=True permite descărcarea fișierelor mari fără a bloca memoria RAM
            response = requests.get(url, stream=True, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return save_path
            else:
                print(f"Eroare {response.status_code} pentru: {url}")
                return None
        except Exception as e:
            print(f"Eroare la descărcarea {url}: {e}")
            return None

    def download_batch(self, files_list):
        """Descarcă o listă întreagă de fișiere cu progress bar."""
        print(f"Începe descărcarea a {len(files_list)} fișiere...")
        downloaded_paths = []
        
        for file in tqdm(files_list):
            path = self.download_file(file)
            if path:
                downloaded_paths.append(path)
        
        return downloaded_paths

# Test rapid
if __name__ == "__main__":
    # Simulăm o listă de test
    test_files = [
        {'url': 'https://www.ulbsibiu.ro/wp-content/uploads/Carta-ULBS-2024.pdf', 'type': 'pdf'},
        # Poți adăuga un link de imagine real de pe site pentru test
    ]
    downloader = ULBDownloader()
    downloader.download_batch(test_files)