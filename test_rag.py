#!/usr/bin/env python3
"""Test RAG retrieval and prompt generation"""

import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = 'mongodb+srv://db_user:db_user@cluster0.9a1tk8o.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_URI)
db = client['medical_rag']
collection = db['medical_documents']

print('Connecting to MongoDB...')
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')

vectorstore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embedding_model,
    index_name='vector_index',
    text_key='text',
    embedding_key='embedding'
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

print('Testing retrieval for: Hand Anatomy\n')
docs = retriever.invoke('Hand Anatomy')
print(f'✓ Retrieved {len(docs)} documents\n')

for i, doc in enumerate(docs, 1):
    print(f'--- Document {i} ---')
    print(doc.page_content[:300])
    print('...\n')

# Build final prompt
context = '\n\n'.join([doc.page_content for doc in docs])

print('Generating final image prompt with GPT-4...\n')

llm = ChatOpenAI(model='gpt-4', temperature=0.1)

system_prompt = """You are an elite medical visual prompt architect specializing in high-end USMLE and board-review medical illustrations.

Your task is to transform the user's request into a realistic, natural, and highly detailed image-generation prompt suitable for professional medical illustration.

Guidelines:
• Maintain scientific accuracy at USMLE Step 1 / Step 2 CK level.
• Write in natural descriptive language (not robotic bullet rules).
• Create a visually vivid, clinically realistic scene.
• Ensure the illustration feels professional, modern, and publication-quality.
• Add missing high-yield pathophysiologic details when necessary.
• Remove redundant or irrelevant user input.
• Emphasize clarity of mechanism and clinical correlation."""

construction_prompt = f"""Retrieved High-Yield Context:
{context}

User Request: Hand Anatomy

Return a complete structured image generation prompt for a medical illustration."""

response = llm.invoke([
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': construction_prompt}
])

print('\n' + '='*80)
print('FINAL IMAGE PROMPT')
print('='*80 + '\n')
print(response.content)
print('\n' + '='*80)
