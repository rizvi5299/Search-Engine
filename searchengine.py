import json
import re
from rank_bm25 import BM25Okapi
import time

class SearchEngine:
    def __init__(self, w1=0.7, w2=0.3):
        with open('data/index.json', 'r') as f:
            self.index = json.load(f)
        with open('data/doc_info.json', 'r') as f:
            self.doc_info = json.load(f)
        with open('data/stats.json', 'r') as f:
            self.stats = json.load(f)
        with open('data/pagerank.json', 'r') as f:
            self.pagerank = json.load(f)

        # ranking weights
        self.w1 = w1
        self.w2 = w2

        self.doc_ids = list(self.doc_info.keys())
        self.corpus = []

        # build token lists for BM25. based on term frequencies in the index
        for doc_id in self.doc_ids:
            tokens = []
            for term, postings in self.index.items():
                if doc_id in postings:
                    tf = postings[doc_id]
                    tokens.extend([term] * tf)
            self.corpus.append(tokens)

        # initialize BM25 model
        self.bm25 = BM25Okapi(self.corpus)

    def tokenize(self, text):
        # lowercase alphanumeric tokenizer
        return re.findall(r'\b[a-z0-9]+\b', text.lower())

    def normalize(self, scores):
        # normalize values to 0 to 1 for score blending
        if not scores:
            return {}
        vals = list(scores.values())
        lo, hi = min(vals), max(vals)
        if lo == hi:
            return {k: 0.5 for k in scores}
        return {k: (v - lo) / (hi - lo) for k, v in scores.items()}

    def search(self, query, top_k):
        start = time.perf_counter()
        terms = self.tokenize(query)
        if not terms:
            return []

        # identify candidate documents containing at least one query term
        candidates = set()
        for t in terms:
            if t in self.index:
                candidates.update(self.index[t])

        if not candidates:
            return []

        # compute BM25 scores for the query
        raw_scores = self.bm25.get_scores(terms)

        # filter BM25 scores to only candidate documents
        bm25_scores = {
            doc_id: raw_scores[i]
            for i, doc_id in enumerate(self.doc_ids)
            if doc_id in candidates
        }

        bm25_norm = self.normalize(bm25_scores)

        # combine BM25 and PageRank scores
        final_scores = {
            doc: self.w1 * bm25_norm.get(doc, 0) + self.w2 * self.pagerank.get(doc, 0)
            for doc in candidates
        }

        # sort and select top ranked documents
        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for doc, score in ranked:
            info = self.doc_info[doc]
            results.append({
                "doc_id": doc,
                "url": info["url"],
                "title": info["title"],
                "score": score,
                "bm25": bm25_norm.get(doc, 0),
                "pagerank": self.pagerank.get(doc, 0)
            })

        end = time.perf_counter()
        total = end - start

        return results, total
