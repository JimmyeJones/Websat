import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

# IP of Flask server
base_url = st.secrets["IP"]

st.title("WebSat")
st.text("Satellite reception site")

load_limit = st.slider("Number of Images to load", 0, 50, 5, 5)

# Sidebar
req_1 = st.sidebar.selectbox("Satellite/Source", ["GOES-16", "GOES-18", "NWS", "Unknown"])
req_2 = st.sidebar.selectbox("Image Size", ["", "Full Disk", "Mesoscale 1", "Mesoscale 2"])
req_3 = st.sidebar.selectbox("Channel", ["", "_Clean_Longwave_IR_Window"])

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

# Function to extract datetime from path
def extract_datetime_from_path(path):
    try:
        date_str = path.split('/')[-2]
        return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None

# Get the list of image paths
all_image_paths = get_image_paths()

# Sort image paths by datetime
sorted_image_paths = sorted(
    [path for path in all_image_paths if extract_datetime_from_path(path) is not None],
    key=lambda x: extract_datetime_from_path(x),
    reverse=True
)

# Filter image paths based on criteria
filtered_image_paths = [path for path in sorted_image_paths if req_1 in path and req_2 in path and req_3 in path]

st.write(f"Found {len(filtered_image_paths)} images.")

# Display images
images_shown = 0
for image_path in filtered_image_paths:
    if images_shown >= load_limit:
        break
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
            images_shown += 1
        else:
            st.write(f"Error loading preview: {response.status_code}")
    except Exception as e:
        st.write(f"Exception loading preview: {e}")
