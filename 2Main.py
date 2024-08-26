import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
from functools import lru_cache

# PAGE SETUP
st.set_page_config(
    page_title="Websat",
    page_icon="https://raw.githubusercontent.com/JimmyeJones/Websat/main/icon.jpg",
    initial_sidebar_state="expanded"
)

# Hiding the footer and hamburger menu
st.markdown(
    """
    <style>
    .st-emotion-cache-mnu3yk.ef3psqc6, .st-emotion-cache-mnu3yk.ef3psqc6 {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# IP of Flask server
base_url = st.secrets["IP"]

@st.cache_data(show_spinner=False)
def get_image_paths():
    try:
        response = requests.get(f"{base_url}/images")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

@st.cache_data(show_spinner=False)
def extract_datetime_from_path(path):
    try:
        date_str = path.split('/')[-2]
        return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None

# Get the list of image paths
all_image_paths = get_image_paths()

# Sidebar
prereq_1 = [["GOES-16", "GOES-18", "NWS", "Unknown"], ["GOES 16 Geostationary Satellite", "GOES 18 Geostationary Satellite", "National Weather Service", "Other"]]
req_1 = st.sidebar.selectbox("Satellite/Source", prereq_1[1])
req_1_out = prereq_1[0][prereq_1[1].index(req_1)]

@st.cache_data(show_spinner=False)
def filter_images_by_source(all_paths, req_1_out):
    return [path for path in all_paths if req_1_out in path]

req_1_image_paths = filter_images_by_source(all_image_paths, req_1_out)

preprereq_2 = ["", "Full Disk", "Mesoscale 1", "Mesoscale 2"]
prereq_2 = sorted(set([pre for path in req_1_image_paths for pre in preprereq_2 if pre in path]))
req_2 = st.sidebar.selectbox("Image Size", prereq_2)

preprereq_3 = [["", "_Clean_Longwave_IR_Window", "Dirty_Longwave_Window", "Dirty_Longwave_Window_-_CIRA", "GEO_False_Color", "Infrared_Longwave_Window_Band", "Mid-level_Tropospheric_Water_Vapor", "Shortwave_Window_Band", "Upper-Level_Tropospheric_Water_Vapor", "G16_2", "G16_7", "G16_8", "G16_9", "G16_13", "G16_14", "G16_15"],
               ["All Channels", "Clean Longwave IR Window", "Dirty Longwave Window", "Dirty Longwave Window - CIRA", "False Color", "Infrared Longwave Window Band", "Mid-level Tropospheric Water Vapor", "Shortwave Window Band", "Upper-Level Tropospheric Water Vapor", "Channel 2", "Channel 7", "Channel 8", "Channel 9", "Channel 13", "Channel 14", "Channel 15"]]

prereq_3 = sorted(set([preprereq_3[1][preprereq_3[0].index(pre)] for path in req_1_image_paths for pre in preprereq_3[0] if pre in path]))
req_3 = st.sidebar.selectbox("Channel", prereq_3)
req_3_out = preprereq_3[0][preprereq_3[1].index(req_3)]

prereq_4 = ["None"] if req_1_out in ["NWS", "Unknown"] else ["None", "Map"]
req_4 = st.sidebar.selectbox("Overlay", prereq_4)
req_4 = "" if req_4 == "None" else "_map"

# Filter image paths based on criteria
@st.cache_data(show_spinner=False)
def filter_images(req_1_out, req_2, req_3_out, req_4, sorted_paths):
    return [
        path for path in sorted_paths
        if req_1_out in path and req_2 in path and req_3_out in path and (req_4 == "" and "_map" not in path or req_4 in path)
    ]

# Sort and filter paths
paths_with_dates = [path for path in all_image_paths if extract_datetime_from_path(path) is not None]
paths_without_dates = [path for path in all_image_paths if extract_datetime_from_path(path) is None]
sorted_paths = sorted(paths_with_dates, key=lambda x: extract_datetime_from_path(x), reverse=True) + sorted(paths_without_dates)

filtered_image_paths = filter_images(req_1_out, req_2, req_3_out, req_4, sorted_paths)

st.write(f"Found {len(filtered_image_paths)} images.")

viewmode = st.selectbox("Select display mode", ["List view", "Frame view"])

if viewmode == "List view":
    load_limit = st.slider("Number of Images to load", 5, 50, 5, 5)
    images_shown = 0
    for image_path in filtered_image_paths[:load_limit]:
        preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
        full_url = f"{base_url}/image/{image_path}"
        try:
            response = requests.get(full_url if req_1_out == "NWS" else preview_url)
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
    if "image_index" not in st.session_state:
        st.session_state.image_index = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous") and st.session_state.image_index > 0:
            st.session_state.image_index -= 1
    with col2:
        if st.button("Reset"):
            st.session_state.image_index = 0
    with col3:
        if st.button("Next") and st.session_state.image_index < len(filtered_image_paths) - 1:
            st.session_state.image_index += 1
    
    image_path = filtered_image_paths[st.session_state.image_index]
    preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
    full_url = f"{base_url}/image/{image_path}"
    try:
        response = requests.get(full_url if req_1_out == "NWS" else preview_url)
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
