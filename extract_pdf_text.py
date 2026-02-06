from pypdf import PdfReader
import sys

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"--- Extracting from {pdf_path} ---")
        print(f"Number of pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            print(f"\n[Page {i+1}]")
            text = page.extract_text()
            print(text)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_text(sys.argv[1])
