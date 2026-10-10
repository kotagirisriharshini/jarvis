import os
import requests
import logging
from typing import Tuple, Optional
from dotenv import load_dotenv

from voice.text_to_speech import speak

load_dotenv()
logger = logging.getLogger("JARVIS.Weather")

def get_weather(city: Optional[str] = None, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Fetch comprehensive weather report using OpenWeatherMap API (if key present in .env)
    or wttr.in fallback service.
    Reports temperature, condition, feels-like temperature, humidity, and wind speed.
    """
    target_city = city.strip() if city else "Hyderabad"
    # Capitalize city for clean speech
    target_city_display = target_city.title()
    api_key = os.getenv("WEATHER_API_KEY")

    logger.info(f"Fetching weather report for city: '{target_city_display}'")

    if api_key and api_key.strip() and api_key.strip() != "your_openweather_api_key_here":
        # Use OpenWeatherMap API
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={target_city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                
                msg = (
                    f"The weather in {target_city_display} is currently {desc} with a temperature of {temp:.1f} degrees Celsius, "
                    f"feels like {feels_like:.1f} degrees, {humidity} percent humidity, and wind speed of {wind_speed} meters per second."
                )
                speak(msg)
                return True, msg
            else:
                logger.warning(f"OpenWeatherMap API status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"OpenWeatherMap request failed for {target_city_display}: {e}")

    # Fallback to keyless wttr.in JSON API
    try:
        url = f"https://wttr.in/{target_city}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            curr = data["current_condition"][0]
            temp_c = curr["temp_C"]
            feels_c = curr["FeelsLikeC"]
            desc = curr["weatherDesc"][0]["value"]
            humidity = curr["humidity"]
            wind_kmph = curr["windspeedKmph"]

            msg = (
                f"The current weather in {target_city_display} is {desc} with a temperature of {temp_c} degrees Celsius, "
                f"feels like {feels_c} degrees, {humidity} percent humidity, and wind speed of {wind_kmph} kilometers per hour."
            )
            speak(msg)
            return True, msg
    except Exception as e:
        logger.error(f"wttr.in request failed for {target_city_display}: {e}")

    msg = f"Sorry {speaker_role}, weather information for {target_city_display} is currently unavailable. Please check your internet connection or verify WEATHER_API_KEY in your .env file."
    speak(msg)
    return False, msg
