# Daily Zephyr

Daily Zephyr is a Python-based project that generates daily geopolitics and market reports using large language models (LLMs). It fetches the most recent news and market data from various sources, processes the information, and generates a comprehensive report in HTML format.

## Features

- Fetches geopolitical, stock market, economic, and general news using the Perplexity API
- Generates a detailed executive market report based on the fetched data
- Embeds citations and sources within the generated report
- Outputs the report in both Markdown and HTML formats

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/daily_zephyr.git
   ```

2. Navigate to the project directory:
   ```
   cd daily_zephyr
   ```

3. Run the setup script:
   ```
   ./setup.sh
   ```

4. Update the `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PERPLEXITY_API_KEY=your_perplexity_api_key
   ```

## Usage

To generate the daily report, run the following command:

```
./run.sh
```
