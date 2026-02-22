from typing import List, Tuple

# PDF and document processing
from langchain_classic.schema import Document

# Embeddings and VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def retrieve_chunks(query: str, vectorstore: Chroma, k: int = 6) -> List[Tuple[Document, float]]:
    """Retrieve top-k chunks (Document, score) from the Chroma vectorstore."""
    # Use the vectorstore's similarity search API (returns (doc, score))
    return vectorstore.similarity_search_with_score(query, k=k)

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.1
)

def extract_retrieval_query(user_prompt):
    system = """Extract:
        1. Primary medical condition
        2. Mechanism keywords
        3. Clinical keywords

        Return short structured text only.
        """

    response = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt}
    ])

    return response.content



embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    persist_directory="./medical_vectorstore",
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6}
)


def retrieve_chunks(user_prompt):
    query = extract_retrieval_query(user_prompt)
    docs = retriever.invoke(query)
    return docs

def build_final_image_prompt(user_prompt, system_prompt):

    docs = retrieve_chunks(user_prompt)
    context = "\n\n".join([doc.page_content for doc in docs])

    
    construction_prompt = f"""
        Retrieved High-Yield Context:
        {context}

        User Prompt:
        {user_prompt}

        Return a complete structured image generation prompt.
        """

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": construction_prompt}
    ])

    return response.content


def rag_image_prompt_pipeline(user_prompt):
    final_prompt = build_final_image_prompt(user_prompt)
    return final_prompt


final_prompt = rag_image_prompt_pipeline(user_prompt)

from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(api_key=GOOGLE_GENERATIVE_AI_API_KEY)

prompt = (final_prompt)
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image9.png")