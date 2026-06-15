import io
import zipfile

import fitz
from docx import Document
from pathlib import Path
from typing import List, Optional


def parse_pdf(data: bytes) -> str:
    """提取所有文本"""
    text_parts = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def parse_docx(data: bytes) -> str:
    """提取所有文本"""
    doc = Document(io.BytesIO(data))
    text_parts = [para.text for para in doc.paragraphs]
    return "\n".join(text_parts)


def parse(data: bytes) -> str:
    if data[:5] == b'%PDF-':
        return parse_pdf(data)
    elif data[:4] == b'PK\x03\x04':
        # 尝试作为 ZIP 解析，检查内部文件
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                # DOCX 必须包含 word/document.xml
                if 'word/document.xml' in zf.namelist():
                    return parse_docx(data)
                else:
                    raise ValueError("未知的文件格式")
        except zipfile.BadZipFile:
            raise ValueError("未知的文件格式")
    else:
        raise ValueError("未知的文件格式")


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size 必须大于 overlap")

    if not text:
        return []

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunks.append(text[start:start + chunk_size])
    return chunks
