import re

def split_by_newlines(text):
    # Split into chunks where there are 2 or more consecutive newlines
    chunks = re.split(r'\n{2,}', text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def clean_chunk(text):
    text = re.sub(r'\x0c', ' ', text)
    text = re.sub(r'[0-9]+', ' ', text)  # Remove all English digits
    text = re.sub(r'\[?লুকছল.*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'অনলাইন.*?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace("\n", " ")  # Flatten remaining line breaks
    text = re.sub(r'[^\u0980-\u09FF০-৯ ]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def combine_small_chunks(chunks, threshold=500):
    combined = []
    buffer = ""

    for chunk in chunks:
        if len(buffer) + len(chunk) < threshold:
            buffer += " " + chunk  # Add to buffer
        else:
            if buffer:
                combined.append(buffer.strip())
                buffer = ""
            combined.append(chunk.strip())  # Add large chunk directly

    if buffer:
        combined.append(buffer.strip())  # Add remaining buffer

    return combined

def add_overlap(chunks, overlap=50):
    overlapped = []
    for i in range(len(chunks)):
        current = chunks[i]
        if i > 0:
            # Take last `overlap` words from previous chunk
            prev = overlapped[-1].split()
            tail = prev[-overlap:] if len(prev) > overlap else prev
            current = " ".join(tail) + " " + current
        overlapped.append(current)
    return overlapped

def clean_and_chunk_document(raw_text):
    rough_chunks = split_by_newlines(raw_text)
    cleaned_chunks = [clean_chunk(c) for c in rough_chunks if len(c.strip()) > 10]
    merged_chunks = combine_small_chunks(cleaned_chunks, threshold=500)
    overlapped_chunks = add_overlap(merged_chunks, overlap=100)
    return overlapped_chunks

