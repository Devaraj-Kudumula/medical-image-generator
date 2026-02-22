from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import requests
from pathlib import Path
from typing import List
from io import BytesIO

# LangChain and OpenAI imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Google Gemini for image generation
from google import genai
from google.genai import types
from PIL import Image

app = Flask(__name__)
CORS(app)

# Configure API keys
openai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')

# Create directory for generated images
IMAGES_DIR = Path('generated_images')
IMAGES_DIR.mkdir(exist_ok=True)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,
    api_key=openai_api_key
)

# Initialize Google Gemini client for image generation
gemini_client = genai.Client(api_key=google_api_key) if google_api_key else None

# Load vectorstore
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=openai_api_key
)

vectorstore = None
retriever = None

# Try to load vectorstore if it exists
vectorstore_path = Path('./medical_vectorstore')
if vectorstore_path.exists():
    try:
        vectorstore = Chroma(
            persist_directory=str(vectorstore_path),
            embedding_function=embedding_model
        )
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 6}
        )
        print("✓ Medical vectorstore loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load vectorstore: {str(e)}")
else:
    print("⚠️ Warning: Medical vectorstore not found. RAG features will be limited.")


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    """
    Generate a detailed image prompt using RAG-enhanced LLM based on system instruction
    """
    try:
        data = request.get_json()
        system_instruction = data.get('system_instruction', '')
        user_question = data.get('user_question', 'A serene landscape at sunset')
        
        if not system_instruction:
            return jsonify({'error': 'System instruction is required'}), 400
        
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'}), 500
        
        # Use RAG if vectorstore is available
        if retriever:
            try:
                # Extract retrieval query
                extract_system = """Extract:
                    1. Primary medical condition
                    2. Mechanism keywords
                    3. Clinical keywords
                    
                    Return short structured text only.
                """
                
                extract_response = llm.invoke([
                    {"role": "system", "content": extract_system},
                    {"role": "user", "content": user_question}
                ])
                
                retrieval_query = extract_response.content
                
                # Retrieve relevant documents
                docs = retriever.invoke(retrieval_query)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Build final prompt with RAG context
                construction_prompt = f"""
                    Retrieved High-Yield Medical Context:
                    {context}
                    
                    User Request:
                    {user_question}
                    
                    Return a complete structured image generation prompt following the system instruction guidelines.
                """
                
                response = llm.invoke([
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": construction_prompt}
                ])
                
                generated_prompt = response.content.strip()
                
            except Exception as e:
                print(f"RAG retrieval failed, using direct generation: {str(e)}")
                # Fallback to direct generation without RAG
                response = llm.invoke([
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Create a detailed medical illustration prompt for: {user_question}"}
                ])
                generated_prompt = response.content.strip()
        else:
            # Direct generation without RAG
            response = llm.invoke([
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Create a detailed medical illustration prompt for: {user_question}"}
            ])
            generated_prompt = response.content.strip()
        
        return jsonify({
            'prompt': generated_prompt,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating prompt: {str(e)}'}), 500


@app.route('/generate-image', methods=['POST'])
def generate_image():
    """
    Generate an image using Google Gemini based on the provided prompt
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if not google_api_key:
            return jsonify({'error': 'Google Generative AI API key not configured. Please set GOOGLE_GENERATIVE_AI_API_KEY environment variable.'}), 500
        
        if not gemini_client:
            return jsonify({'error': 'Gemini client not initialized'}), 500
        
        print(f"Generating image with prompt: {prompt[:100]}...")
        
        # Call Gemini API to generate image
        response = gemini_client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
        )
        
        print(f"Response received. Extracting image...")
        
        # Extract image from response (matching working notebook code)
        image_saved = False
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'image_{timestamp}.png'
        filepath = IMAGES_DIR / filename
        
        try:
            # Access via candidates[0].content.parts (correct path based on working code)
            for part in response.candidates[0].content.parts:
                if part.text:
                    print(f"Text part found: {part.text[:100] if len(part.text) > 100 else part.text}")
                
                elif part.inline_data:
                    print("Image data found, saving...")
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(str(filepath))
                    image_saved = True
                    print(f"Image saved successfully to {filepath}")
                    break
        except Exception as part_error:
            print(f"Error extracting image from response: {str(part_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error processing Gemini response: {str(part_error)}'}), 500
        
        if not image_saved:
            return jsonify({'error': 'No image generated in response. Check server logs for details.'}), 500
        
        # Return the local URL for serving
        local_url = f'http://localhost:5001/images/{filename}'
        
        return jsonify({
            'image_url': local_url,
            'filename': filename,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generating image: {str(e)}'}), 500


@app.route('/images/<filename>')
def serve_image(filename):
    """
    Serve generated images
    """
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == '__main__':
    print("=" * 60)
    print("AI Prompt to Image Generator Server")
    print("=" * 60)
    print("\nIMPORTANT: Make sure to set your OpenAI API key:")
    print("  export OPENAI_API_KEY='your-api-key-here'")
    
    # Use PORT environment variable for deployment, default to 5001 for local
    port = int(os.environ.get('PORT', 5001))
    print(f"\nServer starting on http://localhost:{port}")
    print(f"Open your browser and navigate to http://localhost:{port}")
    print("=" * 60)
    
    # For production (Render, Railway, etc.), set host to 0.0.0.0
    app.run(debug=True, host='0.0.0.0', port=port)
