import os
import sys
from pypdf import PdfReader, PdfWriter

def embed_files(input_pdf_path: str, file_paths: list[str], output_pdf_path: str):
    if not os.path.isfile(input_pdf_path):
        raise FileNotFoundError(f"No se encontró el PDF de origen: {input_pdf_path}")
    for path in file_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"No se encontró el archivo a adjuntar: {path}")

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    writer.append_pages_from_reader(reader)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    for path in file_paths:
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        writer.add_attachment(filename, data)
        print(f"  • Adjuntado: {filename}")

    with open(output_pdf_path, "wb") as out_pdf:
        writer.write(out_pdf)
    print(f"\nPDF resultante escrito en: {output_pdf_path}")


if __name__ == "__main__":
    # ---------- CONFIGURA AQUÍ TUS RUTAS ----------
    input_pdf = "input.pdf"         
    attachments = [
        "file1.dwg",                  
        "file2.pdf"                           
    ]
    output_pdf = "output.pdf" 
    # -----------------------------------------------

    try:
        embed_files(input_pdf, attachments, output_pdf)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")
        sys.exit(1)
    print("Proceso completado correctamente.")
