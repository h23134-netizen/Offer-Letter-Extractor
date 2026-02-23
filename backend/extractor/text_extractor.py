import io
import docx
import fitz  # PyMuPDF
import re
from .config import SECTION_HEADERS

class TextExtractor:
    def split_sections(self, full_text: str) -> dict:
        """
        Splits document into sections using case-insensitive anchors.
        """
        sections = {
            "header": "",
            "compensation": "",
            "terms": "",
            "byod": "",
            "scheduleA": "",
            "salary_table": "",
            "acceptance": ""
        }
        
        header_mapping = {
            "OFFER LETTER": "header",
            "Compensation & Benefits": "compensation",
            "Additional Terms and Conditions": "terms",
            "BYOD": "byod",
            "Schedule A": "scheduleA",
            "SALARY COMPUTATION": "salary_table",
            "ACCEPTANCE OF OFFER TERMS AND CONDITIONS": "acceptance"
        }
        
        found_sections = []
        for header, key in header_mapping.items():
            # Find the header case-insensitively
            for match in re.finditer(re.escape(header), full_text, re.IGNORECASE):
                found_sections.append((match.start(), key))
                break  # Take the first occurrence
                
        # Sort sections by their physical position in the document
        found_sections.sort(key=lambda x: x[0])
        
        if not found_sections:
            sections["header"] = full_text
            return sections
            
        # The text before the first detected header is considered the 'header' or 'intro'
        first_section_start = found_sections[0][0]
        if first_section_start > 0:
            sections["header"] = full_text[:first_section_start].strip()
            
        # Extract content for each section
        for i in range(len(found_sections)):
            start_idx = found_sections[i][0]
            key = found_sections[i][1]
            end_idx = found_sections[i+1][0] if i + 1 < len(found_sections) else len(full_text)
            sections[key] = full_text[start_idx:end_idx].strip()
            
        return sections

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extracts raw text from a file (DOCX or PDF).
        Returns the extracted text string.
        Raises ValueError for unsupported types or empty content.
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith(".docx"):
            return self._extract_docx(file_content)
        elif filename_lower.endswith(".pdf"):
            return self._extract_pdf(file_content)
        else:
            raise ValueError("INVALID_TYPE: Unsupported file format. Please upload DOCX or PDF.")

    def _extract_docx(self, content: bytes) -> str:
        try:
            doc = docx.Document(io.BytesIO(content))
            from docx.oxml.text.paragraph import CT_P
            from docx.oxml.table import CT_Tbl
            from docx.text.paragraph import Paragraph
            from docx.table import Table

            full_text = []
            for child in doc.element.body:
                if isinstance(child, CT_P):
                    full_text.append(Paragraph(child, doc).text)
                elif isinstance(child, CT_Tbl):
                    tbl = Table(child, doc)
                    for row in tbl.rows:
                        row_text = []
                        for cell in row.cells:
                            # Remove excessive newlines in table cells to keep them on one line
                            row_text.append(cell.text.strip().replace('\n', ' '))
                        full_text.append(" ".join(row_text))
            
            return "\n".join(full_text)
        except Exception as e:
            raise ValueError(f"PARSE_FAILED: Failed to parse DOCX. {str(e)}")

    def _extract_pdf(self, content: bytes) -> str:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            full_text = []
            
            for page in doc:
                words = page.get_text("words")
                if words:
                    # Sort words spatially to preserve table layouts
                    # words are (x0, y0, x1, y1, "word", block_no, line_no, word_no)
                    lines = {}
                    for w in words:
                        # Group by y0, using a tolerance of e.g. 5 pixels to handle slight misalignments
                        y = round(w[1] / 5) * 5
                        if y not in lines:
                            lines[y] = []
                        lines[y].append(w)
                    
                    for y in sorted(lines.keys()):
                        # Sort left to right
                        line_words = sorted(lines[y], key=lambda x: x[0])
                        full_text.append(" ".join(w[4] for w in line_words))
                else:
                    # Fallback if words extraction fails (unlikely for text PDFs)
                    text = page.get_text("text")
                    if text.strip():
                        full_text.append(text)
            
            extracted_text = "\n".join(full_text)
            
            # Heuristic for scanned PDF
            if len(extracted_text.strip()) < 50 and len(doc) > 0:
                 raise ValueError("SCANNED_PDF: Text extraction yielded minimal results. File might be a scanned image.")

            return extracted_text
            
        except ValueError as ve:
             raise ve
        except Exception as e:
            raise ValueError(f"PARSE_FAILED: Failed to parse PDF. {str(e)}")
