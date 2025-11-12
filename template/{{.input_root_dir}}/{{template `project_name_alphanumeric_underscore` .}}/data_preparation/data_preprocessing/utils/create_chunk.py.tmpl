"""
This sample module contains data preprocessing logic to chunk HTML text.
You should plug in your own data chunking logic in the split_html_on_p method below.
"""

from langchain.text_splitter import (
    HTMLHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from lxml import etree


def get_splitters(tokenizer, max_chunk_size: int, chunk_overlap: int):
    """Initialize splitters with the shared tokenizer.

    :param max_chunk_size: The maximum size of a chunk.
    :param chunk_overlap: Target overlap between chunks.
    Overlapping chunks helps to mitigate loss of information when context is divided between chunks.
    :return: A tuple of text splitter and html text splitter
    """
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer, chunk_size=max_chunk_size, chunk_overlap=chunk_overlap
    )
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=[("p", "paragraph")])
    return text_splitter, html_splitter


def split_html_on_p(
    html: str,
    tokenizer,
    chunk_overlap: int = 50,
    min_chunk_size: int = 20,
    max_chunk_size: int = 500,
):
    try:
        """Parse and split HTML content into chunks.

        Split on <p>, but merge small paragraph chunks together to avoid too small.
        It uses HTMLHeaderTextSplitter to parse the HTML content and
        RecursiveCharacterTextSplitter to split the text into chunks

        TODO: Update and adapt the sample code for your use case

        :param html: HTML content
        :param chunk_overlap: Target overlap between chunks.
        Overlapping chunks helps to mitigate loss of information when context is divided between chunks.
        :param min_chunk_size: The minimum size of a chunk.
        :param max_chunk_size: The maximum size of a chunk.
        :return: List of chunked text for input HTML content
        """
        if not html:
            return []

        # Get splitters
        text_splitter, html_splitter = get_splitters(
            tokenizer, max_chunk_size, chunk_overlap
        )

        p_chunks = html_splitter.split_text(html)
        chunks = []
        previous_chunk = ""

        # Merge chunks together to add text before <p> and avoid too small docs.
        for c in p_chunks:
            # Concat the paragraph
            content = c.page_content
            if len(tokenizer.encode(previous_chunk + content)) <= max_chunk_size / 2:
                previous_chunk += content + "\n"
            else:
                chunks.extend(text_splitter.split_text(previous_chunk.strip()))
                previous_chunk = content + "\n"

        if previous_chunk:
            chunks.extend(text_splitter.split_text(previous_chunk.strip()))

        # Discard chunks smaller than min_chunk_size
        return [c for c in chunks if len(tokenizer.encode(c)) > min_chunk_size]

    except etree.XSLTApplyError as e:
        print(f"XSLTApplyError: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None