## Modo de Ejecución en la Terminal (Flujo Propuesto)

Una vez implementados los cambios propuestos en `IMPROVEMENTS_PLAN.md`, el flujo de trabajo en la terminal se volverá más modular y flexible, permitiendo un mayor control al usuario.

### Paso 1: Procesar las Imágenes Localmente

Utilizarás el comando `process` para que `AutoEdit Drive` realice todo el trabajo de detección de ROI, recorte, ajustes de color y aplicación de marca de agua. Los resultados se guardarán en una carpeta local de tu elección.

```bash
python -m autoEdit.autoedit process \
  --input "fotos_originales" \
  --output "./fotos_procesadas" \
  --water-mark "ruta/a/tu/logo.png" \
  --log
```

**Explicación:**
*   `fotos_originales`: Es la carpeta que contiene tus imágenes sin editar.
*   `./fotos_procesadas`: Es la carpeta donde `AutoEdit Drive` guardará las imágenes resultantes de todo el procesamiento. Esta carpeta se creará si no existe.
*   `ruta/a/tu/logo.png`: La ruta a tu archivo de marca de agua.
*   `--log`: (Opcional) Guardará un archivo `process_log.txt` en la carpeta de salida con un registro del procesamiento.

Después de ejecutar este comando, tendrás todas tus imágenes procesadas y guardadas en la carpeta `./fotos_procesadas`.

### Paso 2: (Opcional) Revisar las Fotos Procesadas

En este punto, puedes abrir la carpeta `./fotos_procesadas` y revisar los resultados. Puedes:
*   Visualizar las imágenes.
*   Eliminar las que no te gusten.
*   Incluso abrir alguna imagen con tu editor favorito para hacer ajustes manuales finos si lo deseas.

Este paso te da un control completo antes de que las imágenes se suban a la nube.

### Paso 3: Subir las Imágenes Procesadas a Google Drive

Una vez que estés satisfecho con las imágenes en tu carpeta local, utilizarás el comando `upload` para subirlas a Google Drive. Este comando es "inteligente" y solo subirá las fotos que aún no estén en la carpeta de destino de Drive.

```bash
python -m autoEdit.autoedit upload \
  --source "./fotos_procesadas" \
  --drive-folder "ID_DE_TU_CARPETA_EN_GOOGLE_DRIVE" \
  --log
```

**Explicación:**
*   `./fotos_procesadas`: Es la carpeta local que contiene las imágenes que quieres subir.
*   `ID_DE_TU_CARPETA_EN_GOOGLE_DRIVE`: Es el identificador único de la carpeta en Google Drive donde deseas que se suban las imágenes.
*   `--log`: (Opcional) Guardará un archivo `upload_log.txt` en la carpeta de origen con un registro de la subida.

---

Este flujo desacoplado te proporciona un control mucho mayor sobre el proceso, mejorando la flexibilidad y la resiliencia ante errores de red o cualquier necesidad de revisión manual.
