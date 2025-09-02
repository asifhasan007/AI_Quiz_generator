import fitz 
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_stream):
    try:
        logger.info("-> Opening PDF from stream...")
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        logger.info("---> PDF text extraction successful.")
        return full_text
    except Exception as e:
        logger.error(f"Error processing PDF file stream: {e}", exc_info=True)
        return ""
