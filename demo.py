import folium
import folium.plugins as plugins
import streamlit as st
from streamlit_folium import folium_static
import xarray as xr
from syn_sar import *

# Page Configuration
st.set_page_config(layout="wide")

# Title and Description
st.title("Forecasting Inundation Extents using REOF Analysis (FIER)-Bangladesh")


row1_col1, row1_col2 = st.columns([2, 1])
# Set up Geemap
with row1_col1:
    m = folium.Map(
        zoom_start=7,
        location =(23.68,90.35),
        control_scale=True,
    )
    plugins.Fullscreen(position='topright').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    m.add_child(folium.LatLngPopup())
    folium.LayerControl().add_to(m)

with row1_col2:
    # Form
    with st.form('Perform REOF Analysis'):
        # lAT / LONG
        station = st.selectbox(
     'Determine station:',
     ('SW72','New_Station' ),
     )

     #    resolution = st.select_slider(
     # 'Select resolution',
     # options=['100m','500m',],
     # )
        st.write('Input water level between 0 and 7.4 m')
        lw = st.number_input("Water level:",
        value = 5.0,
        format = '%.2f',
        min_value = 0.0,
        max_value = 7.4,
        )


        # Submit Button
        submitted = st.form_submit_button("Submit")

        if submitted:
            if station == 'SW72':

                st.write('Station: ',station)
                # st.write('resolution: ',resolution)
                st.write('Water level (m): %.2f'%(lw))

                location = [24.81, 91.12]
                m = folium.Map(
                    zoom_start = 9,
                    location = location,
                    control_scale=True,
                )


                RSM = xr.open_dataset('Bangladesh/RSM/' + station + '/RSM_hydro.nc')
                bounds = [[RSM.lat.values.min(), RSM.lon.values.min()], [RSM.lat.values.max(), RSM.lon.values.max()]]

                # Add RSM
                for i in range(1,5):
                    image_name = 'Bangladesh/RSM/' + station + '/RSM_%s.png'%(i)
                    folium.raster_layers.ImageOverlay(
                        image= image_name,
                        bounds = bounds,
                        opacity = 0.7,
                        name = 'RSM ' + str(i),
                        show = False
                    ).add_to(m)

                # Add SYN_SAR Image
                image_folder = image_output(station, float(lw))

                folium.raster_layers.ImageOverlay(
                    image= image_folder +'/syn_sar.png',
                    bounds = bounds,
                    opacity = 0.5,
                    name = 'Synthesized Sar Image_' + station + '_' + str(lw),
                    show = False
                ).add_to(m)

                # Add Z_SCORE
                folium.raster_layers.ImageOverlay(
                    image= image_folder +'/z_score.png',
                    bounds = bounds,
                    opacity = 0.5,
                    name = 'Z-score Image_' + station + '_' + str(lw),
                    show = False
                ).add_to(m)

                # Add Inundation
                folium.raster_layers.ImageOverlay(
                    image= image_folder +'/water_map.png',
                    bounds = bounds,
                    opacity = 0.5,
                    name = 'Inundation Map_' + station + '_' + str(lw),
                    show = True
                ).add_to(m)

                plugins.Fullscreen(position='topright').add_to(m)
                folium.TileLayer('Stamen Terrain').add_to(m)
                m.add_child(folium.LatLngPopup())
                folium.LayerControl().add_to(m)


with row1_col1:
    folium_static(m, height = 600, width = 900)
    st.write('Disclaimer: This is a test version of FIER method for Bangladesh')
    url = "https://www.sciencedirect.com/science/article/pii/S0034425720301024?casa_token=kOYlVMMWkBUAAAAA:fiFM4l6BUzJ8xTCksYUe7X4CcojddbO8ybzOSMe36f2cFWEXDa_aFHaGeEFlN8SuPGnDy7Ir8w"
    st.write("Reference: [Chang, C. H., Lee, H., Kim, D., Hwang, E., Hossain, F., Chishtie, F., ... & Basnayake, S. (2020). Hindcast and forecast of daily inundation extents using satellite SAR and altimetry data with rotated empirical orthogonal function analysis: Case study in Tonle Sap Lake Floodplain. Remote Sensing of Environment, 241, 111732.](%s)" % url)
