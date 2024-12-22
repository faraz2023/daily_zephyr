import markdown
import os
import argparse

def convert_md_to_html(chat_raw_output_path, chat_html_output_path, html_template_path):

    try:
        with open(chat_raw_output_path, 'r', encoding='utf-8') as md_file:
            md_content = md_file.read()
        
        extensions = [
        'fenced_code',
        'codehilite',
        # 'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        # 'markdown.extensions.footnotes'
        ]

        html_content = markdown.markdown(md_content, extensions=extensions)
        
        with open(html_template_path, 'r', encoding='utf-8') as html_template_file:
            html_template = html_template_file.read()
        
        final_html_content = html_template.replace("{html_content}", html_content)
        
        with open(chat_html_output_path, 'w', encoding='utf-8') as output_html_file:
            output_html_file.write(final_html_content)
        
        print(f"HTML file successfully created at: {chat_html_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


