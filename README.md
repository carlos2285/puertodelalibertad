
# Dashboard Paramapa

Este repositorio contiene un tablero interactivo construido con **Streamlit** + **Folium** que
permite explorar el dataset `paramapa.xlsx` mediante filtros, mapa web y gráficas dinámicas.

## Estructura

```
.
├─ app.py               # Código principal de Streamlit
├─ requirements.txt     # Dependencias para instalar en Streamlit Cloud o local
└─ data/
    └─ paramapa.xlsx    # Base de datos (puedes reemplazarla por una versión actualizada)
```

## Ejecución local

```bash
# crea entorno
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# corre la app
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Haz *fork* o clona este repo y súbelo a tu cuenta de GitHub.
2. Entra a https://streamlit.io/cloud → **New app** → selecciona el repositorio.
3. Rama: `main`, archivo principal: `app.py`.
4. Click **Deploy** y comparte la URL generada.

¡Listo!
