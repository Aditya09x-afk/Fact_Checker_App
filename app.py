import streamlit as st
import tempfile
import os
import json
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize clients - try secrets first (for deployment), fall back to env vars (for local)
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    tavily_api_key = st.secrets["TAVILY_API_KEY"]
except:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

openai_client = OpenAI(api_key=openai_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)

def extract_claims(text):
    """Extract verifiable claims from text using OpenAI"""
    
    prompt = f"""Analyze this document and extract ONLY specific, verifiable factual claims.
    Focus on:
    - Statistics and percentages
    - Dates and timelines
    - Financial figures (prices, revenues, market caps, GDP)
    - Technical specifications
    - Quantifiable statements
    
    Return ONLY a JSON array of claims, nothing else. No markdown, no explanations.
    Format: [{{"claim": "specific claim here"}}, ...]
    
    Document:
    {text[:8000]}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise claim extractor. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Parse JSON response
        claims_json = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if claims_json.startswith("```"):
            claims_json = claims_json.split("```")[1]
            if claims_json.startswith("json"):
                claims_json = claims_json[4:]
        claims_json = claims_json.strip()
        
        claims_data = json.loads(claims_json)
        return [c['claim'] for c in claims_data]
    except Exception as e:
        st.error(f"Error extracting claims: {str(e)}")
        return []

def verify_claim(claim):
    """Verify a single claim using web search"""
    
    try:
        # Search the web
        search_results = tavily_client.search(
            query=claim,
            max_results=3
        )
        
        # Use OpenAI to analyze search results
        context = "\n\n".join([
            f"Source: {r['url']}\n{r['content']}" 
            for r in search_results.get('results', [])
        ])
        
        verification_prompt = f"""Given this claim and web search results, determine if the claim is:
        - "Verified" (accurate based on current data)
        - "Inaccurate" (outdated or slightly wrong)
        - "False" (contradicts evidence or no support found)
        
        Claim: {claim}
        
        Search Results:
        {context}
        
        Return ONLY a JSON object, no markdown, no explanations:
        {{
            "status": "Verified/Inaccurate/False",
            "explanation": "brief explanation with specific facts",
            "sources": ["url1", "url2"]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fact checker. Return only valid JSON."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0.3
        )
        
        result_json = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result_json.startswith("```"):
            result_json = result_json.split("```")[1]
            if result_json.startswith("json"):
                result_json = result_json[4:]
        result_json = result_json.strip()
        
        result = json.loads(result_json)
        result['claim'] = claim
        
        return result
    except Exception as e:
        return {
            'claim': claim,
            'status': 'Error',
            'explanation': f'Could not verify: {str(e)}',
            'sources': []
        }

# Streamlit UI
st.set_page_config(page_title="AI Fact Checker", page_icon="📄")

st.title("📄 AI Fact Checking Web App")
st.write("Upload a PDF to extract and analyze its text.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name
    
    # Load and extract text
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        text = " ".join([page.page_content for page in pages])
        
        st.success("PDF text extracted successfully!")
        st.subheader("🔍 Text Preview (first 500 characters)")
        st.write(text[:500])
        
        # Extract claims
        with st.spinner("🔍 Extracting claims from document..."):
            claims = extract_claims(text)
        
        if claims:
            st.subheader("📋 Extracted Claims")
            st.write(f"Found {len(claims)} claims to verify")
            
            # Verify each claim
            results = []
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            for i, claim in enumerate(claims):
                status_placeholder.write(f"Verifying claim {i+1}/{len(claims)}...")
                verification = verify_claim(claim)
                results.append(verification)
                progress_bar.progress((i + 1) / len(claims))
            
            status_placeholder.empty()
            
            # Display results
            st.subheader("✅ Verification Results")
            
            # Summary statistics
            verified_count = sum(1 for r in results if r['status'] == 'Verified')
            inaccurate_count = sum(1 for r in results if r['status'] == 'Inaccurate')
            false_count = sum(1 for r in results if r['status'] == 'False')
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Verified", verified_count)
            col2.metric("⚠️ Inaccurate", inaccurate_count)
            col3.metric("❌ False", false_count)
            
            st.markdown("---")
            
            # Display each result
            status_emoji = {
                "Verified": "✅",
                "Inaccurate": "⚠️",
                "False": "❌",
                "Error": "🔴"
            }
            
            for result in results:
                emoji = status_emoji.get(result['status'], "❓")
                claim_preview = result['claim'][:100] + "..." if len(result['claim']) > 100 else result['claim']
                
                with st.expander(f"{emoji} {claim_preview}"):
                    st.markdown(f"**Status:** {result['status']}")
                    st.markdown(f"**Claim:** {result['claim']}")
                    st.markdown(f"**Finding:** {result['explanation']}")
                    if result.get('sources'):
                        st.markdown("**Sources:**")
                        for source in result['sources']:
                            st.markdown(f"- {source}")
        else:
            st.warning("No verifiable claims found in the document.")
            
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
else:
    st.info("👆 Upload a PDF file to get started")
