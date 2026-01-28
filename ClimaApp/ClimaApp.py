#!/usr/bin/python
# -*- coding: latin-1 -*-
from cProfile import label
import email
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import opencage
import tkinter as tk
from tkinter import Entry, ttk, messagebox
from plyer import notification
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# print('Insira o seu email:')
# email = str(input()) 

#função para enviar email
def send_email(subject, body, entry_email):
    from_email = "contadeavisos@gmail.com"
    from_password = "wiwz wnwm ieeu tsuq"

    msg = MIMEMultipart()
    msg['From'] = from_email 
    msg['To'] = email
    msg['Subject'] = subject 

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, from_password)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

# Funções comuns para obtenção de latitude/longitude e dados meteorológicos
def obter_lat_lng(localidade):
    try:
        geolocator = Nominatim(user_agent="Weather App")
        location = geolocator.geocode(localidade, timeout=10)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            return latitude, longitude
        else:
            print("Não foi possível obter a localização com Nominatim. Tentando com OpenCage...")
            return obter_lat_lng_opencage(localidade)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Erro ao obter a localização com Nominatim: {e}. Tentando com OpenCage...")
        return obter_lat_lng_opencage(localidade)

def obter_lat_lng_opencage(localidade):
    key = '4cdf892c9f7b4550a2f6e2b7f644a103'  
    geocoder = opencage.Geocoder(key)
    try:
        result = geocoder.geocode(localidade)
        if result and result['results']:
            latitude = result['results'][0]['geometry']['lat']
            longitude = result['results'][0]['geometry']['lng']
            return latitude, longitude
        else:
            print("Não foi possível obter a localização com OpenCage.")
            return None, None
    except Exception as e:
        print(f"Erro ao obter a localização com OpenCage: {e}")
        return None, None
#função para obeter os dados da previsão do tempo
def get_weather_forecast(lat, long, variables):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ",".join(variables)
    }
    
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_data = {
            "datetime": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        for i, variable in enumerate(variables):
            values = hourly.Variables(i).ValuesAsNumpy()
            hourly_data[variable] = values

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Isolar os valores da coluna wind_speed_100m
        if 'wind_speed_100m' in hourly_dataframe.columns:
            wind_speed_values = hourly_dataframe['wind_speed_100m']
            
            mean_wind_speed = wind_speed_values.mean()
            #Enviar notificação para cada categoria do furacão
            if 0 <= mean_wind_speed <= 153 :
                subject=  'Aviso Climático'
                body = 'Alerta de furacão e categoria 1'
                email
                send_email(subject, body,email)
                
            elif 154 <= mean_wind_speed <= 177 :
                subject = 'Aviso Climático'
                body = 'Alerta de furacão e categoria 2'
                email
                send_email(subject, body,email)
                
            elif 178 <= mean_wind_speed <= 208 :
                subject = 'Aviso Climático'
                body =  'Alerta de furacão e categoria 3' 
                email
                send_email(subject, body,email)
                
            elif 209 <= mean_wind_speed <= 251 :
                subject = 'Aviso Climático'
                body  = 'Alerta de furacão e categoria 4'
                email
                send_email(subject, body,email)
              
            elif 252 <= mean_wind_speed  :
                subject = 'Aviso Climático'
                body = 'Alerta de furacão e categoria 5'
                email 
                send_email(subject, body,email)
                
        
        # Isolar os valores da coluna precipitation_probability
        if 'precipitation_probability' in hourly_dataframe.columns:
            precipitation_probability_values = hourly_dataframe['precipitation_probability']
           
            precip_mean = precipitation_probability_values.mean()
            #Enviar notificação para chuva
            if  80 <= precip_mean :
                sujbect =  'Aviso de chuva'
                body = 'Alta probabilidade de chuva e possiveis inchentes, cuidado!'
                email
                send_email(subject, body,email)
                
            
            
        # Isolar os valores da coluna showfall
        if 'snowfall' in hourly_dataframe.columns:
            snowfall_values = hourly_dataframe['snowfall']
            snow_sun = snowfall_values.mean()
            #Enviar notificação para chuva
            if 151 <= snow_sun <= 300 :
                subject = 'Queda de neve'
                body = 'Queda de neve pesada, recomendado não sair de casa'
                email
                send_email(subject, body,email)
                
            elif 301 <= snow_sun :
                subject = 'Queda de neve'
                body = 'Queda de neve muito  pesada, por favor permaneçam nas suas casas'
                email
                send_email (subject, body,email)
                
        #isolar os valores da coluna temperature        
        if 'temperature_2m' in hourly_dataframe.columns:
            temperature_2m_values = hourly_dataframe['temperature_2m']
           
            temp_mean = temperature_2m_values.mean()
            #Enviar notificação para frio/calor extremo
            if  temp_mean <= -1 :
                 subject = 'Aviso de frio'
                 body = 'Temperaturas muito baixas, risco de gelo'
                 email
                 send_email(subject, body,email)
                
            elif  30 <= temp_mean  :
                 subject = 'Aviso de calor'
                 body = 'Temperaturas muito altas, risco de incêndio '
                 email 
                 send_email(subject, body,email)
                 
        return hourly_dataframe

    except Exception as e:
        print(f"Erro ao obter a previsão do tempo: {e}")
        return None

#função para obeter os dados do histórico do tempo
def get_historical_weather(lat, long, start_date, end_date, variables):
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": variables
    }
    
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_data = {
            "datetime": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        for i, variable in enumerate(variables):
            values = hourly.Variables(i).ValuesAsNumpy()
            hourly_data[variable] = values

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        return hourly_dataframe
    except Exception as e:
        print(f"Erro ao obter os dados históricos do tempo: {e}")
        return None
#função que organiza os dados
def format_weather_data(dataframe):
    descriptions = []
    dataframe['date'] = dataframe['datetime'].dt.date  # Converte a coluna de datas para apenas data
    grouped = dataframe.groupby('date')
    
    for date, group in grouped:
        description = f"Data: {date}"
        if 'temperature_2m' in group:
            temp_mean = group['temperature_2m'].mean()
            description += f", Temperatura média: {round(temp_mean)}°C"
        if 'precipitation_probability' in group:
            precip_mean = group['precipitation_probability'].mean()
            description += f", Probabilidade média de precipitação: {precip_mean:.2f}%"
        if 'wind_speed_100m' in group:
            wind_mean = group['wind_speed_100m'].mean()
            description += f", Velocidade média do vento a 100m: {round(wind_mean)} m/s"
        if 'snowfall' in group:
            snow_sum = group['snowfall'].sum()
            description += f", Total de queda de neve: {snow_sum:.2f} mm"
        if 'cloud_cover' in group:
            cloud_mean = group['cloud_cover'].mean()
            description += f", Cobertura média de nuvens: {cloud_mean:.2f}%"
        if 'precipitation' in group:
            prep_mean = group['precipitation'].mean()
            description += f", precipitação: {round(prep_mean)}%"
        descriptions.append(description)
    return "\n".join(descriptions)
#função que mostra os dados de uma data especifica
def display_weather_for_specific_day(dataframe, selected_date):
    selected_date = pd.to_datetime(selected_date).date()
    specific_day_data = dataframe[dataframe['datetime'].dt.date == selected_date]
    
    if specific_day_data.empty:
        return f"Não há dados disponíveis para {selected_date}."
    
    descriptions = []
    for _, row in specific_day_data.iterrows():
        description = f"Hora: {row['datetime'].strftime('%H:%M')}"
        if 'temperature_2m' in row:
            description += f", Temperatura: {round(row['temperature_2m'])}°C"
        if 'precipitation_probability' in row:
            description += f", Probabilidade de precipitação: {row['precipitation_probability']}%"
        if 'wind_speed_100m' in row:
            description += f", Velocidade do vento a 100m: {round(row['wind_speed_100m'])} m/s"
        if 'snowfall' in row:
            description += f", Queda de neve: {row['snowfall']} mm"
        if 'cloud_cover' in row:
            description += f", Cobertura de nuvens: {row['cloud_cover']}%"
        descriptions.append(description)
    
    return "\n".join(descriptions)
#criação da interface
def gui_interface():
    
    def fetch_forecast():
        localidade = entry_localidade.get()
        tipo = combobox_tipo.get()
        specific_date = entry_specific_date.get()
        email = entry_email.get()
        

        selected_variables = [var for var, var_state in variable_states.items() if var_state.get()]

        if not localidade:
            messagebox.showerror("Erro", "Por favor, insira uma localidade.")
            return

        latitude, longitude = obter_lat_lng(localidade)
        if latitude is None or longitude is None:
            messagebox.showerror("Erro", "Não foi possível obter a localização.")
            return

        if tipo == 'Previsão':
            weather_forecast = get_weather_forecast(latitude, longitude, selected_variables)
            if weather_forecast is not None:
                text_output.delete(1.0, tk.END)
                if specific_date:
                    detailed_forecast = display_weather_for_specific_day(weather_forecast, specific_date)
                    text_output.insert(tk.END, detailed_forecast)
                else:
                    formatted_forecast = format_weather_data(weather_forecast)
                    text_output.insert(tk.END, formatted_forecast)
        elif tipo == 'Histórico':
            start_date = entry_start_date.get()
            end_date = entry_end_date.get()
            if not start_date or not end_date:
                messagebox.showerror("Erro", "Por favor, insira as datas de início e término.")
                return

            historical_weather = get_historical_weather(latitude, longitude, start_date, end_date, selected_variables)
            if historical_weather is not None:
                text_output.delete(1.0, tk.END)
                if specific_date:
                    detailed_historical = display_weather_for_specific_day(historical_weather, specific_date)
                    text_output.insert(tk.END, detailed_historical)
                else:
                    formatted_historical = format_weather_data(historical_weather)
                    text_output.insert(tk.END, formatted_historical)
#Atuliza a interface para a previsão e o historico
    def update_fields(*args):
        
        tipo = combobox_tipo.get()
        if tipo == 'Previsão':
            label_specific_date.grid(row=4, column=0, sticky=tk.W)
            entry_specific_date.grid(row=4, column=1, sticky=(tk.W, tk.E))
            label_start_date.grid_remove()
            entry_start_date.grid_remove()
            label_end_date.grid_remove()
            entry_end_date.grid_remove()
        elif tipo == 'Histórico':
            label_specific_date.grid_remove()
            entry_specific_date.grid_remove()
            label_start_date.grid(row=4, column=0, sticky=tk.W)
            entry_start_date.grid(row=4, column=1, sticky=(tk.W, tk.E))
            label_end_date.grid(row=5, column=0, sticky=tk.W)
            entry_end_date.grid(row=5, column=1, sticky=(tk.W, tk.E))

    root = tk.Tk()
    root.title("Weather App")

    variables = ["temperature_2m", "precipitation_probability", "wind_speed_100m", "snowfall", "cloud_cover", "precipitation"]
    variable_states = {var: tk.BooleanVar() for var in variables}

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    #Adiciona o label para introduzir a localidade e posiciona o campo de entrada no grid
    ttk.Label(frame, text="Localidade:").grid(row=0, column=0, sticky=tk.W)
    entry_localidade = ttk.Entry(frame, width=30)
    entry_localidade.grid(row=0, column=1, sticky=(tk.W, tk.E))
    
    #Adiciona a combobox para o utilizador escolher entre a função de previsão e historico e posiciona o campo de entrada no grid
    ttk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W)
    combobox_tipo = ttk.Combobox(frame, values=["Previsão", "Histórico"], state="readonly")
    combobox_tipo.grid(row=1, column=1, sticky=(tk.W, tk.E))
    combobox_tipo.set("Previsão")
    combobox_tipo.bind('<<ComboboxSelected>>', update_fields)

    # Adicionando checkboxes para selecionar variáveis meteorológicas
    variables_frame = ttk.LabelFrame(frame, text="Variáveis Meteorológicas")
    variables_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

    for i, var in enumerate(variables):
        ttk.Checkbutton(variables_frame, text=var.replace("_", " ").capitalize(), variable=variable_states[var]).grid(row=i // 2, column=i % 2, sticky=tk.W)
    
    #Adiciona o label para introduzir o email e Posiciona o campo de entrada no grid
    ttk.Label(frame, text="Introduza o seu e-mail para receber avisos em casos de desastres naturais:").grid(row=2, column=0, sticky=tk.W)
    entry_email = ttk.Entry(frame, width=30)
    entry_email.grid(row=2, column=1, sticky=(tk.W, tk.E))

    #Adiciona o label para analisar os dados de um dia especifico e posiciona o campo de entrada no grid
    label_specific_date = ttk.Label(frame, text="Data específica (opcional, YYYY-MM-DD):")
    label_specific_date.grid(row=4, column=0)
    entry_specific_date = ttk.Entry(frame, width=30)
    entry_specific_date.grid(row=4, column=1)
    
    #Adiciona o label para introduzir a data inicial do hitorico e posiciona o campo de entrada no grid
    label_start_date = ttk.Label(frame, text="Data de início (YYYY-MM-DD):")
    label_start_date.grid(row=5, column=0, sticky=tk.W)
    entry_start_date = ttk.Entry(frame, width=30)
    entry_start_date.grid(row=5, column=1, sticky=(tk.W, tk.E))
    
    #Adiciona o label para introduzir a data final do hitorico e posiciona o campo de entrada no grid
    label_end_date = ttk.Label(frame, text="Data de término (YYYY-MM-DD):")
    label_end_date.grid(row=6, column=0, sticky=tk.W)
    entry_end_date = ttk.Entry(frame, width=30)
    entry_end_date.grid(row=6, column=1, sticky=(tk.W, tk.E))
    
    #Adiciona o botão para obeter os dados pedidos pelo o utilizador posiciona-o no grid
    button_fetch = ttk.Button(frame, text="Obter Dados", command=fetch_forecast)
    button_fetch.grid(row=7, column=0, columnspan=2, pady=10)
    
    #Adiciona a tabela que mostra os dados e posiciona-a no grid
    text_output = tk.Text(frame, wrap="word", height=15, width=50)
    text_output.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E))

    update_fields()
    
    root.mainloop()


# create_gui()
gui_interface()


# Função principal
if __name__ == "__main__":
    gui_interface()












