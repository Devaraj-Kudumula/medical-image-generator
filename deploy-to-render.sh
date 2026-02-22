#!/bin/bash

# Medical Image Generation App - Render.com Deployment Script
# This script prepares your app for deployment to Render.com

set -e

echo "=================================="
echo "Render.com Deployment Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if Git is initialized
echo -e "${BLUE}Step 1: Checking Git repository...${NC}"
if [ -d ".git" ]; then
    echo -e "${GREEN}✓ Git repository exists${NC}"
else
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    git add .
    git commit -m "Initial commit - Medical Image Generation App"
    echo -e "${GREEN}✓ Git repository initialized${NC}"
fi
echo ""

# Step 2: Create GitHub repository
echo -e "${BLUE}Step 2: Push to GitHub${NC}"
echo "You need to create a GitHub repository to deploy to Render.com"
echo ""
echo "Please follow these steps:"
echo "  1. Go to https://github.com/new"
echo "  2. Repository name: medical-image-generator"
echo "  3. Make it Public (required for free Render deployment)"
echo "  4. DO NOT initialize with README (we already have files)"
echo "  5. Click 'Create repository'"
echo ""
read -p "Press Enter once you've created the repository..."
echo ""

# Step 3: Get GitHub repository URL
echo -e "${YELLOW}Enter your GitHub repository URL:${NC}"
echo "Example: https://github.com/yourusername/medical-image-generator.git"
read -p "GitHub URL: " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo -e "${YELLOW}No URL provided. You can manually add it later:${NC}"
    echo "  git remote add origin YOUR_GITHUB_URL"
    echo "  git push -u origin main"
else
    echo -e "${BLUE}Adding remote and pushing to GitHub...${NC}"
    git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"
    git branch -M main
    git push -u origin main
    echo -e "${GREEN}✓ Code pushed to GitHub${NC}"
fi
echo ""

# Step 4: Render.com deployment instructions
echo -e "${BLUE}Step 3: Deploy to Render.com${NC}"
echo ""
echo "Now deploy to Render.com (100% FREE):"
echo ""
echo "  1. Go to https://render.com and sign up (Use GitHub login)"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect your GitHub repository: medical-image-generator"
echo "  4. Configure the service:"
echo "     - Name: medical-image-generator"
echo "     - Environment: Python 3"
echo "     - Build Command: pip install -r requirements.txt"
echo "     - Start Command: gunicorn server:app --bind 0.0.0.0:\$PORT"
echo "     - Instance Type: Free"
echo ""
echo "  5. Add Environment Variables (click 'Advanced'):"
echo "     Key: OPENAI_API_KEY"
echo "     Value: YOUR_OPENAI_API_KEY"
echo ""
echo "     Key: GOOGLE_GENERATIVE_AI_API_KEY"
echo "     Value: YOUR_GOOGLE_API_KEY"
echo ""
echo "  6. Click 'Create Web Service'"
echo ""
echo "  7. Wait 5-10 minutes for deployment (you'll get a URL like:"
echo "     https://medical-image-generator.onrender.com)"
echo ""
echo -e "${GREEN}=================================="
echo "Deployment setup complete!"
echo "==================================${NC}"
echo ""
echo "Your app will be live at: https://YOUR-APP-NAME.onrender.com"
echo ""
echo "Note: Free tier sleeps after 15 min of inactivity."
echo "First request after sleep takes ~30 seconds to wake up."
echo ""
