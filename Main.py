import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os

# Base URL of the Flask server via ngrok or DDNS
base_url = st.secrets["IP"]  # Keep the environment variable name the same

st.title("GOES 16 Image Viewer")

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

# Function to get subfolders at a given path
def get_subfolders(path, all_paths):
    subfolders = list(set([os.path.join(*p.split(os.path.sep)[:len(path.split(os.path.sep))+1]) 
                           for p in all_paths if p.startswith(path)]))
    subfolders = [os.path.basename(subfolder) for subfolder in subfolders if subfolder != path]
    subfolders.sort()
    return subfolders

# Sidebar for folder selection
selected_folder = ""
all_selected_folders = []

while True:
    folders = get_subfolders(selected_folder, image_paths)
    if not folders:
        break
    selected_sub_folder = st.sidebar.selectbox(f"Select Folder at {selected_folder}", [""] + folders, key=selected_folder)
    if selected_sub_folder == "":
        break
    selected_folder = os.path.join(selected_folder, selected_sub_folder)
    all_selected_folders.append(selected_folder)

# Filter images by selected folder
if all_selected_folders:
    selected_folder = os.path.join(*all_selected_folders)
    image_paths = [path for path in image_paths if path.startswith(selected_folder)]

st.write(f"Found {len(image_paths)} images.")

# Display images
for image_path in image_paths:
    st.write(f"Image: {image_path}")
    preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
    full_url = f"{base_url}/image/{image_path}"
    st.write(f"Preview URL: {preview_url}")
    st.write(f"Full Resolution URL: {full_url}")
    try:
        response = requests.get(preview_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=image_path, use_column_width=True)
            st.write(f"[Download Full Resolution]({full_url})")
        else:
            st.write(f"Error loading preview: {response.status_code}")
    except Exception as e:
        st.write(f"Exception loading preview: {e}")
