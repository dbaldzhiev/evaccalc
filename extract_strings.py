import sys
import re

def extract_strings(filename, min_len=4):
    try:
        with open(filename, "rb") as f:
            data = f.read()
            # Simple regex for printable chunks
            # allowing some european characters if encoded in latin-1 but pdfs are messy
            # We look for ASCII text primarily or UTF-8
            
            text = ""
            # Try decoding as latin-1 (common in PDFs) to keep bytes 
            chars = data.decode("latin-1", errors="ignore")
            
            # Find sequences of printable chars
            strings = re.findall(r"[A-Za-z0-9\s\.\,\:\-\(\)]{4,}", chars)
            
            for s in strings:
                print(s)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_strings(sys.argv[1])
