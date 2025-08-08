#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
embed_files_ui.py

Aplicación PyQt5 para:
  1) Cargar un PDF base
  2) Seleccionar archivos para incrustar
  3) Elegir carpeta destino
  4) Ejecutar incrustación y mostrar estado

Interfaz definida en 'dialog.ui' (Qt Designer).

Dependencias:
  pip install PyQt5 pypdf
"""
import os
import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from pypdf import PdfReader, PdfWriter

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

UI_FILE = resource_path("gui_adjuntar.ui")

class EmbedFilesDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        # Variables internas
        self.selected_files = []
        # Conectar señales
        self.pushButton_cargar_pdf_base.clicked.connect(self.load_base_pdf)
        self.pushButton_seleccionar_archivos.clicked.connect(self.select_files)
        self.pushButton_elegir_Carpeta_destino.clicked.connect(self.choose_output_folder)
        self.pushButton_ejecutar_programa.clicked.connect(self.execute_embed)
        # Hacer QLabel clickeable
        self.label.mousePressEvent = self.show_message

    def load_base_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF base", "", "PDF Files (*.pdf)")
        if path:
            self.lineEdit_cargar_pdf_base.setText(path)

    def select_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos a incrustar", "", "All Files (*)")
        if paths:
            self.selected_files = paths
            self.listWidget_archivos_seleccionados.clear()
            self.listWidget_archivos_seleccionados.addItems(paths)

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta destino")
        if folder:
            self.lineEdit_carpeta_destino_elegida.setText(folder)

    def execute_embed(self):
        input_pdf = self.lineEdit_cargar_pdf_base.text().strip()
        output_dir = self.lineEdit_carpeta_destino_elegida.text().strip()
        # Validaciones
        if not os.path.isfile(input_pdf):
            QMessageBox.critical(self, "Error", f"PDF base no encontrado:\n{input_pdf}")
            return
        if not self.selected_files:
            QMessageBox.warning(self, "Atención", "No se seleccionaron archivos para incrustar.")
            return
        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Error", f"Carpeta destino no válida:\n{output_dir}")
            return
        # Construir ruta de salida
        base = os.path.splitext(os.path.basename(input_pdf))[0]
        output_pdf = os.path.join(output_dir, f"{base}_con_adjuntos.pdf")
        try:
            self.embed_files(input_pdf, self.selected_files, output_pdf)
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))
            return
        # Éxito
        self.lineEdit_indicar_trabajo_terminado.setText("¡Listo!")
        QMessageBox.information(self, "Completado", f"PDF generado:\n{output_pdf}")

    @staticmethod
    def embed_files(input_pdf_path: str, file_paths: list, output_pdf_path: str):
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        if reader.metadata:
            writer.add_metadata(reader.metadata)
        for path in file_paths:
            name = os.path.basename(path)
            with open(path, "rb") as f:
                data = f.read()
            writer.add_attachment(name, data)
        with open(output_pdf_path, "wb") as out:
            writer.write(out)

    def show_message(self, event):
        QMessageBox.information(self, "Mensaje", "Desarrollado por bmalpartida")

def main():
    app = QApplication(sys.argv)
    dlg = EmbedFilesDialog()
    dlg.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

