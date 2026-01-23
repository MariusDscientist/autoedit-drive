import argparse
from .pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Auto edit images and upload to drive")
    parser.add_argument("--input", required=True, help= " Carpeta local con imagenes")
    parser.add_argument("--output", required=True, help= " Carpeta local temporal de salida")
    parser.add_argument("--drive-folder", required=True, help= " Carpeta destino de google Drive")
    parser.add_argument("--water-mark", required=True, help="RUta a la marca de agua")
    parser.add_argument("--preview", action="store_true", help= "Mostrar preview de la primer imagen")
    parser.add_argument("--log", action="store_true", help= " Guardar log de procesamiento")

    args = parser.parse_args()

    run_pipeline(
        input_folder = args.input,
        output_folder = args.output,
        drive_folder = args.drive_folder,
        watermark_path = args.water_mark,
        preview = args.preview,
        log = args.log
    )
if __name__ == "__main__":
    main()