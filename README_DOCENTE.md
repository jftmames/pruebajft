# Kit docente — Actividad: Crea tu primer repo en GitHub con Streamlit

**Objetivo de la actividad (30–45 min):**
- Entender repositorio, commit, README, .gitignore, LICENSE, rama principal.
- Generar un esqueleto reproducible y (opcional) crear el repo vía API de GitHub.

## Archivos incluidos
- `streamlit_app.py` — App Streamlit con Modo A (ZIP) y Modo B (API GitHub).
- `requirements.txt` — Dependencias mínimas.
- `README.md` — Guía breve para el alumno.

## Puesta en marcha (local)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Flujo recomendado en clase
1. Modo A (sin API) para toda la clase.
2. Modo B (API) como opcional para quien vaya rápido.
3. Verificar en GitHub que el repo contiene README, .gitignore, LICENSE (si procede) y `streamlit_app.py`.
4. Cerrar con 3 preguntas rápidas (Kahoot/Mentimeter):
   - ¿Qué añade `.gitignore`?
   - ¿Qué hace un commit?
   - ¿Qué debe contener un buen `README`?

## Notas de seguridad
- Si se usa la API: recomendar **tokens de corta duración** y repos privados.
- Recordatorio RGPD: no subir datos personales ni credenciales.

## Rúbrica sugerida (4 puntos)
- Estructura (1 p), Comprensión (1 p), Reproducibilidad (1 p), Higiene (1 p).
