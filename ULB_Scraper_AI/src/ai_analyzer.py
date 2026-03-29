import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
try:
    from langchain_ollama import OllamaEmbeddings, OllamaLLM
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.llms import Ollama as OllamaLLM
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents import create_pandas_dataframe_agent

class ULBAdvancedAnalyzer:
    def __init__(self, csv_path="data/database/files_index.csv"):
        self.csv_path = csv_path
        self.persist_directory = "data/database/chroma_db"
        self.model_name = "llama3"
        
        self.embeddings = OllamaEmbeddings(model=self.model_name)
        self.llm = OllamaLLM(model=self.model_name, temperature=0)

        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            # Ne asigurăm că avem o coloană curată pentru extensii
            if 'url' in self.df.columns:
                self.df['extensie'] = self.df['url'].str.split('.').str[-1].str.lower().str[:4]
            
            self.pandas_agent = create_pandas_dataframe_agent(
                self.llm, 
                self.df, 
                verbose=True, 
                agent_type="zero-shot-react-description",
                allow_dangerous_code=True
            )
        else:
            print(f"❌ Fișierul {self.csv_path} nu a fost găsit!")

    def build_knowledge_base(self):
        """Construiește baza de date vectorială din CSV."""
        from langchain_community.document_loaders import CSVLoader
        if not os.path.exists(self.csv_path): return

        print("⏳ Indexare text în curs (Llama3)...")
        # Încărcăm doar coloanele utile pentru a nu polua memoria
        loader = CSVLoader(file_path=self.csv_path, encoding='utf-8')
        documents = loader.load()
        
        self.vector_db = Chroma.from_documents(
            documents=documents, 
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("Indexare completă! Acum pot citi conținutul fișierelor.")

    def ask_about_content(self, query):
        """Căutare inteligentă în documente."""
        if not hasattr(self, 'vector_db'):
            if os.path.exists(self.persist_directory):
                self.vector_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
            else:
                return "Baza de date nu este construită. Scrie 'da' la început."
        
        retriever = self.vector_db.as_retriever(search_kwargs={"k": 5}) # Căutăm în top 5 fragmente
        
        template = """Ești un asistent util pentru studenții ULBS. 
        Folosește DOAR contextul de mai jos pentru a răspunde.
        Dacă nu găsești informația, spune că fișierul există dar textul nu a fost extras corect.

        Context: {context}
        Întrebare: {question}
        Răspuns:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | self.llm | StrOutputParser())
        return chain.invoke(query)

    def analyze_data(self, query):
        """Analiză statistici/grafice."""
        print(f"\n[Analiză Date]: {query}")
        try:
            # Folosim invoke pentru a evita deprecation warnings
            response = self.pandas_agent.invoke(query)
            if plt.get_fignums():
                plt.show()
                plt.close('all')
            return response['output'] if isinstance(response, dict) else response
        except Exception as e:
            return f"Eroare: {str(e)}"