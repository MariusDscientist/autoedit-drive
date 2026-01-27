import argparse
from .pipeline import run_processing_pipeline, run_upload_pipeline # Updated import

def main():
    parser = argparse.ArgumentParser(description="AutoEdit Drive: Procesamiento y carga de imágenes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Comando 'process' ---
    parser_process = subparsers.add_parser("process", help="Procesa las imágenes localmente.")
    parser_process.add_argument("--input", required=True, help="Carpeta de entrada.")
    parser_process.add_argument("--output", required=True, help="Carpeta de salida.")
    parser_process.add_argument("--water-mark", required=True, help="Ruta a la marca de agua.")
    parser_process.add_argument("--preview", action="store_true", help="Procesar solo la primera imagen y mostrarla.")
    parser_process.add_argument("--log", action="store_true", help="Guardar log de procesamiento.")

    # --- Comando 'upload' ---
    parser_upload = subparsers.add_parser("upload", help="Sube las imágenes procesadas a Google Drive.")
    parser_upload.add_argument("--source", required=True, help="Carpeta local con archivos a subir.")
    parser_upload.add_argument("--drive-folder", required=True, help="ID de la carpeta de destino en Google Drive.")
    parser_upload.add_argument("--log", action="store_true", help="Guardar log de subida.")

    args = parser.parse_args()

    if args.command == "process":
        run_processing_pipeline(
            input_folder = args.input,
            output_folder = args.output,
            watermark_path = args.water_mark,
            preview = args.preview,
            log = args.log
        )
    elif args.command == "upload":
        run_upload_pipeline(
            source_folder = args.source,
            drive_folder_id = args.drive_folder,
            log = args.log
        )

if __name__ == "__main__":
    main()