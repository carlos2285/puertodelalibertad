
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from streamlit_folium import st_folium
import folium
import plotly.express as px
import branca
import os

# ---------- Paths ----------
DATA_FILE = os.path.join('data', 'paramapa_clean.csv')
SHAPE_FILE = os.path.join('data', 'limites.shp')  # rename if needed

POINT_LAT = 'p002__Latitude'
POINT_LON = 'p002__Longitude'
AREA_NAME_COL = 'SECTOR'  # change to your shapefile field

st.set_page_config(layout='wide', page_title='Dashboard Paramapa v4')
st.title('Dashboard Paramapa v4')

# ---------- Load data ----------
@st.cache_resource
def load_points():
    df = pd.read_csv(DATA_FILE)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df[POINT_LON], df[POINT_LAT])],
        crs='EPSG:4326'
    )
    return gdf

@st.cache_resource
def load_polys():
    if os.path.exists(SHAPE_FILE):
        polys = gpd.read_file(SHAPE_FILE).to_crs('EPSG:4326')
        return polys
    return None

gdf = load_points()
polys = load_polys()

# ---------- Sidebar Filters ----------
st.sidebar.header('Filtros Geo')
if polys is not None and AREA_NAME_COL in polys.columns:
    areas = sorted(polys[AREA_NAME_COL].unique())
    area_sel = st.sidebar.multiselect('Área', areas, default=areas)
    polys_sel = polys[polys[AREA_NAME_COL].isin(area_sel)]
    gdf = gpd.sjoin(gdf, polys_sel, predicate='within')

# Variable selector
st.sidebar.header('Variable a explorar')
numeric_cols = gdf.select_dtypes(include=['float','int']).columns.tolist()
cat_cols = [c for c in gdf.columns if gdf[c].dtype.name == 'category' or gdf[c].dtype == object]
var = st.sidebar.selectbox('Selecciona variable', numeric_cols + cat_cols)

# ---------- Summary ----------
st.subheader(f'Distribución de {var}')
colA, colB = st.columns([2,1])

if var in numeric_cols:
    # Histogram
    fig = px.histogram(gdf, x=var, nbins=30, title=f'Histograma de {var}')
    colA.plotly_chart(fig, use_container_width=True)
else:
    counts = gdf[var].value_counts().reset_index()
    counts.columns = [var, 'n']
    fig = px.bar(counts, x=var, y='n', title=f'Frecuencia de {var}')
    colA.plotly_chart(fig, use_container_width=True)

# Table preview
colB.write(gdf[[var]].describe(include='all'))

# ---------- Map ----------
st.subheader('Mapa interactivo')
center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
m = folium.Map(location=center, zoom_start=15, tiles='CartoDB positron')

# Add polygons
if polys is not None and not polys.empty:
    folium.GeoJson(polys_sel.__geo_interface__, name='Áreas', style_function=lambda x:{
        'fillColor':'#00000000','color':'#555','weight':1
    }).add_to(m)

if var in numeric_cols:
    minv, maxv = gdf[var].min(), gdf[var].max()
    cmap = branca.colormap.LinearColormap(['blue','lime','yellow','red'], vmin=minv, vmax=maxv)
    for _, r in gdf.iterrows():
        folium.CircleMarker(
            [r.geometry.y, r.geometry.x],
            radius=4,
            color=cmap(r[var]),
            fill=True, fill_opacity=0.8,
            popup=f'{var}: {r[var]}'
        ).add_to(m)
    cmap.add_to(m)
else:
    cat_values = gdf[var].unique()
    palette = px.colors.qualitative.Set3
    color_dict = {v: palette[i % len(palette)] for i,v in enumerate(cat_values)}
    legend_html = ''
    for cat, colr in color_dict.items():
        legend_html += f'<i style="background:{colr}"></i> {cat}<br>'
    for _, r in gdf.iterrows():
        folium.CircleMarker(
            [r.geometry.y, r.geometry.x],
            radius=4,
            color=color_dict.get(r[var],'gray'),
            fill=True, fill_opacity=0.8,
            popup=f'{var}: {r[var]}'
        ).add_to(m)
    legend = folium.Element(f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: auto; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; padding: 10px;">
            <b>{var}</b><br>
            {legend_html}
        </div>
    ''')
    m.get_root().html.add_child(legend)

st_folium(m, use_container_width=True, height=600)

st.caption('© 2025 – Dashboard Paramapa v4 (auto-clean)')
