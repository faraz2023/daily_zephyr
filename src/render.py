import markdown
import os
import argparse

def convert_md_to_html(md_file_path, output_html_path):
    import markdown
    import os
    
    if not os.path.exists(md_file_path):
        raise FileNotFoundError(f"The file {md_file_path} does not exist.")

    with open(md_file_path, "r", encoding="utf-8") as f:
        md_content = f.read()


    extensions = [
        'fenced_code',
        'codehilite',
        # 'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        # 'markdown.extensions.footnotes'
    ]

    html_content = markdown.markdown(md_content, extensions=extensions)

    # Define a modern and minimal HTML template with Bootstrap
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Zaphyer</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #ffffff;
                --text-color: #333333;
                --accent-color: #3498db;
                --secondary-bg: #f0f0f0;
                --header-bg: #2c3e50;
                --header-text: #ffffff;
            }}
            [data-theme="dark"] {{
                --bg-color: #1a1a1a;
                --text-color: #f0f0f0;
                --accent-color: #3498db;
                --secondary-bg: #2c2c2c;
                --header-bg: #2c3e50;
                --header-text: #ffffff;
            }}
            body {{
                font-family: 'Roboto', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                transition: background-color 0.3s, color 0.3s;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            header {{
                background-color: var(--header-bg);
                color: var(--header-text);
                padding: 20px 0;
                text-align: center;
            }}
            h1 {{
                font-family: 'Playfair Display', serif;
                font-size: 2.5em;
                margin: 0;
            }}
            h2, h3, h4, h5, h6 {{
                font-family: 'Playfair Display', serif;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            p {{
                line-height: 1.6;
                margin-bottom: 1em;
            }}
            pre {{
                background-color: var(--secondary-bg);
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            code {{
                font-family: 'Roboto Mono', monospace;
                background-color: var(--secondary-bg);
                padding: 2px 4px;
                border-radius: 3px;
            }}
            ul, ol {{
                margin-bottom: 1em;
                padding-left: 1.5em;
            }}
            .theme-toggle {{
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: var(--accent-color);
                color: #ffffff;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            }}
            .theme-toggle:hover {{
                background-color: #2980b9;
            }}
            article {{
                background-color: var(--bg-color);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 30px;
                margin-bottom: 30px;
            }}
            .date {{
                font-size: 0.9em;
                color: var(--accent-color);
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Daily Zaphyer</h1>
        </header>
        <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
        <div class="container">
            <article>
                <div class="date">May 15, 2023</div>
                {html_content}
            </article>
        </div>
        <script>
            function toggleTheme() {{
                const body = document.body;
                if (body.getAttribute('data-theme') === 'dark') {{
                    body.removeAttribute('data-theme');
                }} else {{
                    body.setAttribute('data-theme', 'dark');
                }}
            }}

            // Check for user's preferred color scheme
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                document.body.setAttribute('data-theme', 'dark');
            }}
        </script>
    </body>
    </html>
    """
    # Write the HTML output
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"HTML file has been saved to: {output_html_path}")