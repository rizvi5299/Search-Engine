# Web Search Engine System

A Python-based web search engine that crawls, indexes, and ranks web pages using a combination of BM25 text relevance and PageRank link authority. The system provides a simple web interface for querying indexed content.

## Overview

This project implements a small-scale search engine designed for Python-related documentation websites. It crawls approximately 500 web pages, builds an inverted index, computes PageRank scores based on link structure, and returns ranked search results through a Flask web application.

## Features

- Ethical web crawling with robots.txt compliance and request delays  
- Inverted index with weighted title and body terms  
- BM25 ranking for textual relevance  
- PageRank for link-based authority scoring  
- Combined ranking using weighted BM25 and PageRank scores  
- Web-based search interface with JSON API responses  


## How It Works

1. **Crawling**  
   `crawler.py` downloads HTML pages starting from seed URLs, extracts text and links, and stores the data in JSON format.

2. **Indexing**  
   `indexer.py` processes crawled pages, tokenizes text, applies stopword removal, weights titles higher than body text, and builds an inverted index.

3. **PageRank**  
   `pagerank.py` constructs a directed graph of pages and computes normalized PageRank scores using NetworkX.

4. **Searching**  
   `searchengine.py` combines BM25 relevance scores and PageRank authority scores into a final ranking.

5. **Web Interface**  
   `webapp.py` exposes a Flask-based interface where users can submit queries and view ranked results.

## How to Run
Run the components in the following order:

```bash
docker build -t search-engine .
docker run -p 5000:5000 search-engine
```


