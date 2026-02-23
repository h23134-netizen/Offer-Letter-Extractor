import fitz
from backend.extractor.text_extractor import TextExtractor

# First, let's see RAW PyMuPDF string output
doc = fitz.open('dummy_offer.pdf')
print("--- RAW Paged Output ---")
for page in doc:
    print(page.get_text('text'))

print("\n--- Extractor Class Output ---")
with open('dummy_offer.pdf', 'rb') as f:
    extractor = TextExtractor()
    extracted = extractor._extract_pdf(f.read())
    print(extracted)
