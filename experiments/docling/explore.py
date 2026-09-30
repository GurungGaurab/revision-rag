from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend


options = PdfPipelineOptions(do_ocr=False)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF : PdfFormatOption(
            pipeline_options=options, 
            backend= PyPdfiumDocumentBackend
        )

    }
)

doc = converter.convert("handbook_2025.pdf").document

for item, level in doc.iterate_items():
    kind = type(item).__name__
    text = getattr(item, "text", "")
    print(level, kind, text)
    if kind == "SectionHeaderItem":
        print("   heading level:", item.level)

    print()