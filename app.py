
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from streamlit_folium import st_folium
import folium
import plotly.express as px
import os

DATA_PATH = os.path.join('data', 'paramapa.xlsx')

@st.cache_resource
def load_data():
    df = pd.read_excel(DATA_PATH, sheet_name=0)
    df = df.dropna(subset=['p002__Latitude', 'p002__Longitude'])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['p002__Longitude'], df['p002__Latitude'])],
        crs='EPSG:4326'
    )
    return gdf

gdf = load_data()

st.set_page_config(page_title='Dashboard Paramapa', layout='wide')
st.title('Dashboard Paramapa')

# Sidebar filters
st.sidebar.header('Filtros')
encs = sorted(gdf['enc'].dropna().unique())
sel_enc = st.sidebar.multiselect('Tipo de encuestador', encs, default=encs)

bloques = sorted(gdf['bloque'].unique())
sel_bloc = st.sidebar.multiselect('Bloque', bloques, default=bloques)

mask = gdf['enc'].isin(sel_enc) & gdf['bloque'].isin(sel_bloc)
sub = gdf.loc[mask]

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric('Registros', len(sub))
col2.metric('Encuestadores', sub['enc'].nunique())
col3.metric('Bloques', sub['bloque'].nunique())

# Map
st.subheader('Mapa interactivo')
m = folium.Map(
    location=[sub.geometry.y.mean(), sub.geometry.x.mean()],
    zoom_start=15,
    tiles='CartoDB positron'
)

color_map = {'hogar': '#1f78b4', 'negocio': '#33a02c', 'mixto': '#ff7f00'}

for _, r in sub.iterrows():
    folium.CircleMarker(
        [r.geometry.y, r.geometry.x],
        radius=4,
        tooltip=f"Bloque {r['bloque']} | {r['enc']}",
        color=color_map.get(str(r.get('enc')).lower(), '#7570b3'),
        fill=True, fill_opacity=0.8
    ).add_to(m)

st_folium(m, height=600, use_container_width=True)

# Bar chart
st.subheader('Distribución por bloque')
counts = (
    sub.groupby('bloque')
       .size()
       .reset_index(name='n')
       .sort_values('n', ascending=False)
)
fig = px.bar(counts, x='bloque', y='n',
             labels={'bloque': 'Bloque', 'n': 'Observaciones'},
             height=400)
st.plotly_chart(fig, use_container_width=True)

st.caption('© 2025 – Dashboard Paramapa • Streamlit + Folium')
