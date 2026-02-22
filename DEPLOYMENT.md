# Deployment Guide - AI Medical Image Generator

This guide covers multiple deployment options for making your website accessible to external users.

---

## 🚀 Quick Deploy Options

### Option 1: ngrok (Fastest - For Testing/Demo)

**Best for:** Quick sharing, demos, testing with a few users

**Steps:**

1. **Install ngrok:**
   ```bash
   brew install ngrok
   # Or download from https://ngrok.com/download
   ```

2. **Start your Flask server:**
   ```bash
   cd Project-1
   export OPENAI_API_KEY='your-key'
   export GOOGLE_GENERATIVE_AI_API_KEY='your-key'
   python server.py
   ```

3. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 5001
   ```

4. **Share the URL:**
   - ngrok will provide a public URL (e.g., `https://abc123.ngrok.io`)
   - Share this URL with users
   - **Note:** Free tier has session limits and URL changes on restart

**Pros:** Instant, no configuration
**Cons:** Temporary URL, not for production, limited bandwidth

---

### Option 2: Render.com (Recommended for Production)

**Best for:** Production apps, permanent URL, free tier available

**Steps:**

1. **Create `render.yaml`** (I'll create this for you)

2. **Push code to GitHub:**
   ```bash
   cd Project-1
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create medical-image-generator --public --source=. --push
   ```

3. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Sign up/Log in
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render auto-detects settings
   - Add environment variables:
     - `OPENAI_API_KEY`
     - `GOOGLE_GENERATIVE_AI_API_KEY`
   - Click "Create Web Service"

4. **Your app will be live at:** `https://your-app-name.onrender.com`

**Pros:** Free tier, auto-deploys, permanent URL, SSL included
**Cons:** Spins down after inactivity (free tier)

---

### Option 3: Railway.app (Easy Alternative)

**Best for:** Similar to Render, generous free tier

**Steps:**

1. **Push to GitHub** (same as above)

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo
   - Add environment variables in Settings
   - Railway auto-builds and deploys

**Pros:** Easy setup, generous free tier, fast deployment
**Cons:** Less configuration options than others

---

### Option 4: PythonAnywhere (Python-Specific Hosting)

**Best for:** Python apps, beginner-friendly

**Steps:**

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Upload your files:**
   - Use their web interface or Git

3. **Configure WSGI:**
   - Create a WSGI configuration file (see template below)
   - Set environment variables in web app settings

4. **Your app:** `https://yourusername.pythonanywhere.com`

**Pros:** Python-focused, easy to use
**Cons:** Free tier has limitations, slower than others

---

### Option 5: DigitalOcean/Linode VPS (Most Control)

**Best for:** Full control, scaling, custom domains

**Steps:**

1. **Create a Droplet/VPS:**
   - Choose Ubuntu 22.04
   - At least 2GB RAM recommended

2. **SSH into server and setup:**
   ```bash
   ssh root@your-server-ip
   apt update && apt upgrade -y
   apt install python3-pip python3-venv nginx -y
   ```

3. **Deploy your app:**
   ```bash
   git clone your-repo
   cd Project-1
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Use Gunicorn + Nginx:**
   - Install: `pip install gunicorn`
   - Create systemd service
   - Configure Nginx as reverse proxy

**Pros:** Full control, custom domain, scalable
**Cons:** More complex, requires server management

---

## 🔧 Pre-Deployment Checklist

Before deploying, update these configurations:

### 1. Update CORS Settings in `server.py`

```python
# Replace
CORS(app)

# With
CORS(app, resources={
    r"/*": {
        "origins": ["https://yourdomain.com", "http://localhost:5001"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 2. Update URLs in `index.html`

Replace hardcoded `localhost:5001` with environment variable or dynamic URL:

```javascript
const API_URL = window.location.origin;
// Then use: `${API_URL}/generate-prompt`
```

### 3. Add Production Server

Install production WSGI server:
```bash
pip install gunicorn
```

Run with:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 server:app
```

### 4. Environment Variables

Never commit API keys! Use environment variables:
- Render/Railway: Set in dashboard
- VPS: Use `.env` file with `python-dotenv`

---

## 📊 Deployment Comparison

| Option | Cost | Ease | Speed | Control | Best For |
|--------|------|------|-------|---------|----------|
| ngrok | Free | ⭐⭐⭐⭐⭐ | ⚡ Instant | ⭐ Low | Testing |
| Render | Free/Paid | ⭐⭐⭐⭐ | ⚡ Fast | ⭐⭐⭐ | Production |
| Railway | Free/Paid | ⭐⭐⭐⭐⭐ | ⚡ Fast | ⭐⭐⭐ | Production |
| PythonAnywhere | Free/Paid | ⭐⭐⭐ | ⚡ Medium | ⭐⭐ | Python Apps |
| VPS | $5-50/mo | ⭐⭐ | ⚡ Fast | ⭐⭐⭐⭐⭐ | Scaling |

---

## 🎯 Recommended Path

**For Quick Demo:** Use **ngrok** (5 minutes)
**For Production:** Use **Render.com** or **Railway.app** (30 minutes)
**For Custom Domain:** Add domain to Render/Railway or use VPS

---

## 🔐 Security Notes

1. **Never commit API keys** to Git
2. Use **HTTPS** in production (auto with Render/Railway)
3. Add **rate limiting** for API endpoints
4. Set up **CORS** properly
5. Monitor **API usage** and costs

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- ngrok Docs: https://ngrok.com/docs

---

Let me know which deployment method you'd like to use, and I can provide more detailed instructions!
