# Registro de cambios

## [2026-06-22] - Referencias bibliográficas y trazabilidad de fuentes

- build: agregué el archivo `LICENSE` con el texto oficial de GNU GPLv3 para licenciamiento personal del proyecto.
- docs: añadí al `README.md` el pie de licencia GPLv3 y la línea de copyright 2026 con atribución personal.
- docs: incorporé referencias cruzadas al repositorio `rules`, incluyendo rutas local/remota y vínculos a `SKILL`, CoT y ruleset de `bmail`.
- docs: añadí en `README.md` un ejemplo concreto de plantilla en `~/rules/templates/bmail/` y ejemplos de uso del skill `bmail`.
- docs: prioricé la cita bibliográfica del libro como fuente principal en la documentación del repositorio.
- chore: agregué `docs/business_email.pdf` a `.gitignore` para excluir el insumo local del control de versiones.
- refactor: actualicé los scripts de extracción e índice para emitir `Source` con referencia bibliográfica y `SourceFile` como trazabilidad técnica.
- docs: ajusté los encabezados del dataset generado en `templates/example_*.txt` y `templates/business_email_examples_index.txt` para mantener consistencia con la nueva convención de fuente.
