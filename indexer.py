import json
import re
from collections import defaultdict, Counter

inverted_index = defaultdict(dict)
doc_info = {}
total_docs = 0
avg_doc_length = 0
with open('stopwords.txt', 'r') as f:
    stopwords = f.read().splitlines()

def tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b[a-z0-9]+\b', text)
    return [t for t in tokens if t not in stopwords]
    
def build_index():
    print("Building index...")
    with open('data/pages.json') as f:
        pages = json.load(f)
        
    total_docs = len(pages)
    total_length = 0
    
    for page in pages:
        doc_id = page['doc_id']
        full_text = (page['title'] + ' ') * 3 + page['text']
        tokens = tokenize(full_text)
        term_freq = Counter(tokens)
        doc_length = len(tokens)
        total_length += doc_length
        
        doc_info[doc_id] = {
            'url': page['url'],
            'title': page['title'],
            'length': doc_length
        }
        
        for term, freq in term_freq.items():
            inverted_index[term][doc_id] = freq
    
    avg_doc_length = total_length / total_docs
    
    with open('data/index.json', 'w') as f:
        json.dump(dict(inverted_index), f)
    with open('data/doc_info.json', 'w') as f:
        json.dump(doc_info, f)
    with open('data/stats.json', 'w') as f:
        json.dump({
            'total_docs': total_docs,
            'avg_doc_length': avg_doc_length,
            'vocab_size': len(inverted_index)
        }, f)
    
    print(f"Indexed {total_docs} docs, {len(inverted_index)} terms")

if __name__ == '__main__':
    build_index()