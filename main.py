import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import configparser
import requests
import json
from datetime import datetime, timedelta

# Parametres de configuration de la page 
st.set_page_config(
    page_title="",
    page_icon="",
    layout="wide"
    
)



with st.container() :

 st.title("Application de prévision météreologique Météo")

col1, col2, col3 = st.columns(3)




def local_css(file_name) :
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css") 

def get_user_ip():
    ip_url = "https://api.ipify.org?format=json"
    try:
        ip_response = requests.get(ip_url)
        return ip_response.json()["ip"]
    except requests.exceptions.RequestException as e:
        st.write("Impossible de récupérer l'adresse IP de l'utilisateur.")
        st.write("Erreur:", e)
        return None

def get_location(ip):
    api_key = "aee7849fb61944aaa17409660529bc5d"
    geolocation_url = "https://api.ipgeolocation.io/ipgeo?apiKey={}&ip={}".format(api_key,ip)
    try:
        geolocation_response = requests.get(geolocation_url)
        location = geolocation_response.json()
        return location
    except requests.exceptions.RequestException as e:
        st.write("Impossible de récupérer les informations de géolocalisation.")
        st.write("Erreur:", e)
        return None

def get_city_coordinates(city):
    api_key = "26788b89116e49fc8199d5798a73d02d"
    geocode_url = "https://api.opencagedata.com/geocode/v1/json?q={}&key={}".format(city, api_key)
    try:
        geocode_response = requests.get(geocode_url)
        lat = geocode_response.json()["results"][0]["geometry"]["lat"]
        lon = geocode_response.json()["results"][0]["geometry"]["lng"]
        return lat, lon
    except requests.exceptions.RequestException as e:
        st.write("Impossible de récupérer les coordonnées de la ville.")
        st.write("Erreur:", e)
        return None

def get_weather(lat, lon):
    api_key = "8ad73f301dd774a37a0a13c03ed2f8f1"
    url = "http://api.openweathermap.org/data/2.5/weather?lat={}&units=metric&lon={}&appid={}".format(lat, lon, api_key)
    try:
        r = requests.get(url)
        data = r.json()
        icon_code = data["weather"][0]["icon"]
        data["icon_url"] = "http://openweathermap.org/img/wn/{}@2x.png".format(icon_code)
        return data
    except requests.exceptions.RequestException as e:
        st.write("Impossible de récupérer les données météo.")
        st.write("Erreur:", e)
        return None


def get_forecast_weather(city):
    api_key = "8ad73f301dd774a37a0a13c03ed2f8f1"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}".format(city, api_key)
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()
    elements = []
    for forecast in forecast_data['list']:
        datee = datetime.utcfromtimestamp(forecast['dt'])
        if datee.hour%6==0:
            elements.append(forecast)
    
    for forecast in elements:
        icon_code = forecast["weather"][0]["icon"]
        forecast["icon_url"] = "http://openweathermap.org/img/wn/{}@2x.png".format(icon_code)
    return elements


def weather_app():
    ip = get_user_ip()
    location = get_location(ip)
    if location:
        lat, lon = location['latitude'], location['longitude'] 
        data = get_weather(lat, lon)
        if data:
            try:

                with col1: 
                    col1.success("Meteo Actuelle")
                    st.write("Récupération de la météo à votre position actuelle:")
                    st.image(data["icon_url"], width=100)
                    st.write("Température: {}°C".format(data["main"]["temp"]))
                    st.write("Humidité: {}%".format(data["main"]["humidity"]))
                    st.write("Pression: {} hPa".format(data["main"]["pressure"]))
            except KeyError:
                st.write("Données météorologiques non disponibles pour votre position actuelle.")
    else:
        st.write("Impossible de récupérer les informations de géolocalisation.")
    with col2:   
        city = st.text_input("Entrez le nom de la ville:")
        btn_Valider = st.button("Valider") 
    if btn_Valider: 
        lat, lon = get_city_coordinates(city)
        if lat and lon:
            data = get_weather(lat, lon)
            if data:
                with col3 :
                    st.write("Météo à {}:".format(city))
                    st.image(data["icon_url"], width=100)
                    st.write("Température: {}°C".format(data["main"]["temp"]))
                    st.write("Humidité: {}%".format(data["main"]["humidity"]))
                    st.write("Pression: {} hPa".format(data["main"]["pressure"]))
                forecast_data = get_forecast_weather(city)

                containt = st.container()

                with containt :
                    st.write("Prévisions météo pour les prochains 5 jours:")
                    cols = st.columns(20)
                    a = 0
                    for day in forecast_data:
                            with containt :    
                                with cols[a]:
                                    st.image(data["icon_url"], width=100)
                                    st.write("Date: {}".format(day["dt_txt"]))
                                    st.write("Température: {}°C".format(day["main"]["temp"]))
                                    st.write("Humidité: {}%".format(day["main"]["humidity"]))
                                    a = a + 1
        else:
            st.write("Impossible de récupérer les coordonnées de la ville.")
            st.write("Veuillez remplacer 'YOUR_API_KEY' par votre propre clé API")
if __name__ == "__main__":
    weather_app()