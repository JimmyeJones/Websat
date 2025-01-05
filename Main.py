import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

# PAGE SETUP
st.set_page_config(
    page_title="Websat",
    page_icon="https://raw.githubusercontent.com/JimmyeJones/Websat/main/icon.jpg",
    initial_sidebar_state="expanded"
)

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

# IP of Flask server (secondary storage server)
base_url = st.secrets["IP"]  # Use the public IP or domain of your secondary storage server

# Function to get all image paths
def get_image_paths():
    try:
        response = requests.get(f"{base_url}/images")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching image paths: {e}")
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

# MAIN APP
st.title("WebSat")
st.text("Satellite reception site")

viewmode = st.selectbox("Select display mode", ["List view", "Frame view"])

# Sidebar filters
prereq_1 = [["GOES-16", "GOES-18", "NWS", "Unknown"], ["GOES 16 Geostationary Satellite", "GOES 18 Geostationary Satellite", "National Weather Service", "Other"]]
req_1 = st.sidebar.selectbox("Satellite/Source", prereq_1[1])
req_1_out = prereq_1[0][prereq_1[1].index(req_1)]

req_1_image_paths = [img for img in all_image_paths if req_1_out in img]
req_2 = st.sidebar.selectbox("Image Size", ["", "Full Disk", "Mesoscale 1", "Mesoscale 2"])
req_2_image_paths = [img for img in req_1_image_paths if req_2 in img]

# Further filtering
preprereq_3 = [["", "_Clean_Longwave_IR_Window", "GEO_False_Color", "Mid-level_Tropospheric_Water_Vapor"], ["All Channels", "Clean Longwave IR Window", "False Color", "Mid-level Tropospheric Water Vapor"]]
req_3 = st.sidebar.selectbox("Channel", preprereq_3[1])
req_3_out = preprereq_3[0][preprereq_3[1].index(req_3)]
req_3_image_paths = [img for img in req_2_image_paths if req_3_out in img]

req_4 = st.sidebar.selectbox("Overlay", ["None", "Map"])
req_4 = "_map" if req_4 == "Map" else ""
filtered_image_paths = [img for img in req_3_image_paths if req_4 in img]

st.write(f"Found {len(filtered_image_paths)} images.")

# Display images
if viewmode == "List view":
    load_limit = st.slider("Number of Images to load", 5, 50, 5, 5)
    for image_path in filtered_image_paths[:load_limit]:
        preview_url = f"{base_url}/preview/{image_path}"
        full_url = f"{base_url}/image/{image_path}"
        
        # Display preview
        st.image(preview_url, caption=image_path, use_column_width=True)

        # Download button
        if st.button(f"Load Download Button", key=image_path):
            st.markdown(
                f'<a href="{full_url}" download="{image_path.split("/")[-1]}">Download Full Resolution</a>',
                unsafe_allow_html=True
            )

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
    preview_url = f"{base_url}/preview/{image_path}"
    full_url = f"{base_url}/image/{image_path}"
    
    st.image(preview_url, caption=image_path, use_column_width=True)
    st.markdown(
        f'<a href="{full_url}" download="{image_path.split("/")[-1]}">Download Full Resolution</a>',
        unsafe_allow_html=True
    )
