import pandas as pd
import re
from geopy.geocoders import Nominatim 
import streamlit as st
from matplotlib import pyplot as mp
import plotly.express as px
import matplotlib.pyplot as plt
import folium as f
from streamlit_folium import folium_static
from folium.plugins import  MarkerCluster
import os

# leitura das planilhas
data_eats_order_details = pd.read_csv('Data Export Dashboard/Uber Data/Eats/eats_order_details.csv')
data_eats_restaurant_names = pd.read_csv('Data Export Dashboard/Uber Data/Eats/eats_restaurant_names.csv')
data_rider_app_analytics = pd.read_csv('Data Export Dashboard/Uber Data/Rider/rider_app_analytics-0.csv')
data_trips_data = pd.read_csv('Data Export Dashboard/Uber Data/Rider/trips_data.csv')
data_profile_data = pd.read_csv('Data Export Dashboard/Uber Data/Account and Profile/profile_data.csv')


# atraves do regex extrai da data do timezone

# through regex extract date from time zone
def extact_dates_UTC(array_UTC):
    dates = []
    for i in range(len(array_UTC)):
        x = re.search("\d{4}[-]\d{2}[-]\d{2}",array_UTC[i][1])
        dates.append(x.group())
    return dates    

# atraves do regex extrai nome de ruas do nome do estabelecimento
# cria coluna e insere as informações de latetude e longitude

# through the regex extracts street names from the name of the establishment
# create column and insert latetitude and longitude information
def extract_coordinates():
    data_eats_restaurant_names['lat'] = "N/A"
    data_eats_restaurant_names['long'] = "N/A"
    for i in range(len(data_eats_restaurant_names)):
        x = re.search("([\w\W])+([\(])([\w\W]+)([\)])",
                      data_eats_restaurant_names.loc[i,"Restaurant Name"])
        geoLoc = Nominatim(user_agent="GetLoc") 
        if x == None:            
            if locname == None:
                data_eats_restaurant_names.loc[i,"lat"] = 0
                data_eats_restaurant_names.loc[i,"long"] = 0
            else:
                data_eats_restaurant_names.loc[i,"lat"] = locname.latitude
                data_eats_restaurant_names.loc[i,"long"] = locname.longitude    
            
        elif x != None:    
            locname = geoLoc.geocode(x.group(3))
            if locname == None:
                data_eats_restaurant_names.loc[i,"lat"] = 0
                data_eats_restaurant_names.loc[i,"long"] = 0
            else:
                data_eats_restaurant_names.loc[i,"lat"] = locname.latitude
                data_eats_restaurant_names.loc[i,"long"] = locname.longitude    
    data_eats_restaurant_names.to_csv("data_er_names_coor.csv", index=False)            

#gera um arquivo se não existe o planilha com as coordenas

#generate a file if the spreadsheet with the coordinates does not exist
def create_data_coor():
    if os.path.isfile('data_er_names_coor.csv') != True:
        extract_coordinates()
        data_eats_restaurant_names.to_csv("data_er_names_coor.csv", index=False)

# array da extração de data do UTC

# UTC date extraction array
array_utc = data_eats_order_details["Order Time"].reset_index().values

# crie um coluna com os datas do utc

# create a column with the utc dates
data_eats_order_details['dates'] = extact_dates_UTC(array_utc)

#crie um coluna extrai o ano da data e plotei

#create a column extract the year from the date and plot it
data_eats_order_details['year'] = pd.to_datetime(data_eats_order_details['dates']).dt.year

# peguei o ano maximo e minimo

# got the maximum and minimum year
min_dates = int(data_eats_order_details['year'].min())
max_dates = int(data_eats_order_details['year'].max())

#unindo dataframes

# merging dataframes
data_eats_od_rn = pd.merge(data_eats_order_details,data_eats_restaurant_names,on='Restaurant ID',how='outer')


#somando preços de acordo com os nomes dos restaurantes

#adding prices according to restaurant names
data_table_map = data_eats_od_rn[['Restaurant Name', 'Order Price']].groupby('Restaurant Name').sum().reset_index()


# titulos e subtitulos

# titles and subtitles
st.title(data_profile_data.iloc[0,0] + ' ' + data_profile_data.iloc[0,1] + ' ' + 'Data')
st.header('eats_order_details')
st.sidebar.title('filters')
st.sidebar.subheader('Select Max Dates')

# crie o slider dentro do sidebar

# create the slider inside the sidebar
f_dates = st.sidebar.slider('dates', min_dates, max_dates, min_dates)

# criei o filtro

# create the filters
df_eats_order_details = data_eats_order_details.loc[data_eats_order_details['year'] <= f_dates]

#crie o grop by para o valor de x e y do grafico

#create the grop by for the x and y value of the graph
df_price_data = df_eats_order_details[['dates','Order Price']].groupby('dates').sum().reset_index()

# subtitlers
st.subheader('chart and price table by date')

#criei o grafico

#create the grafics
fig = px.area( df_price_data,x ='dates', y ='Order Price')

# criando tabelas

#creating tables
st.dataframe(df_price_data, width=800)

# plotei o grafico

#plot the grapics
st.plotly_chart(fig, use_container_width=True)

#subtitulos

#subtitles
st.header('eats_restaurants_name')


# subtitulos
st.subheader('Price disity')


# chamando função

# calling function
create_data_coor()
data_er_names_coor=pd.read_csv('data_er_names_coor.csv')
data_eats_od_rn_coord = pd.merge(data_eats_order_details,data_er_names_coor,on='Restaurant ID',how='outer')

# criando grafico

#creating grapics
region_price_map = f.Map(
    # fazendo media de coordenas para saber onde
    # em que região o grafico vai aparecer primeiro
    
    # averaging coordinates to know where
    # in which region the graph will appear first
    location=[data_eats_od_rn_coord['lat'].mean(), 
    data_eats_od_rn_coord['long'].mean()],
    #zoom
    default_zoom_start=1)

# marcadores

#bookmarks
marker_cluster = MarkerCluster().add_to( region_price_map)

# em cada interação da repetição pega as coordenas
# preco, nome do restaurante

# in each iteration of the repetition get the coordinates
# price, name of restaurant
for name,row  in data_eats_od_rn_coord.iterrows():
    f.Marker([row['lat'], row['long']],
             popup='Price CAD: {0}, Restaurant Name: {1} '.format( 
                                row['Order Price'], 
                                row['Restaurant Name'])).add_to( marker_cluster)
# faz o mapa aparecer

#make the map appear
folium_static(region_price_map)


# subtitulos

# subtitles
st.subheader('table of expenses by addresses' )


# tabela

#table
st.dataframe(data_table_map)