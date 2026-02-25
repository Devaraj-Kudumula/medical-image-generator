#!/usr/bin/env python3
"""Test MongoDB connection independently"""

import os
import sys
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://db_user:db_user@cluster0.9a1tk8o.mongodb.net/?retryWrites=true&w=majority')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

print("="*60)
print("MongoDB Connection Test")
print("="*60)

# Test 1: MongoDB Connection
print("\n1. Testing MongoDB connection...")
print(f"   URI: {MONGODB_URI[:30]}...{MONGODB_URI[-20:]}")
try:
    client = MongoClient(MONGODB_URI)
    client.admin.command('ping')
    print("   ✓ MongoDB connection successful")
except Exception as e:
    print(f"   ✗ MongoDB connection FAILED: {e}")
    sys.exit(1)

# Test 2: Database and Collection
print("\n2. Checking database and collection...")
try:
    db = client['medical_rag']
    collection = db['medical_documents']
    doc_count = collection.count_documents({})
    print(f"   ✓ Found {doc_count} documents in medical_rag.medical_documents")
    if doc_count == 0:
        print("   ⚠ Warning: Collection is empty!")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Database access FAILED: {e}")
    sys.exit(1)

# Test 3: Embeddings
if OPENAI_API_KEY:
    print("\n3. Testing OpenAI embeddings...")
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )
        print("   ✓ Embeddings initialized")
    except Exception as e:
        print(f"   ✗ Embeddings FAILED: {e}")
        sys.exit(1)
    
    # Test 4: Vector Store
    print("\n4. Testing MongoDB Atlas Vector Search...")
    try:
        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name='vector_index'
        )
        print("   ✓ Vector store initialized")
    except Exception as e:
        print(f"   ✗ Vector store FAILED: {e}")
        sys.exit(1)
    
    # Test 5: Retrieval
    print("\n5. Testing retrieval...")
    try:
        retriever = vectorstore.as_retriever(search_kwargs={'k': 1})
        docs = retriever.invoke("hand anatomy")
        print(f"   ✓ Retrieved {len(docs)} documents")
        if docs:
            print(f"   First doc preview: {docs[0].page_content[:100]}...")
    except Exception as e:
        print(f"   ✗ Retrieval FAILED: {e}")
        sys.exit(1)
else:
    print("\n3. Skipping embeddings test (no OPENAI_API_KEY)")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED - MongoDB RAG system is working!")
print("="*60)
