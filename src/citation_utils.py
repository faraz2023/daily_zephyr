import re

def embed_citations(message: str, citations: list) -> str:
    """
    Embed citations in the message by replacing [1], [2], ... with the actual citations from the list,
    using proper Markdown link syntax for citations.
    """
    def replacer(match):
        index = int(match.group(1)) - 1  # Get the citation index
        if 0 <= index < len(citations):
            # Embed the citation as a Markdown link, e.g. [1](URL/Reference)
            return f'[{index + 1}]({citations[index]})'
        return match.group(0)  # Leave the citation unchanged if out of range

    # Replace citation references in the format [1], [2], etc. with Markdown links
    embedded_message = re.sub(r'\[(\d+)\]', replacer, message)
    return embedded_message

def extract_citations(citation_embedded_message: str) -> tuple:
    """
    Extract citations from the message, returning the re-numbered message and a list of unique citations.
    """
    # Find all embedded citations in the format ["citation"]
    citations = re.findall(r'\["(.*?)"\]', citation_embedded_message)
    
    # Create a unique list of citations while preserving order
    unique_citations = list(dict.fromkeys(citations))

    def renumber_replacer(match):
        citation = match.group(1)
        if citation in unique_citations:
            # Renumber the citation based on its order in unique_citations
            return f'[{unique_citations.index(citation) + 1}]'
        return match.group(0)  # Leave unchanged if not found

    # Replace embedded citations with renumbered ones
    renumbered_message = re.sub(r'\["(.*?)"\]', renumber_replacer, citation_embedded_message)
    
    return renumbered_message, unique_citations
