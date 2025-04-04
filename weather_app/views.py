from django.shortcuts import render, HttpResponse, redirect
import requests
from django.http import JsonResponse
from .models import City
from django.contrib import messages

# Create your views here.

def home(request):
    city_name='phnom penh'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    api_key = 'f5c4f97682793f91d93d1a5fd4e3f38e'
    # Check if the request is a POST (when adding a new city)
    if request.method == 'POST':
        city = request.POST.get('city') # get the city name from the form
        # Fetch weather data for the city from the API
        response = requests.get(url.format(city, api_key)).json()

        # Check if the city exists in the API
        if response['cod'] == 200:
            if not City.objects.filter(name=city).exists():
                # save the new city to the database
                City.objects.create(name=city)
                messages.success(request, f'{city} has been added sucessfully!')
            else:
                messages.info(request, f'{city} already exists!')
        else:
            messages.error(request, f'City "{city}" not found!')

        return redirect('home')
    # Fetch weather data for all saved cities
    weather_data = []
    try:
        cities = City.objects.all()
        for city in cities:
            response = requests.get(url.format(city.name, api_key))
            data = response.json()
            if data['cod'] == 200:
                city_weather = {
                    'city': city.name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                }
                weather_data.append(city_weather)
            else:
                City.objects.filter(name=city.name).delete()
    except requests.RequestException as e:
        print('Error Connecting to weather data service. Please try again later.')
    context = {'weather_data': weather_data}
    # return HttpResponse('Hello, Coderistic!')
    # return JsonResponse(response)
    return render(request, 'index.html', context)