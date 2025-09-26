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
    
    ss.tab_list = [ {"value" : 0, "caption" : {"HU" : "Közigazgatási régiók", "EN" : "Regions and Government"},
                     "buttons" : [  {"caption" : {"EN" : "Region", "HU" : "Régió"},                              "value" : "region"    },
                                    {"caption" : {"EN" : "Administrative Units", "HU" : "Közigazgatási egységek"},"value" : "government"}]},
                    {"value" : 1, "caption" : {"HU" : "Népesség és Terület",  "EN" : "Population and Area"},
                     "buttons" :  [ {"caption" : {"EN" : "Population",        "HU" : "Népesség"}  , "value" : "népesség",  },
                                    {"caption" : {"EN" : "Area",              "HU" : "Terület"}   , "value" : "terület km2"},
                                    {"caption" : {"EN" : "Population Density","HU" : "Népsűrűség"}, "value" : "népsűrűség"}]},
                    {"value" : 2, "caption" : {"HU" : "Kor- és nemeloszlás",          "EN" : "Age and Gender Census"},
                     "buttons" : [  {"caption" : {"EN" : "Gender Distribution in the Selected Age Group", "HU" : "Nemek eloszlása a kiválasztott korcsoportban"}          , "value" : "nemek aránya"},
                                    {"caption" : {"EN" : "Selected Age group Ratio to the Whole Population", "HU" : "Kiválasztott korcsoport aránya a teljes lakossághoz"}, "value" : "kor aránya"}]},
                    {"value" : 3, "caption" : {"HU" : "Vallási Adatok",          "EN" : "Religious Census"},
                     "buttons" : [  {"caption" : {"EN" : "Religius majority", "HU" : "Vallási többség"}          , "value" : "majority"}]},
                    {"value" : 4, "caption" : {"EN" : "Literacy", "HU" : "Írni-olvasni Tudás"},
                     "buttons" : [  {"caption" : {"HU" : "Teljes lakosság", "EN": "Total Population"}, "value" : "literate sum ratio"},
                                    {"caption" : {"HU" : "Férfiak", "EN": "Male"}, "value" : "literate male ratio"},
                                    {"caption" : {"HU" : "Nők", "EN": "Female"}, "value" : "literate female ratio"},                                    
                                    {"caption" : {"HU" : "Nemi eloszlás", "EN": "Gender distribution"}, "value" : "literate gender ratio"}]},
                    {"value" : 5, "caption" : {"EN" : "Livestock", "HU" : "Állatállomány"},
                     "buttons" : [  {"caption" : {"HU" : "Leggyakoribb haszonállat", "EN": "Livestock composition"}, "value" : "livestock majority"}]}]
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
                                "Croatia and Slavonia" : "#7F00FF"}    

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
                            "egyéb vallásúak" : "other religion",

                            "méhkasok" : "beehives",
                            "bivalyok": "buffaloes",                                                  
                            "juhok": "sheeps",
                            "szarvasmarhák": "cattles",                                                    
                            "sertések": "pigs",                                                    
                            "kecskék": "goats",
                            "lovak" : "horses",
                            "szamarak" : "donkeys",
                            "öszvérek" : "mules",                            
                            
                            "könnyű kanca" :  "lighter-weight mare",
                            "könnyű csődör" :  "lighter-weight stallion",
                            "könnyű herélt" : "lighter-weight gelding",
                            "nehéz kanca" :  "heavy-weight mare",
                            "nehéz csődör" :  "heavy-weight stallion",
                            "nehéz herélt" : "heavy-weight gelding",
                            "csikó (3 év alatti)" :  "juvenile horses<br>(under 3 years)"
                            }     

    # Language options

    ss.languages = ["HU","EN"]
    ss.selected_language = ss.languages[1]

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

    ss.f_county_filter_for_age = pd.DataFrame()

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

    ss.religion_comparison_buttons = {"buttons": [{"caption" : {"EN" : "Relative", "HU": "Relatív"}, "value" : "relative"},
                                                  {"caption" : {"EN" : "Absolute","HU": "Abszolút"}, "value" : "absolute"}]}
    ss.religion_comparison = "relative"

    # Literacy:

    ss.partial_literacy_included_buttons = {"buttons": [{"caption" : {"EN" : "Include Partial Literacy", "HU": "Csak olvasni tudók is"}, "value" : True}]}
    ss.partial_literacy_included = True

    ss.literacy = pd.read_excel(r"data/literacy.xlsx")    
    ss.literacy = ss.literacy[(ss.literacy["subarea type"] == "megye") | (ss.literacy["subarea type"] == "ország")]

    ss.under_7_children = pd.DataFrame()
    ss.under_7_children = ss.filtered_age_male[ss.filtered_age_male.columns.to_list()[:3]]

    ss.under_7_children["underage boys"] = ss.filtered_age_male.loc[:,"0":"6"].sum(axis = 1)
    ss.under_7_children["underage girls"] = ss.filtered_age_female.loc[:,"0":"6"].sum(axis = 1)
    ss.under_7_children["underage sum"] = ss.under_7_children["underage boys"] + ss.under_7_children["underage girls"]

    ss.literacy = pd.merge(ss.literacy, ss.under_7_children, how = 'left', on = ['county','subarea','subarea type'])

    ss.literacy['illiterate male'] = ss.literacy['illiterate male'] - ss.literacy['underage boys']
    ss.literacy['illiterate female'] = ss.literacy['illiterate female'] - ss.literacy['underage girls']
    ss.literacy['illiterate sum'] = ss.literacy['illiterate sum'] - ss.literacy['underage sum']
    ss.literacy['főösszeg'] = ss.literacy['illiterate sum'] - ss.literacy['underage sum']
    ss.literacy.iloc[:,3:] = ss.literacy.iloc[:,3:].fillna(0)
    ss.literacy.iloc[:,3:] = ss.literacy.iloc[:,3:].astype("int32")  
    for t in ["male","female","sum"]:
        ss.literacy[f'above 6 pop {t}'] = (ss.literacy[f'illiterate {t}'] + ss.literacy[f'literate {t}'] + ss.literacy[f'partially literate {t}'])

        ss.literacy[f'literate {t} ratio'] = (ss.literacy[f'literate {t}'] / (ss.literacy[f'illiterate {t}'] + ss.literacy[f'literate {t}'] + ss.literacy[f'partially literate {t}']))
        ss.literacy[f'literate {t} ratio'] = (ss.literacy[f'literate {t} ratio'] * 100)
        ss.literacy[f'literate {t} ratio'] = ss.literacy[f'literate {t} ratio'].astype('float64')
        ss.literacy[f'literate {t} ratio'] = ss.literacy[f'literate {t} ratio'].round(2)

        ss.literacy[f'partially literate {t} ratio'] = ((ss.literacy[f'literate {t}'] + ss.literacy[f'partially literate {t}']) / (ss.literacy[f'illiterate {t}'] + ss.literacy[f'literate {t}'] + ss.literacy[f'partially literate {t}']))
        ss.literacy[f'partially literate {t} ratio'] = (ss.literacy[f'partially literate {t} ratio'] * 100)
        ss.literacy[f'partially literate {t} ratio'] = ss.literacy[f'partially literate {t} ratio'].astype('float64')
        ss.literacy[f'partially literate {t} ratio'] = ss.literacy[f'partially literate {t} ratio'].round(2)         

    ss.literacy[f'literate gender ratio'] = (ss.literacy[f'literate female'] / ss.literacy[f'literate sum'])
    ss.literacy[f'literate gender ratio'] = (ss.literacy[f'literate gender ratio'] * 100)
    ss.literacy[f'literate gender ratio'] = ss.literacy[f'literate gender ratio'].astype('float64')
    ss.literacy[f'literate gender ratio'] = ss.literacy[f'literate gender ratio'].round(2)

    ss.literacy[f'partially literate gender ratio'] = (ss.literacy[f'partially literate female'] + ss.literacy[f'literate female']) / (ss.literacy[f'literate sum'] + ss.literacy[f'partially literate sum'])
    ss.literacy[f'partially literate gender ratio'] = (ss.literacy[f'partially literate gender ratio'] * 100)
    ss.literacy[f'partially literate gender ratio'] = ss.literacy[f'partially literate gender ratio'].astype('float64')
    ss.literacy[f'partially literate gender ratio'] = ss.literacy[f'partially literate gender ratio'].round(2)    

    for t in ["male","female","sum"]:
        ss.literacy[f'partially literate {t}'] = ss.literacy[f'partially literate {t}'] + ss.literacy[f'literate {t}']

    #Livestock:
    ss.livestock_comparison_buttons = {"buttons": [{"caption" : {"EN" : "Relative", "HU": "Relatív"}, "value" : "relative"},
                                                  {"caption" : {"EN" : "Absolute","HU": "Abszolút"}, "value" : "absolute"}]}    
    ss.livestock_comparison = "relative"

    ss.animals = pd.read_excel(r"data/animal_properties.xlsx")    

    ss.animals = ss.animals[(ss.animals["subarea type"] == "megye") | (ss.animals["subarea type"] == "ország")]
    ss.animals = ss.animals.fillna(0)


    ss.horse_columns = ["csikó (3 év alatti)","nehéz kanca","nehéz herélt","nehéz csődör","könnyű csődör","könnyű herélt","könnyű kanca"]
    #ss.animals["lovak"] = ss.animals[ss.horse_columns].sum(axis = 1)

    ss.cattle_columns = ["magyar bika","magyar tehén","magyar ökör","magyar borjú","magyar összesen","svájci bika","svájci tehén","svájci ökör","svájci borjú"]
    ss.animals["szarvasmarhák"] = ss.animals[ss.cattle_columns].sum(axis = 1)  

    #ss.animals["juhok"] = ss.animals["juh összesen"]

    #ss.animals


    # Legend and colorbart texts:

    ss.legend = {"region":         {"text" : {"HU": "Régió", "EN": "Region"},
                                    "db" : 'counties',
                                    "sort_type" : "values",
                                     "suffix" : {"HU": "", "EN": ""},
                                     "theme": { "Magyarország" : "#FF0000",
                                                "Erdély" : "#20FF20",
                                                "Horvátország" : "#7F00FF",
                                                "Szlavonország" : "#7F007F",
                                                "Magyar határőrvidék" : "#FF7F7F",
                                                "Horvát-Szlavon határőrvidék" : "#AF7FFF",
                                                "Fiume város" : "#FFAF7F"},
                                     "map title": {"HU" : "Szent István Koronájának Országai", "EN" : "Lands of the Crown of Saint Stephen [Transleithania]"}},
                  "government" :    {"text": {"HU": "Közigazgatási<br>egység", "EN": "Administrative<br>Unit"},
                                     "db" : 'counties',
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
                                     "sort_type" : "values",
                                     "db" : 'pop_area',
                                     "suffix" : {"HU" : " fő", "EN": ""},
                                     "theme" : "reds",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia népességi viszonyai", "EN" : "Population of Hungary, Croatia and Slavonia"}},
                  "terület km2" :   {"text": {"HU": "terület", "EN" : "area"},
                                     "sort_type" : "values",
                                     "db" : 'pop_area',
                                     "suffix" : {"HU": " km²", "EN" : " km²"},
                                     "theme"  :"blues",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia területi viszonyai", "EN" : "Area relations of Hungary, Croatia and Slavonia"}},
                  "népsűrűség":     {"text" : {"HU" : "népsűrűség", "EN": "population<br>density"},
                                     "sort_type" : "intensive property",
                                     "db" : 'pop_area',
                                     "suffix" : {"HU" : " fő/km²", "EN": " per km²"},
                                     "theme" : "purples",
                                     "map title": {"HU" : "Magyarország, Horvátország és Szlavónia népsűrűségi viszonyai", "EN" : "Population density of Hungary, Croatia and Slavonia"},
                                     "extra data" : ["népesség","terület km2"]},
                  "nemek aránya":   {"text" : {"HU" : "nők aránya<br>a kiválasztott<br>korcsoportban<br>(AGE_FILTER)", "EN": "female ratio<br>in the selected<br>age group<br>(AGE_FILTER)"},
                                     "sort_type" : "intensive property",
                                     "db" : 'f_county_filter_for_age',
                                     "suffix" : {"HU" : " %", "EN": " %"},
                                     "theme" : [[0, 'rgb(0,0,128)'], [0.40, 'rgb(0,0,255)'],[0.495, 'rgb(191,191,255)'],[0.5, 'rgb(255,223,255)'],[0.505,'rgb(255,191,191)'],[0.60,'rgb(255,0,0)'],[1,'rgb(128,0,0)']],
                                     "map title": {"HU" : "Nők aránya a kiválasztott korcsoportban (AGE_FILTER)", "EN" : "Ratio of females in the selected age group (AGE_FILTER)"},
                                     "extra data" : ["kor aránya"]},
                  "kor aránya" :    {"text" : {"HU" : "kiválasztott<br>korcsoport<br>(AGE_FILTER)<br>aránya a teljes<br>lakossághoz", "EN": "selected age<br>group (AGE_FILTER)<br>ratio to the<br>whole population"},
                                     "sort_type" : "intensive property",
                                     "db" : 'f_county_filter_for_age',
                                     "suffix" : {"HU" : " %", "EN": " %"},
                                     "theme" : [[0, 'rgb(255,255,255)'],[0.5, 'rgb(0,255,0)'],[1,'rgb(0,128,0)']],
                                     "map title": {"HU" : "A kiválasztott korcsoport (AGE_FILTER) aránya a teljes lakossághoz viszonyítva", "EN" : "The proportion of the selected age group (AGE_FILTER) to the total population"}},
                  "majority":       {"text" : {"HU" : "legnépesebb vallási<br>felekezet", "EN": "most popoluos<br>religious denomination"},
                                     "sort_type" : "intensive property",
                                     "db" : 'religions',
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
                                                    "mohamedán": "#008000",
                                                    "egyéb vallásúak" : "#808080"}, 
                                     "melt_down" : True,     
                                     "melt_down abs_rel": "religion_comparison",
                                     "melt_down old_columns" : ss.religions_list,
                                     "melt_down summmary" : "főösszeg",
                                     "melt_down new_columns" :  "religion",
                                     "melt_down value_name" : "population",  
                                     "melt_down relative_factor" : 100,                                     
                                     "melt_down population" : {"HU": " lakosság", "EN": " population"},   
                                     "melt_down population_unit" : {"HU": "fő", "EN" : ""},  
                                     "melt_down relative_unit" : {"HU": " %", "EN" : " %"},                                     
                                     "melt_down yaxis_title_text" : {"HU": "Lakosság vallási eloszlása", "EN" : "Religious distribution"},                                                                   
                                     "melt_down sidebar_title" : {"HU" : "Vallási<br>felekezetek","EN": "Religious<br>denominations"},                                                                                                
                                     "map title": {"HU" : "Legnagyobb vallási felekezet régiónként", "EN" : "Most popolous religious devotions by regions"},
                                     "extra data": ["ratio of majority","number of majority"]},
                   "ratio of majority":{ "text" : {"HU" : "arány", "EN": "ratio"},
                                        "db": 'religions',
                                         "suffix" : {"HU" : " %", "EN": " %"}},
                   "number of majority":{ "text" : {"HU" : "népesség", "EN": "population"},
                                         "db": 'religions',
                                         "suffix" : {"HU" : " fő", "EN": ""}},                                        
                   "literate male ratio": {'text' : {'HU' : "írni-olvasni tudók<br>aránya a 6 évesnél idősebb<br>férfiak között", "EN": "literacy in<br>male population<br>above age 6"},
                                        "db" : 'literacy',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " %", "EN": " %"},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, 'rgb(0,0,255)']],
                                        "map title" : {'HU' : "Írni-olvasni tudók aránya a 6 évesnél idősebb férfiak között", "EN": "Literacy in male population above age 6"}},
                   "literate female ratio": {'text' : {'HU' : "írni-olvasni tudók<br>aránya a 6 évesnél<br>idősebb<br>nők között", "EN": "literacy in<br>female population<br>above age 6"},
                                        "db" : 'literacy',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " %", "EN": " %"},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, 'rgb(255,0,0)']],
                                        "map title" : {'HU' : "Írni-olvasni tudók aránya a 6 évesnél idősebb nők között", "EN": "Literacy in female population above age 6"}},
                  "livestock majority":       {"text" : {"HU" : "leggyakoribb<br>haszonállat", "EN": "most populous<br>livestock "},
                                     "sort_type" : "intensive property",
                                     "db" : 'religions',
                                     "suffix" : {"HU" : "", "EN": ""},
                                     "theme" :  {   "méhkasok" : "#FFD000",
                                                    "bivalyok":"#37291A",                                                  
                                                    "juhok": "#5784FF",
                                                    "szarvasmarhák": "#AA7B49",                                                    
                                                    "sertések": "#FF4375",                                                    
                                                    "kecskék": "#52B929",
                                                    "lovak" : "#FFB86C",
                                                    "szamarak" : "#808080",
                                                    "öszvérek" : "#DCC0A0"},                                                
                                     "melt_down" : True,     
                                     "melt_down abs_rel": "livestock_comparison",
                                     "melt_down summmary" : "népesség",
                                     "melt_down new_columns" :  "livestock types",
                                     "melt_down value_name" : "livestock size",  
                                     "melt_down relative_factor" : 1,
                                     "melt_down population" : {"HU": " darabszáma", "EN": ""}, 
                                     "melt_down population_unit" : {"HU": " db", "EN" : ""}, 
                                     "melt_down relative_unit" : {"HU": " db/fő", "EN" : " per capita"},                                       
                                     "melt_down yaxis_title_text" : {"HU": "Állatállomány összetétele", "EN" : "Livestock composition"},                                                                   
                                     "melt_down sidebar_title" : {"HU" : "Háziállat<br>fajták","EN": "Livestock<br>species"},                                                                                                
                                     "map title": {"HU" : "Leggyakoribb haszonállat régiónként", "EN" : "Most popolous religious devotions by regions"},
                                     "extra data": ["ratio of livestock majority","number of livestock majority"]},
                   "ratio of livestock majority":{ "text" : {"HU" : "állatállomány létszáma<br>az emberek számhoz viszonyítva", "EN": "livestock to<br>population ratio"},
                                        "db": 'animals',
                                         "suffix" : {"HU" : " db per fő", "EN": " per capita"}},
                   "number of livestock majority":{ "text" : {"HU" : "állatállomány", "EN": "livestock"},
                                         "db": 'animals',
                                         "suffix" : {"HU" : " db", "EN": ""}},                                         
                   "méhkasok": {'text' : {'HU' : "méhkasok száma", "EN": "number of beehives"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1,  "#FBDE4E"]],
                                        "map title" : {'HU' : "Méhkasok száma", "EN": "Number of Beehives"}},                                        
                   "bivalyok": {'text' : {'HU' : "bivalyok száma", "EN": "number of Buffalos"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#37291A"]],
                                        "map title" : {'HU' : "Bivalyok száma", "EN": "Number of Buffalos"}},                                        
                   "juhok": {'text' : {'HU' : "juhok száma", "EN": "number of sheeps"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#3C6EF6"]],                                        
                                        "map title" : {'HU' : "Juhok száma", "EN": "Number of Sheeps"}},
                   "szarvasmarhák": {'text' : {'HU' : "szarvasmarhák száma", "EN": "number of cattles"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#AA7B49"]],                                        
                                        "map title" : {'HU' : "Szarvasmarhák száma", "EN": "Number of Cattles"}},  
                   "sertések": {'text' : {'HU' : "sertések száma", "EN": "number of pigs"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#FF4375"]],                                        
                                        "map title" : {'HU' : "Sertések száma", "EN": "Number of Pigs"}},   
                   "kecskék" : {'text' : {'HU' : "kecskék száma", "EN": "number of goats"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#52B929"]],                                        
                                        "map title" : {'HU' : "Kecskék száma", "EN": "Number of Goats"}},
                   "szamarak" : {'text' : {'HU' : "kecskék száma", "EN": "number of goats"},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'], [1, "#52B929"]],                                        
                                        "map title" : {'HU' : "Kecskék száma", "EN": "Number of Goats"}},                                                                                                                                                               
                   "lovak": {"text" : {"HU" : "lovak száma", "EN": "number of horses"},
                                     "sort_type" : "intensive property",
                                     "db" : 'religions',
                                     "suffix" : {"HU" : "", "EN": ""},
                                     "theme" :   [[0, 'rgb(255,255,255)'], [1, "#FFB86C"]],
                                     "bar_theme" :  {"könnyű kanca" : "#FFD000",
                                                    "könnyű herélt" : "#FFA600",
                                                    "könnyű csődör": "#FF8000",
                                                    "nehéz kanca": "#FFAAAA",
                                                    "nehéz csődör": "#FF0000",
                                                    "nehéz herélt": "#FF6666",
                                                    "csikó (3 év alatti)" : "#00AAAA"},                                                     
                                     "melt_down" : True,     
                                     "melt_down abs_rel": "livestock_comparison",                                     
                                     "melt_down old_columns" : ss.horse_columns,
                                     "melt_down summmary" : "lovak",                                     
                                     "melt_down new_columns" :  "lófajták",
                                     "melt_down value_name" : "livestock",  
                                     "melt_down population" : {"HU": " darabszáma", "EN": ""}, 
                                     "melt_down population_unit" : {"HU": "db", "EN" : ""},
                                     "melt_down yaxis_title_text" : {"HU": "Lóállomány összetétele", "EN" : "Composition of horse livestock"},                                                                   
                                     "melt_down sidebar_title" : {"HU" : "","EN": ""}, 
                                     "map title": {"HU" : "legnagyobb vallási felekezet régiónként", "EN" : "most popolous religious devotions by regions"}}}
    


    literacy_map = {"female" : {"color" : [[0, 'rgb(255,255,255)'], [1,'rgb(255,0,0)']],
                              "text_extension" : {"HU" : "nők között", "EN" : "female population"}},
                    "male" :  {"color" : [[0, 'rgb(255,255,255)'], [1,'rgb(0,0,255)']],
                                 "text_extension" : {"HU" : "férfiak között", "EN" : "male population"}},
                    "sum" : {"color" : [[0, 'rgb(255,255,255)'], [1,'rgb(127,0,255)']],
                             "text_extension" : {"HU" : "korcsoportban", "EN" : "the whole population"}}}

    for literacy in literacy_map.keys():
        ss.legend[f"above 6 pop {literacy}"] = {'text' : {"HU" : f"teljes lakosság<br>létszáma a 6 évesnél<br>idősebb<br>{literacy_map[literacy]['text_extension']['HU']}","EN": f"{literacy_map[literacy]['text_extension']['EN']}<br>above age 6" },
                                                "db" : 'literacy',
                                                 "suffix" : {"HU" : " fő", "EN": ""}}

        ss.legend[f"literate {literacy}"] = {'text' : {'HU' : f"írni-olvasni tudók<br>száma a 6 évesnél<br>idősebb<br>{literacy_map[literacy]['text_extension']['HU']}", "EN": f"literacy in<br>{literacy_map[literacy]['text_extension']['EN']}<br>above age 6"},
                                                    "db" : 'literacy',
                                                    "suffix" : {"HU" : " fő", "EN": ""},
                                                    "map title" : {'HU' : f"Írni-olvasni tudók aránya a 6 évesnél idősebb {literacy_map[literacy]['text_extension']['HU']}", "EN": f"Literacy in {literacy_map[literacy]['text_extension']['EN']} above age 6"}}

        ss.legend[f"literate {literacy} ratio"] = {'text' : {'HU' : f"írni-olvasni tudók<br>aránya a 6 évesnél<br>idősebb<br>{literacy_map[literacy]['text_extension']['HU']}", "EN": f"literacy ratio in<br>{literacy_map[literacy]['text_extension']['EN']}<br>above age 6"},
                                                    "db" : 'literacy',
                                                    "sort_type" : "intensive property",
                                                    "suffix" : {"HU" : " %", "EN": " %"},
                                                    "theme" : literacy_map[literacy]['color'],
                                                    "map title" : {'HU' : f"Írni-olvasni tudók aránya a 6 évesnél idősebb {literacy_map[literacy]['text_extension']['HU']}", "EN": f"Literacy ratio in {literacy_map[literacy]['text_extension']['EN']} above age 6"},
                                                    "extra data": [f"literate {literacy}",f"above 6 pop {literacy}"]}
        
        ss.legend[f"partially literate {literacy}"] = {'text' : {'HU' : f"olvasni tudók<br>száma a 6 évesnél<br>idősebb<br>{literacy_map[literacy]['text_extension']['HU']}", "EN": f"literacy in<br>{literacy_map[literacy]['text_extension']['EN']}<br>above age 6"},
                                                    "db" : 'literacy',
                                                    "suffix" : {"HU" : " fő", "EN": ""},
                                                    "map title" : {'HU' : f"Olvasni tudók aránya a 6 évesnél idősebb {literacy_map[literacy]['text_extension']['HU']}", "EN": f"Literacy in {literacy_map[literacy]['text_extension']['EN']} above age 6"}}        
        
        ss.legend[f"partially literate {literacy} ratio"] = {'text' : {'HU' : f"olvasni tudók<br>aránya a 6 évesnél<br>idősebb<br>{literacy_map[literacy]['text_extension']['HU']}", "EN": f"literacy in<br>{literacy_map[literacy]['text_extension']['EN']}<br>above age 6,<br>including partial<br>literacy"},
                                                    "db" : 'literacy',
                                                    "sort_type" : "intensive property",
                                                    "suffix" : {"HU" : " %", "EN": " %"},
                                                    "theme" : literacy_map[literacy]['color'],
                                                    "map title" : {'HU' : f"Olvasni tudók aránya a 6 évesnél idősebb {literacy_map[literacy]['text_extension']['HU']}", "EN": f"Literacy in {literacy_map[literacy]['text_extension']['EN']} above age 6, including partial literacy (read-only)"},
                                                    "extra data": [f"partially literate {literacy}",f"above 6 pop {literacy}"]}        
        
    ss.legend[f"literate gender ratio"] = {'text' : {'HU' : f"nők aránya az<br>írni-olvasni tudók<br>között", "EN": f"Female ratio<br>in the group<br>of literate population"},
                                                "db" : 'literacy',
                                                "sort_type" : "intensive property",
                                                "suffix" : {"HU" : " %", "EN": " %"},
                                                "theme" : [[0, 'rgb(0,0,128)'], [0.40, 'rgb(0,0,255)'],[0.495, 'rgb(191,191,255)'],[0.5, 'rgb(255,223,255)'],[0.505,'rgb(255,191,191)'],[0.60,'rgb(255,0,0)'],[1,'rgb(128,0,0)']],
                                                "map title" : {'HU' : f"Nők aránya az írni-olvasni tudók között", "EN": f"Female ratio in the group of literate population"},
                                                "extra data" : ["literate female", "literate male"]}        
    
    ss.legend[f"partially literate gender ratio"] = {'text' : {'HU' : f"nők aránya az<br>olvasni tudók<br>között", "EN": f"female ratio<br>in the group<br>of literate population,<br>including partial literacy"},
                                                "db" : 'literacy',
                                                "sort_type" : "intensive property",
                                                "suffix" : {"HU" : " %", "EN": " %"},
                                                "theme" : [[0, 'rgb(0,0,128)'], [0.40, 'rgb(0,0,255)'],[0.495, 'rgb(191,191,255)'],[0.5, 'rgb(255,223,255)'],[0.505,'rgb(255,191,191)'],[0.60,'rgb(255,0,0)'],[1,'rgb(128,0,0)']],
                                                "map title" : {'HU' : f"Nők aránya az olvasni tudók között", "EN": f"Female ratio in the group of literate population, including partial literacy"},
                                                "extra data" : ["partially literate female", "partially literate male"]}            

    tab_of_religions  = 0

    for s in range(len(ss.tab_list)):
        if ss.tab_list[s]["caption"]["EN"] == "Religious Census":
            tab_of_religions = s
            break


    for religion, r_color in ss.legend["majority"]["theme"].items():
        ss.legend[religion + " arány"] = {"text" : {"HU" : religion + "<br>népesség aránya", "EN" : "Ratio of<br>" + ss.value_replacement_EN[religion] + "<br>population"},
                                          "db" : 'religions',
                                          "sort_type" : "intensive property",
                                         "suffix" : {"HU" : " %", "EN": " %"},
                                         "theme" : [[0, 'rgb(255,255,255)'],[1, r_color]],
                                         "map title": {"HU" : religion.capitalize() + " népesség aránya", "EN" : "Ratio of " + ss.value_replacement_EN[religion].capitalize() + " population"},
                                         "extra data": [religion]}
        ss.legend[religion] = { "text" : {"HU" : religion.capitalize() + "<br>népesség", "EN": ss.value_replacement_EN[religion].capitalize() + "<br>population"},
                                "db": 'religions',
                                "sort_type" : "intensive property",
                                "theme" : [[0, 'rgb(255,255,255)'],[1, r_color]],
                                "map title": {"HU" : religion.capitalize() + " népesség", "EN" : "" + ss.value_replacement_EN[religion].capitalize() + " population"},
                                "suffix" : {"HU" : " fő", "EN": ""},
                                "extra data": [religion + " arány"]}
        ss.tab_list[tab_of_religions]["buttons"].append({"caption": {"HU" : religion.capitalize(), "EN" : ss.value_replacement_EN[religion].capitalize()}, "value": religion})

    ss.livestock_types_aslist = {}

    ss.livestock_types_aslist = list(ss.legend["livestock majority"]["theme"].keys())
    new_livestock_list = ss.livestock_types_aslist.copy()[1:]
    ss.legend["livestock majority"]["melt_down old_columns"] = new_livestock_list
    ss.animals["livestock"] = ss.animals[ss.livestock_types_aslist].sum(axis = 1)
    ss.animals = pd.merge(ss.animals, ss.pop_area[['county','subarea','subarea type','népesség']],  how = 'left', on = ['county','subarea','subarea type']).fillna(0)
    for animal in ss.livestock_types_aslist:
        ss.animals[animal + " arány"] = (ss.animals[animal] / ss.animals["népesség"]).round(3)

    ss.animals["livestock majority"] = ss.animals[ss.livestock_types_aslist].idxmax(axis = 1)
    ss.animals["number of livestock majority"] = ss.animals[ss.livestock_types_aslist].max(axis = 1)
    ss.animals["ratio of livestock majority"] = (ss.animals["number of livestock majority"] / ss.animals["népesség"]).round(3)

    for s in range(len(ss.tab_list)):
        if ss.tab_list[s]["caption"]["EN"] == "Livestock":
            tab_of_livestock = s
            break

    for livestock in ss.livestock_types_aslist:
        ss.legend[livestock] = {'text' : {'HU' : livestock + " száma", "EN": "number<br>of " + ss.value_replacement_EN[livestock]},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db", "EN": ""},
                                        "theme" : [[0, 'rgb(255,255,255)'],[1,ss.legend["livestock majority"]["theme"][livestock]]],                                        
                                        "map title" : {'HU' : livestock.capitalize() + " száma", "EN": "Number of " + ss.value_replacement_EN[livestock].capitalize()},
                                        "extra data" : [livestock + " arány"]}
        
        ss.legend[livestock + " arány"] = {'text' : {'HU' : livestock + " aránya", "EN": "ratio of " + ss.value_replacement_EN[livestock]},
                                        "db" : 'animals',
                                        "sort_type" : "intensive property",
                                        "suffix" : {"HU" : " db per fő", "EN": " per capita"},
                                        "theme" : [[0, 'rgb(255,255,255)'],[1,ss.legend["livestock majority"]["theme"][livestock]]],                                        
                                        "map title" : {'HU' : livestock.capitalize() + " száma", "EN": "Number of " + ss.value_replacement_EN[livestock].capitalize()},
                                        "extra data" : [livestock]}        
        ss.tab_list[tab_of_livestock]["buttons"].append({"caption": {"HU" : livestock.capitalize(), "EN" : ss.value_replacement_EN[livestock].capitalize()}, "value": livestock})
    #list_of_dicts = ["region", "government", "majority","lovak"]
    list_of_dicts = list(ss.legend.keys())

    for i in list_of_dicts:
        dict_name = ss.legend[i].get("theme",{})
        new_dict = {}
        if isinstance(dict_name,dict):
            if len(dict_name.items()) > 0:        
                for key, value in dict_name.items():
                    new_key = ss.value_replacement_EN.get(key,"")
                    if (new_key != ""):
                        new_dict[new_key] = value

                for key, value in new_dict.items():
                    dict_name[key] = value

    for i in list_of_dicts:
        dict_name = ss.legend[i].get("bar_theme",{})
        new_dict = {}
        if isinstance(dict_name,dict):        
            if len(dict_name.items()) > 0:
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
                    if buttonlist[i]["value"] is True:
                        ss[session_state_variable] = (ss[session_state_variable] == False)
                    else:
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
    if (ss.legend[sort_by].get("melt_down",False) == True):
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
        df_long = filtered_df[["county",ss.legend[sort_by]["melt_down summmary"]] + ss.legend[sort_by]["melt_down old_columns"]]
        df_long = df_long.melt(id_vars = df_long.columns.tolist()[:2],value_vars = df_long.columns[2:], var_name = ss.legend[sort_by]["melt_down new_columns"], value_name = ss.legend[sort_by]["melt_down value_name"])    
        df_long["ratio"] = (df_long[ss.legend[sort_by]["melt_down value_name"]] / df_long[ss.legend[sort_by]["melt_down summmary"]] * ss.legend[sort_by]["melt_down relative_factor"]).round(3)
        value_replacement = ss.value_replacement_EN
        #if "Fiume város és kerület" in value_replacement:
        #    del value_replacement["Fiume város és kerület"]
        if (ss.selected_language != "HU"):
            df_long.replace(value_replacement, inplace = True)           
        if ss[ss.legend[sort_by]["melt_down abs_rel"]] == "absolute":
            sub_sort = ss.legend[sort_by]["melt_down value_name"]
        else:
            sub_sort = "ratio"
        fig = px.bar(df_long,
                x="county",
                y= sub_sort,
                orientation='v',
                color = ss.legend[sort_by]["melt_down new_columns"],
                height = side_chart_hight,
                width = 450,
                color_discrete_map = ss.legend[sort_by].get("bar_theme",ss.legend[sort_by]["theme"]),
                custom_data = ["county", ss.legend[sort_by]["melt_down new_columns"],  ss.legend[sort_by]["melt_down value_name"], "ratio"])
        fig.update_layout(yaxis_title_text = ss.legend[sort_by]["melt_down yaxis_title_text"][ss.selected_language],
            xaxis_title_text = ("" if (counties_selected == False) else ("megye" if ss.selected_language == "HU" else ("county"))),
            legend=dict(
            title = ss.legend[sort_by]["melt_down sidebar_title"][ss.selected_language]))
        fig.update_traces(width = 0.9,
            hovertemplate ="<b>%{customdata[0]}</b><br>"+
                                        "<br>" + 
                                        "%{customdata[1]}"+  ss.legend[sort_by]["melt_down population"][ss.selected_language]  + ":<br>"+
                                        "<b>%{customdata[2]}</b>" + ss.legend[sort_by]["melt_down population_unit"][ss.selected_language] + "<br><br>" + 
                                        "ratio:<br>"+
                                        "<b>%{customdata[3]}</b>" + ss.legend[sort_by]["melt_down relative_unit"][ss.selected_language] + 
                                        "<extra></extra>") 
        st.plotly_chart(fig, theme=None)         
    elif counties_selected == False:
        if (ss.selected_language == "HU"):
            st.markdown("#### Régiónkénti megoszlás")
        elif (ss.selected_language == "EN"):
            st.markdown("#### Distribution by regions")
        sort_type = "units"      
        if (sort_by == "népsűrűség") | (sort_by == "nemek aránya") | (sort_by == "kor aránya") | (ss.tab_list[ss.selected_tab]["caption"]["EN"].find("Religious Census") >= 0) | (sort_by == "literate male ratio"):
            sort_type = "intensive property"  
        sort_type = ss.legend[sort_by]['sort_type']
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
            filtered_df = filtered_df[filtered_df["subarea type"] == "ország"]

            extras = ss.legend[sort_by].get("extra data",[])
            hover_template = ("<b>%{customdata[0]}</b><br>"+
                                            "<br>" + 
                                            "<b>" + ss.legend[sort_by]["text"][ss.selected_language] + ":</b><br>"+
                                            "<b>%{customdata[1]}" + ss.legend[sort_by]["suffix"][ss.selected_language] + "</b>")
            for n,e in enumerate(extras):
                hover_template = hover_template + "<br><br>" + (
                    "<i>" + ss.legend[e]["text"][ss.selected_language] + "</i>:<br>"+
                    "%{customdata[" + str(n + 2) + "]}" + ss.legend[e]["suffix"][ss.selected_language])
            hover_template = hover_template + "<extra></extra>" 
            hover_template = hover_template.replace("(AGE_FILTER)",age_filter_text())

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
        if (sort_by == "nemek aránya") | (sort_by == "literate gender ratio") | (sort_by == "partially literate gender ratio"):
            range_color=(0, 100)
        else:
            db2 = ss[ss.legend[sort_by]["db"]]
            filtered_df2 = db2[db2["subarea type"] == "megye"]
            if (sort_by == "népsűrűség"):
                filtered_df2 = filtered_df2[filtered_df2["county"] != "Fiume város és kerület"]
            max_value = max(filtered_df2[sort_by])            
            range_color=(0, max_value)
        extras = ss.legend[sort_by].get("extra data",[])
        hover_template = ("<b>%{customdata[0]}</b><br>" +
                                        "<br>" + 
                                        "<b>" +ss.legend[sort_by]["text"][ss.selected_language] + ":</b><br>"+
                                        "<b>%{customdata[1]}" + ss.legend[sort_by]["suffix"][ss.selected_language] + "</b>")
        for n,e in enumerate(extras):
            hover_template = hover_template + "<br><br>" + (
                "<i>" + ss.legend[e]["text"][ss.selected_language] + "</i>:<br>"+
                "%{customdata[" + str(n + 2) + "]}" + ss.legend[e]["suffix"][ss.selected_language])
        hover_template = hover_template + "<extra></extra>"
        hover_template = hover_template.replace("(AGE_FILTER)",age_filter_text())                                                   
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
            xaxis_title_text = ("" if (counties_selected == False) else ("megye" if ss.selected_language == "HU" else ("county"))),
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


def age_filter_text():
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
    return age_filter    
    


def draw_map(map_df,sort_by,color_type = "unique coloring"):
    df = map_df[map_df.columns.tolist()[:-1]]
    df[map_df.columns.tolist()[-1]] = map_df[map_df.columns.tolist()[-1]]
    value_replacement = ss.value_replacement_EN
    if (ss.selected_language != "HU"):
        df.replace(value_replacement, inplace = True) 
        df[df.columns.tolist()[0]] = map_df[map_df.columns.tolist()[0]]
    map_title = ss.legend[sort_by]["map title"][ss.selected_language]

    map_title = map_title.replace("(AGE_FILTER)",age_filter_text())
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
        elif (sort_by == "nemek aránya") | (sort_by == "literate gender ratio") | (sort_by == "partially literate gender ratio"):
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
    hover_template = hover_template.replace("(AGE_FILTER)",age_filter_text())

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

# Style
#css = """
#.st-key-my_blue_container {
#    background-color: rgba(100, 100, 200, 0.3);
#}
#"""

#st.html(f"<style>{css}</style>")
#with st.container(key="my_blue_container"):

dashboard = st.container(border = True, key="my_blue_container")    
with dashboard:
    button_list(ss.tab_list,"selected_tab")
    tab_name = ss.tab_list[ss.selected_tab]["caption"]["EN"]
    selected_button_name = "tab" + str(ss.selected_tab) + "button"
    selected_button_value = ss[selected_button_name] 
    st.divider()
    if (tab_name.find("Age and Gender Census") >= 0):
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
                ss.f_county_filter_for_age = f_county_filter_for_age.copy(deep = True)
                button_list(ss.f_county_filter_for_age)                      
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
        with det_col:
            kpi_container = st.container(border = True)
            with kpi_container:
                kpi_label = {"HU" : "Lakosság", "EN" : "Population"}
                kpi_metric = {"HU" : "fő", "EN" : ""}
                st.metric(label = kpi_label[ss.selected_language],value = "14,776,383" + " " + kpi_metric[ss.selected_language])
            kpi_container = st.container(border = True)
            with kpi_container:                
                kpi_label = {"HU" : "Terület", "EN" : "Area"}
                st.metric(label = kpi_label[ss.selected_language],value = "308,360.23 km²")      
            kpi_container = st.container(border = True)
            with kpi_container:
                kpi_label = {"HU" : "Népsűrűség", "EN" : "Population Density"}
                kpi_metric = {"HU" : "fő/km²", "EN" : "per km²"}
                st.metric(label = kpi_label[ss.selected_language],value = "47.92" + " " + kpi_metric[ss.selected_language])                          

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
                button_list(ss.religion_comparison_buttons["buttons"], "religion_comparison")                
                draw_sidechart(filtered_df, sort_by, 565, counties_selected)   
    elif (tab_name.find("Livestock") >= 0):
        map_col, det_col = st.columns([10,4],gap = "small")
        with map_col:
            map_container = st.container(border = True) 
            with map_container:   
                button_list()
                if selected_button_value == "livestock majority":
                    sort_by = "livestock majority"
                elif ss.livestock_comparison == "relative":
                    sort_by = selected_button_value + " arány"
                else:
                    sort_by = selected_button_value
                map = draw_map(ss.animals, sort_by, ("unique coloring" if (selected_button_value == "livestock majority") else "value"))
                selected_counties = st.plotly_chart(map, use_container_width=True, on_select ="rerun")                
        counties_selected = False   
        filtered_df, counties_selected, selected_counties_list = filter_stand_alone_df(ss.animals, selected_counties)     
        with det_col:
            sidechart_container = st.container(border = True)      
            with sidechart_container:
                button_list(ss.livestock_comparison_buttons["buttons"], "livestock_comparison")                
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
    elif (tab_name.find("Literacy") >= 0):
        map_col, det_col = st.columns([10,4],gap = "small")
        with map_col:
            map_container = st.container(border = True) 
            with map_container:        
                button_list()
                map = draw_map(ss.literacy, ("partially " if ss.partial_literacy_included else "")  + selected_button_value, "values")
                selected_counties = st.plotly_chart(map, use_container_width=True, on_select ="rerun")
        counties_selected = False
        filtered_df, counties_selected, selected_counties_list = filter_stand_alone_df(ss.literacy, selected_counties)
        with det_col:
            sidechart_container = st.container(border = True)      
            with sidechart_container:
                button_list(ss. partial_literacy_included_buttons["buttons"], "partial_literacy_included")
                draw_sidechart(filtered_df,("partially " if ss.partial_literacy_included else "")  + selected_button_value, 399, counties_selected)


        #if (ss.selected_language == "HU"):
        #    st.markdown("#### Válassz ki néhány megyét az összehasonlításukhoz [SHIFT + Click]")                            
        #elif (ss.selected_language == "EN"):
        #    st.markdown("#### Select some counties to compare [SHIFT + Click]")                    

        #if (counties_selected):
        #    for county in selected_counties_list:
        #        st.markdown("### " + county)                        
        #        st.dataframe(filtered_df[filtered_df["county"] == county])
        #else:
        #    st.dataframe(filtered_df)                    
                        
