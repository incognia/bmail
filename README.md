# bmail
Repositorio de trabajo para extraer, organizar y reutilizar ejemplos del libro *Business Email: Language, Structure and Style*.

## Objetivo
Construir una base de ejemplos de correos de negocio en inglés para:
- crear plantillas reutilizables,
- alimentar el *skill* `bmail`,
- y tener una referencia rápida por asunto y página.

## Fuente principal
- Obra bibliográfica (desde contenido visible de la portada): Richards, David. *Business Email: Language, Structure and Style*. Published by: The Language Key Ltd. Disponible en: https://www.languagekey.com/business_email.pdf
- Ficha bibliográfica local: `docs/README.md`
- Archivo PDF local de trabajo: `docs/business_email.pdf`
- Total de páginas del PDF: 108

## Atribución de la obra fuente
- Título de la obra original: *Business Email: Language, Structure and Style*.
- Autor visible en portada: **David Richards**.
- Crédito editorial visible en el PDF: **Published by: The Language Key Ltd**.
- Fuente oficial de acceso público: https://www.languagekey.com/business_email.pdf
- Este repositorio no reclama autoría sobre la obra original; los ejemplos se organizan y referencian con atribución explícita a la fuente.

## Preparar entorno Python (venv)
Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## *Scripts* de extracción
Los *scripts* viven en `scripts/`:
- `scripts/extract_emails.py` → extrae/regenera `example_*.txt` desde el PDF.
- `scripts/rebuild_index.py` → reconstruye el índice desde los `.txt` ya existentes.

### 1) Extraer correos desde el PDF
```bash
python scripts/extract_emails.py \
  --pdf docs/business_email.pdf \
  --output-dir templates \
  --page-offset -1
```

Notas:
- `--page-offset -1` mantiene la convención portada=`000`.
- Por defecto limpia `templates/example_*.txt` antes de regenerar.

### 2) Reconstruir solo el índice
```bash
python scripts/rebuild_index.py --templates-dir templates
```

## Contenido del libro (tabla de contenidos)
Secciones principales detectadas en el PDF:
- *Opening and Referencing*
- *Making Enquiries*
- *Informing and Notifying*
- *Replies to Requests*
- *Clarifying and Confirming*
- *Giving Advice and Making Suggestions*
- *Making Arrangements*
- *Addressing Problems and Mistakes*
- *Confirming Orders and Prices*
- *Closing*
- *General Business Writing Skills*
  - *Using the Right Tone*
  - *Developing a Good Writing Style (1, 2, 3)*
  - *Writing in Plain English*

## *Dataset* extraído en este repositorio
La carpeta `templates/` contiene ejemplos en texto plano derivados de la obra bibliográfica descrita en `docs/README.md`.

### Convención de nombres
Cada archivo usa este formato:
- `example_###_{subject}.txt`

Donde:
- `###` es el número de página ajustado con offset `-1` (portada = `000`),
- `{subject}` es el asunto normalizado en *slug*.

Ejemplos:
- `templates/example_004_order-ref-no-856.txt`
- `templates/example_099_request-for-financial-aid.txt`
- `templates/example_100_contract-with-jobsen-ltd.txt`
- `templates/example_101_staff-punctuality.txt`

### Estructura de cada ejemplo
Cada `.txt` incluye:
- `Source`
- `Page`
- `From`
- `To`
- `Subject`
- `FromToStatus` (`extracted` o `n_a`)
- cuerpo del correo

## Índice consolidado
Archivo:
- `templates/business_email_examples_index.txt`

Estado actual del índice:
- *Total examples*: 65
- *With From/To*: 31
- *With From/To as N/A*: 34

## Notas
- Si el ejemplo del PDF no trae encabezados explícitos, se registra `From: N/A` y `To: N/A`.
- La numeración usada en `Page` y en el nombre del archivo ya contempla la portada como página `000`.
- Los derechos de la obra fuente corresponden a su titular original.

## Referencias cruzadas con el repositorio de reglas
- Ruta local del repositorio de reglas: `~/rules/`
- Remoto del repositorio de reglas: `git@github.com:incognia/rules.git`
- *Skill* `bmail`: `~/rules/.agents/skills/bmail/SKILL.md`
- CoT de `bmail`: `~/rules/cot/bmail.md`
- Ruleset de `bmail`: `~/rules/rulesets/BMAIL.md`
- Plantillas de `bmail`: `~/rules/templates/bmail/`

### Ejemplo de plantilla en `~/rules/templates/bmail/`
Archivo: `~/rules/templates/bmail/enquiry_template.html`

Elementos clave de la plantilla:
- Placeholders: `{SUBJECT}`, `{RECIPIENT_NAME}`, `{ENQUIRY_TOPIC}`, `{REQUESTED_INFORMATION}`, `{DEADLINE}`.
- Frases de apoyo incluidas en el cuerpo:
  - `I am writing to enquire about {ENQUIRY_TOPIC}.`
  - `Could you please send me {REQUESTED_INFORMATION}?`
  - `Please could you confirm this by {DEADLINE}?`

### Ejemplos de uso del *skill* `bmail`
Comandos de ejemplo:
- `/bmail enquiry Request for Catalogue`
- `/bmail informing-good Brochure Dispatch Confirmation`
- `/bmail apology-delay Delay in Delivery - Ref 64783`

Comportamiento esperado:
- Selecciona plantilla según la clave (`opening`, `enquiry`, `informing-good`, `informing-bad`, `apology-delay`, `order-status`, `meeting-request`).
- Solicita campos faltantes.
- Genera un HTML final y lo guarda como `YYYY-MM-DD-bmail-{template-key}-{subject-slug}.html`.

## Próximo paso sugerido
Copiar/migrar estos ejemplos al repositorio de reglas para usarlos como fuente directa en `~/rules/templates/bmail/` y en el *skill* `bmail`.

---

*Este proyecto fue elaborado por Rodrigo Álvarez (@incognia) y se distribuye bajo la licencia GPLv3. Para más detalles, consulta el archivo LICENSE.*

*Copyright © 2026, Rodrigo Ernesto Álvarez Aguilera. Este es software libre bajo los términos de la GNU General Public License v3.*
