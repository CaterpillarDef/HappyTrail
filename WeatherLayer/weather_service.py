from datetime import datetime, timedelta, timezone
import datetime as dt
import pytz
from fmiopendata.wfs import download_stored_query
from weather import Weather
import numpy as np
import pandas as pd
import math

#Set as 1 to activate prints
debug=0

# Haversine formula to calculate distance between two lat-lon points
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance


class WeatherService:
    """Class for operations of Weather.
    """

    def __init__(self):
        pass

    def get_nearest_station(self, coords, type):
        """ Method which find nearest weather station.
        Args:
            Coords: tuple lat and lon, both as string
            Type: precipitation, weather
        Functions:
            Example row in stations csv:
            Espoo Nuuksio,852678,60.29,24.57
        Returns:
            tuple (station name, lat, lon, type)
        """
        lat1 = float(coords[0])
        lon1 = float(coords[1])

        # Read the CSV file
        df = pd.read_csv("fmi_stations.csv")
        nearest_station = ""
        closest_distance = 999
        # Loop through rows
        for index, row in df.iterrows():
            if row['Groups'] == type:
                lat2 = row['Lat']
                lon2 = row['Lon']
                distance =  haversine(lat1, lon1, lat2, lon2)
                # Check if closest:
                if distance < closest_distance:
                    closest_distance = distance
                    nearest_station = (row['Name'], row['Lat'], row['Lon'])
        if debug:
            print("RETURN: ", nearest_station, type)

        return nearest_station

    def get_observation_data(self, coords, previous_hours=1, local_end_date=None):
        """ Method which gets observation data for the station from FMI interphase.
        At FMI data is stored in a coordinate (lat,lon) squares = bounding boxes.
        Stations provide new data every 1-10 minutes and
        query returns all data from latest hour.
        Calls for function to check data.

        Request to FMI includes: 
            bounding box around the coordinates of the station.

        Args:
        coords: coordinates
        previous_hours: how many hours back the data is retrieved
        """

        end_time = datetime.now(timezone.utc)
        if local_end_date:
             #"2022-10-11 12:30:00"
            local_tz = pytz.timezone('Europe/Helsinki')  # Define local timezone
            local_dt = dt.datetime.strptime(local_end_date, "%Y-%m-%d %H:%M:%S")
            local_dt = local_tz.localize(local_dt)
            end_time = local_dt.astimezone(pytz.utc)

        start_time = end_time - timedelta(hours=previous_hours)

        # Format as ISO 8601 with Zulu time (UTC)
        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if not coords:
            print("No coords")
            return False

        station_rain= self.get_nearest_station(coords, "precipitation")
        station_temp = self.get_nearest_station(coords, "weather")

        lat_rain = station_rain[1]
        lon_rain = station_rain[2]
        lat2 = station_temp[1]
        lon2 = station_temp[2]
        extra = 0.5

        station_box_rain = f"{str(float(lon_rain)-extra)},{str(float(lat_rain)-extra)},\
        {str(float(lon_rain)+extra)},{str(float(lat_rain)+extra)}"

        station_box_temp = f"{str(float(lon2)-extra)},{str(float(lat2)-extra)},\
        {str(float(lon2)+extra)},{str(float(lat2)+extra)}"

        try:
            obs_rain = download_stored_query("fmi::observations::weather::multipointcoverage",
                              args=[f"bbox={station_box_rain}",
                                "starttime=" + start_time,
                                "endtime=" + end_time])
        except ConnectionError:
            return False

        try:
            obs_temp = download_stored_query("fmi::observations::weather::multipointcoverage",
                              args=[f"bbox={station_box_temp}",
                                "starttime=" + start_time,
                                "endtime=" + end_time])
        except ConnectionError:
            return False

        if debug:
            print("TEST\n")
            print(obs_rain.data)
            #print(obs_temp.data)
            print("\nEND OF TEST")

        # Step 1: Extract all air temperatures
        air_temperatures = []

        for timestamp, data in obs_temp.data.items():
            for location, weather_data in data.items():
                if (location == station_temp[0]):
                    air_temp = weather_data.get('Air temperature', {}).get('value', None)
                    if air_temp is not None:
                        air_temperatures.append(air_temp)

        # Step 2: Calculate the average
        avg_air_temp = None
        if air_temperatures:
            avg_air_temp = np.mean(air_temperatures)
            if debug:
                print(f"Average Air Temperature: {avg_air_temp:.2f} degC")
        else:
            print("No air temperature data available.")


        # Step 1: Extract all rain
        rains = []

        for timestamp, data in obs_rain.data.items():
            for location, weather_data in data.items():
                if (location == station_rain[0]):
                    print("location", location, station_rain[0])
                    rain = weather_data.get('Precipitation amount', {}).get('value', None)
                    if rain is not None:
                        rains.append(rain)

        # Step 2: Calculate the average
        sum_rain = None
        if rains:
            sum_rain = np.sum(rains)
            if debug:
                print(f"Sum of rain: {rains:.2f} mm")
        else:
            print("No rain data available.")

        return ({"Temperature": avg_air_temp, "Rain": sum_rain})
