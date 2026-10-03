import re
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

CURRENT_EDITION = 2026


def pick_edition(question):
    """Return the year mentioned in the question, or the current edition."""
    match = re.search(r"\b(20\d{2})\b", question)
    if match:
        return int(match.group(1))
    return CURRENT_EDITION


# 1. Models
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = Ollama(model="qwen3:4b-instruct", request_timeout=300.0, temperature=0)

# 2. PDF paths
pdf_2025 = Path(__file__).parent.parent / "docling" / "handbook_2025.pdf"
pdf_2026 = Path(__file__).parent.parent / "docling" / "handbook_2026.pdf"

# 3. Docling converter: OCR off + pypdfium2
options = PdfPipelineOptions(do_ocr=False)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=options,
            backend=PyPdfiumDocumentBackend,
        )
    }
)

# 4. Read -> nodes -> edition label
reader = DoclingReader(export_type=DoclingReader.ExportType.JSON, doc_converter=converter)
documents = reader.load_data([pdf_2025, pdf_2026])
nodes = DoclingNodeParser().get_nodes_from_documents(documents)

for node in nodes:
    file_name = node.metadata["origin"]["filename"]
    year = file_name.replace(".pdf", "").split("_")[-1]
    node.metadata["edition"] = int(year)

print("nodes:", len(nodes))

# 5. Index once (outside the loop)
index = VectorStoreIndex(nodes)

questions = [
    "What is the late submission penalty?",
    "How many days do I have to withdraw without penalty?",
    "How much is the BSc Computer Science fee?",
    "When is the first-semester fee due?",
    "What was the late penalty in 2025?",
]

# 6. Per question: choose edition -> filter -> search -> answer
for question in questions:
    edition = pick_edition(question)
    print(question)
    print("edition used:", edition)

    filters = MetadataFilters(filters=[
        MetadataFilter(key="edition", value=edition, operator=FilterOperator.EQ)
    ])
    query_engine = index.as_query_engine(similarity_top_k=3, filters=filters)
    response = query_engine.query(question)
    print("QWEN:", response)

    for node in response.source_nodes:
        print(round(node.score, 4), node.metadata["edition"], node.metadata.get("headings"))

    print()