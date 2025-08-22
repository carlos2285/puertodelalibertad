
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from streamlit_folium import st_folium
import folium
import plotly.express as px
import os

# ---- CONFIG ----
POINT_FILE = os.path.join('data','paramapa.xlsx')
SHAPE_FILE = os.path.join('data','limites.shp')
DWELLING_COL = 'Uso'            # tipo de uso de parcela (ajústalo si quieres)
ENC_COL = 'enc'                 # columna en Excel; ajusta si distinta
POLY_NAME_COL = 'SECTOR'        # nombre del sector dentro del shapefile

st.set_page_config(page_title='Dashboard Paramapa', layout='wide')

# ---- LOAD DATA ----
@st.cache_resource
def load_points():
    df = pd.read_excel(POINT_FILE, sheet_name=0)
    df = df.dropna(subset=['p002__Latitude','p002__Longitude'])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['p002__Longitude'], df['p002__Latitude'])],
        crs='EPSG:4326'
    )
    return gdf

@st.cache_resource
def load_polygons():
    if os.path.exists(SHAPE_FILE):
        poly = gpd.read_file(SHAPE_FILE).to_crs('EPSG:4326')
        return poly
    return None

gdf = load_points()
polygons = load_polygons()

st.title('Dashboard Paramapa')

# ---- SIDEBAR FILTERS ----
st.sidebar.header('Filtros')

# Dwelling type filter
if DWELLING_COL in gdf.columns:
    dw_vals = sorted(gdf[DWELLING_COL].dropna().unique())
    sel_dw = st.sidebar.multiselect('Tipo de uso/vivienda', dw_vals, default=dw_vals)
else:
    sel_dw = gdf[DWELLING_COL].unique() if DWELLING_COL in gdf.columns else []

# enc filter (if exists)
if ENC_COL in gdf.columns:
    enc_vals = sorted(gdf[ENC_COL].dropna().unique())
    sel_enc = st.sidebar.multiselect('Categoría hogar/negocio', enc_vals, default=enc_vals)
else:
    sel_enc = []

# polygon filter
if polygons is not None and POLY_NAME_COL in polygons.columns:
    area_vals = sorted(polygons[POLY_NAME_COL].unique())
    sel_area = st.sidebar.multiselect('Área geográfica', area_vals, default=area_vals)
    polys_sel = polygons[polygons[POLY_NAME_COL].isin(sel_area)]
else:
    polys_sel = None

# ---- FILTER DATA ----
sub = gdf.copy()
if DWELLING_COL in gdf.columns:
    sub = sub[sub[DWELLING_COL].isin(sel_dw)]
if ENC_COL in gdf.columns:
    sub = sub[sub[ENC_COL].isin(sel_enc)]

if polys_sel is not None and not polys_sel.empty:
    sub = gpd.sjoin(sub, polys_sel, predicate='within', how='inner')

if sub.empty:
    st.warning('No hay registros con los filtros seleccionados.')
    st.stop()

# ---- METRICS ----
col1,col2,col3=st.columns(3)
col1.metric('Registros', len(sub))
if DWELLING_COL in sub.columns:
    col2.metric('Tipos de uso', sub[DWELLING_COL].nunique())
if ENC_COL in sub.columns:
    col3.metric('Categorías', sub[ENC_COL].nunique())

# ---- MAP ----
center=[sub.geometry.y.mean(), sub.geometry.x.mean()]
m=folium.Map(location=center, zoom_start=15, tiles='CartoDB positron')

# add polygons layer
if polys_sel is not None and not polys_sel.empty:
    folium.GeoJson(polys_sel.__geo_interface__, name='Áreas', style_function=lambda x:{
        'fillColor':'#00000000',
        'color':'#555555',
        'weight':1
    }).add_to(m)

# color mapping
palette=['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00']
color_dict={v:palette[i%len(palette)] for i,v in enumerate(sub[DWELLING_COL].unique())}

for _, r in sub.iterrows():
    folium.CircleMarker(
        [r.geometry.y, r.geometry.x],
        radius=4,
        color=color_dict.get(r.get(DWELLING_COL),'#3186cc'),
        fill=True, fill_opacity=0.8,
        tooltip=f"{POLY_NAME_COL}: {{r.get(POLY_NAME_COL,'')}}"
    ).add_to(m)

st.subheader('Mapa interactivo')
st_folium(m, height=600, use_container_width=True)

# ---- TABLE ----
if DWELLING_COL in sub.columns:
    st.subheader('Distribución por tipo de uso')
    tbl=(sub[DWELLING_COL].value_counts()
         .rename_axis('Tipo').reset_index(name='n'))
    tbl['%']= (tbl['n']/tbl['n'].sum()*100).round(1)
    st.dataframe(tbl)

st.caption('© 2025 • Dashboard Paramapa v3')
