"""
PDF Summary Tool
Reads a PDF file and prints a structured summary with page citations.
Usage: python pdf_summary.py <path-to-pdf>
"""

import os
import argparse
from openai import OpenAI
from dotenv import load_dotenv
import pdfplumber

load_dotenv()


def parse_page_range(range_str):
    """Parse a 'START-END' string into (start, end) integers.
    Returns None if the format is invalid.
    """
    try:
        parts = range_str.split("-")
        if len(parts) != 2:
            return None
        start = int(parts[0])
        end = int(parts[1])
        if start < 1 or end < start:
            return None
        return start, end
    except (ValueError, TypeError):
        return None


def extract_text_from_pdf(pdf_path, page_range=None):
    """Extract text from a PDF file, returning a dict of {page_number: text}.
    If page_range is given as (start, end), only those pages are extracted.
    Prints progress as: Extracting page 3/10...
    """
    pages = {}
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            # Skip pages outside the requested range
            if page_range and (i < page_range[0] or i > page_range[1]):
                continue
            print(f"Extracting page {i}/{total}...")
            text = page.extract_text()
            if text:
                pages[i] = text
    return pages


def build_prompt(pages, question="Summarize this document"):
    """Build system and user prompts with numbered pages."""
    system_prompt = """You are a precise research assistant. Summarize the provided document.

Rules:
1. Output exactly three sections: ## Overview, ## Key Points, ## Limitations.
2. Overview: 2-3 sentences summarizing the document's main topic.
3. Key Points: exactly 3-5 bullet points. Each bullet MUST start with "- " and end with [Page X].
   Example: "- Python was created by Guido van Rossum in 1991 [Page 1]."
4. Limitations: note any caveats, such as missing context or extraction issues.
5. Do NOT add information beyond what is in the text.
"""

    # Build numbered page text
    numbered_text = ""
    for page_num, text in pages.items():
        numbered_text += f"[Page {page_num}]\n{text}\n\n"

    user_prompt = f"""Here is the document text:

{numbered_text}

Task: {question}"""

    return system_prompt, user_prompt


def ask_llm(pages):
    """Send the extracted text to DeepSeek and return the summary."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is missing. Add it to .env and try again.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    system_prompt, user_prompt = build_prompt(pages)

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="PDF Summary Tool")
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to summarize",
    )
    parser.add_argument(
        "--pages",
        help="Page range to summarize, e.g. 1-5",
    )
    args = parser.parse_args()

    # Parse page range
    page_range = None
    if args.pages:
        page_range = parse_page_range(args.pages)
        if page_range is None:
            raise SystemExit(
                f"错误：无效的页面范围 '{args.pages}'。"
                " 请使用 START-END 格式，例如 --pages 1-5。"
            )

    # Check file exists
    if not os.path.isfile(args.pdf_path):
        raise SystemExit(f"错误：找不到文件 '{args.pdf_path}'。请检查路径是否正确。")

    print(f"正在提取文本：{args.pdf_path} ...")
    pages = extract_text_from_pdf(args.pdf_path, page_range)

    # Check for empty text (scanned PDF)
    if not pages:
        raise SystemExit(
            "无法从此 PDF 中提取文字。它可能是扫描件或图片型 PDF，"
            "当前工具不支持 OCR 识别。"
        )

    print(f"已提取 {len(pages)} 页文字，正在生成摘要...\n")
    summary = ask_llm(pages)

    print(summary)


if __name__ == "__main__":
    main()
