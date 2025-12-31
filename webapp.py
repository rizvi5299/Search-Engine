from flask import Flask, render_template, request, jsonify
from searchengine import SearchEngine

app = Flask(__name__)
engine = SearchEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    # get query from the request
    query = request.args.get('q', '').strip()
    if not query:  # no query provided
        return jsonify({'query': '', 'results': []})
    
    # run the search engine and collect results
    results, time_taken = engine.search(query, top_k=20)
    
    # return results to the frontend as JSON
    return jsonify({'query': query, 'results': results, 'time': time_taken})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
