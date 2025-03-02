import streamlit as st
import pandas as pd
import json
import plotly.express as px
import openpyxl

ss = st.session_state

st.set_page_config(layout="wide")

init = False
if "start" not in ss:
    ss["start"] = True
    init = True

if init == True:
    ss["start"] = False
    
    ss.selected_tab = 0
    ss.tab_list = [ {"value" : 0, "caption" : {"HU" : "Népesség és Terület",  "EN" : "Population and Area"},
                     "buttons" :  [ {"caption" : {"EN" : "Population",        "HU" : "Népesség"}  , "value" : "népesség",  },
                                    {"caption" : {"EN" : "Area",              "HU" : "Terület"}   , "value" : "terület km2"},
                                    {"caption" : {"EN" : "Population Density","HU" : "Népsűrűség"}, "value" : "népsűrűség"}]},
                    {"value" : 1, "caption" : {"HU" : "Koreloszlás",          "EN" : "Age Census"},
                     "buttons" : [  {"caption" : {"EN" : "Gender Distribution in the Selected Age Group", "HU" : "Nemek eloszlása a kiválasztott korcsoportban"}          , "value" : "nemek aránya"},
                                    {"caption" : {"EN" : "Selected Age group Ratio to the Whole Population", "HU" : "Kiválasztott korcsoport aránya a teljes lakossághoz"}, "value" : "kor aránya"}]},
                    {"value" : 2, "caption" : {"HU" : "Vallási Adatok",          "EN" : "Religious Census"},
                     "buttons" : [  {"caption" : {"EN" : "Religius majority", "HU" : "Vallási többség"}          , "value" : "majority"}]},                                    
                    {"value" : 3, "caption" : {"HU" : "Közigazgatási régiók", "EN" : "Regions and Government"},
                     "buttons" : [  {"caption" : {"EN" : "Region", "HU" : "Régió"},                              "value" : "region"    },
                                    {"caption" : {"EN" : "Administrative Unit", "HU" : "Közigazgatási egységek"},"value" : "government"}]}]
    for i in range(len(ss.tab_list)):
        ss["tab" + str(i) + "button"] = ss.tab_list[i]["buttons"][0]["value"]

    ss.region_chart_coloring = {"Magyarország" : "#FF0000",
                                "Hungary" : "#FF0000",
                                "Erdély" : "#20FF20",
                                "Transylvania" : "#20FF20",                                
                                "Határőrvidék" : "#AF7FFF",
                                "Military Frontier" : "#AF7FFF",                                
                                "Fiume város és kerület" : "#FFAF7F",
                                "Fiume city and district" : "#FFAF7F",
                                "Horvát-Szlavónország" : "#7F00FF",
                                "Croatia and Slavonia" : "#7F00FF",                                
                                }    

    ss.value_replacement_EN = {"Magyarország" : "Hungary",
                            "Erdély" : "Transylvania",
                            "Horvát-Szlavónország" : "Croatia and Slavonia",
                            "Horvátország" : "Croatia",
                            "Szlavonország" : "Slavonia",
                            "Határőrvidék" : "Military Frontier",
                            "határőrvidék" : "military frontier",
                            "Magyar határőrvidék" : "Hungarian Military Frontier",
                            "Horvát-Szlavon határőrvidék" : "Croatian Military Frontier",
                            "Fiume város és kerület": "Fiume city and district",
                            "Fiume város" : "Fiume city",
                            "Összesen" : "Sum",
                            "Magyarország és Erdély" : "Hungary and Transylvania",                                                                          

                            "vármegye" : "county",
                            "vidék": "domain",
                            "kerület" : "district",
                            "Fiume város" : "Fiume city",
                            "határőrviék" : "miltary frontier",
                            "székely szék"  : "székely seat",
                            "szász szék" : "saxon seat",
                            "szász vidék" : "saxon domain",
                            "Felső-Fehér vármegye" : "Felső-Fehér county",
                            
                            "római katolikus" : "roman catholic",
                            "görög katolikus": "greek catholic",
                            "görög keleti": "greek orthodox",                                                    
                            "evangélikus": "lutheran",
                            "református": "reformed",
                            "örmény katolikus": "armenian catholic",                                                    
                            "örmény keleti": "armenian orthodox",                                                    
                            "unitárius": "unitarian",
                            "nazarénus": "nazarene",
                            "német katolikus" : "german catholic",
                            "egyéb keresztény": "other christian",
                            "izraelita": "jew",
                            "mohamedán": "muslim",
                            "egyéb vallásúak" : "other religious"}     

    # Language options

    ss.languages = ["HU","EN"]
    ss.selected_language = ss.languages[0]

    # Get borders

    f = open("data/county_borders_1867.geojson","r")
    json_text = f.read()
    f.close()
    ss.geojson = json.loads(json_text)

    # Get region and local goverment type

    ss.locations = pd.read_excel("data/regions.xlsx")
    ss.locations = ss.locations[ss.locations["government"] != "tó"]

    # Population and Area data

    ss.pop_area = pd.read_excel(r"data/population_and_area.xlsx")
    ss.pop_area["népesség"] = ss.pop_area["jelenlévő helybeli"] + ss.pop_area["jelenlévő idegen"]
    ss.pop_area["terület km2"] = (ss.pop_area["area"] * 55.06).round(2)
    ss.pop_area["népsűrűség"] = (ss.pop_area["népesség"] / ss.pop_area["terület km2"]).round(2)

    ss.counties = pd.merge(ss.locations,ss.pop_area[ss.pop_area["subarea"] == "összesen"],how = "left",on = "county").fillna(0)

    # Age Census

    ss.age_filter_1 = "0"
    ss.age_filter_2 = "99+"

    ss.age_census = pd.read_excel(r"data/age_census.xlsx",header = None)
    ss.age_census.iloc[1,1:4] = "county selector"
    new_labels = pd.MultiIndex.from_frame(ss.age_census.iloc[:2].T.astype(str), names=['Age', 'Gender'])
    ss.age_census = ss.age_census.set_axis(new_labels, axis=1).iloc[2:]

    county_filter_for_age = ss.age_census.xs("county selector",level = "Gender",axis = 1)
    extracted_df = ss.age_census.xs("férfi",level = "Gender",axis = 1).fillna(0)
    ss.filtered_age_male =  pd.merge(county_filter_for_age,extracted_df,left_index = True, right_index = True)            
    extracted_df = ss.age_census.xs("nő",level = "Gender",axis = 1).fillna(0)
    ss.filtered_age_female =  pd.merge(county_filter_for_age,extracted_df,left_index = True, right_index = True)
    ss.filtered_age_male.loc[:,"0":"99+"] = ss.filtered_age_male.loc[:,"0":"99+"].astype("int32")
    ss.filtered_age_female.loc[:,"0":"99+"] = ss.filtered_age_female.loc[:,"0":"99+"].astype("int32")

    ss.age_list = ss.filtered_age_male.columns.to_list()
    ss.age_list = ss.age_list[3:]

    ss.filtered_age = ss.filtered_age_male[ss.filtered_age_male.columns.to_list()[:3]]
    ss.filtered_age["férfiak összes"] = ss.filtered_age_male[ss.age_list].sum(axis = 1)
    ss.filtered_age["nők összes"] = ss.filtered_age_female[ss.age_list].sum(axis = 1)
    ss.filtered_age["lakosság"] = ss.filtered_age["férfiak összes"] + ss.filtered_age["nők összes"]

    ss.age_tree_list = []
    group_size = 10
    for age in range(0,100 - group_size + 1,group_size):
        age_upper_limit = age + group_size - 1
        new_column = str(age) + "-" + str(age_upper_limit)
        ss.age_tree_list.append(new_column)
        ss.filtered_age_male[new_column] = ss.filtered_age_male.loc[:,str(age):str(age_upper_limit)].sum(axis = 1)
        ss.filtered_age_female[new_column] = ss.filtered_age_female.loc[:,str(age):str(age_upper_limit)].sum(axis = 1)
    if (age + group_size != 100):
        age = str(age + group_size)
    else:
        age = "99+"
    ss.age_tree_list.append(str(age) + "-")
    ss.filtered_age_male[str(age) + "-"] = ss.filtered_age_male.loc[:,str(age):"99+"].sum(axis = 1)
    ss.filtered_age_female[str(age) + "-"] = ss.filtered_age_female.loc[:,str(age):"99+"].sum(axis = 1)  

    # Religions:

    ss.religions = pd.read_excel(r"data/religions.xlsx")
    ss.religions_list = ss.religions.columns.tolist()[4:]
    #ss.religions[religions_list] = ss.religions[religions_list].astype("int32")
    ss.religions = ss.religions.fillna(0)
    ss.religions["majority"] = ss.religions[ss.religions_list].idxmax(axis = 1)
    ss.religions["number of majority"] = ss.religions[ss.religions_list].max(axis = 1)
    ss.religions["ratio of majority"] = (ss.religions["number of majority"] / ss.religions["főösszeg"] * 100).round(2)
    ss.religions = ss.religions[(ss.religions["subarea"] == "összesen") | (ss.religions["subarea"] == "főösszeg")]

    for r in ss.religions_list:
        ss.religions[r + " arány"] = (ss.religions[r] / ss.religions["főösszeg"] * 100).round(3)

    ss.religion_comparison_buttons = {"buttons": [{"caption" : {"EN" : "Realtive", "HU": "Relatív"}, "value" : "relative"},
                                                  {"caption" : {"EN" : "Absolute","HU": "Abszolút"}, "value" : "absolute"}]}
    ss.religion_comparison = "relative"

    # Legend and colorbart texts:

    ss.legend = {"region":         {"text" : {"HU": "régió", "EN": "region"},
                                    "db" : ss.counties,
                                     "suffix" : {"HU": "", "EN": ""},
                                     "theme": { "Magyarország" : "#FF0000",
                                                "Erdély" : "#20FF20",
                                                "Horvátország" : "#7F00FF",
                                                "Szlavonország" : "#7F007F",
                                                "Magyar határőrvidék" : "#FF7F7F",
                                                "Horvát-Szlavon határőrvidék" : "#AF7FFF",
                                                "Fiume város" : "#FFAF7F"},
                                     "map title": {"HU" : "Szent István Koronájának Országai", "EN" : "Lands of the Crown of Saint Stephen [Transleithania]"}},
                  "government" :    {"text": {"HU": "közigazgatási<br>egység", "EN": "administrative<br>unit"},
                                     "db" : ss.counties,
                                     "suffix" : {"HU": "", "EN": ""},
                                     "theme" :  {   "vármegye" : "#FF0000",
                                                    "Felső-Fehér vármegye": "#DF2020", 
                                                    "vidék": "#AF0000",
                                                    "kerület": "#FFFF00",
                                                    "székely szék": "#00FFFF",
                                                    "szász szék": "#00FF00",
                                                    "szász vidék": "#00AF00",
                                                    "határőrvidék": "#AF7FFF",
                                                    "Fiume város" : "#FFAF7F"},
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia közigazgatási egységei", "EN" : "Administrative units of Hungary, Croatia and Slavonia"}},
                  "népesség" :      {"text" :{"HU" : "népesség", "EN": "population"},
                                     "db" : ss.pop_area,
                                     "suffix" : {"HU" : " fő", "EN": ""},
                                     "theme" : "reds",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia népességi viszonyai", "EN" : "Population of Hungary, Croatia and Slavonia"}},
                  "terület km2" :   {"text": {"HU": "terület", "EN" : "area"},
                                     "db" : ss.pop_area,
                                     "suffix" : {"HU": " km²", "EN" : " km²"},
                                     "theme"  :"blues",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia területi viszonyai", "EN" : "Area relations of Hungary, Croatia and Slavonia"}},
                  "népsűrűség":     {"text" : {"HU" : "népsűrűség", "EN": "population<br>density"},
                                     "db" : ss.pop_area,
                                     "suffix" : {"HU" : " fő/km²", "EN": " per km²"},
                                     "theme" : "purples",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia népsűrűségi viszonyai", "EN" : "Population density of Hungary, Croatia and Slavonia"},
                                     "extra data" : ["népesség","terület km2"]},
                  "nemek aránya":   {"text" : {"HU" : "nők aránya<br>a kiválasztott<br>korcsoportban", "EN": "female ratio<br>in the selected<br>age group"},
                                     "suffix" : {"HU" : " %", "EN": " %"},
                                     "theme" : [[0, 'rgb(0,0,128)'], [0.40, 'rgb(0,0,255)'],[0.495, 'rgb(191,191,255)'],[0.5, 'rgb(255,223,255)'],[0.505,'rgb(255,191,191)'],[0.60,'rgb(255,0,0)'],[1,'rgb(128,0,0)']],
                                     "map title": {"HU" : "Nők aránya a kiválasztott korcsoportban (AGE_FILTER)", "EN" : "Ratio of females in the selected age group (AGE_FILTER)"},
                                     "extra data" : ["kor aránya"]},
                  "kor aránya" :    {"text" : {"HU" : "kiválasztott korcsoport<br>aránya a teljes<br>lakossághoz", "EN": "selected age group<br>ratio to the<br>whole population"},
                                     "suffix" : {"HU" : " %", "EN": " %"},
                                     "theme" : [[0, 'rgb(255,255,255)'],[0.001, 'rgb(223,255,223)'], [0.01, 'rgb(128,255,128)'], [0.1,'rgb(128,223,128)'],[0.5,'rgb(0,128,0)'],[1,'rgb(0,32,0)']],
                                     "map title": {"HU" : "A kiválasztott korcsoport (AGE_FILTER) aránya a teljes lakossághoz viszonyítva", "EN" : "The proportion of the selected age group (AGE_FILTER) to the total population"}},
                  "majority":       {"text" : {"HU" : "Legnépesebb vallási<br>felekezet", "EN": "Most popoluos<br>religious denomination"},
                                     "db" : ss.religions,
                                     "suffix" : {"HU" : "", "EN": ""},
                                     "theme" :  {   "római katolikus" : "#FFD000",
                                                    "görög katolikus": "#FF8000",
                                                    "görög keleti": "#A05050",                                                    
                                                    "református": "#0000FF",
                                                    "evangélikus": "#8000FF",                                                    
                                                    "örmény katolikus": "#FF0080",                                                    
                                                    "örmény keleti": "#8000FF",                                                    
                                                    "unitárius": "#80FF00",
                                                    "nazarénus": "#00FF80",
                                                    "egyéb keresztény": "#FF0000",
                                                    "izraelita": "#0080FF",
                                                    "mohamedán": "#00FF00",
                                                    "egyéb vallásúak" : "#808080"},                                     
                                     "map title": {"HU" : "Legnagyobb vallási felekezet régiónként", "EN" : "Most popolous religious devotions by regions"},
                                     "extra data": ["ratio of majority","number of majority"]},
                   "ratio of majority":{ "text" : {"HU" : "arány", "EN": "ratio"},
                                        "db": ss.religions,
                                         "suffix" : {"HU" : " %", "EN": " %"}},
                   "number of majority":{ "text" : {"HU" : "népesség", "EN": "population"},
                                         "db": ss.religions,
                                         "suffix" : {"HU" : " fő", "EN": ""}}}


    for religion, r_color in ss.legend["majority"]["theme"].items():
        ss.legend[religion + " arány"] = {"text" : {"HU" : religion + "<br>népesség aránya", "EN" : "Ratio of<br>" + ss.value_replacement_EN[religion] + "<br>population"},
                                          "db" : ss.religions,
                                         "suffix" : {"HU" : " %", "EN": " %"},
                                         "theme" : [[0, 'rgb(255,255,255)'],[1, r_color]],
                                         "map title": {"HU" : religion.capitalize() + " népesség aránya", "EN" : "Ratio of " + ss.value_replacement_EN[religion].capitalize() + " population"},
                                         "extra data": [religion]}
        ss.legend[religion] = { "text" : {"HU" : religion.capitalize() + "<br>népesség", "EN": ss.value_replacement_EN[religion].capitalize() + "<br>population"},
                                "db": ss.religions,
                                "theme" : [[0, 'rgb(255,255,255)'],[1, r_color]],
                                "map title": {"HU" : religion.capitalize() + " népesség", "EN" : "" + ss.value_replacement_EN[religion].capitalize() + " population"},
                                "suffix" : {"HU" : " fő", "EN": ""},
                                "extra data": [religion + " arány"]}
        ss.tab_list[2]["buttons"].append({"caption": {"HU" : religion.capitalize(), "EN" : ss.value_replacement_EN[religion].capitalize()}, "value": religion})

    list_of_dicts = ["region", "government", "majority"]

    for i in list_of_dicts:
        dict_name = ss.legend[i]["theme"]
        new_dict = {}
        for key, value in dict_name.items():
            new_key = ss.value_replacement_EN.get(key,"")
            if (new_key != ""):
                new_dict[new_key] = value

        for key, value in new_dict.items():
            dict_name[key] = value




locations = ss.locations
geojson = ss.geojson

def button_list(buttonlist = None, session_state_variable = None):
    if (session_state_variable is None):
        session_state_variable = "tab" + str(ss.selected_tab) + "button"
        buttonlist = ss.tab_list[ss.selected_tab]["buttons"]
    if ((buttonlist == ss.tab_list) | (buttonlist == ss.languages)):
        max_column = len(buttonlist)
    else:
        if len(buttonlist) > 4:
            max_column = 4
        else:
            max_column = len(buttonlist)
    button_column = st.columns(([1] * max_column))        
    for i in range(len(buttonlist)):
        with button_column[i % max_column]:
            if buttonlist == ss.languages:
                if st.button(buttonlist[i],use_container_width=True,type = ("primary" if (ss[session_state_variable] == buttonlist[i]) else "secondary")):
                    ss[session_state_variable] = buttonlist[i]
                    st.rerun()                
            else:
                if st.button(buttonlist[i]["caption"][ss.selected_language],use_container_width=True,type = ("primary" if (ss[session_state_variable] == buttonlist[i]["value"]) else "secondary")):
                    ss[session_state_variable] = buttonlist[i]["value"]
                    st.rerun()

def filter_stand_alone_df(df, selected_counties):
    selected_counties_list = []
    if (len(selected_counties["selection"]["points"]) == 0):
        counties_selected = False
        value_replacement = ss.value_replacement_EN
        filtered_df = (df[df["subarea"] == "főösszeg"])
        if (ss.selected_language != "HU"):
            filtered_df.replace(value_replacement, inplace = True)
    else:
        counties_selected = True        
        selected_counties_list = []
        for c in range(len(selected_counties["selection"]["points"])):
            selected_counties_list.append(selected_counties["selection"]["points"][c]["location"])
        filtered_df = (df[df["county"].isin(selected_counties_list)])
        filtered_df = filtered_df[filtered_df["subarea type"] == "megye"]
        filtered_df = filtered_df[filtered_df["subarea"] != "főösszeg"]    
    return(filtered_df, counties_selected, selected_counties_list)

def draw_sidechart(filtered_df, sort_by, side_chart_hight =  456,counties_selected = "False"):
    if (sort_by == "majority"):
        if counties_selected == False:        
            if (ss.selected_language == "HU"):
                st.markdown("#### Régiónkénti megoszlás")
            elif (ss.selected_language == "EN"):
                st.markdown("#### Distribution by regions")  
        else:
            if (ss.selected_language == "HU"):
                st.markdown("#### Megyék összehasonlítása")
            elif (ss.selected_language == "EN"):
                st.markdown("#### County comparison")                         
        button_list(ss.religion_comparison_buttons["buttons"], "religion_comparison")        
        df_long = filtered_df[["county","főösszeg"] + ss.religions_list]
        df_long = df_long.melt(id_vars = df_long.columns.tolist()[:2],value_vars = df_long.columns[2:], var_name = "religion", value_name = "population")    
        df_long["ratio"] = (df_long["population"] / df_long["főösszeg"] * 100).round(3)
        value_replacement = ss.value_replacement_EN
        if (ss.selected_language != "HU"):
            df_long.replace(value_replacement, inplace = True)           
        if ss.religion_comparison == "absolute":
            sub_sort = "population"
        else:
            sub_sort = "ratio"
        fig = px.bar(df_long,
                x="county",
                y= sub_sort,
                orientation='v',
                color='religion',
                height = side_chart_hight,
                width = 450,
                color_discrete_map = ss.legend["majority"]["theme"],
                custom_data = ["county", "religion", "population", "ratio"])
        hover_template = {"HU" : "<b>%{customdata[0]}</b><br>"+
                                        "<br>" + 
                                        "%{customdata[1]} népesség:<br>"+
                                        "<b>%{customdata[2]}</b> fő<br><br>" + 
                                        "arány:<br>"+
                                        "<b>%{customdata[3]}</b> %" + 
                                        "<extra></extra>",
                        "EN" : "<b>%{customdata[0]}</b><br>"+
                                        "<br>" + 
                                        "%{customdata[1]} population:<br>"+
                                        "<b>%{customdata[2]}</b><br><br>" + 
                                        "ratio:<br>"+
                                        "<b>%{customdata[3]}</b> %" + 
                                        "<extra></extra>"}
        fig.update_layout(yaxis_title_text = ("Vallási eloszlás" if (ss.selected_language == "HU") else "Religious distribution"),
            xaxis_title_text = ("" if (counties_selected == False) else ("megye" if ss.selected_language == "HU" else ("county"))),
            legend=dict(
            title = ("vallási felekezetek:" if (ss.selected_language == "HU") else "religious denominations:")))
        fig.update_traces(width = 0.9,
            hovertemplate = hover_template[ss.selected_language])          
        st.plotly_chart(fig, theme=None)         
    elif counties_selected == False:
        if (ss.selected_language == "HU"):
            st.markdown("#### Régiónkénti megoszlás")
        elif (ss.selected_language == "EN"):
            st.markdown("#### Distribution by regions")
        sort_type = "units"      
        if (sort_by == "népsűrűség") | (sort_by == "nemek aránya") | (sort_by == "kor aránya") | (ss.tab_list[ss.selected_tab]["caption"]["EN"].find("Religious Census") >= 0):
            sort_type = "intensive property"  
        if (sort_type != "intensive property"): #If the sorted values can be added up to sum, then pie chart                                                       
            fig = px.pie(filtered_df[filtered_df["subarea type"] == "ország"],
                            values = sort_by,
                            names = "county",
                            color = "county",
                            height = side_chart_hight,
                            color_discrete_map = ss.region_chart_coloring,
                            custom_data = ["county",sort_by])
            fig.update_traces(hovertemplate = "<b>%{customdata[0][0]}</b><br>"+
                                    "<br>" + 
                                    ss.legend[sort_by]["text"][ss.selected_language] + ":<br>"+
                                    "<b>%{customdata[0][1]}</b>" + ss.legend[sort_by]["suffix"][ss.selected_language] +
                                    "<extra></extra>")                            
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="top",
                xanchor="center",
            ))
            st.plotly_chart(fig, theme=None)
        elif (sort_type == "intensive property"): #In this case bar chart
            if (sort_by == "népsűrűség"):
                filtered_df = filtered_df[(filtered_df["county"] != "Fiume város és kerület") & (filtered_df["county"] != "Fiume city and district")]
            elif (ss.tab_list[ss.selected_tab]["caption"]["EN"].find("Religious Census") >= 0):
                button_list(ss.religion_comparison_buttons["buttons"], "religion_comparison")  
            filtered_df = filtered_df[filtered_df["subarea type"] == "ország"]

            extras = ss.legend[sort_by].get("extra data",[])
            hover_template = ("<b>%{customdata[0]}</b><br>"+
                                            "<br>" + 
                                            "<b>" +ss.legend[sort_by]["text"][ss.selected_language] + ":</b><br>"+
                                            "<b>%{customdata[1]}" + ss.legend[sort_by]["suffix"][ss.selected_language] + "</b>")
            for n,e in enumerate(extras):
                hover_template = hover_template + "<br><br>" + (
                    "<i>" + ss.legend[e]["text"][ss.selected_language] + "</i>:<br>"+
                    "%{customdata[" + str(n + 2) + "]}" + ss.legend[e]["suffix"][ss.selected_language])
            hover_template = hover_template + "<extra></extra>" 

            fig = px.bar(filtered_df,
                            x="county",
                            y= sort_by,
                            color= "county",
                            text = "county",
                            height = side_chart_hight,                            
                            color_discrete_map = ss.region_chart_coloring,
                            custom_data = ["county",sort_by] + extras)
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                yaxis_title_text = ss.legend[sort_by]["text"][ss.selected_language].capitalize() + ("" if (ss.legend[sort_by]["suffix"][ss.selected_language] == "") else "<br> [" + ss.legend[sort_by]["suffix"][ss.selected_language] + " ]"),
                xaxis_title_text = ss.legend["region"]["text"][ss.selected_language].capitalize(),
                showlegend = False)
            fig.update_traces(hovertemplate = hover_template)
            fig.update_xaxes(showticklabels=False)                                    
            st.plotly_chart(fig, theme=None)
    else:
        if (ss.selected_language == "HU"):
            st.markdown("#### Megyék összehasonlítása")
        elif (ss.selected_language == "EN"):
            st.markdown("#### County comparison")
        if (ss.tab_list[ss.selected_tab]["caption"]["EN"].find("Religious Census") >= 0):
            button_list(ss.religion_comparison_buttons["buttons"], "religion_comparison")              
        if (sort_by == "nemek aránya") | (sort_by == "kor aránya"):
            range_color=(0, 100)
        else:
            db2 = ss.legend[sort_by]["db"]
            filtered_df2 = db2[db2["subarea type"] == "megye"]
            if (sort_by == "népsűrűség"):
                filtered_df2 = filtered_df2[filtered_df2["county"] != "Fiume város és kerület"]
            max_value = max(filtered_df2[sort_by])            
            range_color=(0, max_value)
        extras = ss.legend[sort_by].get("extra data",[])
        hover_template = ("<b>%{customdata[0]}</b><br>"+
                                        "<br>" + 
                                        "<b>" +ss.legend[sort_by]["text"][ss.selected_language] + ":</b><br>"+
                                        "<b>%{customdata[1]}" + ss.legend[sort_by]["suffix"][ss.selected_language] + "</b>")
        for n,e in enumerate(extras):
            hover_template = hover_template + "<br><br>" + (
                "<i>" + ss.legend[e]["text"][ss.selected_language] + "</i>:<br>"+
                "%{customdata[" + str(n + 2) + "]}" + ss.legend[e]["suffix"][ss.selected_language])
        hover_template = hover_template + "<extra></extra>"                                                   
        fig = px.bar(filtered_df,
                        x = "county",
                        y = sort_by,
                        color = sort_by,
                        height = side_chart_hight,
                        color_continuous_scale = ss.legend[sort_by]["theme"],
                        range_color = range_color,
                        custom_data = ["county",sort_by] + extras)
        fig.update_traces(hovertemplate = hover_template)                        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            coloraxis_showscale = False)
        st.plotly_chart(fig, theme=None) 

def draw_age_tree(selected_counties):
    age_tree_male = filter_stand_alone_df(ss.filtered_age_male, selected_counties)[0]
    age_tree_male["nem"] = "Férfi"    
    age_tree_male = age_tree_male[age_tree_male.columns.tolist()[:3] + ["nem"] + ss.age_tree_list]
    age_tree_male = age_tree_male[(age_tree_male["subarea type"] == "ország") | (age_tree_male["subarea type"] == "megye")]
    df_long = age_tree_male.melt(id_vars = age_tree_male.columns.tolist()[:4],value_vars = age_tree_male.columns[3:], var_name = "age group", value_name = "population")
    age_tree_female = filter_stand_alone_df(ss.filtered_age_female, selected_counties)[0]
    age_tree_female["nem"] = "Női"        
    age_tree_female = age_tree_female[age_tree_female.columns.tolist()[:3] + ["nem"] + ss.age_tree_list]
    age_tree_female = age_tree_female[(age_tree_female["subarea type"] == "ország") | (age_tree_female["subarea type"] == "megye")]
    df_long_2 = age_tree_female.melt(id_vars = age_tree_female.columns.tolist()[:4],value_vars = age_tree_female.columns[3:], var_name = "age group", value_name = "population")    
    df_long_2["population"] = -df_long_2["population"]
    df_long = pd.concat([df_long,df_long_2])
    df_long["abs population"] = abs(df_long["population"])
    if (ss.selected_language == "HU"):
        side_title = "#### Korfa"
    elif (ss.selected_language == "EN"):
        side_title = "#### Age tree"
        df_long["nem"] = df_long["nem"].map({"Női" : "Female", "Férfi" : "Male"})        
    st.write(side_title)
    fig = px.bar(df_long,
                 x="population",
                 y="age group",
                 orientation='h',
                 color='county',
                 width = 750,
                 height = 643,
                 color_discrete_map = ss.region_chart_coloring,
                 custom_data = ["county","nem","age group","abs population"])
    fig.update_layout(barmode='relative',
        yaxis_title = None,
        xaxis_title = None,
        legend=dict(
        title = None,
        orientation="h",
        yanchor="top",
        xanchor="center"
    ))
    hover_template = {"HU" : "<b>%{customdata[0]}</b><br>"+
                                      "<br>" + 
                                      "%{customdata[1]} lakosság<br>a %{customdata[2]} korcsoportban:<br>"+
                                      "<b>%{customdata[3]}</b>" + ss.legend["népesség"]["suffix"][ss.selected_language] +
                                      "<extra></extra>",
                      "EN" : "<b>%{customdata[0]}</b><br>"+
                                      "<br>" + 
                                      "%{customdata[1]} population<br>in the %{customdata[2]} age group:<br>"+
                                      "<b>%{customdata[3]}</b>" + ss.legend["népesség"]["suffix"][ss.selected_language] +
                                      "<extra></extra>"}
    fig.update_traces(width = 1,
        hovertemplate = hover_template[ss.selected_language])    
    st.plotly_chart(fig, theme=None)        



def draw_map(map_df,sort_by,color_type = "unique coloring"):
    df = map_df[map_df.columns.tolist()[:-1]]
    df[map_df.columns.tolist()[-1]] = map_df[map_df.columns.tolist()[-1]]
    value_replacement = ss.value_replacement_EN
    if (ss.selected_language != "HU"):
        df.replace(value_replacement, inplace = True) 
        df[df.columns.tolist()[0]] = map_df[map_df.columns.tolist()[0]]
    map_title = ss.legend[sort_by]["map title"][ss.selected_language]
    if (ss.age_filter_1 == "0") & (ss.age_filter_2 == "99+"):
        if ss.selected_language == "HU":
            age_filter = "teljes népesség"
        elif ss.selected_language == "EN":
            age_filter = "total population"
    elif (ss.age_filter_1 == ss.age_filter_2):
        if (ss.age_filter_1 == "99+"):
            age_filter = "100 - "
        else:
            age_filter = ss.age_filter_1
    elif (ss.age_filter_2 == "99+"):
        age_filter = ss.age_filter_1 + " - "
    else:
        age_filter = ss.age_filter_1 + " - " + ss.age_filter_2 
    age_filter = "(" + age_filter + ")"
    map_title = map_title.replace("(AGE_FILTER)",age_filter)
    st.markdown("### " + map_title)
    if color_type == "unique coloring":
        region_map = ss.legend[sort_by]["theme"]
        color_map = region_map
        df["color"] = df[sort_by].map(region_map) 
        color_map = df["color"].drop_duplicates().tolist()
        color_scale = None
        range_color = None
    else:
        region_map = None
        color_map = None
        color_scale = ss.legend[sort_by]["theme"]
        min_value = 0             
        max_value = max(df[(df["subarea type"] == "megye")][sort_by])
        if (sort_by == "népsűrűség"):
            max_value = max(df[(df["county"] != "Fiume város és kerület") & (df["county"] != "Fiume city and district")][sort_by])
        elif (sort_by == "nemek aránya") | (sort_by == "kor aránya"):
            min_value = 0
            max_value = 100          
  

        range_color= (min_value, max_value)

    extras = ss.legend[sort_by].get("extra data",[])
    hover_template = ("<b>%{customdata[0]}</b><br>"+
                                      "<br>" + 
                                      "<b>" +ss.legend[sort_by]["text"][ss.selected_language] + ":</b><br>"+
                                      "<b>%{customdata[1]}" + ss.legend[sort_by]["suffix"][ss.selected_language] + "</b>")
    for n,e in enumerate(extras):
        hover_template = hover_template + "<br><br>" + (
            "<i>" + ss.legend[e]["text"][ss.selected_language] + "</i>:<br>"+
            "%{customdata[" + str(n + 2) + "]}" + ss.legend[e]["suffix"][ss.selected_language])
    hover_template = hover_template + "<extra></extra>" 

    fig = px.choropleth(df,
            geojson=geojson,
            color = sort_by,
            color_discrete_sequence = color_map,
            color_continuous_scale = color_scale,
            range_color = range_color,   
            locations = df["county"],
            custom_data = ["county",sort_by] + extras)
    fig.update_geos(fitbounds="locations", visible=False)                                   
    fig.update_traces(hovertemplate = hover_template)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      coloraxis_colorbar_title = ss.legend[sort_by]["text"][ss.selected_language] + ("" if (ss.legend[sort_by]["suffix"][ss.selected_language] == "") else "<br> [" + ss.legend[sort_by]["suffix"][ss.selected_language] + " ]"),
                      legend_title_text = ss.legend[sort_by]["text"][ss.selected_language] + ("" if (ss.legend[sort_by]["suffix"][ss.selected_language] == "") else "<br> [" + ss.legend[sort_by]["suffix"][ss.selected_language] + " ]"),
                      coloraxis_colorbar_xanchor = "right",
                      legend_xanchor = "right",
                      height=400)
    return(fig)

header_column, language_buttons = st.columns([15,2])
with language_buttons:
    button_list(ss.languages,"selected_language")
with header_column:
    if ss.selected_language == "EN":
        st.title("Hungarian Census of 1869")
    elif ss.selected_language == "HU":
        st.title("1869-as magyarországi népszámlálás")

dashboard = st.container(border = True)    
with dashboard:
    button_list(ss.tab_list,"selected_tab")
    tab_name = ss.tab_list[ss.selected_tab]["caption"]["EN"]
    selected_button_name = "tab" + str(ss.selected_tab) + "button"
    selected_button_value = ss[selected_button_name] 
    st.divider()
    if (tab_name.find("Age Census") >= 0):
        map_col, det_col = st.columns([10,4],gap = "small")
        with map_col:
            filter_container = st.container(border = True)
            with filter_container:
                filter_title = {'HU': '### Változtasd meg a korcsoportot az arányok átszámításhoz:',
                                'EN': '### Filter the age group to recalculate the statistics:'}
                st.markdown(filter_title[ss.selected_language])
                age_filter_1, age_filter_2 = st.select_slider("",options= ss.age_list, value = (ss.age_filter_1,ss.age_filter_2))
                if (age_filter_1 != ss.age_filter_1) | (age_filter_2 != ss.age_filter_2):
                    ss.age_filter_1 = age_filter_1
                    ss.age_filter_2 = age_filter_2
                    st.rerun()
            map_container = st.container(border = True)
            county_filter_for_age = ss.filtered_age.copy(deep = False)
            county_filter_for_age["férfi"] = ss.filtered_age_male.loc[:,ss.age_filter_1 : ss.age_filter_2].sum(axis = 1)
            county_filter_for_age["nő"] = ss.filtered_age_female.loc[:,ss.age_filter_1 : ss.age_filter_2].sum(axis = 1)
            with map_container:
                #map = draw_map(selected_button, "values",map_title)
                county_filter_for_age["nemek aránya"] = county_filter_for_age.apply(lambda row: row['nő'] / (row['nő'] + row['férfi']) if (row['nő'] + row['férfi'] > 0) else 0.5, axis=1)
                county_filter_for_age["nemek aránya"] = county_filter_for_age["nemek aránya"] * 100
                county_filter_for_age["nemek aránya"] = county_filter_for_age["nemek aránya"].astype('float').round(2)
                county_filter_for_age["kor aránya"] = (county_filter_for_age["nő"] + county_filter_for_age["férfi"]) / county_filter_for_age["lakosság"] * 100
                county_filter_for_age["kor aránya"] = county_filter_for_age["kor aránya"].astype('float').round(3)                        
                f_county_filter_for_age = county_filter_for_age[county_filter_for_age["subarea"] == "összesen"]
                button_list()                      
                map = draw_map(f_county_filter_for_age, selected_button_value, "values")
                selected_counties = st.plotly_chart(map, use_container_width=True, on_select ="rerun")
        with det_col:
            sidechart_container = st.container(border = True)
            filtered_df, counties_selected, selected_counties_list = filter_stand_alone_df(county_filter_for_age, selected_counties)                 
            with sidechart_container:
                if (ss.age_filter_1 == "0") & (ss.age_filter_2 == "99+") & (selected_button_value == "kor aránya"):
                    draw_age_tree(selected_counties)
                else:
                    draw_sidechart(filtered_df,selected_button_value,643,counties_selected)                                            

    elif (tab_name.find("Regions and Government") >= 0):
        map_col ,det_col = st.columns([10,4],gap = "small")
        with map_col:
            map_container = st.container(border = True) 
            with map_container:            
                button_list()
                map = draw_map(ss.counties, selected_button_value)        
                st.plotly_chart(map, use_container_width=True)

    elif (tab_name.find("Religious Census") >= 0):
        map_col, det_col = st.columns([10,4],gap = "small")
        with map_col:
            map_container = st.container(border = True) 
            with map_container:   
                button_list()
                if selected_button_value == "majority":
                    sort_by = "majority"
                elif ss.religion_comparison == "relative":
                    sort_by = selected_button_value + " arány"
                else:
                    sort_by = selected_button_value
                map = draw_map(ss.religions, sort_by, ("unique coloring" if (selected_button_value == "majority") else "value"))
                selected_counties = st.plotly_chart(map, use_container_width=True, on_select ="rerun")                
        counties_selected = False   
        filtered_df, counties_selected, selected_counties_list = filter_stand_alone_df(ss.religions, selected_counties)
        with det_col:
            sidechart_container = st.container(border = True)      
            with sidechart_container:
                draw_sidechart(filtered_df, sort_by, 565, counties_selected)                     
    elif (tab_name.find("Population and Area") >= 0):
        map_col, det_col = st.columns([10,4],gap = "small")
        with map_col:
            map_container = st.container(border = True) 
            with map_container:        
                button_list()
                map = draw_map(ss.counties, selected_button_value, "values")
                selected_counties = st.plotly_chart(map, use_container_width=True, on_select ="rerun")
        counties_selected = False
        filtered_df, counties_selected, selected_counties_list = filter_stand_alone_df(ss.pop_area, selected_counties)
        with det_col:
            sidechart_container = st.container(border = True)      
            with sidechart_container:
                draw_sidechart(filtered_df,selected_button_value, 456, counties_selected)

        if (ss.selected_language == "HU"):
            st.markdown("#### Válassz ki néhány megyét az összehasonlításukhoz [SHIFT + Click]")                            
        elif (ss.selected_language == "EN"):
            st.markdown("#### Select some counties to compare [SHIFT + Click]")                    

        #if (counties_selected):
        #    for county in selected_counties_list:
        #        st.markdown("### " + county)                        
        #        st.dataframe(filtered_df[filtered_df["county"] == county])
        #else:
        #    st.dataframe(filtered_df)                    
                        
