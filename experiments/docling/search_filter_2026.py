import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

conn = psycopg.connect("dbname=revrag", autocommit=True)
register_vector(conn)

model = SentenceTransformer(MODEL_NAME)

questions = [
    "What is the late submission penalty?",
    "How many days do I have to withdraw without penalty?",
    "How much is the BSc Computer Science fee?",
    "When is the first-semester fee due?",
    "What was the late penalty in 2025?",
]

for question in questions: 
    q_vector = model.encode([question], normalize_embeddings=True)[0]    
    print(question)
    rows = conn.execute(
    "SELECT edition, heading, embedding <=> %s AS distance  FROM chunks WHERE edition = %s ORDER BY distance LIMIT 3",
    (Vector(q_vector),2026),
        ).fetchall()
    for edition, heading, distance in rows:
        print(edition, heading, distance)




