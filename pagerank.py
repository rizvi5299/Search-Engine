import json
import networkx as nx

DAMPING = 0.85
        
def calculate():
    print("Calculating PageRank...")
    with open('data/pages.json', 'r') as f:
        pages = json.load(f)
    
    # build graph
    G = nx.DiGraph()
    url_to_id = {p['url']: p['doc_id'] for p in pages}
    
    # add nodes here
    for page in pages:
        G.add_node(page['doc_id'])
    
    # add edges here
    for page in pages:
        doc_id = page['doc_id']
        for outlink in page['outlinks']:
            if outlink in url_to_id:
                target = url_to_id[outlink]
                G.add_edge(doc_id, target)
    
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # calculate PageRank 
    pagerank = nx.pagerank(G, alpha=DAMPING, max_iter=100, tol=1e-6)
    
    # normalize to [0,1]
    min_pr = min(pagerank.values())
    max_pr = max(pagerank.values())
    if max_pr > min_pr:
        pagerank = {k: (v - min_pr) / (max_pr - min_pr) for k, v in pagerank.items()}
    else:
        pagerank = {k: 0.5 for k in pagerank}
    
    with open('data/pagerank.json', 'w') as f:
        json.dump(pagerank, f)
    
    print("PageRank done!")

if __name__ == '__main__':
    calculate()
