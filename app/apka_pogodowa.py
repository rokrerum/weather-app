from CTkMessagebox import CTkMessagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import customtkinter
import requests
from PIL import Image
import json
import os

# Słowniki do przechowywania lokalizacji i nawigacji
localizations = {}
localizations_nav = {}

# Klucz API do pogodowej usługi
weather_api = ""

# Klasa wykresy odpowiadająca za tworzenie wykresów pogodowych
class wykresy():
    def __init__(self, parent_frame):  # Przyjmujemy ramkę nadrzędną
        self.daily_weather_frame = parent_frame  # Zapisujemy ją w obiekcie

    def temperatura(self, co):
        # Inicjalizacja klasy 'weatherr' do pobierania danych pogodowych
        weatherv = weatherr(weather_api)
        dane_pogodowe = weatherv.get_weather(co)

        # Wybrane godziny, które nas interesują
        wybrane_godziny = ["00:00", "03:00", "06:00", "09:00", 
                          "12:00", "15:00", "18:00", "21:00"]

        # Słownik do przechowywania unikalnych danych pogodowych
        unique_data = {}

        # Iterujemy po wszystkich danych pogodowych i wybieramy te z interesujących godzin
        for entry in dane_pogodowe['list']:
            full_time = entry['dt_txt'][-8:-3]  # "HH:MM"
            hour = full_time[:2]                # "HH"

            if full_time in wybrane_godziny and hour not in unique_data:
                unique_data[hour] = {
                    "temp": entry['main']['temp'],
                    "humidity": entry['main']['humidity'],
                    "pressure": entry['main']['pressure'],
                    "wind_speed": entry['wind']['speed'],
                    "uv_index": entry.get('uv', 0),
                    "air_quality": entry.get('air_quality', 50)
                }

        # Przygotowanie danych do wykresu
        x = list(unique_data.keys())
        temp = [d["temp"] for d in unique_data.values()]
        humidity = [d["humidity"] for d in unique_data.values()]
        pressure = [d["pressure"] for d in unique_data.values()]
        wind_speed = [d["wind_speed"] for d in unique_data.values()]
        uv_index = [d["uv_index"] for d in unique_data.values()]
        air_quality = [d["air_quality"] for d in unique_data.values()]

        # Funkcja do tworzenia wykresów
        def create_plot(frame, data, title, color):
            fig, ax = plt.subplots(figsize=(3.6, 1.9), dpi=100)  # Zwiększona wysokość z 2 na 3
            ax.plot(x, data, marker="o", linestyle="-", color=color, linewidth=2)

            # Specjalne ustawienia dla osi Y
            ax.yaxis.label.set_color('#00BFFF')  # Jasnoniebieski
            ax.tick_params(axis='y', labelsize=9, labelcolor='#333333')

            # Dodatkowe efekty wizualne
            for label in ax.get_yticklabels():
                label.set_rotation(30)
                label.set_ha('right')

            ax.set_title(title, fontsize=10, color="white")
            ax.grid(True, linestyle="--", alpha=0.6)

            # Stylizacja tła wykresu
            ax.set_facecolor("#242424")
            fig.patch.set_facecolor("#1E1E1E")
            ax.spines["bottom"].set_color("white")
            ax.spines["left"].set_color("white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")
            ax.tick_params(axis="x", colors="white")
            ax.tick_params(axis="y", colors="white")

            # Dodanie wykresu do tkinter
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.get_tk_widget().pack()

        # Parametry wykresów do stworzenia
        params = [
            (temp, "Temperatura (°C)", "deepskyblue"),
            (humidity, "Wilgotność (%)", "limegreen"),
            ([round(val) for val in pressure], "Ciśnienie (hPa)", "gold"),
            (wind_speed, "Wiatr (km/h)", "orange"),
            (uv_index, "UV Index", "violet"),
            (air_quality, "Jakość powietrza (AQI)", "red"),
        ]

        # Tworzymy wykresy dla każdego parametru
        for i, (data, title, color) in enumerate(params):
            row, col = divmod(i, 2)  # Ustawienie 2 kolumn
            frame = customtkinter.CTkFrame(
                self.daily_weather_frame, 
                corner_radius=15, 
                width=480,  # Zwiększona szerokość
                height=280,  # Zwiększona wysokość
                fg_color="#242424"
            )
            frame.grid(row=row, column=col, padx=0, pady=(0, 10))  # Zmniejsz odstępy między kolumnami
            create_plot(frame, data, title, color)

# Klasa odpowiedzialna za dodawanie i usuwanie lokalizacji w aplikacji
class tworzenie(wykresy):
    def __init__(self):
        super().__init__()

    # Dodanie lokalizacji do aplikacji
    def add_location(self, co):
        weatherv = weatherr(weather_api)
        dane_pogodowe = weatherv.get_weather(co)

        if dane_pogodowe == None:
            CTkMessagebox(title="Error", message="Something went wrong!!!", icon="cancel")
            return

        datav = data()
        datav.add(co)
        self.add_to_interface(co)

    # Aktualizowanie interfejsu o dodane lokalizacje
    def add_to_interface(self, co):     
        self.add_location_to_pane(co)
        self.add_buttons_to_navigato(co)

    # Tworzenie ramki z danymi lokalizacji
    def add_location_to_pane(self, co):
        weatherv = weatherr(weather_api)
        dane_pogodowe = weatherv.get_weather(co)

        # Tworzymy ramkę dla lokalizacji
        self.location_frame = customtkinter.CTkFrame(self, corner_radius=20, fg_color="#1E2A38", width=375, height=430)
        self.location_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.location_frame.grid_propagate(False)

        # Tworzenie górnej sekcji z przyciskiem "Cofnij"
        self.top_location_frame = customtkinter.CTkFrame(self.location_frame, corner_radius=20, width=375)
        self.top_location_frame.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        self.top_location_frame.grid_columnconfigure(0, weight=1)
        self.top_location_frame.grid_columnconfigure(1, weight=1)

        # Przycisk do cofania
        self.cofnij_przycisk = customtkinter.CTkButton(self.top_location_frame, text="Cofnij", command=lambda: self.select_frame_by_name("home"), width=50, height=40, fg_color="#4C6E91", hover_color="#5A88A9")
        self.cofnij_przycisk.grid(padx=(10, 140), pady=20, row=0, column=0, sticky="nsew")

        # Etykieta z nazwą lokalizacji
        self.location_label = customtkinter.CTkLabel(
            self.top_location_frame, 
            text=f"{co.capitalize()}", 
            font=("Helvetica", 22, "bold"),
            text_color="#FFFFFF",
            anchor="w",
            wraplength=150,
            justify="left"
        )
        self.location_label.grid(row=0, column=1, padx=(0, 0), pady=10, sticky="nsw")

        # Sekcja prognozy na tydzień
        self.week_weather_frame = customtkinter.CTkFrame(self.location_frame, corner_radius=20)
        self.week_weather_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew", columnspan=2)

        # Mapowanie ikon do pogody
        icon_path = {
            "Clouds": "cloud.png",
            "Clear": "sun.png",
            "Rain": "cloud-rain.png",
            "Snow": "snow-fall.png",
            "Thunderstorm": "thunderstorm.png",
        }

        fixed_hours = ["12:00:00"]
        selected_forecast = []

        # Wybieramy prognozy na określoną godzinę
        for entry in dane_pogodowe['list']:
            date_time = entry['dt_txt']
            hour = date_time.split(" ")[1]

            if hour in fixed_hours:
                selected_forecast.append(entry)

        # Tworzenie ramek z prognozami
        for col_index, forecast in enumerate(selected_forecast):
            datee = forecast['dt_txt'][6:11]
            weather_type = forecast['weather'][0]['main']

            self.day_frame = customtkinter.CTkFrame(self.week_weather_frame, corner_radius=20, width=60, height=80)
            self.day_frame.grid(row=2, column=col_index, padx=5, pady=5, sticky="nsew")
            self.day_frame.grid_propagate(False)

            self.day_label = customtkinter.CTkLabel(self.day_frame, text=f"{datee}", font=("Helvetica", 16, "bold"), anchor="w", text_color="#FFFFFF", wraplength=50)
            self.day_label.grid(row=0, padx=(15, 10), pady=(5, 0), sticky="ew")

            # Załaduj odpowiednią ikonę pogodową
            if weather_type in icon_path:
                pil_image = Image.open(icon_path[weather_type])
                self.weather_image = customtkinter.CTkImage(pil_image, size=(40, 40))
                self.weather_icon = customtkinter.CTkLabel(self.day_frame, image=self.weather_image, text="")
                self.weather_icon.place(x=11, y=30)

        # Tworzenie wykresów pogodowych
        self.daily_weather_frame = customtkinter.CTkScrollableFrame(self.location_frame, corner_radius=20)
        self.daily_weather_frame.grid(row=2, column=0, padx=0, pady=(0,0), sticky="ew", columnspan=2)

        vwyk = wykresy(self.daily_weather_frame)
        vwyk.temperatura(co)

        # Zapisywanie lokalizacji
        localizations[co] = self.location_frame

    # Funkcja do wybierania ramki z lokalizacją
    def select_frame_by_name(self, name):
        for i in localizations.values():
            i.grid_remove()

        localizations[name].grid()

    # Usuwanie lokalizacji
    def remove_location_from_app(self, co):
        self.remove_location_to_pane(co)
        self.remove_buttons_from_navigato(co)
        datav = data()
        datav.delete(co)

    # Usuwanie lokalizacji z ekranu
    def remove_location_to_pane(self, co):
        localizations[co].grid_remove()

    # Usuwanie przycisków z nawigacji
    def remove_buttons_from_navigato(self, co):
        localizations_nav[co].grid_remove()

    # Dodanie przycisków do nawigacji
    def add_buttons_to_navigato(self, co):
        self.dd = customtkinter.CTkFrame(self.place_frame, corner_radius=10, fg_color="#3E4A58", height=80)
        self.dd.grid(sticky="nsew", padx=10, pady=10)

        # Przycisk do wybrania lokalizacji
        self.przycisk = customtkinter.CTkButton(self.dd, text=co, command=lambda: self.select_frame_by_name(co), width=180, height=50, fg_color="#5D6D7E", hover_color="#7A8B9A")
        self.przycisk.grid(row=0, column=0, padx=10, pady=10)

        # Przycisk do usuwania lokalizacji
        self.usun_button = customtkinter.CTkButton(self.dd, text="X", width=40, height=40, command=lambda: self.remove_location_from_app(co), fg_color="red", hover_color="#FF4136")
        self.usun_button.grid(row=0, column=1, padx=10, pady=10)

        localizations_nav[co] = self.dd



    def add_buttons_to_navigato(self, co):
        self.dd = customtkinter.CTkFrame(self.place_frame, corner_radius=10, fg_color="#3E4A58", height=80)
        self.dd.grid(sticky="nsew", padx=10, pady=10)
        
        self.przycisk = customtkinter.CTkButton(self.dd, text=co, command=lambda: self.select_frame_by_name(co), width=180, height=50, fg_color="#5D6D7E", hover_color="#7A8B9A")
        self.przycisk.grid(row=0, column=0, padx=10, pady=10)
    
        # Przycisk do usuwania grupy
        self.usun_button = customtkinter.CTkButton(self.dd, text="X", width=40, height=40, command=lambda: self.remove_location_from_app(co), fg_color="red", hover_color="#FF4136")
        self.usun_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        localizations_nav[co] = self.dd

    
class data():
    def __init__(self):
        pass


    def list_to_str(co):
            sum = ""
            for j in co:
                sum += j
            return sum
    
    
    def create(self):
        pliki = os.listdir() 
        if "dane.json" not in pliki:
            podstawa = {
            }
            with open('dane.json', 'w') as file:
                json.dump(podstawa, file, indent=4)
    

    def load(self):
            # Załaduj dane z pliku
        with open('dane.json', 'r') as file:
            data = json.load(file)
        
        # Pobierz dane z określonej grupy i umieść je w osobnych listach
        global lista_danych
        lista_danych = [list(item) for item in data]
        return lista_danych
     

    def delete(self, name):               #XXXXXX
        # Załaduj dane z pliku
        with open('dane.json', 'r') as file:
            data = json.load(file)

        # Sprawdź, czy grupa istnieje, jeśli tak, usuń ją
        if name in data:
            del data[name]

            # Zapisz zaktualizowane dane do pliku JSON
            with open('dane.json', 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Usunięto grupę: {name}")
        else:
            print(f"Grupa {name} nie istnieje.")


    def search(self):
        pass
    
    def add(self, nazwa_grupy):    
        # Załaduj dane z pliku
        with open('dane.json', 'r') as file:
            data = json.load(file)
        
        data[nazwa_grupy] = (nazwa_grupy)  # nazwa grupy, do której dodajesz dane
        print(f"Dodano nową osobę do grupy {nazwa_grupy}.")
        # Zapisz zaktualizowane dane do pliku JSON
        with open('dane.json', 'w') as file:
            json.dump(data, file, indent=4)
    

class weatherr():                #XXXXXX
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.base_weather_url = "https://api.openweathermap.org/data/2.5/forecast"

    def get_coordinates(self, city_name):
        try:
            params = {
                "q": city_name,
                "appid": self.api_key,
                "limit": 1
            }
            response = requests.get(self.base_geo_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                return None
            latitude = data[0]["lat"]
            longitude = data[0]["lon"]
            return latitude, longitude
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def get_weather(self, city_name):
        if coordinates := self.get_coordinates(city_name):
            params = {
                "lat": coordinates[0],
                "lon": coordinates[1],
                "appid": self.api_key,
                "units": "metric",
            }
            response = requests.get(self.base_weather_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        return None


class App(customtkinter.CTk, tworzenie):
    def __init__(self):
        super().__init__()
        
        self.geometry("373x430")
        self.title("Aplikacja pogodowa")
        
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="#2C3E50")
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=2)
        
        self.add_place_frame = customtkinter.CTkFrame(self.navigation_frame, corner_radius=0, fg_color="#34495E")
        self.add_place_frame.grid(row=0, column=0, sticky="nsew")
        
        self.input = customtkinter.CTkEntry(self.add_place_frame, placeholder_text="Wpisz miasto", width=200, height=40, font=("Helvetica", 16))
        self.input.grid(padx=(10, 10), pady=20, row=0, column=0, sticky="nsew")
        self.buttonSerch = customtkinter.CTkButton(self.add_place_frame, text="Wyszukaj", command=lambda: self.add_location(self.input.get()), width=140, height=45, fg_color="#8E44AD", hover_color="#9B59B6")
        self.buttonSerch.grid(padx=(5, 10), pady=20, row=0, column=1, sticky="nsew")
        
        self.place_frame = customtkinter.CTkScrollableFrame(self.navigation_frame, corner_radius=0, fg_color="#1F2A38", height=345)
        self.place_frame.grid(row=1, column=0, sticky="nsew")
        localizations["home"] = self.navigation_frame

        print(lista_danych)
        for i in lista_danych:
            self.add_to_interface(data.list_to_str(i))
        
        self.select_frame_by_name("home")

    
if __name__ == "__main__":
    datav = data()
    datav.create()
    datav.load()
    # Wstaw tutaj swój klucz API
    weatherv = weatherr(weather_api)
    asasdas = weatherv.get_weather("Warszawa")
    print(asasdas)
    
    app = App()
    app.mainloop()
