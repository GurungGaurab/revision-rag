from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.chunking import HybridChunker

options = PdfPipelineOptions(do_ocr=False)

converter = DocumentConverter(
    format_options= {
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=options, 
            backend=PyPdfiumDocumentBackend,
        )
    }
)

doc = converter.convert("handbook_2025.pdf").document
chunker = HybridChunker()
chunks = list(chunker.chunk(dl_doc=doc ))

print("Number of chunks: ", len(chunks)) 

for i, chunk in enumerate(chunks):
    print("==== Chunk Number====", i+1)
    print("Heading: ", chunk.meta.headings)
    print(chunker.contextualize(chunk = chunk))
    print()