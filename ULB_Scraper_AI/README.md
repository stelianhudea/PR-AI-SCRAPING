chmod +x START-NOU.sh
./START-NOU.sh



1. src/crawler.py (Ochii)
Se ocupă de navigarea recursivă pe ulbsibiu.ro și găsirea link-urilor.
Funcție cheie: is_valid_url (permite subdomenii) și scrape_page (recursivitate).

2. src/downloader.py (Mâna)
Primește un URL de la crawler și îl salvează fizic în data/raw/.
Funcție cheie: download(url) (creează subfoldere pe extensii: /pdf, /docx).

3. src/extractors.py (Traducătorul)
Deschide PDF-urile descărcate și pune textul în CSV.
Funcție cheie: extract_pdf(path) și process_all() (completează coloana continut_text).

4. src/ai_analyzer.py (Creierul)
Folosește Llama 3 pentru a răspunde din context (RAG) sau pentru a face grafice (Pandas Agent).
Funcție cheie: ask_about_content (Text) și analyze_data (Grafice/Tabele).

⚠️ Ultimul detaliu: Fișierul src/__init__.py
Acesta este un fișier GOL. Trebuie doar să existe în folderul src/. Fără el, Python nu va lăsa main.py să importe modulele (from src.crawler import ...).