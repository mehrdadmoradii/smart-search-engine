from flask import Flask, render_template, request

from search import SearchEngine 


app = Flask(__name__)
search_engine = SearchEngine()

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/search')
def results_page():
    query = request.args.get('query')
    result = search_engine.semantic_search(query)
    return render_template('search-result.html', result=result, query=query)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
