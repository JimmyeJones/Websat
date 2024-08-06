import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime

# IP of Flask server
base_url = st.secrets["IP"]

st.title("WebSat")
st.text("Satellite reception site")

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
    preview_url = f"{base_url}/preview/{image_path}?width=700&height=700"
    full_url = f"{base_url}/image/{image_path}"
    st.write(f"Preview URL: {preview_url}")
    st.write(f"Full Resolution URL: {full_url}")
    try:
        response = requests.get(preview_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=image_path, use_column_width=True)
            image_url = full_url

            # Fetch the image
            response = requests.get(image_url)
            # Get the current time
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            # Extract file extension from the image URL
            file_extension = image_url.split('.')[-1]
    
            # Create a filename with the current timestamp
            file_name = f"image_{timestamp}.{file_extension}"

            st.download_button(
                label="Download Full Resolution",
                data=response.content,
                file_name=file_name,
                mime=f"image/{file_extension}"
            )
        
        else:
            st.write(f"Error loading preview: {response.status_code}")
    except Exception as e:
        st.write(f"Exception loading preview: {e}")
