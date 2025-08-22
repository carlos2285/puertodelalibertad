
# Paramapa Dashboard v4

Este repositorio incluye:
* **data/paramapa_clean.csv** — versión depurada del Excel (se eliminaron 20 columnas con >90 % de valores nulos).
* **data/limites.* ** — shapefile con las áreas de intervención (renombrado).
* **app.py** — tablero Streamlit con selector dinámico de cualquier variable.

## Cómo levantar

```bash
# local
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud
1. Haz **push** de todo el repo a GitHub.
2. En https://streamlit.io/cloud → **New app** → elige repo, rama y archivo `app.py`.
3. ¡Listo! URL pública en ~1 min.
