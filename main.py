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


    all_messages = {'geopolitics news': geopolitics_message,
                    'stock market news': stock_market_message,
                    'market news': market_news_message,
                    'economic news': economic_news_message,
                    'general news': general_news_message}


    overall_news_message = ""
    for key, value in all_messages.items():
        overall_news_message += f"## {key}:\n{value}\n------------------------------------\n\n"


    return overall_news_message


def main(export_path):
    # overall_news_message = get_news_from_perplexity()
    # openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # if not os.path.exists(export_path):
    #     os.makedirs(export_path)


    # start_time = time.time()
    # prompt = f"""
    # Using all insights and news provided below, write a detailed daily executive market report, titled "Daily Zephyr", tailored to the current date: {datetime.now().strftime('%Y-%m-%d')}. 
    # Follow these instructions: 
    # 1. IMPORTANT: Executive stock market report, in markdown format, at least 4000 words long and based solely on factual and actual information gathered from reputable sources and provided below. 
    # 2. IMPORTANT: The citations and sources are provided to you for factual information, pay attention to keeping them, using them as reference and adding them in the output. For each cited source, keep the exact, full URL. ALL CITATION FOR EACH REFERENCED ITEM NEEDS TO BE INLINE AND FULLY WITHIN THE TEXT.
    # 3. IMPORTANT: INCLUDE AS MUCH AS ACTUAL, MOST UP TO DATE NUMERICAL DATA AS POSSIBLE. DO NOT MAKE UP ANY INFORMATION, BUT TRY TO USE AS MUCH AS POSSIBLE THE INFORMATION PROVIDED TO YOU.
    # 4. Most recent developments (economic, geopolitics, and general news) and their potential impact on Markets,  
    # 5. Sector-wise Stock Trends (Technology, Healthcare, Energy, Financial Services, etc.) with specific references and values with most up to date information. 
    # 6. Opportunities and Risks, with specific references and values with most up to date information. 
    # 7. Output should be in (and only in) fully compliant markdown syntax and be formatted for professional distribution.
    # Focus on providing numerical data and clear, actionable insights. Ample information is provided to you, do not make up information or use generalized suggestions, we want the report to be exhaustive, long, specific and advantageous as possible.
    # Do not make up information or use generalized suggestions, we want the report to be specific and advantageous as possible.
    # If you are using any of the references provided to you, make sure to cite them, provide full source in ["<source>"] format.
    # Ensure the report is well-structured, long, and formatted for professional distribution.


    # This should be a template for your table of contents:

    # ## Table of Contents

    # 1. [Executive Summary](#executive-summary)
    # 2. [Recent Developments and Market Impacts](#recent-developments-and-market-impacts)
    # - [Geopolitical Landscape](#geopolitical-landscape)
    # - [Economic Indicators](#economic-indicators)
    # - [Global Market Trends](#global-market-trends)
    # - more if applicable..
    # 3. [Sector-wise Stock Trends](#sector-wise-stock-trends)
    # - [Technology Sector](#technology-sector)
    # - [Healthcare Sector](#healthcare-sector)
    # - [Energy Sector](#energy-sector)
    # - [Financial Services Sector](#financial-services-sector)
    # - [Consumer Discretionary Sector](#consumer-discretionary-sector)
    # - [Communication Services Sector](#communication-services-sector)
    # - [Industrials Sector](#industrials-sector)
    # - [Materials Sector](#materials-sector)
    # - [Real Estate Sector](#real-estate-sector)
    # - more if applicable..
    # 4. [Opportunities and Risks](#opportunities-and-risks)
    # - [Opportunities](#opportunities)
    # - [Risks](#risks)
    # 5. [Conclusion](#conclusion)
    # 6. [References](#references)

    # Here is the context information provided to you:
    # {overall_news_message}
    # """

    # response = get_openai_response(openai_client, prompt)
    # print(f"Finished openai response, took {round(time.time() - start_time, 2)} seconds")

    chat_raw_output_path = os.path.join(export_path, "chat_raw_output.md")
    # with open(chat_raw_output_path, "w") as f:
    #     f.write(response)

    # news_raw_output_path = os.path.join(export_path, "news_raw_output.md")
    # with open(news_raw_output_path, "w") as f:
    #     f.write(overall_news_message)
    
    chat_html_output_path = os.path.join(export_path, "daily_zephyr.html")
    convert_md_to_html(chat_raw_output_path, chat_html_output_path)







if __name__ == "__main__":
    export_path = os.path.join(os.getcwd(), "exports", datetime.now().strftime("%Y-%m-%d"))
    main(export_path)
