import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import base64
import os
import warnings

GEMINI_API_KEY = st.sidebar.text_input(label="Enter your Gemini-pro API key", type="password")
load_dotenv()
warnings.filterwarnings("ignore")


def get_response(text):
    model=ChatGoogleGenerativeAI(
        api_key=GEMINI_API_KEY,
        model="gemini-2.0-flash",
        temperature=1
    )
    response = model.invoke(messages)  # send the prompt + image
    return response.content


def get_file(file):
    content = file.read()
    encode = base64.b64encode(content).decode()
    return encode


file_upload = st.sidebar.file_uploader("upload image", type=["jpg","png","jpeg"])
if file_upload:
    st.sidebar.image(file_upload)
    st.sidebar.success("submit the image ✅")

# --- Camera Control for Wildfire Capture ---

# Disable camera if a file is uploaded
camera_disabled = file_upload is not None
st.subheader("📸 Capture or Upload Wildfire Image")

if st.button("Close Camera"):
    camera_disabled = True
if st.button("Open Camera"):
    if file_upload:
        camera_disabled = True
        st.warning("⚠️ Please remove the uploaded image before using the camera.")
    else:
        camera_disabled = False

# Capture photo using camera
photo = st.camera_input("Capture wildfire image", disabled=camera_disabled)

# --- Determine which image source to use ---
if photo:
    st.success("✅ Wildfire image captured successfully!")
    encode = get_file(photo)
elif file_upload:
    encode = get_file(file_upload)
    st.success("✅ Wildfire image uploaded successfully!")
else:
    encode = None
    st.info("📤 Please upload or capture an image showing the wildfire scene.")

# if file_upload:
#     encode = get_file(file_upload)
# else:
#     encode = None



st.subheader("🌦️ Wildfire Environmental Conditions")

# Use columns for a neat layout
col1, col2 = st.columns(2)

with col1:
    wind_speed = st.text_input("🌬️ Wind Speed", placeholder="e.g., 25 km/h")
    temperature = st.text_input("🌡️ Temperature", placeholder="e.g., 38°C")

with col2:
    season = st.selectbox(
        "🌤️ Season",
        ["Select Season", "Summer", "Winter", "Monsoon", "Autumn", "Spring"]
    )
    vegetation_type = st.text_input("🌾 Vegetation Type", placeholder="e.g., Dry grass, Forest, Shrubs")

# Separate full-width input for terrain and safety
terrain = st.text_input("⛰️ Terrain Type", placeholder="e.g., Hilly, Flat, Forested, Coastal")
precaution = st.text_area(
    "🚨 Safety Measures or Notes",
    height=100,
    placeholder="Example: Evacuate nearby areas, alert authorities, use fire retardant around structures."
)

# Combine all user inputs into one formatted string for AI
wildfire_context = (
    f"Wind Speed: {wind_speed}\n"
    f"Temperature: {temperature}\n"
    f"Season: {season}\n"
    f"Vegetation Type: {vegetation_type}\n"
    f"Terrain: {terrain}\n"
    f"Precautionary Notes: {precaution}"
)


submit=st.button("submit the image")

# --- Fire Detection & Analysis Prompt ---
# prompt = """
# You are an advanced AI system trained for wildfire detection and environmental impact assessment.
# Your task is to analyze the uploaded image and determine:
# 1. Whether fire or no fire is present.
# 2. If fire is detected:
#    - Estimate the intensity and speed of fire spread.
#    - Estimate the amount of CO₂ emissions based on visual cues (e.g., smoke density, area affected).
#    - Estimate the number of wildfire sources visible.
#    - Suggest appropriate safety and wildfire prevention precautions.
# 3. If no fire is detected, simply respond with "No Fire Detected" and provide brief environmental safety recommendations.

# Guidelines:
# - Base your analysis only on the visible image content.
# - Use clear, concise, and factual language.
# - Provide numerical or qualitative estimates (e.g., "Moderate CO₂ emission", "Rapid spread likely").
# - Maintain a professional and informative tone.
# - Avoid unnecessary explanations — focus on detection, estimation, and prevention advice.
# """

prompt = f"""
You are an advanced AI system trained for wildfire detection and environmental impact assessment.

Your task is to analyze the uploaded image **along with the following environmental details** provided by the user:

{wildfire_context}

You must determine:
1. Whether fire or no fire is present.
2. If fire is detected:
   - Estimate the **intensity** and **speed of fire spread** considering the given conditions (e.g., wind speed, temperature, vegetation type, terrain).
   - Estimate the **amount of CO₂ emissions** based on visual cues (e.g., smoke density, area affected) and environmental context.
   - Estimate the **number of wildfire sources** visible in the image.
   - Suggest **appropriate safety measures** and **wildfire prevention precautions**.
3. If no fire is detected:
   - Respond with **"No Fire Detected"**.
   - Provide **brief environmental safety recommendations** based on the context provided.

Guidelines:
- Base your primary detection on the **uploaded image**, but refine your estimates using the **environmental inputs** above.
- Use clear, concise, and factual language.
- Provide **numerical or qualitative estimates** (e.g., "Moderate CO₂ emission", "Rapid spread likely").
- Maintain a **professional, analytical, and informative tone**.
- Focus strictly on detection, estimation, and prevention advice.
"""


# --- Message Construction for Gemini ---
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"Follow the instructions: {prompt}"
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{encode}"
            },
           {
                "type": "text",
                "text": f"Additional wildfire environmental context:\n{wildfire_context}"
            }
        ]
    }
]

# --- Submit Button: Get Fire Analysis ---
if submit:    
    with st.spinner("Analyzing image for wildfire detection and CO₂ estimation..."):
        try:
            response = get_response(messages)
            st.success("✅ Analysis Complete!")
            
            # Display structured result
            st.subheader("🌋 Fire Detection Report")
            st.write(response)

        except Exception as e:
            st.error(f"⚠️ Error during analysis: {str(e)}")