import os
import sys
from src.crawler import ULBDeepScraper
from src.ai_analyzer import ULBAdvancedAnalyzer

def main():
    print("\n" + "="*50)
    print("ULB SIBIU - SISTEM INTEGRAT DE COLECTARE ȘI AI")
    print("="*50)

    print("\nAlege o opțiune:")
    print("1. Scraping + Download (Crawler Deep)")
    print("2. Chat AI & Analiză (Llama 3)")
    print("3. ❌ Ieșire")
    
    choice = input("\nOpțiunea ta: ")

    if choice == "1":
        limit = input("Câte pagini să explorez? (Implicit 500, max recomandat 2000): ")
        limit = int(limit) if limit.isdigit() else 500
        
        scraper = ULBDeepScraper(max_pages=limit)
        scraper.run()
        print("\n[INFO] Colectarea s-a terminat. Acum poți reporni programul și alege opțiunea 2.")

    elif choice == "2":
        csv_path = "data/database/files_index.csv"
        if not os.path.exists(csv_path):
            print("❌ Eroare: Nu am găsit date. Rulează mai întâi opțiunea 1!")
            return

        analyzer = ULBAdvancedAnalyzer(csv_path=csv_path)
        
        # Verificăm dacă avem baza de date vectorială (Chroma)
        if not os.path.exists("data/database/chroma_db"):
            ask = input("Vrei să indexăm conținutul pentru întrebări despre text? (da/nu): ")
            if ask.lower() == 'da':
                analyzer.build_knowledge_base()

        print("\nSistemul de analiză este online. (Scrie 'exit' pentru a închide)")
        while True:
            try:
                query = input("\n[Tu]: ").strip()
                if query.lower() in ['exit', 'quit', 'iesire']: break
                if not query: continue

                # Identificăm tipul de întrebare
                data_keywords = ['tabel', 'grafic', 'plot', 'cate', 'cati', 'top', 'statistica', 'extensie']
                
                if any(kw in query.lower() for kw in data_keywords):
                    print(f"\n[AI Analiză]: {analyzer.analyze_data(query)}")
                else:
                    print(f"\n[AI Chat]: {analyzer.ask_about_content(query)}")
            except KeyboardInterrupt:
                break

    else:
        print("La revedere!")

if __name__ == "__main__":
    main()