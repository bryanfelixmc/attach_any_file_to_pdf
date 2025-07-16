#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
embed_files.py

Script para insertar uno o varios archivos dentro de un PDF sin usar argumentos de línea de comandos.
Define directamente las rutas en las variables del bloque principal.
Dependencias: pip install pypdf
"""

import os
import sys
from pypdf import PdfReader, PdfWriter

def embed_files(input_pdf_path: str, file_paths: list[str], output_pdf_path: str):
    # Verificar existencia de archivos
    if not os.path.isfile(input_pdf_path):
        raise FileNotFoundError(f"No se encontró el PDF de origen: {input_pdf_path}")
    for path in file_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"No se encontró el archivo a adjuntar: {path}")

    # 1. Leer el PDF base
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # 2. Copiar todas las páginas
    writer.append_pages_from_reader(reader)

    # 3. (Opcional) conservar metadata
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # 4. Adjuntar cada archivo
    for path in file_paths:
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        writer.add_attachment(filename, data)
        print(f"  • Adjuntado: {filename}")

    # 5. Escribir el PDF de salida
    with open(output_pdf_path, "wb") as out_pdf:
        writer.write(out_pdf)
    print(f"\nPDF resultante escrito en: {output_pdf_path}")


if __name__ == "__main__":
    # ---------- CONFIGURA AQUÍ TUS RUTAS ----------
    input_pdf = "NAZ-004-04-26165-0000-17-38-0002_0.pdf"         # PDF de origen
    attachments = [
        "NAZ-004-04-26165-0000-17-38-0002.dwg",                  # Archivo 1 a adjuntar
        "CSL-250202-2-1-06-003.pdf",                              # Archivo 2 a adjuntar
        # Añade más rutas según tus necesidades
    ]
    output_pdf = "salida_con_adjuntos.pdf"                         # Nombre del PDF resultante
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
