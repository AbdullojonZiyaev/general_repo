import fitz  # PyMuPDF
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# --- CONFIG ---
OUTPUT_FILE = "formatted_highlights3.txt"
NUM_TOP_SENTENCES = 5  # number of top sentences per section

# --- FUNCTIONS ---
def extract_sections(page_text):
    lines = page_text.split('\n')
    sections = {}
    current_section = "General"
    sections[current_section] = []

    for line in lines:
        if re.match(r'^[A-Z \-]{4,}$', line.strip()):  # detect all-caps headings
            current_section = line.strip()
            sections[current_section] = []
        else:
            sections[current_section].append(line.strip())

    return sections

def extract_top_sentences(text_block, top_n=NUM_TOP_SENTENCES):
    sentences = re.split(r'(?<=[.!?]) +', text_block)
    if len(sentences) <= top_n:
        return sentences
    
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1)
    
    ranked_sentences = sorted(
        [(s, scores[i, 0]) for i, s in enumerate(sentences)],
        key=lambda x: x[1],
        reverse=True
    )
    
    top_sentences = [s for s, _ in ranked_sentences[:top_n]]
    return top_sentences

# Commented out the image extraction part
# def extract_images_and_captions(page):
#     images = []
    
#     # Get all images on the page
#     image_list = page.get_images(full=True)
    
#     for img in image_list:
#         xref = img[0]  # Image reference
#         # Get the image's bounding box (position on the page)
#         img_bbox = fitz.Rect(img[3])  # The 3rd element in the tuple is the bounding box (position)
        
#         # Try to find caption text below the image
#         caption_text = ""
#         for block in page.get_text("dict")['blocks']:
#             if block['type'] == 0:  # Text block
#                 block_rect = fitz.Rect(block['bbox'])
#                 if block_rect.y0 > img_bbox.y1 and block_rect.y0 < img_bbox.y1 + 50:  # Look for text blocks below the image
#                     caption_text = block['lines'][0]['spans'][0]['text']
#                     break
        
#         images.append((xref, caption_text))
    
#     return images

# --- MAIN SCRIPT ---

doc = fitz.open("file3.pdf")
all_highlights = []

for page in doc:
    sections = extract_sections(page.get_text())
    
    for section, lines in sections.items():
        section_text = ' '.join(lines)
        top_sentences = extract_top_sentences(section_text)
        
        if top_sentences:
            all_highlights.append(f"=== {section} ===\n")
            for sent in top_sentences:
                all_highlights.append(f"• {sent}\n")
            all_highlights.append("\n")
    
    # Commented out the images part
    # images = extract_images_and_captions(page)
    # if images:
    #     all_highlights.append(f"=== Images and Captions (Page {page.number + 1}) ===\n")
    #     for idx, caption in images:
    #         if caption:
    #             all_highlights.append(f"• Image {idx}: {caption}\n")
    #         else:
    #             all_highlights.append(f"• Image {idx}: [No caption found]\n")
    #     all_highlights.append("\n")

# Write to output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.writelines(all_highlights)

print(f"✅ Highlights saved to {OUTPUT_FILE}")
