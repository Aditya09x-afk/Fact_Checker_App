# Fact_Checker_App
AI-powered fact-checking web app that verifies claims in PDFs against live web data.
# AI Fact-Checking Web App

An automated fact-checking tool that verifies claims in PDF documents against live web data.

## Features
- Extracts verifiable claims from PDFs (statistics, dates, financial figures, technical specs)
- Searches the web to verify each claim
- Classifies claims as Verified, Inaccurate, or False
- Provides sources and explanations

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **Search**: Tavily API
- **PDF Processing**: LangChain + PyPDF

## Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/fact-checker-app.git
cd fact-checker-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

4. Run the app:
```bash
streamlit run app.py
```

## How It Works

1. **Upload PDF**: User uploads a document
2. **Extract Text**: PyPDF extracts text from the PDF
3. **Identify Claims**: GPT-4o-mini identifies specific, verifiable claims
4. **Web Search**: Tavily searches for current information on each claim
5. **Verify**: GPT-4o-mini compares claims against search results
6. **Report**: Display verification status with sources

## Deployment

Live app: [YOUR_DEPLOYED_URL_HERE]
```

### 3. **Record Demo Video** (30 seconds)
Use screen recording software:
- **Windows**: Win + G (Xbox Game Bar)
- **Mac**: Cmd + Shift + 5
- **Online**: Loom.com (free)

**What to show:**
1. Open the app (3 sec)
2. Upload a PDF (5 sec)
3. Show claims being extracted (7 sec)
4. Show verification results (10 sec)
5. Click on an expander to show details (5 sec)

Upload to YouTube/Google Drive and get the link.

---

## 📋 Final Submission Checklist:

Create a document with:
```
AI Fact-Checking Web App - Submission

1. Deployed App Link: 
   https://your-app-name.streamlit.app

2. GitHub Repository: 
   https://github.com/YOUR_USERNAME/fact-checker-app

3. Demo Video: 
   https://youtu.be/YOUR_VIDEO_ID
   (or Google Drive link)
