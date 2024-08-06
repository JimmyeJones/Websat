import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Base URL of the Flask server via ngrok
base_url = "https://d124-24-149-99-6.ngrok-free.app"  # Replace with your ngrok URL

st.title("GOES 16 Image Viewer")

st.write(f"Using Flask server at: {base_url}")

# Function to get all image paths
def get_image_paths():
    try:
        response = requests.get(f"{base_url}/images")
        st.write(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            st.write(f"Error: {response.text}")
            return []
    except Exception as e:
        st.write(f"Exception: {e}")
        return []

# Get the list of image paths
image_paths = get_image_paths()

st.write(f"Found {len(image_paths)} images.")

# Display images
for image_path in image_paths:
    st.write(f"Image: {image_path}")
    image_url = f"{base_url}/image/{image_path}"
    st.write(f"Image URL: {image_url}")
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=image_path)
        else:
            st.write(f"Error loading image: {response.status_code}")
    except Exception as e:
        st.write(f"Exception loading image: {e}")
