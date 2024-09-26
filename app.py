import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import openai

# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# OpenWeatherMap API key
API_KEY = st.secrets["OPENWEATHERMAP_API_KEY"]

def get_weather_data(city_name):
    if city_name:
        API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric'
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching weather data for {city_name}.")
            st.error(f"Status Code: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
    else:
        st.error("Please provide a city name.")
        return None

def map_weather_to_traits(weather_data):
    traits = {}

    # Random Skin Color
    skin_colors = ['fair skin', 'light skin', 'olive skin', 'brown skin', 'dark skin']
    traits['skin_color'] = random.choice(skin_colors)

    # Eye Types
    eye_types = ['large and round eyes', 'average-sized eyes', 'almond-shaped eyes']
    traits['eyes'] = random.choice(eye_types)

    # Nose Sizes
    nose_sizes = ['small nose', 'medium-sized nose', 'large nose']
    traits['nose'] = random.choice(nose_sizes)

    # Temperature mapping for clothing
    temperature = weather_data['main']['temp']
    if temperature <= 10:
        traits['clothing'] = 'wearing a warm coat and scarf'
    elif 10 < temperature <= 20:
        traits['clothing'] = 'wearing a light jacket'
    elif 20 < temperature <= 30:
        traits['clothing'] = 'in casual wear like a t-shirt and jeans'
    else:
        traits['clothing'] = 'wearing summer attire like shorts and a tank top'

    # Weather condition mapping for accessories and background
    weather_condition = weather_data['weather'][0]['main'].lower()
    if 'rain' in weather_condition:
        traits['accessories'] = 'holding an umbrella'
        traits['background'] = 'a rainy background with puddles'
    elif 'cloud' in weather_condition:
        traits['accessories'] = 'no accessories'
        traits['background'] = 'an overcast sky'
    elif 'clear' in weather_condition:
        traits['accessories'] = 'wearing sunglasses'
        traits['background'] = 'a clear, sunny sky'
    elif 'snow' in weather_condition:
        traits['accessories'] = 'wearing gloves'
        traits['background'] = 'a snowy landscape'
    else:
        traits['accessories'] = 'no accessories'
        traits['background'] = 'a typical day'

    # Time of day mapping using local time of the location
    timezone_offset = weather_data['timezone']  # in seconds
    local_time = datetime.utcnow() + timedelta(seconds=timezone_offset)
    current_hour = local_time.hour

    if 6 <= current_hour < 12:
        traits['time_of_day'] = 'morning'
    elif 12 <= current_hour < 18:
        traits['time_of_day'] = 'afternoon'
    elif 18 <= current_hour < 21:
        traits['time_of_day'] = 'evening'
    else:
        traits['time_of_day'] = 'night'

    # Wind speed mapping for hair
    wind_speed = weather_data['wind']['speed']
    if wind_speed > 10:
        traits['hair'] = 'hair is blowing in the wind'
    else:
        traits['hair'] = 'hair is neatly styled'

    # Humidity mapping for expression
    humidity = weather_data['main']['humidity']
    if humidity > 80:
        traits['expression'] = 'looks a bit uncomfortable due to humidity'
    else:
        traits['expression'] = 'has a cheerful expression'

    return traits

def generate_character_description(traits):
    description = (
        f"A cartoon {traits['gender']} character with {traits['skin_color']}, "
        f"{traits['eyes']}, {traits['nose']}, {traits['clothing']}, {traits['hair']}, "
        f"{traits['accessories']}, and {traits['expression']}. "
        f"The background is {traits['background']} during the {traits['time_of_day']}."
    )
    return description

def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

def main():
    st.title("Weather Data to Character Design")

    # Tabs for better organization
    tab1, tab2 = st.tabs(["Character Generator", "About"])

    with tab1:
        # Columns for inputs
        col1, col2 = st.columns(2)

        with col1:
            st.header("Enter Location")
            city_name = st.text_input("City Name")

        with col2:
            st.header("Character Gender")
            gender_options = ['male', 'female', 'non-binary']
            selected_gender = st.selectbox("Gender", gender_options)

        if city_name:
            weather_data = get_weather_data(city_name=city_name)

            if weather_data:
                # Display weather data
                st.subheader("Current Weather Data")
                st.write(f"**Location:** {weather_data['name']}, {weather_data['sys']['country']}")
                local_time = datetime.utcnow() + timedelta(seconds=weather_data['timezone'])
                st.write(f"**Local Time:** {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Temperature:** {weather_data['main']['temp']} °C")
                st.write(f"**Weather:** {weather_data['weather'][0]['description'].title()}")
                st.write(f"**Humidity:** {weather_data['main']['humidity']}%")
                st.write(f"**Wind Speed:** {weather_data['wind']['speed']} m/s")

                traits = map_weather_to_traits(weather_data)
                traits['gender'] = selected_gender  # Set the selected gender

                # Hide trait customization and description under an expander
                with st.expander("Customize Character Traits (Optional)", expanded=False):
                    st.header("Customize Character Traits")
                    skin_colors = ['fair skin', 'light skin', 'olive skin', 'brown skin', 'dark skin']
                    eye_types = ['large and round eyes', 'average-sized eyes', 'almond-shaped eyes']
                    nose_sizes = ['small nose', 'medium-sized nose', 'large nose']

                    selected_skin_color = st.selectbox(
                        "Skin Color", skin_colors, index=skin_colors.index(traits['skin_color'])
                    )
                    selected_eye_type = st.selectbox(
                        "Eye Type", eye_types, index=eye_types.index(traits['eyes'])
                    )
                    selected_nose_size = st.selectbox(
                        "Nose Size", nose_sizes, index=nose_sizes.index(traits['nose'])
                    )

                    # Update traits with user selections
                    traits['skin_color'] = selected_skin_color
                    traits['eyes'] = selected_eye_type
                    traits['nose'] = selected_nose_size

                    description = generate_character_description(traits)
                    st.subheader("Generated Character Description:")
                    st.write(description)

                # Generate and display the image
                st.subheader("Generated Character Image:")
                with st.spinner("Generating image..."):
                    image_url = generate_image(description)
                    if image_url:
                        st.image(image_url, caption="Generated by DALL·E", use_column_width=True)
            else:
                st.error("Failed to generate character description due to missing weather data.")
        else:
            st.info("Please enter a city name.")

    with tab2:
        st.header("About This App")
        st.write("This app generates a character based on the weather data of a chosen location.")

if __name__ == "__main__":
    main()
