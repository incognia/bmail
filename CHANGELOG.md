# Registro de cambios

## [2026-06-22] - Referencias bibliográficas y trazabilidad de fuentes

- docs: compacté `README.md` al fusionar secciones redundantes de fuente y atribución en un bloque único.
- docs: moví la tabla de contenidos detallada del libro a `docs/README.md` y dejé en `README.md` un resumen con referencia al detalle.
- docs: corregí la atribución bibliográfica para tomar el autor visible en portada (`David Richards`) y reflejarlo en `README.md` y `docs/README.md`.
- refactor: sincronicé la referencia `Source` con autor y editor en `scripts/extract_emails.py`, `scripts/rebuild_index.py`, `templates/example_*.txt` y `templates/business_email_examples_index.txt`.
- feat: agregué `scripts/discover_site_pdfs.py` para descubrir PDFs del sitio, emitir salida JSON y descargar los archivos encontrados.
- chore: añadí `downloads/` a `.gitignore` para excluir artefactos descargados del control de versiones.
- docs: documenté la URL oficial de descarga `https://www.languagekey.com/business_email.pdf` en `README.md` y `docs/README.md`.
- refactor: actualicé los scripts de extracción e índice para usar la URL oficial del PDF en la referencia bibliográfica generada.
- docs: corregí las referencias `Source` del dataset (`templates/example_*.txt` e índice consolidado) para apuntar a la URL oficial de descarga.
- build: agregué el archivo `LICENSE` con el texto oficial de GNU GPLv3 para licenciamiento personal del proyecto.
- docs: añadí al `README.md` el pie de licencia GPLv3 y la línea de copyright 2026 con atribución personal.
- docs: incorporé referencias cruzadas al repositorio `rules`, incluyendo rutas local/remota y vínculos a `SKILL`, CoT y ruleset de `bmail`.
- docs: añadí en `README.md` un ejemplo concreto de plantilla en `~/rules/templates/bmail/` y ejemplos de uso del skill `bmail`.
- docs: prioricé la cita bibliográfica del libro como fuente principal en la documentación del repositorio.
- chore: agregué `docs/business_email.pdf` a `.gitignore` para excluir el insumo local del control de versiones.
- refactor: actualicé los scripts de extracción e índice para emitir `Source` con referencia bibliográfica y `SourceFile` como trazabilidad técnica.
- docs: ajusté los encabezados del dataset generado en `templates/example_*.txt` y `templates/business_email_examples_index.txt` para mantener consistencia con la nueva convención de fuente.
