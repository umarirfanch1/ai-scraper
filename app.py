import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
from openai import OpenAI
import json

st.title("AI Web Scraper Agent")

st.write("Enter a website URL and describe what data you want. The AI will extract it for you.")

# User inputs
url = st.text_input("Website URL")
prompt = st.text_area("Describe what data you want extracted")

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_html(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.text

def ai_extract_data(html, prompt):
    instructions = f"""
You are an AI agent. User wants the following information from the webpage:

User request: {prompt}

Here is the webpage HTML:

{html}

Extract the required data.
Return the output ONLY in JSON format (list of objects).
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": instructions}]
    )

    try:
        return json.loads(resp.choices[0].message["content"])
    except:
        return None

if st.button("Scrape Website"):
    if not url or not prompt:
        st.error("Please enter URL and prompt")
    else:
        st.write("Scraping website...")

        html = extract_html(url)

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
