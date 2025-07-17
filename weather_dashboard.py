import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
import threading
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # API key - You'll need to get this from OpenWeatherMap
        self.api_key = "32bfbb07ac815824d01a2b2197918ff0"  # Replace with your actual API key
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="Weather Dashboard", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack()
        
        # Search frame
        search_frame = tk.Frame(self.root, bg='#2c3e50')
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Enter City:", 
                font=('Arial', 12), fg='white', bg='#2c3e50').pack(side=tk.LEFT, padx=5)
        
        self.city_entry = tk.Entry(search_frame, font=('Arial', 12), width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind('<Return>', lambda e: self.get_weather())
        
        search_btn = tk.Button(search_frame, text="Get Weather", 
                              command=self.get_weather, 
                              bg='#3498db', fg='white', 
                              font=('Arial', 10, 'bold'),
                              cursor='hand2')
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg='#2c3e50')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Current weather frame
        self.current_frame = tk.LabelFrame(self.content_frame, text="Current Weather", 
                                          font=('Arial', 14, 'bold'), 
                                          fg='white', bg='#34495e',
                                          relief=tk.RAISED, bd=2)
        self.current_frame.pack(fill=tk.X, pady=5)
        
        # Forecast frame
        self.forecast_frame = tk.LabelFrame(self.content_frame, text="5-Day Forecast", 
                                           font=('Arial', 14, 'bold'), 
                                           fg='white', bg='#34495e',
                                           relief=tk.RAISED, bd=2)
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Charts frame
        self.charts_frame = tk.LabelFrame(self.content_frame, text="Temperature Chart", 
                                         font=('Arial', 14, 'bold'), 
                                         fg='white', bg='#34495e',
                                         relief=tk.RAISED, bd=2)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Enter a city name to get weather information")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W, 
                             bg='#34495e', fg='white')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name")
            return
            
        self.status_var.set("Fetching weather data...")
        
        # Run API calls in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.fetch_weather_data, args=(city,))
        thread.daemon = True
        thread.start()
        
    def fetch_weather_data(self, city):
        try:
            # Get current weather
            current_url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric"
            current_response = requests.get(current_url, timeout=10)
            
            if current_response.status_code == 401:
                self.root.after(0, lambda: self.status_var.set("API key invalid. Please get a valid API key from OpenWeatherMap."))
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    "Invalid API key. Please:\n1. Sign up at openweathermap.org\n2. Get your free API key\n3. Replace 'YOUR_API_KEY_HERE' in the code"))
                return
                
            if current_response.status_code != 200:
                self.root.after(0, lambda: self.status_var.set(f"City not found: {city}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"City '{city}' not found"))
                return
                
            current_data = current_response.json()
            
            # Get 5-day forecast
            forecast_url = f"{self.base_url}forecast?q={city}&appid={self.api_key}&units=metric"
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_data = forecast_response.json()
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_weather_display(current_data, forecast_data))
            
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.status_var.set("Network error occurred"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Network error: {str(e)}"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("An error occurred"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            
    def update_weather_display(self, current_data, forecast_data):
        # Clear previous data
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
            
        # Display current weather
        self.display_current_weather(current_data)
        
        # Display forecast
        self.display_forecast(forecast_data)
        
        # Display temperature chart
        self.display_temperature_chart(forecast_data)
        
        self.status_var.set(f"Weather data updated for {current_data['name']}")
        
    def display_current_weather(self, data):
        main_frame = tk.Frame(self.current_frame, bg='#34495e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - main info
        left_frame = tk.Frame(main_frame, bg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # City and country
        city_label = tk.Label(left_frame, 
                             text=f"{data['name']}, {data['sys']['country']}", 
                             font=('Arial', 20, 'bold'), 
                             fg='white', bg='#34495e')
        city_label.pack(anchor=tk.W)
        
        # Temperature
        temp_label = tk.Label(left_frame, 
                             text=f"{data['main']['temp']:.1f}°C", 
                             font=('Arial', 32, 'bold'), 
                             fg='#e74c3c', bg='#34495e')
        temp_label.pack(anchor=tk.W)
        
        # Description
        desc_label = tk.Label(left_frame, 
                             text=data['weather'][0]['description'].title(), 
                             font=('Arial', 14), 
                             fg='white', bg='#34495e')
        desc_label.pack(anchor=tk.W)
        
        # Right side - additional info
        right_frame = tk.Frame(main_frame, bg='#34495e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20)
        
        info_data = [
            ("Feels like", f"{data['main']['feels_like']:.1f}°C"),
            ("Humidity", f"{data['main']['humidity']}%"),
            ("Pressure", f"{data['main']['pressure']} hPa"),
            ("Wind Speed", f"{data['wind']['speed']} m/s"),
            ("Visibility", f"{data.get('visibility', 'N/A')/1000:.1f} km" if 'visibility' in data else "N/A"),
            ("Sunrise", datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")),
            ("Sunset", datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M"))
        ]
        
        for label, value in info_data:
            info_frame = tk.Frame(right_frame, bg='#34495e')
            info_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(info_frame, text=f"{label}:", 
                    font=('Arial', 10), fg='#bdc3c7', bg='#34495e').pack(side=tk.LEFT)
            tk.Label(info_frame, text=value, 
                    font=('Arial', 10, 'bold'), fg='white', bg='#34495e').pack(side=tk.RIGHT)
    
    def display_forecast(self, data):
        # Create scrollable frame
        canvas = tk.Canvas(self.forecast_frame, bg='#34495e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.forecast_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        # Process forecast data (take every 8th item for daily forecast)
        daily_forecasts = data['list'][::8][:5]  # 5-day forecast
        
        for i, forecast in enumerate(daily_forecasts):
            day_frame = tk.Frame(scrollable_frame, bg='#2c3e50', relief=tk.RAISED, bd=1)
            day_frame.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.BOTH)
            
            # Date
            date = datetime.fromtimestamp(forecast['dt'])
            day_name = date.strftime("%a")
            date_str = date.strftime("%m/%d")
            
            tk.Label(day_frame, text=day_name, 
                    font=('Arial', 12, 'bold'), 
                    fg='white', bg='#2c3e50').pack(pady=5)
            tk.Label(day_frame, text=date_str, 
                    font=('Arial', 10), 
                    fg='#bdc3c7', bg='#2c3e50').pack()
            
            # Weather icon (using emoji as placeholder)
            weather_icons = {
                'clear': '☀️', 'clouds': '☁️', 'rain': '🌧️', 
                'snow': '❄️', 'thunderstorm': '⛈️', 'mist': '🌫️'
            }
            weather_main = forecast['weather'][0]['main'].lower()
            icon = weather_icons.get(weather_main, '🌤️')
            
            tk.Label(day_frame, text=icon, 
                    font=('Arial', 24), bg='#2c3e50').pack(pady=5)
            
            # Temperature
            tk.Label(day_frame, text=f"{forecast['main']['temp']:.1f}°C", 
                    font=('Arial', 12, 'bold'), 
                    fg='#e74c3c', bg='#2c3e50').pack()
            
            # Description
            tk.Label(day_frame, text=forecast['weather'][0]['description'].title(), 
                    font=('Arial', 8), 
                    fg='white', bg='#2c3e50', 
                    wraplength=80).pack(pady=2)
            
            # Additional info
            tk.Label(day_frame, text=f"💧 {forecast['main']['humidity']}%", 
                    font=('Arial', 8), 
                    fg='#3498db', bg='#2c3e50').pack()
            tk.Label(day_frame, text=f"💨 {forecast['wind']['speed']:.1f} m/s", 
                    font=('Arial', 8), 
                    fg='#95a5a6', bg='#2c3e50').pack()
        
        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")
    
    def display_temperature_chart(self, data):
        # Prepare data for chart
        times = []
        temps = []
        
        for item in data['list'][:24]:  # Next 24 hours
            time = datetime.fromtimestamp(item['dt'])
            times.append(time.strftime("%H:%M"))
            temps.append(item['main']['temp'])
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#34495e')
        ax.set_facecolor('#2c3e50')
        
        # Plot temperature line
        ax.plot(times, temps, color='#e74c3c', linewidth=2, marker='o', markersize=4)
        ax.fill_between(times, temps, alpha=0.3, color='#e74c3c')
        
        # Customize chart
        ax.set_title('24-Hour Temperature Forecast', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Temperature (°C)', color='white')
        ax.tick_params(colors='white', rotation=45)
        ax.grid(True, alpha=0.3)
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        # Show every 3rd label to avoid crowding
        for i, label in enumerate(ax.get_xticklabels()):
            if i % 3 != 0:
                label.set_visible(False)
        
        plt.tight_layout()
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def main():
    root = tk.Tk()
    app = WeatherDashboard(root)
    
    # Show initial instructions
    messagebox.showinfo("Setup Required", 
                       "To use this weather dashboard:\n\n"
                       "1. Sign up for a free account at openweathermap.org\n"
                       "2. Get your API key from your account dashboard\n"
                       "3. Replace 'YOUR_API_KEY_HERE' in the code with your actual API key\n\n"
                       "Required packages: requests, Pillow, matplotlib\n"
                       "Install with: pip install requests Pillow matplotlib")
    
    root.mainloop()

if __name__ == "__main__":
    main()