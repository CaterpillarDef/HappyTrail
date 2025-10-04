from weather_service import WeatherService

weather_request = WeatherService()

#print("MAIN\n")

#coords=("60.29","24.57") #Nuuksio
coords=("60.2","25") #Kumpula 60.2091° N, 24.9647° E
previous_hours = 24
local_end_date = None
local_end_date="2024-09-15 23:00:00"

print(weather_request.get_observation_data(coords, previous_hours, local_end_date))