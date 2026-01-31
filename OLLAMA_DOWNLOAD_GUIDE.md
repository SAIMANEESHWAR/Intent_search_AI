# 📥 Ollama Download & Installation Guide

## Where to Download Ollama

### Official Download Links

**Windows:**
- **URL:** https://ollama.ai/download
- **Direct Download:** https://ollama.ai/download/windows
- **File:** `OllamaSetup.exe` (or similar)

**Mac:**
- **URL:** https://ollama.ai/download
- **Direct Download:** https://ollama.ai/download/mac
- **File:** `Ollama.dmg`

**Linux:**
- **URL:** https://ollama.ai/download
- **Install via command:** `curl -fsSL https://ollama.ai/install.sh | sh`

---

## Installation Location

### Important: Ollama is a System-Wide Application

**Ollama does NOT need to be in your project folder!**

- ✅ **Install Ollama anywhere** - It's a system application
- ✅ **Default location is fine** - Usually `C:\Users\YourName\AppData\Local\Programs\Ollama` (Windows)
- ✅ **Your project stays separate** - Ollama runs independently

### How It Works

```
Your Project Folder (D:\desktop-top\Intent_search_Cine_Ai\)
    ├── app.py
    ├── rag_generator.py
    ├── .env (configures connection to Ollama)
    └── ... (your project files)

Ollama (System Installation - separate location)
    ├── Installed in: C:\Users\YourName\AppData\Local\Programs\Ollama (Windows)
    ├── Runs as: Background service
    ├── Listens on: http://localhost:11434
    └── Models stored in: C:\Users\YourName\.ollama\models (Windows)
```

**Your project connects to Ollama via HTTP** - They don't need to be in the same folder!

---

## Step-by-Step Installation

### Step 1: Download Ollama

1. Go to: **https://ollama.ai/download**
2. Click download for your operating system
3. Save the installer file (can save anywhere, like Downloads folder)

### Step 2: Install Ollama

**Windows:**
1. Double-click the downloaded installer
2. Follow installation wizard
3. Ollama will install to: `C:\Users\YourName\AppData\Local\Programs\Ollama`
4. Ollama will start automatically as a background service

**Mac:**
1. Open the `.dmg` file
2. Drag Ollama to Applications folder
3. Open Applications → Ollama
4. Ollama will start automatically

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 3: Verify Installation

Open a **new terminal/command prompt** (anywhere, not in your project):

```bash
ollama --version
```

You should see version information.

### Step 4: Download Model (Still in Any Terminal)

```bash
ollama pull llama3.2:1b
```

**Model Location:**
- Windows: `C:\Users\YourName\.ollama\models\`
- Mac: `~/.ollama/models/`
- Linux: `~/.ollama/models/`

**You don't need to know this location** - Ollama manages it automatically!

### Step 5: Configure Your Project

**Go to your project folder:**
```
D:\desktop-top\Intent_search_Cine_Ai\
```

**Create `.env` file here** (in your project root):

**Windows PowerShell:**
```powershell
cd D:\desktop-top\Intent_search_Cine_Ai
echo "OLLAMA_URL=http://localhost:11434" > .env
echo "OLLAMA_MODEL=llama3.2:1b" >> .env
```

**Windows CMD:**
```cmd
cd D:\desktop-top\Intent_search_Cine_Ai
echo OLLAMA_URL=http://localhost:11434 > .env
echo OLLAMA_MODEL=llama3.2:1b >> .env
```

**Mac/Linux:**
```bash
cd /path/to/Intent_search_Cine_Ai
cat > .env << EOF
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
EOF
```

---

## Directory Structure

### Your Project (Stays Where It Is)
```
D:\desktop-top\Intent_search_Cine_Ai\
├── app.py
├── rag_generator.py
├── .env                    ← Create this here
├── requirements.txt
├── vector_store.py
├── rag_search.py
├── semantic_search.py
└── ... (all your project files)
```

### Ollama (System Installation - Separate)
```
C:\Users\YourName\AppData\Local\Programs\Ollama\    (Windows)
    └── ollama.exe

C:\Users\YourName\.ollama\models\                    (Windows - Models)
    └── llama3.2:1b\                                 (1.6 GB model)
```

**They are separate!** Your project connects to Ollama via `http://localhost:11434`

---

## How Connection Works

```
┌─────────────────────────────────────┐
│  Your Project                       │
│  D:\desktop-top\Intent_search_Cine_Ai\ │
│                                     │
│  rag_generator.py                   │
│  └─> Calls: http://localhost:11434  │
└──────────────┬──────────────────────┘
               │ HTTP Request
               │
               ▼
┌─────────────────────────────────────┐
│  Ollama Service                     │
│  Running on: localhost:11434        │
│  Location: System-wide              │
│                                     │
│  └─> Processes request              │
│  └─> Uses model: llama3.2:1b        │
│  └─> Returns response              │
└─────────────────────────────────────┘
```

---

## Important Points

### ✅ What You Need to Know

1. **Download Ollama** from https://ollama.ai/download
2. **Install it** (default location is fine)
3. **Download model** with `ollama pull llama3.2:1b`
4. **Create `.env` in your project** (not in Ollama folder)
5. **Start your project** - It will connect to Ollama automatically

### ❌ What You DON'T Need to Know

1. ❌ Exact Ollama installation path (not needed)
2. ❌ Model storage location (Ollama manages it)
3. ❌ How to configure Ollama (defaults work fine)
4. ❌ Moving files around (keep everything separate)

---

## Quick Setup Checklist

- [ ] Download Ollama from https://ollama.ai/download
- [ ] Install Ollama (use default location)
- [ ] Verify: `ollama --version` works
- [ ] Download model: `ollama pull llama3.2:1b`
- [ ] Verify: `ollama list` shows the model
- [ ] Go to your project: `D:\desktop-top\Intent_search_Cine_Ai\`
- [ ] Create `.env` file in project root
- [ ] Add: `OLLAMA_URL=http://localhost:11434`
- [ ] Add: `OLLAMA_MODEL=llama3.2:1b`
- [ ] Start your server: `uvicorn app:app --reload`
- [ ] Test RAG search in UI

---

## Troubleshooting

### "Ollama not found" after installation

**Windows:**
- Restart your terminal/command prompt
- Or add Ollama to PATH manually (usually not needed)

**Mac/Linux:**
- Restart terminal
- Or run: `source ~/.bashrc` (or `~/.zshrc`)

### "Cannot connect to Ollama"

**Check if Ollama is running:**
```bash
ollama list
```

**If not running:**
- Windows: Search "Ollama" in Start menu and open it
- Mac: Open Applications → Ollama
- Linux: Run `ollama serve`

### Model location issues

**You don't need to know model location!** Ollama manages it automatically.

If you want to check:
```bash
ollama list  # Shows downloaded models
```

---

## Summary

1. **Download Ollama:** https://ollama.ai/download (anywhere is fine)
2. **Install Ollama:** Use default location (system-wide)
3. **Download Model:** `ollama pull llama3.2:1b` (any terminal)
4. **Configure Project:** Create `.env` in your project folder
5. **Connect:** Your project connects to Ollama via `localhost:11434`

**Key Point:** Ollama and your project are separate. They communicate via HTTP on `localhost:11434`. No need to put them in the same folder!

---

## Visual Guide

```
┌─────────────────────────────────────────┐
│  STEP 1: Download Ollama                │
│  From: https://ollama.ai/download        │
│  Save to: Downloads folder (anywhere)    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  STEP 2: Install Ollama                 │
│  Location: System folder (automatic)     │
│  Windows: C:\Users\...\Programs\Ollama   │
│  Starts automatically as service         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  STEP 3: Download Model                 │
│  Command: ollama pull llama3.2:1b       │
│  Location: ~/.ollama/models (automatic) │
│  Size: 1.6 GB                            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  STEP 4: Configure Your Project         │
│  Location: D:\desktop-top\Intent_search_Cine_Ai\ │
│  Create: .env file                      │
│  Content: OLLAMA_URL=http://localhost:11434 │
│           OLLAMA_MODEL=llama3.2:1b      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  STEP 5: Start Your Project              │
│  Command: uvicorn app:app --reload      │
│  Your project connects to Ollama        │
│  via: http://localhost:11434            │
└─────────────────────────────────────────┘
```

---

## Final Answer

**Where to download:** https://ollama.ai/download

**Where to install:** Default location (system folder) - you don't need to choose

**Where to configure:** Your project folder (`D:\desktop-top\Intent_search_Cine_Ai\`) - create `.env` here

**How they connect:** Via HTTP on `localhost:11434` - no need to be in same folder!

That's it! Simple and clean separation. 🚀

