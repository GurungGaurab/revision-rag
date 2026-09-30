from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker 
from sentence_transformers import SentenceTransformer
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat

def find_chunk_text(chunks, heading):
    for chunk in chunks:
        if chunk.meta.headings == [heading]:
            return chunker.contextualize(chunk = chunk)
    return None


options = PdfPipelineOptions(do_ocr=False)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF : PdfFormatOption(
        pipeline_options=options, 
        backend=PyPdfiumDocumentBackend,
    )
    }

)
doc_2025 = converter.convert("handbook_2025.pdf").document
doc_2026 = converter.convert("handbook_2026.pdf").document 

chunker = HybridChunker()
chunks_2025 = list(chunker.chunk(dl_doc=doc_2025))
chunks_2026 = list(chunker.chunk(dl_doc=doc_2026))

print("Number of chunks 2025: ", len(chunks_2025))
print("Number of chunks 2026 : ", len(chunks_2026))

text_2025 = find_chunk_text(chunks_2025, '3.1 Late submission')
text_2026 = find_chunk_text(chunks_2026, '3.1 Late submission')

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentence = [text_2025, text_2026]

vector = model.encode(sentence, normalize_embeddings=True)
scores = model.similarity(vector, vector)
print(scores)

question = "What is the late submission penalty?"
question_vector = model.encode([question], normalize_embeddings=True)

q_scores = model.similarity(question_vector, vector)
print(q_scores)
