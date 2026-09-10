from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBaseRetriever:

    def __init__(self):
        self.documents: List[Dict] = []
        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )
        self.matrix = None

    def add_documents(self, documents: List[Dict]):
        """
        documents format:

        [
            {
                "id": "doc1",
                "text": "Python was created by Guido van Rossum."
            }
        ]
        """

        self.documents.extend(documents)

        texts = [doc["text"] for doc in self.documents]

        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:

        if not self.documents or self.matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            results.append({
                "id": self.documents[index]["id"],
                "text": self.documents[index]["text"],
                "score": float(similarities[index])
            })

        return results