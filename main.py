import re
import os
import requests
from datetime import datetime
import json
import markdown
import dotenv
from src.citation_utils import embed_citations, extract_citations
from src.lllm_utils import get_openai_response, query_perplexity
from src.render import convert_md_to_html
import time

dotenv.load_dotenv()
from openai import OpenAI


def get_news_from_perplexity():

    start_time = time.time()
    immediate_stock_market_news = query_perplexity(f"Provide an exhaustive and detailed report on the stock market activity. Focused on today and ONLY today's date: {datetime.now().strftime('%Y-%m-%d')}\
                                            We want a sector by sector breakdown of the market activity and the most recent developments and changes in the market from the past 24 hours.\
                                            In each sector provide most recent changes for the whole sector as well as most important stocks in the sector. Focus only on the verified and factual information. Go overboard and overdrive with reading accurate and reliable sources.\
                                            it is important that our analysis covers areas such as at least tech, health, energy, financial, consumer discretionary, communication, industrials, materials, real estate. Report should be at least 2000 words long\
                                            !!! If you are reading from a chart, make sure to really pay attention to the chart and the data and provide the most accurate and up to date information from the chart.", search_recency_filter="day")
    
    immediate_stock_market_news_message = embed_citations(immediate_stock_market_news['choices'][0]['message']['content'], immediate_stock_market_news['citations'])
    print(f"Finished immediate stock market news query, took {round(time.time() - start_time, 2)} seconds")

    start_time = time.time()
    geopolitics_response = query_perplexity("Provide an exhaustive and detailed report on the geopolitical landscape and its\
                                        potential impact on the stock market. Focus on the most recent developments and their potential implications\
                                        for the market. Try to delve deep into the geopolitical landscape the tensions and growing areas of risk and opportunity. Report should be at least 2000 words long")

    geopolitics_message = embed_citations(geopolitics_response['choices'][0]['message']['content'], geopolitics_response['citations'])
    print(f"Finished geopolitics query, took {round(time.time() - start_time, 2)} seconds")
    start_time = time.time()
    stock_market_response = query_perplexity(f"Provide an exhaustive and detailed report on the stock market activity.\
                                            We want a sector by sector breakdown of the market activity and the most recent developments and changes in the market.\
                                            In each sector provide most recent changes for the whole sector as well as most important stocks in the sector.\
                                            Focus on factual and numerical data available from the market from today's date: {datetime.now().strftime('%Y-%m-%d')}\
                                            it is important that our analysis covers areas such as at least tech, health, energy, financial, consumer discretionary, communication, industrials, materials, real estate. Report should be at least 2000 words long")
                                            
    stock_market_message = embed_citations(stock_market_response['choices'][0]['message']['content'], stock_market_response['citations'])
    print(f"Finished stock market query, took {round(time.time() - start_time, 2)} seconds")
    start_time = time.time()
    market_news_response = query_perplexity(f"Provide an exhaustive and detailed report on the most recent global markets news.\
                                            We want a sector by sector breakdown of the market news and the most recent developments and changes in the market.\
                                            Focus on factual and numerical data available from the market from today's date: {datetime.now().strftime('%Y-%m-%d')}\
                                            focus on geographic regions such as US, Europe, Asia, Middle East, Africa, etc. Try to provide evidence for areas of risk and opportunity.\
                                            Report should be at least 2000 words long and include areas such as tech, health, energy, financial, consumer discretionary, communication, industrials, materials, real estate")
                                            
    market_news_message = embed_citations(market_news_response['choices'][0]['message']['content'], market_news_response['citations'])
    print(f"Finished market news query, took {round(time.time() - start_time, 2)} seconds")
    start_time = time.time()
    economic_news_response = query_perplexity(f"Provide an exhaustive and detailed report on the most recent global economic news.\
                                            We want to have the most up to date information about the economic planning in the world, \
                                            including the most recent decisions and updates from the feds, central banks, and other economic planning bodies.\
                                            Focus on factual and numerical data available from the news from today's date: {datetime.now().strftime('%Y-%m-%d')}\
                                            focus on geographic regions such as US, Europe, Asia, Middle East, Africa, etc. Try to provide evidence for areas of risk and opportunity. Report should be at least 2000 words long")
                                            
    economic_news_message = embed_citations(economic_news_response['choices'][0]['message']['content'], economic_news_response['citations'])
    print(f"Finished economic news query, took {round(time.time() - start_time, 2)} seconds")
    start_time = time.time()
    general_news_response = query_perplexity(f"Provide an exhaustive and detailed report on the most recent global news, ranging from politics, economy, technology, science, culture, sports, entertainment, etc.\
                                            We want a sector by sector breakdown of the news and the most recent developments and changes in the news.\
                                            Focus on factual and numerical data available from the news from today's date: {datetime.now().strftime('%Y-%m-%d')}\
                                            focus on geographic regions such as US, Europe, Asia, Middle East, Africa, etc. Try to provide evidence for areas of risk and opportunity. Report should be at least 2000 words long")
                                            
    general_news_message = embed_citations(general_news_response['choices'][0]['message']['content'], general_news_response['citations'])
    print(f"Finished general news query, took {round(time.time() - start_time, 2)} seconds")


    all_messages = {
        'immediate stock market news (24 hours- most up to date available information)': immediate_stock_market_news_message,
        'geopolitics news': geopolitics_message,
        'stock market news': stock_market_message,
        'market news': market_news_message,
        'economic news': economic_news_message,
        'general news': general_news_message}


    overall_news_message = ""
    for key, value in all_messages.items():
        overall_news_message += f"## {key}:\n{value}\n------------------------------------\n\n"


    return overall_news_message


def main(export_path):
    overall_news_message = get_news_from_perplexity()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if not os.path.exists(export_path):
        os.makedirs(export_path)


    start_time = time.time()
    prompt = f"""
    Using all insights and news provided below, write a detailed daily executive market report, titled "Daily Zephyr", tailored to the current date: {datetime.now().strftime('%Y-%m-%d')}. 
    Follow these instructions: 
    1. IMPORTANT: Executive geopolitics and stock market report, in markdown format, at least 5000 words long and based solely on factual and actual information gathered from reputable sources and provided below. 
    2. IMPORTANT: The citations and sources are provided to you for factual information, pay attention to keeping them, using them as reference and adding them in the output. MAXIMIZE THE USE OF THE CITATIONS PROVIDED TO YOU for anything that needs to be cited. This is EXTREMELY important. For each cited source, keep the exact, full URL. ALL CITATION FOR EACH REFERENCED ITEM NEEDS TO BE INLINE AND FULLY WITHIN THE TEXT so it can work as a hyperlink in the markdown code ( go with format e.g., :[^1](https://tandemadvisors.com/notes-)).
    3. IMPORTANT: INCLUDE AS MUCH AS ACTUAL, MOST UP TO DATE NUMERICAL DATA AS POSSIBLE. DO NOT MAKE UP ANY INFORMATION, BUT TRY TO USE AS MUCH AS POSSIBLE THE INFORMATION PROVIDED TO YOU. Prioritize the most up to date information from the context provided to you.
    4. IMPORTANT: MOST RECENT DEVELOPMENTS (ECONOMIC, GEOPOLITICAL, AND GENERAL NEWS) AND THEIR POTENTIAL IMPACT ON MARKETS, 
    5. IMPORTANT: SECTOR-WISE STOCK TRENDS (TECHNOLOGY, HEALTHCARE, ENERGY, FINANCIAL SERVICES, ETC.) WITH SPECIFIC REFERENCES AND VALUES WITH MOST UP TO DATE INFORMATION. 
    6. IMPORTANT: OPPORTUNITIES AND RISKS, WITH SPECIFIC REFERENCES AND VALUES WITH MOST UP TO DATE INFORMATION. 
    7. IMPORTANT: OUTPUT SHOULD BE IN (AND ONLY IN) FULLY COMPLIANT MARKDOWN SYNTAX AND BE FORMATTED FOR PROFESSIONAL DISTRIBUTION.
    Focus on providing numerical data and clear, actionable insights. Ample information is provided to you, do not make up information or use generalized suggestions, we want the report to be exhaustive, long, specific and advantageous as possible.
    Do not make up information or use generalized suggestions, we want the report to be specific and advantageous as possible.
    If you are using any of the references provided to you, make sure to cite them, provide full source in ["<source>"] format.
    Ensure the report is well-structured, long, and formatted for professional distribution.

    Start with: 

    '''
    # Daily Zephyr
    ## Date: {datetime.now().strftime("%B %d, %Y")}
    ---
    '''

    At the very very end, and after the references section, add this disclaimer:

    '''
    ---
    *[Note: All data and events are accurate as of {datetime.now().strftime('%Y-%m-%d')} based on the provided sources. This report is intended for informational purposes and should not be construed as investment advice.]*
    '''


    This should be a template for your table of contents:

    ## Table of Contents

    1. Executive Summary (with references and citations focusing on the most updated information for today's date: {datetime.now().strftime('%Y-%m-%d')} | {datetime.now().strftime("%B %d, %Y")})
    2. Recent Developments and Market Impacts
    - Geopolitical Landscape
    - Economic Indicators
    - Global Market Trends
    - more if applicable.. (and do not hesitate to add more sections if needed)
    3. Economic News
    - itemized market and economic news
    4. General News
    - general day news items... 
    5. Sector-wise Stock Trends
    - Technology Sector
    - Healthcare Sector
    - Energy Sector
    - Financial Services Sector
    - Consumer Discretionary Sector
    - Communication Services Sector
    - Industrials Sector
    - Materials Sector
    - Real Estate Sector
    - more if applicable.. (and do not hesitate to add more sections if needed)
    6. Opportunities and Risks
    - Opportunities
    - Risks
    7. Conclusion
    8. References (list, with items following style: e.g., [^1]: [Trading Economics - United States Stock Market](https://tradingeconomics.com/united-states/stock-market))


    
    Here is the context information provided to you:
    {overall_news_message}
    """

    response = get_openai_response(openai_client, prompt)
    print(f"Finished openai response, took {round(time.time() - start_time, 2)} seconds")

    chat_raw_output_path = os.path.join(export_path, "chat_raw_output.md")
    with open(chat_raw_output_path, "w") as f:
        f.write(response)

    news_raw_output_path = os.path.join(export_path, "news_raw_output.md")
    with open(news_raw_output_path, "w") as f:
        f.write(overall_news_message)
    

    # chat_raw_output_path = os.path.join(export_path, "chat_raw_output.md")
    chat_html_output_path = os.path.join(export_path, "daily_zephyr.html")
    convert_md_to_html(chat_raw_output_path, chat_html_output_path, os.path.join(os.getcwd(), "templates", "dz_v2.html"))







if __name__ == "__main__":
    export_path = os.path.join(os.getcwd(), "exports", datetime.now().strftime("%Y-%m-%d"))
    main(export_path)
