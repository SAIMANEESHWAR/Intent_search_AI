# 🎬 Semantic Video Search - React Frontend

Modern React + Vite frontend for the Semantic Video Search application.

## 🚀 Quick Start

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

The frontend will run on `http://localhost:5500`

### Build for Production
```bash
npm run build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── VideoLoader.jsx  # Video loading component
│   │   ├── BasicSearch.jsx  # Basic search component
│   │   ├── RAGSearch.jsx    # RAG-enhanced search
│   │   └── ResultCard.jsx   # Result display card
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.jsx             # Main app component
│   ├── App.css             # Global styles
│   └── main.jsx            # React entry point
├── index.html              # HTML template
├── package.json            # Dependencies
└── vite.config.js         # Vite configuration
```

## 🔌 Backend Connection

The frontend connects to the FastAPI backend running on `http://localhost:8000`.

Make sure your backend is running:
```bash
# In the main project directory
uvicorn app:app --reload
```

## ✨ Features

- ✅ Modern React with Hooks
- ✅ Vite for fast development
- ✅ Responsive design
- ✅ Real-time status updates
- ✅ AI-powered explanations
- ✅ Video previews
- ✅ Clickable suggestions
- ✅ Error handling
- ✅ Loading states

## 🛠️ Technologies

- **React 18** - UI library
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS3** - Styling

## 📝 API Endpoints Used

- `POST /process-video` - Process YouTube video
- `GET /process-status` - Get processing status
- `POST /intent-search` - Basic semantic search
- `POST /rag-search` - RAG-enhanced search

## 🎨 Features

1. **Video Loading**
   - Paste YouTube URL
   - Real-time status updates
   - Progress indicators

2. **Basic Search**
   - Semantic search
   - Temporal intent (before/after/during)
   - Video clip results

3. **RAG Search**
   - AI-generated explanations
   - Intelligent suggestions
   - Result summaries
   - Enhanced user experience

## 🚀 Running the Application

### Terminal 1: Backend
```bash
cd D:\desktop-top\Intent_search_Cine_Ai
uvicorn app:app --reload
```

### Terminal 2: Frontend
```bash
cd D:\desktop-top\Intent_search_Cine_Ai\frontend
npm run dev
```

### Open Browser
Navigate to: `http://localhost:5500`

## 📦 Build

```bash
npm run build
```

Output will be in `dist/` directory.

## 🔧 Configuration

Edit `vite.config.js` to change:
- Port number
- API proxy settings
- Build options

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running on port 8000
- Check CORS settings in `app.py`

### "Module not found"
- Run `npm install` again
- Delete `node_modules` and reinstall

### Port already in use
- Change port in `vite.config.js`
- Or kill process using port 5500

