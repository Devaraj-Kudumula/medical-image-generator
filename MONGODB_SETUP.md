# MongoDB Vector Store Setup Guide

## Quick Start

### 1. Build the Vector Store

Run the build script to populate MongoDB with your medical documents:

```bash
python build_mongo_vectorstore.py
```

This will:
- Load your First Aid PDF
- Chunk it into optimal segments
- Create embeddings using OpenAI
- Store in MongoDB Atlas

### 2. Create Vector Search Index

**IMPORTANT:** You must create a vector search index in MongoDB Atlas UI:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Navigate to: **Database** → **Browse Collections** → **Search**
3. Click **Create Index**
4. Select database: `medical_rag`
5. Select collection: `medical_documents`
6. Use index name: `vector_index`
7. Switch to **JSON Editor** and paste:

```json
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
```

8. Click **Create Search Index**
9. Wait for index to build (usually 1-2 minutes)

### 3. Deploy to Render

Add MongoDB URI as environment variable in Render:

```
MONGODB_URI=mongodb+srv://db_user:db_user@cluster0.9a1tk8o.mongodb.net/
```

Then deploy:

```bash
git add .
git commit -m "Switch to MongoDB Atlas for vector storage"
git push
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for embeddings
- `MONGODB_URI` - MongoDB Atlas connection string (has default)
- `GOOGLE_GENERATIVE_AI_API_KEY` - For image generation

### MongoDB Details

- **Database**: `medical_rag`
- **Collection**: `medical_documents`
- **Index Name**: `vector_index`
- **Embedding Dimensions**: 1536 (text-embedding-3-small)

## Troubleshooting

### "Collection is empty"
Run `build_mongo_vectorstore.py` first to populate the database.

### "Index not found"
Create the vector search index in MongoDB Atlas UI (see step 2 above).

### "Connection failed"
Check your MongoDB URI and ensure IP whitelist includes your server's IP (or use 0.0.0.0/0 for testing).

## Testing Locally

```bash
# Set environment variable
export OPENAI_API_KEY='your-key-here'

# Build vectorstore
python build_mongo_vectorstore.py

# Run server
python server.py
```

Visit http://localhost:5001/health to verify MongoDB connection.

## Advantages over ChromaDB

- ✅ No large binary files to commit to git
- ✅ More reliable on free tier deployments
- ✅ Persistent across deployments
- ✅ Better performance for production
- ✅ Easier to update/maintain
