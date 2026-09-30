from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentence = [
    "The cat sat on the mat.", 
    "A kitten reseted on the rug.", 
    "Stock prices fell sharply today."
    ]

vectors = model.encode(sentence, normalize_embeddings=True)
print(vectors.shape)
print(vectors[0][:5])

scores = model.similarity(vectors, vectors)
print(scores)