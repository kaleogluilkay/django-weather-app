import requests
from django.shortcuts import render


# Eğer direkt kullanacaksan:
API_KEY = '2cd80753bd6803a925813336db17c8d6'

def home(request):
    weather_data = None
    city = None

    # Kullanıcı koordinatlarını al
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if request.method == 'POST':
        city = request.POST.get('city')
        # Türkçe karakterleri ASCII ile değiştir
        city = city.encode('ascii', 'ignore').decode()

    # API URL belirleme
    if city:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    elif lat and lon:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    else:
        url = None

    if url:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                icon = data['weather'][0]['icon']

                # Arkaplan rengi
                if icon.startswith('01'):
                    background = 'linear-gradient(to bottom, #fceabb, #f8b500)'
                elif icon.startswith(('02','03','04')):
                    background = 'linear-gradient(to bottom, #bdc3c7, #2c3e50)'
                elif icon.startswith(('09','10')):
                    background = 'linear-gradient(to bottom, #4b79a1, #283e51)'
                elif icon.startswith('11'):
                    background = 'linear-gradient(to bottom, #232526, #414345)'
                elif icon.startswith('13'):
                    background = 'linear-gradient(to bottom, #e0eafc, #cfdef3)'
                else:
                    background = 'linear-gradient(to bottom, #74ebd5, #ACB6E5)'

                weather_data = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': icon,
                    'background': background
                }

                # 5 günlük tahmin
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={data['name']}&appid={API_KEY}&units=metric"
                forecast_response = requests.get(forecast_url, timeout=5)
                forecast_data = []
                if forecast_response.status_code == 200:
                    forecast_json = forecast_response.json()
                    for item in forecast_json['list'][:5]:
                        forecast_data.append({
                            'date': item['dt_txt'],
                            'temp': item['main']['temp'],
                            'desc': item['weather'][0]['description'],
                            'icon': item['weather'][0]['icon']
                        })
                weather_data['forecast'] = forecast_data
            else:
                weather_data = {'error': f"Şehir bulunamadı! (HTTP {response.status_code})"}

        except requests.exceptions.RequestException:
            weather_data = {'error': "API ile bağlantı kurulamadı. İnternet veya API keyinizi kontrol edin."}

    return render(request, 'weather/home.html', {'weather': weather_data})
