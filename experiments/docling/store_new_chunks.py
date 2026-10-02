from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker 
from sentence_transformers import SentenceTransformer
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector
from pathlib import Path


conn = psycopg.connect("dbname=revrag", autocommit=True)
register_vector(conn)

count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
print("Rows in Chunks: ", count)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
HERE_2025 = Path(__file__).parent / "handbook_2025.pdf"
HERE_2026 = Path(__file__).parent / "handbook_2026.pdf"



def find_chunk_test(chunks, heading): #Find the chunnked test
    for chunk in chunks:
        if chunk.meta.headings == [heading]:
            return chunker.contextualize(chunk = chunk)
    return None

options = PdfPipelineOptions(do_ocr=False) #turn OCR off for the default pdf reader for docling 

converter = DocumentConverter( #options for docling converter 
    format_options= {
        InputFormat.PDF : PdfFormatOption(
            pipeline_options= options, 
            backend = PyPdfiumDocumentBackend,
        )
    }
)

chunker = HybridChunker() #import chunker from docling 

doc_2025 = converter.convert(HERE_2025).document #convert the pdf to python readable doc 
doc_2026 = converter.convert(HERE_2026).document

chunk_2025 = list(chunker.chunk(dl_doc = doc_2025))
chunk_2026 = list(chunker.chunk(dl_doc = doc_2026))

test_2025 = find_chunk_test(chunk_2025, '3.1 Late submission') #specific chunk test 
test_2026 = find_chunk_test(chunk_2026, '3.1 Late submission')

model = SentenceTransformer(MODEL_NAME) #importing senter transformer that will find simialirities 

sentence = [test_2025, test_2026] 

vector = model.encode(sentence,normalize_embeddings=True)
scores = model.similarity(vector, vector) #comparing the cosine calculations against the 2 vectors 
print(scores)

question = "What is the late submission penalty?"
q_test = model.encode([question], normalize_embeddings=True)

q_scores = model.similarity(vector, q_test)
print(q_scores)


for edition, pdf in [(2025, HERE_2025), (2026, HERE_2026)]:
    doc = converter.convert(pdf).document 
    chunks = list(chunker.chunk(dl_doc = doc))
    for chunk in chunks:
        text = chunker.contextualize(chunk = chunk)
        heading = chunk.meta.headings[0] if chunk.meta.headings else None
        vec = model.encode([text], normalize_embeddings=True)[0]
        conn.execute(
            "INSERT INTO chunks (edition, heading, content, embedding_model, embedding) "
            "VALUES (%s, %s, %s, %s, %s)",
            (edition, heading, text, MODEL_NAME, Vector(vec)),
        )

count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
print("Rows after loading: ", count)





