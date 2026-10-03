import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
import ollama

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
    "SELECT edition, heading, content, embedding <=> %s AS distance FROM chunks ORDER BY distance LIMIT 3",
    (Vector(q_vector),),
        ).fetchall()
    context = ""
    for edition, heading, content, distance in rows:
        context += f"[{edition} edition | {heading}]\n{content}\n\n"
        print(edition, heading, distance)
    prompt = (
       "Answer using ONLY the extracts below. If they don't contain the answer, say so. "
       "Cite the edition and section you used.\n\n"
       f"{context}Question: {question}"
   )
    response = ollama.chat(
       model="qwen3:4b-instruct",
       messages=[{"role": "user", "content": prompt}],
       options={"temperature": 0},
   )
    print("QWEN:", response["message"]["content"])
    print()




