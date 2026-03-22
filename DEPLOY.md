# Vercel Deployment Guide

## Bundle size: ~45 MB (well within Vercel's 500 MB limit) ✅

---

## Step 1 — Add Google Vision API Key (for image/scanned PDF OCR)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable **Cloud Vision API**
3. Go to **APIs & Services → Credentials → Create API Key**
4. Copy your key

In Vercel dashboard → your project → **Settings → Environment Variables**:
```
GOOGLE_VISION_API_KEY = your_api_key_here
SECRET_KEY            = any_random_string
```

> **Free tier:** 1000 image requests/month — plenty for a portfolio project.
> Digital PDFs and DOCX files work without the API key.

---

## Step 2 — Deploy

### Option A: GitHub (recommended)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/sahravi63/pdf-dataExtraction
git push origin main
```
Then go to [vercel.com](https://vercel.com) → **New Project** → Import from GitHub → Deploy ✅

### Option B: Vercel CLI
```bash
npm i -g vercel
vercel
```

---

## What was changed to make Vercel work

| Before | After | Why |
|---|---|---|
| `easyocr` (~7 GB) | Google Vision API | Vercel 500 MB limit |
| `pdf2image` + poppler | `pypdf` image extraction | No system deps on Vercel |
| `spacy` (~600 MB) | Regex-based NER | Too large for Lambda |
| `numpy` | Removed | Only needed by EasyOCR |
| Local `uploads/` folder | `tempfile.gettempdir()` | Vercel filesystem is read-only |

