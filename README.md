# AI Prompt to Image Generator

A web application that uses AI to generate detailed image prompts and then creates images based on those prompts.

## Features

- 🤖 **Editable System Instructions**: Customize how the LLM generates prompts
- ✨ **LLM-Powered Prompt Generation**: Automatically generate detailed, creative image prompts
- ✏️ **Editable Prompts**: Fine-tune the generated prompts before creating images
- 🎨 **AI Image Generation**: Create images using DALL-E based on your prompts
- 💾 **Download Images**: Save generated images to your device
- 🎯 **Beautiful UI**: Modern, responsive interface with smooth animations

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenAI API key:**
   
   **macOS/Linux:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
   
   **Or add it to your `~/.zshrc` or `~/.bashrc` for persistence:**
   ```bash
   echo "export OPENAI_API_KEY='your-api-key-here'" >> ~/.zshrc
   source ~/.zshrc
   ```

## Usage

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Generate prompts and images:**
   - Edit the system instruction (optional) to customize how prompts are generated
   - Click "Generate Prompt using LLM" to create an image prompt
   - Edit the generated prompt if needed
   - Click "Generate Image" to create the image
   - Download the image using the "Download Image" button

## How It Works

1. **System Instruction**: Guides the LLM on how to create prompts
2. **Prompt Generation**: Uses GPT-4 to generate detailed image descriptions
3. **Image Generation**: Uses DALL-E to create images from the prompts
4. **Local Storage**: Generated images are saved in the `generated_images/` folder

## File Structure

```
Project-1/
├── server.py              # Flask backend server
├── index.html             # Frontend interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── generated_images/     # Folder for saved images (created automatically)
```

## API Endpoints

- `GET /` - Serves the main HTML page
- `POST /generate-prompt` - Generates a prompt using LLM
- `POST /generate-image` - Generates an image using DALL-E
- `GET /images/<filename>` - Serves generated images

## Cost Considerations

- GPT-4 API calls: ~$0.03-0.06 per request
- DALL-E image generation: ~$0.02 per 1024x1024 image
- You can switch to GPT-3.5-turbo in `server.py` for cheaper prompt generation

## Customization

### Change the AI Model

In `server.py`, you can modify:
- LLM model: Change `model="gpt-4"` to `model="gpt-3.5-turbo"`
- Image size: Change `size="1024x1024"` to `"512x512"` or `"256x256"`

### Modify the Default System Instruction

Edit the default text in `index.html` in the system instruction textarea.

## Troubleshooting

**"OpenAI API key not configured"**
- Make sure you've set the `OPENAI_API_KEY` environment variable
- Restart the server after setting the environment variable

**"Rate limit exceeded"**
- You've hit OpenAI's rate limit. Wait a few minutes and try again
- Consider upgrading your OpenAI API plan

**Image not displaying**
- Check the browser console for errors
- Ensure the `generated_images/` folder has write permissions

## License

MIT License - Feel free to use and modify!

---

## 🚀 Deployment for External Users

Want to make your app accessible to others? See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions.

### Quick Deploy Options:

1. **🚀 ngrok (Instant - For Testing/Demo)**
   ```bash
   ./deploy-ngrok.sh
   ```
   Get a public URL in seconds! Perfect for sharing with friends or testing.

2. **🌐 Render.com (Recommended for Production)**
   - Free tier available
   - Auto-deploys from GitHub
   - Permanent URL with SSL
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step guide

3. **🚂 Railway.app (Alternative)**
   - Easy GitHub integration
   - Generous free tier
   - Fast deployment

4. **💻 Custom VPS**
   - Full control
   - Custom domain
   - Scalable

**Run the deployment guide:**
```bash
./DEPLOY_GUIDE.sh
```

**Required for deployment:**
- `OPENAI_API_KEY` environment variable
- `GOOGLE_GENERATIVE_AI_API_KEY` environment variable

---

## 📁 Project Structure

```
Project-1/
├── server.py              # Flask backend with RAG + LLM
├── index.html             # Frontend interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── DEPLOYMENT.md         # Detailed deployment guide
├── deploy-ngrok.sh       # Quick ngrok deployment
├── DEPLOY_GUIDE.sh       # Interactive deployment guide
├── render.yaml           # Render.com configuration
├── Procfile              # For Heroku/Railway
├── medical_vectorstore/  # RAG medical knowledge base
└── generated_images/     # Saved generated images
```
