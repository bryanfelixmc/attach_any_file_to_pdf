import os
import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox, QListWidget
from pypdf import PdfReader, PdfWriter
import fitz

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

UI_FILE = resource_path("gui_adjuntar.ui")

from PyQt5.QtWidgets import QListWidget

class FileDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.selected_files = set()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        new_files = False
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                if path not in self.selected_files:
                    self.selected_files.add(path)
                    new_files = True
        if new_files:
            self.clear()
            self.addItems(sorted(self.selected_files))


class EmbedFilesDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        # Variables internas
        self.selected_files = set()
        # Conectar señales
        self.pushButton_cargar_pdf_base.clicked.connect(self.load_base_pdf)
        self.pushButton_seleccionar_archivos.clicked.connect(self.select_files)
        self.pushButton_clear1.clicked.connect(self.clear1)

        self.pushButton_elegir_Carpeta_destino.clicked.connect(self.choose_output_folder)
        self.pushButton_incrustar.clicked.connect(self.execute_embed)
        self.pushButton_eliminar_incrustados.clicked.connect(self.execute_desincrustar)
        # Hacer QLabel clickeable
        self.label.mousePressEvent = self.show_message


    def load_base_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF base", "", "PDF Files (*.pdf)")
        if path:
            self.lineEdit_cargar_pdf_base.setText(path)

    def select_files(self):
        
        paths, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos a incrustar", "", "All Files (*)")
        if paths:
            self.selected_files.update(paths)
            self.listWidget_archivos_seleccionados.clear()
            self.listWidget_archivos_seleccionados.addItems(self.selected_files)

    def clear1(self):
        self.selected_files.clear()
        self.listWidget_archivos_seleccionados.clear()

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
        self.lineEdit_indicar_incrustado_ok.setText("¡Listo!")
        QMessageBox.information(self, "Completado", f"PDF generado:\n{output_pdf}")


    def execute_desincrustar(self):
        input_pdf = self.lineEdit_cargar_pdf_base.text().strip()
        output_dir = self.lineEdit_carpeta_destino_elegida.text().strip()

        # Validaciones
        if not os.path.isfile(input_pdf):
            QMessageBox.critical(self, "Error", f"PDF base no encontrado:\n{input_pdf}")
            return
        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Error", f"Carpeta destino no válida:\n{output_dir}")
            return

        # Construir ruta de salida
        base = os.path.splitext(os.path.basename(input_pdf))[0]
        output_pdf = os.path.join(output_dir, f"{base}_sin_adjuntos.pdf")

        try:
            eliminados = self.remove_all_attachments(input_pdf, output_pdf)
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))
            return

        # Éxito
        self.lineEdit_indicar_desincrustado_ok.setText("¡Listo!")
        if eliminados:
            QMessageBox.information(
                self,
                "Completado",
                f"Se eliminaron {len(eliminados)} adjuntos:\n" +
                "\n".join(eliminados) +
                f"\n\nPDF generado en:\n{output_pdf}"
            )
        else:
            QMessageBox.information(
                self,
                "Completado",
                f"No se encontraron adjuntos.\nPDF generado en:\n{output_pdf}"
            )


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

    # --- función para eliminar adjuntos ---
    @staticmethod
    def remove_all_attachments(input_path: str, output_path: str):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"No se encontró el archivo: {input_path}")

        removed_files = []

        with fitz.open(input_path) as doc:
            attachments = doc.embfile_names()
            if attachments:
                for name in attachments:
                    doc.embfile_del(name)
                    removed_files.append(name)
            doc.save(output_path, garbage=4, deflate=True)

        return removed_files



def main():
    app = QApplication(sys.argv)
    dlg = EmbedFilesDialog()
    dlg.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
