import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
st.set_page_config(
    page_title="Websat",
    page_icon="https://raw.githubusercontent.com/JimmyeJones/Websat/main/icon.jpg",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# IP of Flask server
base_url = st.secrets["IP"]

st.title("WebSat")
st.text("Satellite reception site")

viewmode = st.selectbox("Select display mode", ["List view", "Frame view"])


# Sidebar
req_1 = st.sidebar.selectbox("Satellite/Source", ["GOES-16", "GOES-18", "NWS", "Unknown"])
req_2 = st.sidebar.selectbox("Image Size", ["", "Full Disk", "Mesoscale 1", "Mesoscale 2"])
req_3 = st.sidebar.selectbox("Channel", ["", "_Clean_Longwave_IR_Window", "Dirty_Longwave_Window", "Dirty_Longwave_Window_-_CIRA", "GEO_False_Color", "Infrared_Longwave_Window_Band", "Mid-level_Tropospheric_Water_Vapor", "Shortwave_Window_Band", "Upper-Level_Tropospheric_Water_Vapor", "G16_2", "G16_7", "G16_8", "G16_9", "G16_13", "G16_14", "G16_15"])
req_4 = st.sidebar.selectbox("Overlay", ["", "_map"])

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

# Separate paths with valid dates and those without
paths_with_dates = [path for path in all_image_paths if extract_datetime_from_path(path) is not None]
paths_without_dates = [path for path in all_image_paths if extract_datetime_from_path(path) is None]

# Sort paths with valid dates by datetime
sorted_paths_with_dates = sorted(paths_with_dates, key=lambda x: extract_datetime_from_path(x), reverse=True)

# Sort paths without valid dates alphabetically
sorted_paths_without_dates = sorted(paths_without_dates)

# Combine sorted paths with dates and sorted paths without dates
sorted_image_paths = sorted_paths_with_dates + sorted_paths_without_dates

# Filter image paths based on criteria
filtered_image_paths = []
for path in sorted_image_paths:
    if req_1 in path:
        if req_2 in path:
            if req_3 in path:
                if req_4 == "":
                    if "_map" not in path:
                        filtered_image_paths.append(path)
                elif req_4 in path:
                    filtered_image_paths.append(path)
st.write(f"Found {len(filtered_image_paths)} images.")



if viewmode == "List view":
    load_limit = st.slider("Number of Images to load", 0, 50, 5, 5)
    # Display images
    images_shown = 0
    for image_path in filtered_image_paths:
        if images_shown >= load_limit:
            break
        preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
        full_url = f"{base_url}/image/{image_path}"
        try:
            if req_1 == "NWS":
                response = requests.get(full_url)
            else:
                response = requests.get(preview_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=image_path, use_column_width=True)
                images_shown += 1
                if st.button(f"Load Download Button for {image_path}"):
                    st.download_button(
                        label="Download Full Resolution",
                        data=requests.get(full_url).content,
                        file_name=image_path.split("/")[-1],
                        mime='image/jpeg'
                    )
            else:
                st.write(f"Error loading preview: {response.status_code}")
        except Exception as e:
            st.write(f"Exception loading preview: {e}")   



elif viewmode == "Frame view":
    image_index = 0
    while viewmode == "Frame view":
        

        # Displaying the buttons inside the container
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Previous"):
                image_index += -1
        with col2:
            if st.button("Next"):
                image_index += 1
            
        image_path = filtered_image_paths[image_index]
        preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
        full_url = f"{base_url}/image/{image_path}"
        try:
            if req_1 == "NWS":
                response = requests.get(full_url)
            else:
                response = requests.get(preview_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=image_path, use_column_width=True)
                if st.button(f"Load Download Button for {image_path}"):
                    st.download_button(
                        label="Download Full Resolution",
                        data=requests.get(full_url).content,
                        file_name=image_path.split("/")[-1],
                        mime='image/jpeg'
                    )
            else:
                st.write(f"Error loading preview: {response.status_code}")
        except Exception as e:
            st.write(f"Exception loading preview: {e}")   
