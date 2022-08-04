from sentence_transformers import SentenceTransformer, util
import os

from elasticsearch import Elasticsearch


class SearchEngine:
    
    def __init__(self):
        self._client = Elasticsearch(os.getenv('ELASTICSEARCH_HOSTS'))
        self._model = SentenceTransformer('prajjwal1/bert-tiny')

    def semantic_search(self, query:str):
        search_result = self._client.search(
            index='articles',
            body= self._get_search_dsl(query)
        )['hits']['hits']
        res = [self._parse_article(article, query) for article in search_result]
        res = sorted(res, reverse=True, key=lambda x: x['score'])
        return res[:10]

    def _parse_article(self, article: dict, query: str):
        """Parse the article document that comes from elasticsearch.
        
        """
        source = article['_source']
        highlight = ' '.join(article['highlight']['text']) 
        url = source['source_url'] + '#' + source['section_title']
        relevancy_score = self._score(article['_source']['text'], query)
        return {
            'article_title': source['article_title'],
            'section_title': source['section_title'],
            'url': url,
            'highlight': highlight,
            'score': relevancy_score,
        }

    def _score(self, text:str, query:str):
        query_vector = self._model.encode(query)
        text_vector = self._model.encode(text)
        cos_sim_score = util.cos_sim(query_vector, text_vector)
        return cos_sim_score.item()

    def _get_search_dsl(self, query: str, page_size=50) -> str:
        return {
            "size": page_size,
            "query": {
                "bool": {
                "must": [
                    {"multi_match": {
                    "query": query,
                    "fields": ["text^3", "article_title^3"]
                    }}
                ],
                "must_not": [
                    {"match": {"main_section": "External links"}}
                ],
                "should": [
                    {"match": {"main_section": {"query": "Summary","boost": 2}}}
                ]
                }
            },
            "highlight": {
                "fields": {
                "text": {}
                } 
            }
        }