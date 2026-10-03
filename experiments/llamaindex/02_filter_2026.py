from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend


from llama_index.core import VectorStoreIndex, Settings
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import MetadataMode
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

# 1. Models LlamaIndex should use everywhere
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Ollama(model="qwen3:4b-instruct", request_timeout=300.0, temperature=0)

# 2. PDF paths (the PDFs live in experiments/docling/)
pdf_2025 = Path(__file__).parent.parent / "docling" / "handbook_2025.pdf"
pdf_2026 = Path(__file__).parent.parent / "docling" / "handbook_2026.pdf"

# 3. Docling converter: OCR off + pypdfium2 reader (same as store_new_chunks.py)
options = PdfPipelineOptions(do_ocr=False)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=options,
            backend=PyPdfiumDocumentBackend,
        )
    }
)

# 4. Read both PDFs -> 2 documents
reader = DoclingReader(export_type=DoclingReader.ExportType.JSON, doc_converter=converter)
documents = reader.load_data([pdf_2025, pdf_2026])
print("documents:", len(documents))

# 5. Split into nodes (chunks)
parser = DoclingNodeParser()
nodes = parser.get_nodes_from_documents(documents)
print("nodes:", len(nodes))

for node in nodes:
    file_name = node.metadata["origin"]["filename"]
    name = file_name.replace(".pdf", "").split("_")[-1]
    node.metadata["edition"] = int(name)


questions = [
       "What is the late submission penalty?",
       "How many days do I have to withdraw without penalty?",
       "How much is the BSc Computer Science fee?",
       "When is the first-semester fee due?",
       "What was the late penalty in 2025?",
   ]

# 6. Embed + store in memory, then ask
index = VectorStoreIndex(nodes)   
filters = MetadataFilters(filters=[
    MetadataFilter(key="edition", value=2026, operator=FilterOperator.EQ)
   ])
query_engine = index.as_query_engine(similarity_top_k=3, filters = filters)

for question in questions: 
    print(question)
    response = query_engine.query(question)
    print("QWEN: ", response)
    for node in response.source_nodes:
        print(round(node.score, 4), node.metadata["edition"], node.metadata.get("headings"))

    print()


