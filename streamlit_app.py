import streamlit as st
import pandas as pd
import json
import plotly.express as px

ss = st.session_state

st.set_page_config(layout="wide")
st.title("Hungarian Census of 1869")

st.write(ss)

init = False
if "start" not in ss:
    ss["start"] = True
    ss["tab0button"] = "region"
    init = True

st.write(ss)

if init == True:
    ss["start"] = False

    # Get borders

    f = open("county_borders_1867.geojson","r")
    json_text = f.read()
    f.close()
    geojson = json.loads(json_text)

    # Get region and local goverment type

    locations = pd.read_excel("regions.xlsx")

def draw_map(sort_by):
    if (sort_by == "region"):
        region_map = {"Magyarország" : "#FF0000",
                    "Erdély" : "#0000FF",
                    "Horvátország" : "#7F00FF",
                    "Szlavonország" : "#7F007F",
                    "Magyar határőrvidék" : "#FF7F7F",
                    "Horvát-Szlavon határőrvidék" : "#AF7FFF",
                    "Fiume város" : "#FFAF7F"}
    elif (sort_by == "government"):
        region_map = {"vármegye" : "#FF0000",
                    "Felső-Fehér vármegye": "#AF0000", 
                    "vidék": "#DF2020",
                    "kerület": "#FFFF00",
                    "székely szék": "#00FFFF",
                    "szász szék": "#00FF00",
                    "határőrvidék": "#AF7FFF",
                    "Fiume város" : "#FFAF7F"}

    locations["color"] = locations[sort_by].map(region_map) 

    color_map = locations["color"].drop_duplicates().tolist()

    fig = px.choropleth(
            geojson=geojson,
            color=locations[sort_by],
            color_discrete_sequence = color_map,
            locations=locations["county"])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()    

dashboard = st.container(border = True)    
with dashboard:
    tab_list = ["Regions and Government","Age Census"]
    longest_text = 0
    for text in tab_list:
        if (len(text) > longest_text):
            longest_text = len(text)
    longest_text = longest_text + 8
    for i,text in enumerate(tab_list):
        text = "**" + "_" * ((longest_text - len(text)) // 2) + " " + text + " " + (longest_text - len(text) - ((longest_text - len(text)) // 2)) * "_" + "**"
        tab_list[i] = text
    tabs = st.tabs(tab_list)
    with tabs[0]: # SUMMARY
        selected_tab = 0
        kpi_col, map_col ,col3 = st.columns([3,10,6],gap = "small")
        with kpi_col:
            pass
        with map_col:
            map_container = st.container(border = True) 
            with map_container:            
                map_list = ["Region","Government"]
                button_column = st.columns(([1] * len(map_list)))
                for i in range(len(map_list)):
                    with button_column[i]:
                        if st.button(map_list[i],use_container_width=True,type = ("primary" if (ss["tab" + str(selected_tab) + "button"] == map_list[i]) else "secondary")):
                            ss.sales_map = map_list[i]
                            st.rerun()            
