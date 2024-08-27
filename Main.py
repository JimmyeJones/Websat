import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime


#PAGE SETUP
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
#END OF PAGE SETUP



# IP of Flask server
base_url = st.secrets["IP"]



# Function to get all image paths
def get_image_paths():
    try:
        response = requests.get(f"{base_url}/images")
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
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




st.title("WebSat")
st.text("Satellite reception site")

viewmode = st.selectbox("Select display mode", ["List view", "Frame view"])

# Sidebar

prereq_1 = [["GOES-16", "GOES-18", "NWS", "Unknown"], ["GOES 16 Geostationary Satellite", "GOES 18 Geostationary Satellite", "National Weather Service", "Other"]]

req_1 = st.sidebar.selectbox("Satellite/Source", prereq_1[1])

req_1_out = prereq_1[0][prereq_1[1].index(req_1)]

req_1_image_paths = []
for image86 in all_image_paths:
    if req_1_out in image86:
        req_1_image_paths.append(image86)
preprereq_2 = ["", "Full Disk", "Mesoscale 1", "Mesoscale 2"]
prereq_2 = []
for imagepath1 in req_1_image_paths:
    for pre in preprereq_2:
        if pre in imagepath1:
            if pre not in prereq_2:
                prereq_2.append(pre)
                break
            
req_2 = st.sidebar.selectbox("Image Size", prereq_2)

req_2_image_paths = []
for image86 in req_1_image_paths:
    if req_2 in image86:
        req_2_image_paths.append(image86)
preprereq_3 = [["", "_Clean_Longwave_IR_Window", "Dirty_Longwave_Window", "Dirty_Longwave_Window_-_CIRA", "GEO_False_Color", "Infrared_Longwave_Window_Band", "Mid-level_Tropospheric_Water_Vapor", "Shortwave_Window_Band", "Upper-Level_Tropospheric_Water_Vapor", "G16_2", "G16_7", "G16_8", "G16_9", "G16_13", "G16_14", "G16_15"], ["All Channels", "Clean Longwave IR Window", "Dirty Longwave Window", "Dirty Longwave Window - CIRA", "False Color", "Infrared Longwave Window Band", "Mid-level Tropospheric Water Vapor", "Shortwave Window Band", "Upper-Level Tropospheric Water Vapor", "Channel 2", "Channel 7", "Channel 8", "Channel 9", "Channel 13", "Channel 14", "Channel 15"]]
prereq_3 = []
for imagepath1 in req_2_image_paths:
    for pre in preprereq_3[0]:
        if pre in imagepath1:
            if preprereq_3[1][preprereq_3[0].index(pre)] not in prereq_3:
                prereq_3.append(preprereq_3[1][preprereq_3[0].index(pre)])
                break


req_3 = st.sidebar.selectbox("Channel", prereq_3)
req_3_out = preprereq_3[0][preprereq_3[1].index(req_3)]
if req_1_out == "NWS" or req_1_out == "Unknown":
    prereq_4 = ["None"]
else:
    prereq_4 = ["None", "Map"]
req_4 = st.sidebar.selectbox("Overlay", prereq_4)
if req_4 == "None":
    req_4 = ""
elif req_4 == "Map":
    req_4 = "_map"
#Report a bug

st.sidebar.link_button("Report a bug", "https://docs.google.com/forms/d/e/1FAIpQLSdHtg0td5xtoKiJftAAhd9x-T80IpTNn_cWLaxAHsNssbrVbw/viewform?usp=sf_link")

#contact me
st.sidebar.link_button("Contact", "mailto:app.websat@gmail.com")


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
    if req_1_out in path:
        if req_2 in path:
            if req_3_out in path:
                if req_4 == "":
                    if "_map" not in path:
                        filtered_image_paths.append(path)
                elif req_4 in path:
                    filtered_image_paths.append(path)

st.write(f"Found {len(filtered_image_paths)} images.")

if viewmode == "List view":
    load_limit = st.slider("Number of Images to load", 5, 50, 5, 5)
    # Display images
    images_shown = 0
    for image_path in filtered_image_paths:
        if images_shown >= load_limit:
            break
        preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
        full_url = f"{base_url}/image/{image_path}"
        try:
            if req_1_out == "NWS":
                response = requests.get(full_url)
            else:
                response = requests.get(preview_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=image_path, use_column_width=True)
                images_shown += 1
                if st.button(f"Load Download Button"):
                    st.download_button(
                        label="Download Full Resolution",
                        data=requests.get(full_url).content,
                        file_name=image_path.split("/")[-1],
                        mime='image/jpeg'
                    )
            else:
                print(f"Error loading preview: {response.status_code}")
        except Exception as e:
            print(f"Exception loading preview: {e}")   

elif viewmode == "Frame view":
    # Set up the stateful image index
    if "image_index" not in st.session_state:
        st.session_state.image_index = 0

    # Displaying the buttons inside the container
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Next") and st.session_state.image_index > 0:
            st.session_state.image_index -= 1
    with col2:
        if st.button("Reset"):
            st.session_state.image_index = 0
    with col3:
        if st.button("Previous") and st.session_state.image_index < len(filtered_image_paths) - 1:
            st.session_state.image_index += 1   
    try:
        image_path = filtered_image_paths[st.session_state.image_index]
    except IndexError:
        st.session_state.image_index = 0
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
            print(f"Error loading preview: {response.status_code}")
    except Exception as e:
        print(f"Exception loading preview: {e}")


