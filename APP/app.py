

#Create Streamlit App with Map visualization of train routes in Austria
def main():
    from sys import prefix
    import streamlit as st
    import folium
    from folium import plugins
    from folium.plugins import MarkerCluster
    import pandas as pd
    import random
    import colorsys
    from streamlit_folium import st_folium
    # app.py
    import streamlit as st
    from streamlit_folium import st_folium
    import folium
    import pandas as pd
    import numpy as np

    # -----------------------------
    # Load preprocessed data
    # -----------------------------
    #load data from data directory
    stop_times_geo_with_startEnd_calc = pd.read_csv("../data/oebb_gtfs/stop_times_geo_with_startEnd_calc.csv")


    st.set_page_config(page_title="Austrian Train Routes Visualization", layout="wide")
    st.title("Austrian Train Routes Visualization")
    st.markdown("This app visualizes train routes in Austria using Folium and Streamlit.")

    # -----------------------------
    # Columns (adjust here if needed)
    # -----------------------------
    lat_col = "stop_lat"
    lon_col = "stop_lon"
    route_id_col = "route_id"
    route_name_col = "route_short_name"
    trip_id_col = "trip_id"
    seq_col = "stop_sequence"
    speed_col = "speed"
    EPI_col= "EPI_segment"

    # -----------------------------
    # Sidebar options
    # -----------------------------
    st.sidebar.header("Options")
    #sample_n no steps but directly input number
    sample_n = st.sidebar.number_input("Use first N rows (0 = all)", min_value=0, value=100, step=100)
    DRAW_MARKERS = st.sidebar.checkbox("Draw stop markers", value=True)
    DRAW_LABELS  = st.sidebar.checkbox("Show labels next to markers", value=False)
    HIGHLIGHT_MAX_SPEED = st.sidebar.checkbox("Highlight highest-speed segment (per trip)", value=bool(speed_col))
    map_height = st.sidebar.slider("Map height (px)", min_value=400, max_value=1000, value=750, step=50)
    Select_Route = st.sidebar.selectbox("Select Route to Highlight", options=["All"] + stop_times_geo_with_startEnd_calc[route_name_col].astype(str).unique().tolist())
    ONLY_AUSTRIA_MAP = st.sidebar.checkbox("Only Austria Map View", value=True)

    highlighted_segments = {"Route": [],"Trip": [], "From_Stop": [], "To_Stop": [], "From_Lat": [], "From_Lon": [], "To_Lat": [], "To_Lon": [], "EPI": []}
    # -----------------------------
    # Prepare data
    # -----------------------------

    #Apply all filter possibilities
    if ONLY_AUSTRIA_MAP:
        stop_times_geo_with_startEnd_calc = stop_times_geo_with_startEnd_calc[stop_times_geo_with_startEnd_calc["country_stop"] == "Austria"]
        if sample_n and sample_n > 0:
            df = stop_times_geo_with_startEnd_calc[:sample_n].copy()
        if Select_Route != "All":
            df = df[df[route_name_col].astype(str) == Select_Route].copy()
    else:
        df = stop_times_geo_with_startEnd_calc.copy()
        if sample_n and sample_n > 0:
            df = stop_times_geo_with_startEnd_calc[:sample_n].copy()
        if Select_Route != "All":
            df = df[df[route_name_col].astype(str) == Select_Route].copy()


    #make black and white folium map
    m = folium.Map(location=[47.5, 14.5], zoom_start=7,tiles= 'CartoDB positron')

    #make all color markers small red dots
    stops_color = "#FF0000"
    route_color= "#000000"

    routes = df["route_id"].astype(str).unique()
    route_names = df["route_short_name"].astype(str).unique()


    linestyles = {}
    line_styles_list = [None, '10, 5']
    def get_linestyle(route_name, default_color=route_color):
        """
        Returns (linestyle, color) for a given route name string.
        """
        rn = str(route_name).upper()

        # --- Commuter / S-Bahn type ---
        if rn.startswith("S") or rn.startswith("CAT") or rn.endswith("S"):   # CAT = City Airport Train
            return  None, "#2A98E2"

        # --- Regional services (REX, RX, R, SV etc.) ---
        if any(rn.startswith(prefix) for prefix in ["REX", "RX", "R", "SV"]):
            #return solid line with default color
            return None, default_color

        # --- Intercity / Long-distance (RJ, RJX, CJX, IC, EC, EN, WB, A*, D*, CH*, CZ*, HU*, SI*) ---
        if any(rn.startswith(prefix) for prefix in [
            "RJ", "RJX", "CJX", "IC", "EC", "EN", "WB", "A", "D", "CH", "CZ", "HU", "SI"
        ]) or any(rn.endswith(prefix) for prefix in [
            "RJ", "RJX", "CJX", "IC", "EC", "EN", "WB", "A", "D", "CH", "CZ", "HU", "SI"
        ]):
            return '10, 5', default_color

        # --- Default fallback ---
        return None, default_color

    for r in routes:
        r_group = folium.FeatureGroup(name=f"Route {r}", show=True)
        m.add_child(r_group)

        g_route = df[df["route_id"].astype(str) == r].copy()
        g_route.sort_values(["trip_id", "stop_sequence"], inplace=True)

        
        for _, row in g_route.iterrows():
                linestyle, route_color = get_linestyle(row['route_short_name'])
                lat = row['stop_lat']
                lon = row['stop_lon']
                if DRAW_MARKERS:
                    #red markers with black border
                    folium.CircleMarker(
                        location=(lat, lon),
                        radius=2.6,
                        color=stops_color,
                        fill=True,
                        fill_color=stops_color,
                        fill_opacity=1.0,
                        stroke=True,
                        weight=0,
                        popup=folium.Popup(row['stop_name'])
                        ).add_to(m)
        
        #Draw Routes but as popup do start station name and end station of g_route.grouped
        for trip_id, g_trip in g_route.groupby("trip_id"):
            # Highlight highest-speed segment if option selected
            if HIGHLIGHT_MAX_SPEED:
                max_speed_idx = g_trip[EPI_col].idxmax()
                if not pd.isna(max_speed_idx):
                    max_speed_row = g_trip.loc[max_speed_idx]
                    max_speed_idx_loc = g_trip.index.get_loc(max_speed_idx)

                    #if max speed is at first stop and last stop, set prev and next accordingly
                    if max_speed_row[seq_col] == g_trip[seq_col].min() and max_speed_row[seq_col] == g_trip[seq_col].max():
                        continue

                    #elif max speed is the last stop
                    elif max_speed_row[seq_col] == g_trip[seq_col].max():
                        prev_idx = max_speed_idx_loc - 1
                        points_before = list(zip(g_trip.iloc[:max_speed_idx_loc]["stop_lat"], g_trip.iloc[:max_speed_idx_loc]["stop_lon"]))
                        folium.PolyLine(
                            locations=points_before,
                            color=route_color,
                            weight=2,
                            opacity=0.5,
                            dash_array=linestyle,
                            popup=f"{g_trip['route_short_name'].iloc[0]}",
                        ).add_to(m)

                        folium.PolyLine(
                            locations=[(g_trip.iloc[prev_idx]['stop_lat'], g_trip.iloc[prev_idx]['stop_lon']),
                                        (max_speed_row['stop_lat'], max_speed_row['stop_lon'])],
                            color='green',
                            weight=4,
                            opacity=0.7,
                            dash_array='5, 5',
                            popup=f"{g_trip.iloc[prev_idx]['stop_name']} - {max_speed_row['stop_name']} "
                        ).add_to(m)

                        highlighted_segments["Route"].append(g_trip['route_short_name'].iloc[0])
                        highlighted_segments["Trip"].append(trip_id)
                        highlighted_segments["From_Stop"].append(g_trip.iloc[prev_idx]['stop_name'])
                        highlighted_segments["To_Stop"].append(max_speed_row['stop_name'])
                        highlighted_segments["From_Lat"].append(g_trip.iloc[prev_idx]['stop_lat'])
                        highlighted_segments["From_Lon"].append(g_trip.iloc[prev_idx]['stop_lon'])
                        highlighted_segments["To_Lat"].append(max_speed_row['stop_lat'])
                        highlighted_segments["To_Lon"].append(max_speed_row['stop_lon'])
                        highlighted_segments["EPI"].append(max_speed_row['EPI_segment'])


                    #elif max speed is the first stop
                    elif max_speed_row[seq_col] == g_trip[seq_col].min():
                        next_idx = max_speed_idx_loc + 1
                        points_after = list(zip(g_trip.iloc[max_speed_idx_loc:]["stop_lat"], g_trip.iloc[max_speed_idx_loc:]["stop_lon"]))
                        folium.PolyLine(
                            locations=points_after,
                            color=route_color,
                            weight=2,
                            opacity=0.5,
                            dash_array=linestyle,
                            popup=f"{g_trip['route_short_name'].iloc[0]}",
                        ).add_to(m)
                        
                        folium.PolyLine(
                            locations=[(max_speed_row['stop_lat'], max_speed_row['stop_lon']),
                                        (g_trip.iloc[next_idx]['stop_lat'], g_trip.iloc[next_idx]['stop_lon'])],
                            color='green',
                            weight=4,
                            opacity=0.7,
                            dash_array='5, 5',
                            popup=f"{max_speed_row['stop_name']} - {g_trip.iloc[next_idx]['stop_name']}"

                        ).add_to(m)
                        
                        highlighted_segments["Route"].append(g_trip['route_short_name'].iloc[0])
                        highlighted_segments["Trip"].append(trip_id)
                        highlighted_segments["From_Stop"].append(g_trip.iloc[next_idx]['stop_name'])
                        highlighted_segments["To_Stop"].append(max_speed_row['stop_name'])
                        highlighted_segments["From_Lat"].append(g_trip.iloc[next_idx]['stop_lat'])
                        highlighted_segments["From_Lon"].append(g_trip.iloc[next_idx]['stop_lon'])
                        highlighted_segments["To_Lat"].append(max_speed_row['stop_lat'])
                        highlighted_segments["To_Lon"].append(max_speed_row['stop_lon'])
                        highlighted_segments["EPI"].append(max_speed_row['EPI_segment'])
                    else:
                        prev_idx = max_speed_idx_loc - 1
                        next_idx = max_speed_idx_loc + 1
                        points_before = list(zip(g_trip.iloc[:max_speed_idx_loc]["stop_lat"], g_trip.iloc[:max_speed_idx_loc]["stop_lon"]))
                        points_after = list(zip(g_trip.iloc[max_speed_idx_loc:]["stop_lat"], g_trip.iloc[max_speed_idx_loc:]["stop_lon"]))
                        
                        folium.PolyLine(
                            locations=points_before,
                            color=route_color,
                            weight=2,
                            opacity=0.5,
                            dash_array=linestyle,
                            popup=f"{g_trip['route_short_name'].iloc[0]}",
                        ).add_to(m)

                        folium.PolyLine(
                            locations=[(g_trip.iloc[prev_idx]['stop_lat'], g_trip.iloc[prev_idx]['stop_lon']),
                                        (max_speed_row['stop_lat'], max_speed_row['stop_lon'])],
                            color='green',
                            weight=4,
                            opacity=0.7,
                            dash_array='5, 5',
                            popup=f"{g_trip.iloc[prev_idx]['stop_name']} - {max_speed_row['stop_name']} "
                        ).add_to(m)

                        folium.PolyLine(
                            locations=points_after,
                            color=route_color,
                            weight=2,
                            opacity=0.5,
                            dash_array=linestyle,
                            popup=f"{g_trip['route_short_name'].iloc[0]}",
                        ).add_to(m)

                        #add highlighted segment to pandas list
                        highlighted_segments["Route"].append(g_trip['route_short_name'].iloc[0])
                        highlighted_segments["Trip"].append(trip_id)
                        highlighted_segments["From_Stop"].append(g_trip.iloc[prev_idx]['stop_name'])
                        highlighted_segments["To_Stop"].append(max_speed_row['stop_name'])
                        highlighted_segments["From_Lat"].append(g_trip.iloc[prev_idx]['stop_lat'])
                        highlighted_segments["From_Lon"].append(g_trip.iloc[prev_idx]['stop_lon'])
                        highlighted_segments["To_Lat"].append(max_speed_row['stop_lat'])
                        highlighted_segments["To_Lon"].append(max_speed_row['stop_lon'])
                        highlighted_segments["EPI"].append(max_speed_row['EPI_segment'])
            else:
                # Draw the route line normally
                points = list(zip(g_trip["stop_lat"], g_trip["stop_lon"]))
                folium.PolyLine(
                    locations=points,
                    color=route_color,
                    weight=2,
                    opacity=1,
                    dash_array=linestyle,
                    popup=f"{g_trip['route_short_name'].iloc[0]}",
                ).add_to(m)

    # Render in Streamlit
    highlighted_segments_df = pd.DataFrame(highlighted_segments)
    save_csv = highlighted_segments_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download highlighted segments as CSV",
        data=save_csv,
        file_name='highlighted_segments.csv',
        mime='text/csv',
    )
    st_folium(m, width="100%", height=map_height)