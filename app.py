import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
from openai import OpenAI
import json
import time
from openai.error import RateLimitError

st.set_page_config(page_title="AI Web Scraper", layout="wide")
st.title("AI Web Scraper Agent")
st.write("Enter a website URL and describe what data you want. The AI will extract it for you.")

# User inputs
url = st.text_input("Website URL")
prompt = st.text_area("Describe what data you want extracted")

# Load OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Function to fetch HTML
def extract_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        return response.text
    except Exception as e:
        st.error(f"Failed to fetch website: {e}")
        return None

# AI extraction with retries
def ai_extract_data(html, prompt):
    instructions = f"""
You are an AI agent. User wants the following information from the webpage:

User request: {prompt}

Here is the webpage HTML:

{html}

Extract the required data.
Return the output ONLY in JSON format (list of objects).
"""
    for attempt in range(3):  # retry up to 3 times
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",  # cheaper and faster
                messages=[{"role": "user", "content": instructions}]
            )
            return json.loads(resp.choices[0].message["content"])
        except RateLimitError:
            if attempt < 2:
                st.warning(f"Rate limit hit. Retrying in 5 seconds... (attempt {attempt+1})")
                time.sleep(5)
            else:
                st.error("API rate limit reached. Please try again later.")
                return None
        except json.JSONDecodeError:
            st.error("Failed to parse AI output. Try a simpler prompt.")
            return None

# Main scraping workflow
if st.button("Scrape Website"):
    if not url or not prompt:
        st.error("Please enter URL and prompt")
    else:
        html = extract_html(url)
        if html:
            st.write("AI extracting data...")
            results = ai_extract_data(html, prompt)
            if results:
                df = pd.DataFrame(results)
                st.write(df)
                st.download_button(
                    "Download Excel",
                    df.to_excel("output.xlsx", index=False),
                    file_name="scraped_data.xlsx"
                )
            else:
                st.error("AI could not extract structured data. Try a clearer prompt.")
