import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os

# Base URL of the Flask server via ngrok or DDNS
base_url = st.secrets["IP"]  # Keep the environment variable name the same

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

# Extract unique folder names for filtering
folders = list(set([os.path.dirname(path) for path in image_paths]))
folders.sort()

# Sidebar for folder selection
selected_folder = st.sidebar.selectbox("Select Folder", ["All"] + folders)

# Filter images by selected folder
if selected_folder != "All":
    image_paths = [path for path in image_paths if path.startswith(selected_folder)]

st.write(f"Found {len(image_paths)} images.")

# Display images
for image_path in image_paths:
    st.write(f"Image: {image_path}")
    preview_url = f"{base_url}/preview/{image_path}"
    full_url = f"{base_url}/image/{image_path}"
    st.write(f"Preview URL: {preview_url}")
    st.write(f"Full Resolution URL: {full_url}")
    try:
        response = requests.get(preview_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=image_path)
            st.write(f"[Download Full Resolution]({full_url})")
        else:
            st.write(f"Error loading preview: {response.status_code}")
    except Exception as e:
        st.write(f"Exception loading preview: {e}")
