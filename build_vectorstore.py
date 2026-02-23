"""
Script to build and populate the medical vectorstore for RAG
This script should be run locally to create the vectorstore, then commit the result to git
"""

import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List

# Sample medical documents - REPLACE WITH YOUR ACTUAL MEDICAL CONTENT
# You should load this from your medical textbooks, notes, or databases
MEDICAL_DOCUMENTS = [
    {
        "content": """Hand Anatomy: The human hand consists of 27 bones including 8 carpals, 5 metacarpals, 
        and 14 phalanges. The carpal bones are arranged in two rows - proximal (scaphoid, lunate, triquetrum, 
        pisiform) and distal (trapezium, trapezoid, capitate, hamate). Blood supply is primarily from radial 
        and ulnar arteries forming palmar arches.""",
        "metadata": {"topic": "anatomy", "region": "hand", "type": "bones"}
    },
    {
        "content": """Myocardial Infarction Pathophysiology: Occurs when coronary artery occlusion leads to 
        myocardial ischemia and necrosis. Typically caused by atherosclerotic plaque rupture with thrombus 
        formation. Presents with chest pain, diaphoresis, dyspnea. ECG shows ST elevation in affected leads. 
        Troponin elevation confirms diagnosis. Treatment includes aspirin, anticoagulation, reperfusion therapy.""",
        "metadata": {"topic": "cardiology", "condition": "MI", "type": "pathophysiology"}
    },
    {
        "content": """Pneumonia: Inflammation of lung parenchyma caused by bacterial, viral, or fungal pathogens. 
        Common organisms include Streptococcus pneumoniae, Haemophilus influenzae, atypical bacteria. 
        Symptoms include fever, cough, dyspnea, pleuritic chest pain. Chest X-ray shows infiltrates. 
        Treatment based on severity and organism (antibiotics, supportive care).""",
        "metadata": {"topic": "pulmonology", "condition": "pneumonia", "type": "infectious_disease"}
    },
    # Add more medical documents here from your knowledge base
]

def load_medical_documents() -> List[Document]:
    """
    Load medical documents from your source (textbooks, notes, database).
    Modify this function to load from your actual medical content source.
    """
    documents = []
    
    # Convert to LangChain Document objects
    for doc_dict in MEDICAL_DOCUMENTS:
        doc = Document(
            page_content=doc_dict["content"],
            metadata=doc_dict["metadata"]
        )
        documents.append(doc)
    
    return documents

def build_vectorstore(persist_directory: str = "./medical_vectorstore"):
    """
    Build and populate the medical vectorstore with embeddings.
    """
    print("="*60)
    print("Building Medical Vectorstore")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set!")
    
    print(f"✓ API key found (length: {len(api_key)})")
    
    # Initialize embeddings
    print("Initializing embedding model...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )
    print("✓ Embedding model initialized")
    
    # Load medical documents
    print("Loading medical documents...")
    documents = load_medical_documents()
    print(f"✓ Loaded {len(documents)} medical documents")
    
    # Create vectorstore (will delete existing one if present)
    print(f"Creating vectorstore at: {persist_directory}")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print("✓ Vectorstore created and populated")
    
    # Verify
    count = vectorstore._collection.count()
    print(f"✓ Vectorstore contains {count} documents")
    
    # Test retrieval
    print("\nTesting retrieval...")
    results = vectorstore.similarity_search("hand anatomy", k=1)
    if results:
        print(f"✓ Sample retrieval successful:")
        print(f"  {results[0].page_content[:150]}...")
    
    print("\n" + "="*60)
    print("Vectorstore build complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add this vectorstore to git:")
    print("   git add medical_vectorstore/")
    print("   git commit -m 'Add populated medical vectorstore'")
    print("   git push")
    print("\n2. Deploy to Render - RAG will now work!")
    
    return vectorstore

if __name__ == "__main__":
    # Build the vectorstore
    vectorstore = build_vectorstore()
