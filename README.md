# EDD Utils

Script y funciones de utilidad para la evaluación de tareas del curso.

Cumple el mismo objetivo que `Technical-Guide`, pero se adapta mejor a los nuevos cambios de GitHub (con GitHub Classroom), y usa código para la configuración en vez de archivos de configuración.

## Funciones

- Librería `edd_utils` en Python

  - `gekito`: El “generador de tests chiquito”, un micro framework para generar tests cases de forma ordenada.
  - `collector`: Utilidades para recolectar entregas, pensado en Google Colab, y subir cada entrega a una carpeta en Google Drive para ser revisada junto a la asignación, fecha de entrega, y más, en Google Sheets.
  - `run` y `tests`: Para correr tests de una entrega en particular.
  - `grade`: Para correr todas las entregas y generar un archivo TSV con las notas.

- `Makefile` actualizado

  - El estándar para compilar código en el curso.
  - Con versión más estándar de C (`-pedantic-errors`) y con sanitizador de memoria (`-fsanitize=address`).
  - Se puede añadir carpeta de binarios o librerías en común, si se requiere adaptar para otras necesidades.

## Instalación

```sh
python -m venv .venv
source .venv/bin/activate
git clone git@github.com:IIC2133-PUC/edd_utils.git
(cd edd_utils && pip install .)
```

## Ejemplos

- [Grader para obtener las notas](./examples/grader.py)
- [Código para correr alumno en particular](./examples/student.py.py)
