import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Base URL of the Flask server via ngrok
base_url = "https://d124-24-149-99-6.ngrok-free.app"  # Replace with your ngrok URL

# Function to get all image paths
def get_image_paths():
    response = requests.get(f"{base_url}/images")
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Function to load an image from a URL
def load_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

# Streamlit App
st.title("GOES 16 Image Viewer")

# Get the list of image paths
image_paths = get_image_paths()

# Create a sidebar for folder selection
folder = st.sidebar.selectbox("Select Folder", list(set(os.path.dirname(path) for path in image_paths)))

# Filter images by selected folder
folder_images = [path for path in image_paths if path.startswith(folder)]

# Display images
for image_path in folder_images:
    st.write(f"Image: {os.path.basename(image_path)}")
    image = load_image(f"{base_url}/image/{image_path}")
    if image:
        st.image(image, caption=os.path.basename(image_path))
