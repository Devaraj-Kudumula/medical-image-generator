"""
Build MongoDB Atlas Vector Store from First Aid PDF
Replaces ChromaDB with MongoDB for better deployment reliability
"""

import os
import sys
from pathlib import Path
from typing import List
import PyPDF2
from langchain_classic.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import re

# Configuration
MONGODB_URI = "mongodb+srv://db_user:db_user@cluster0.9a1tk8o.mongodb.net/"
DB_NAME = "medical_rag"
COLLECTION_NAME = "medical_documents"
INDEX_NAME = "vector_index"

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set!")


class MedicalPDFProcessor:
    """Process medical PDFs with intelligent chunking"""

    def __init__(self, pdf_path: str, chunk_size: int = 1500, chunk_overlap: int = 200):
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_pdf(self) -> List[Document]:
        """Load PDF using LangChain PyPDFLoader"""
        print(f"Loading PDF from: {self.pdf_path}")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        try:
            loader = PyPDFLoader(self.pdf_path)
            documents = loader.load()
            if not documents:
                raise ValueError("No pages extracted from PDF")
            print(f"✓ Loaded {len(documents)} pages from PDF")
            return documents
        except Exception as e:
            print(f"✗ Error loading PDF: {str(e)}")
            raise

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'[ ]{2,}', ' ', text)
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        return text.strip()

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Intelligently chunk documents for medical content"""
        separators = [
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]

        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        print(f"Chunking documents (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})...")
        chunked_docs = text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunked_docs)} chunks from {len(documents)} pages")

        # Preprocess and enhance metadata
        enhanced_docs = []
        for i, doc in enumerate(chunked_docs):
            doc.page_content = self.preprocess_text(doc.page_content)
            doc.metadata['chunk_id'] = i
            doc.metadata['chunk_size'] = len(doc.page_content)
            
            # Extract keywords
            keywords = self._extract_keywords(doc.page_content)
            if keywords:
                doc.metadata['keywords'] = ', '.join(keywords)
            
            enhanced_docs.append(doc)

        return enhanced_docs

    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract potential medical keywords from chunk"""
        potential_keywords = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        common_words = {'The', 'This', 'That', 'These', 'Those', 'Note', 'Important', 'A', 'An'}
        keywords = [kw for kw in potential_keywords if kw not in common_words]
        return keywords[:max_keywords] if keywords else []


def create_mongodb_vectorstore(documents: List[Document], mongodb_uri: str, db_name: str, collection_name: str, index_name: str):
    """Create MongoDB Atlas Vector Store"""
    
    print("\n" + "="*80)
    print("Creating MongoDB Atlas Vector Store")
    print("="*80)
    
    # Initialize embeddings
    print("Initializing OpenAI embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )
    print("✓ Embedding model initialized")
    
    # Connect to MongoDB
    print(f"Connecting to MongoDB Atlas...")
    client = MongoClient(mongodb_uri)
    
    # Test connection
    try:
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        raise
    
    # Get database and collection
    db = client[db_name]
    collection = db[collection_name]
    
    # Clear existing documents
    print(f"Clearing existing documents from {collection_name}...")
    collection.delete_many({})
    print("✓ Collection cleared")
    
    # Create vector store
    print(f"Creating vector store with {len(documents)} documents...")
    vectorstore = MongoDBAtlasVectorSearch.from_documents(
        documents=documents,
        embedding=embeddings,
        collection=collection,
        index_name=index_name
    )
    print("✓ Vector store created successfully")
    
    # Verify
    doc_count = collection.count_documents({})
    print(f"✓ Verified: {doc_count} documents in MongoDB")
    
    return vectorstore, client


def main():
    """Main execution"""
    print("="*80)
    print("Medical PDF to MongoDB Vector Store")
    print("="*80)
    
    # Update this path to your First Aid PDF
    pdf_path = "/Users/apple/Downloads/_OceanofPDF.com_First_Aid_for_the_USMLE_Step_1_2025_-_Tao_Le.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"\n✗ PDF not found at: {pdf_path}")
        print("Please update the pdf_path variable with the correct path to your First Aid PDF")
        return
    
    # Process PDF
    processor = MedicalPDFProcessor(
        pdf_path=pdf_path,
        chunk_size=1500,
        chunk_overlap=200
    )
    
    documents = processor.load_pdf()
    chunked_documents = processor.chunk_documents(documents)
    
    # Create MongoDB vector store
    vectorstore, client = create_mongodb_vectorstore(
        documents=chunked_documents,
        mongodb_uri=MONGODB_URI,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        index_name=INDEX_NAME
    )
    
    # Test retrieval
    print("\n" + "="*80)
    print("Testing Retrieval")
    print("="*80)
    
    test_query = "hand anatomy bones"
    print(f"Query: {test_query}")
    results = vectorstore.similarity_search(test_query, k=2)
    
    if results:
        print(f"✓ Retrieved {len(results)} documents")
        print(f"\nSample result:")
        print(f"  {results[0].page_content[:200]}...")
    else:
        print("⚠ No results found")
    
    client.close()
    
    print("\n" + "="*80)
    print("MongoDB Vector Store Build Complete!")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Database: {DB_NAME}")
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Index: {INDEX_NAME}")
    print(f"\nNext: Create vector search index in MongoDB Atlas UI")
    print(f"  1. Go to Atlas UI → Database → Search")
    print(f"  2. Create Search Index on collection: {COLLECTION_NAME}")
    print(f"  3. Use index name: {INDEX_NAME}")
    print(f"  4. Use JSON config:")
    print("""
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
""")


if __name__ == "__main__":
    main()
