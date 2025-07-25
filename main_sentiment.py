
import os
from datetime import datetime
import dotenv
from flask import Flask, render_template, request, jsonify
import concurrent.futures
import time

from src.citation_utils import embed_citations
from src.lllm_utils import get_openai_response, query_perplexity
from openai import OpenAI
import markdown

dotenv.load_dotenv()

app = Flask(__name__)

# --- Model Configuration ---
PERPLEXITY_MODEL = "sonar"
OPENAI_MODEL = "gpt-4o"
# -------------------------

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_asset_queries(asset_name):
    """
    Generates a list of Perplexity AI queries for a given asset.
    Each query is a dictionary with the query string and the recency filter.
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    return [
        # === Same-Day, High-Frequency Queries ===
        {
            "query": f"What is the absolute latest, breaking news and market-moving information for {asset_name} released TODAY, {today_str}? Focus on information from the last 24 hours from top-tier financial news outlets, press releases, and regulatory filings.",
            "filter": "day"
        },
        {
            "query": f"Analyze the intraday trading activity and technical indicators for {asset_name} for today, {today_str}. Include real-time price movements, trading volume patterns, key support/resistance levels, and any significant market maker activity.",
            "filter": "day"
        },
        {
            "query": f"What is the real-time social media and forum sentiment for {asset_name} over the past 24 hours? Scan X (formerly Twitter), Reddit (e.g., r/wallstreetbets, r/stocks), and other financial forums for any sudden shifts in discussion volume or sentiment.",
            "filter": "day"
        },
        # === Broader Context Queries ===
        {
            "query": f"Provide a detailed report on the recent financial performance of {asset_name}. Include information on quarterly earnings, revenue growth, profit margins, and any recent SEC filings. Focus on the last 12 months.",
            "filter": "month"  # Use month to capture latest quarterly reports
        },
        {
            "query": f"What are the most significant news and developments related to {asset_name} in the last month? Include product announcements, partnerships, management changes, and any regulatory news.",
            "filter": "month"
        },
        {
            "query": f"Summarize recent analyst ratings and price targets for {asset_name} from the past three months. What is the consensus sentiment among financial analysts from top-tier firms?",
            "filter": "month"
        },
        {
            "query": f"What are the major market trends and competitive landscape for the sector {asset_name} operates in? How is {asset_name} positioned against its main competitors?",
            "filter": "month"
        },
        {
            "query": f"What are the biggest risks and opportunities facing {asset_name} in the next 6-12 months? Consider macroeconomic factors, company-specific issues, and market competition.",
            "filter": "month"
        }
    ]

def get_openai_prompt(asset_name, context):
    """
    Generates the prompt for the OpenAI API call.
    """
    return f"""
You are a world-class, highly experienced financial analyst, known for your sharp, data-driven insights and clear, decisive recommendations. You are working for a top-tier investment firm and your analysis is highly valued.

Based on the following comprehensive research report for **{asset_name}**, provide a detailed investment analysis. The report is compiled from multiple up-to-date sources and covers various aspects of the asset.

**Your Task:**

1.  **Synthesize the information:** Read through all the provided sections carefully. Identify the most critical pieces of information that would influence an investment decision.
2.  **Provide a final, decisive recommendation:** State clearly whether your recommendation is **BUY**, **SELL**, or **HOLD**. Do not be ambiguous.
3.  **Justify your recommendation:** Provide a detailed, evidence-based rationale for your recommendation. Your justification should be at least 500 words, using the data and facts from the provided context.
4.  **Structure your analysis for an executive audience:** Organize your response in markdown format with the following sections:
    *   **Recommendation:** (e.g., **BUY**)
    *   **Confidence Score:** (e.g., High / Medium / Low)
    *   **Time Horizon:** (e.g., Short-term (0-3 months) / Medium-term (3-12 months) / Long-term (1+ years))
    *   **Executive Summary:** A brief, impactful overview of the key findings and your recommendation.
    *   **Positive Catalysts (The Bull Case):** Key strengths, opportunities, and potential positive triggers. Use bullet points.
    *   **Negative Risk Factors (The Bear Case):** Key weaknesses, risks, and potential negative triggers. Use bullet points.
    *   **Detailed Analysis:** A comprehensive analysis integrating all the provided information. Refer to specific data points and news items from the context. This should be the longest part of your report.
    *   **Conclusion:** A concluding thought on the asset's future outlook and reiteration of your core thesis.

**CRITICAL INSTRUCTIONS:**
*   Your analysis must be based **exclusively** on the information provided below. Do not use any external knowledge or make up information.
*   Preserve and use the citations `[^...](...)` provided in the text. This is extremely important for source verification.
*   Be objective and balanced, but your final call must be decisive. Acknowledge both bull and bear cases clearly.
*   The final output must be in professional, well-formatted markdown.

---
**Collected Intelligence Report for {asset_name} (Date: {datetime.now().strftime('%Y-%m-%d')})**

{context}
---
"""

def run_perplexity_query(query_data):
    """Wrapper function to run a single perplexity query and handle exceptions."""
    query = query_data["query"]
    recency_filter = query_data["filter"]
    try:
        response = query_perplexity(query, model=PERPLEXITY_MODEL, search_recency_filter=recency_filter)
        if response and 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content']
            citations = response.get('citations', [])
            context_with_citations = embed_citations(content, citations)
            return f"### Research Angle: {query}\n\n{context_with_citations}\n\n------------------------------------\n\n"
        else:
            error_message = f"Query '{query[:50]}...' returned no valid response."
            print(f"  - {error_message}")
            return f"### Research Angle: {query}\n\n{error_message}\n\n------------------------------------\n\n"
    except Exception as e:
        error_message = f"Error running query '{query[:50]}...': {e}"
        print(f"  - {error_message}")
        return f"### Research Angle: {query}\n\n{error_message}\n\n------------------------------------\n\n"

@app.route('/')
def index():
    return render_template('sentiment_index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    assets_text = data.get('assets')
    if not assets_text:
        return jsonify({"error": "Please provide some asset names."}), 400

    assets = [asset.strip().upper() for asset in assets_text.split(',') if asset.strip()]
    
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    analysis_results = {}
    for asset in assets:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{asset.replace('/', '_').replace('-', '_')}_{timestamp}.md"
        log_filepath = os.path.join(tmp_dir, log_filename)

        print(f"Analyzing {asset}...")
        queries = get_asset_queries(asset)

        log_content = f"# Analysis Log for {asset}\n"
        log_content += f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_content += f"**Perplexity Model:** `{PERPLEXITY_MODEL}`\n"
        log_content += f"**OpenAI Model:** `{OPENAI_MODEL}`\n\n"
        log_content += "## Perplexity Queries\n"
        for i, q_data in enumerate(queries):
            log_content += f"{i+1}. (Filter: `{q_data['filter']}`) `{q_data['query']}`\n"
        log_content += "\n<hr>\n\n## Perplexity Raw Results\n"

        full_context = ""
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(queries)) as executor:
            future_to_query = {executor.submit(run_perplexity_query, q_data): q_data for q_data in queries}
            
            print(f"  - Running {len(queries)} queries in parallel for {asset}...")
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_query):
                query_data = future_to_query[future]
                query = query_data["query"]
                try:
                    result_context = future.result()
                    full_context += result_context
                    print(f"  - Finished query for {asset}: '{query[:40]}...'")
                except Exception as exc:
                    error_msg = f"  - Query for {asset} generated an exception: {exc}"
                    print(error_msg)
                    full_context += f"### Research Angle: {query}\n\nAn exception occurred: {exc}\n\n------------------------------------\n\n"

        log_content += full_context

        openai_prompt = get_openai_prompt(asset, full_context)
        
        print(f"  - Getting OpenAI analysis for {asset}...")
        try:
            analysis = get_openai_response(openai_client, openai_prompt, model=OPENAI_MODEL)
            analysis_html = markdown.markdown(analysis, extensions=['extra'])
            analysis_results[asset] = analysis_html
            log_content += "\n<hr>\n\n## OpenAI Final Analysis\n"
            log_content += analysis
        except Exception as e:
            error_msg = f"  - Error getting OpenAI analysis for {asset}: {e}"
            print(error_msg)
            analysis_results[asset] = f"<p>{error_msg}</p>"
            log_content += f"\n<hr>\n\n## OpenAI Analysis Error\n`{e}`\n"

        try:
            with open(log_filepath, "w", encoding="utf-8") as f:
                f.write(log_content)
            print(f"  - Log file created at {log_filepath}")
        except Exception as e:
            print(f"  - Could not write log file for {asset}: {e}")
        
        print(f"Finished analyzing {asset}.")

    return jsonify(analysis_results)


if __name__ == '__main__':
    app.run(debug=True, port=5001) 