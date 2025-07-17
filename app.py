import streamlit as st
from PIL import Image
import time
import os

# --- Import our real AI and Form Filling functions ---
from ai_handler import classify_image, generate_complaint_text
from form_filler import submit_to_replica_form

# --- Page Configuration (Must be the first command) ---
st.set_page_config(
    page_title="Complaingo",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Aesthetics (Pastel/Sage Green Theme) ---
# --- NO CHANGES IN THIS SECTION ---
st.markdown("""
<style>
    /* --- Import Google Font --- */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    :root {--sage-green: #8A9A5B; --dark-sage: #556B2F; --pastel-pink: #FFDAB9; --light-ivory: #FFFFF0; --text-color: #36454F;}
    html, body, [class*="st-"], .st-emotion-cache-1gulkj5 {font-family: 'Montserrat', sans-serif; color: var(--text-color);}
    .stApp {background-color: var(--light-ivory);}
    h1, h2, h3 {color: var(--dark-sage); font-weight: 700;}
    .stButton > button {color: #FFFFFF; background-color: var(--sage-green); border: 2px solid var(--sage-green);
        border-radius: 50px; padding: 12px 30px; font-weight: 600; transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 14px 0 rgba(0,0,0,0.1);}
    .stButton > button:hover {background-color: var(--dark-sage); border-color: var(--dark-sage);
        transform: translateY(-3px); box-shadow: 0 6px 20px 0 rgba(0,0,0,0.15);}
    .stButton > button:active {transform: translateY(0px);}
    [data-testid="stTextInput"] input, [data-testid="stFileUploader"] {border-radius: 10px; border: 2px solid var(--sage-green);}
    [data-testid="stSidebar"] {background-color: #FFFFFF; border-right: 2px solid #F0F0F0;}
</style>
""", unsafe_allow_html=True)


# --- DELETE THE MOCK AI and FORM FILLER FUNCTIONS --- ### 2. CHANGE THIS LINE ###
# The `mock_fill_form` function is no longer needed. We are now using the real one.


# --- Initialize Session State ---
# --- NO CHANGES IN THIS SECTION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.phone_number = ""
    st.session_state.image_processed = False


# ===================================================================
# ======================== LOGIN PAGE ===============================
# ===================================================================
# --- NO CHANGES IN THIS SECTION ---
def display_login_page():
    st.title("Welcome to Complaingo 🌿")
    st.header("*Jo Dikhe, Bol Do — On-the-Go!*")
    st.markdown("---")
    with st.form("login_form"):
        name = st.text_input("Your Name", placeholder="e.g., Ananya Sharma")
        phone = st.text_input("Your Contact Number", placeholder="e.g., 9876543210")
        submitted = st.form_submit_button("Start Complaining")
        if submitted:
            if name and phone:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.phone_number = phone
                st.rerun()
            else:
                st.error("Please enter both your name and phone number.")


# ===================================================================
# ======================== MAIN APP PAGE ============================
# ===================================================================
def display_main_app():
    # --- Sidebar with Profile ---
    # --- NO CHANGES IN THIS SECTION ---
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user_name.split(' ')[0]}!")
        st.markdown(f"""<div style="text-align: center;"><img src="https://static.vecteezy.com/system/resources/previews/009/292/244/original/default-avatar-icon-of-social-media-user-vector.jpg" width="100" style="border-radius: 50%;"></div>""", unsafe_allow_html=True)
        st.write(f"**Name:** {st.session_state.user_name}")
        st.write(f"**Phone:** {st.session_state.phone_number}")
        if st.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # --- Main Content ---
    st.title("Complaingo Dashboard")
    st.markdown("Just capture the issue. We'll handle the rest.")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📸 Capture the Issue")
        source_choice = st.radio("Choose your source:", ("Upload a Photo", "Use Webcam"), horizontal=True)
        image_data = None
        if source_choice == "Upload a Photo":
            image_data = st.file_uploader("Select an image file", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        else:
            image_data = st.camera_input("Point your camera at the issue", label_visibility="collapsed")

    # --- Processing and Results ---
    if image_data and not st.session_state.image_processed:
        with col2:
            st.subheader("⚙️ AI Analysis & Submission in Progress...")
            st.image(image_data, caption="Analyzing this image...")

            with st.spinner("AI is working its magic..."):
                # --- THIS IS THE MAIN CHANGE ---  ### 3. CHANGE THIS BLOCK ###

                # 1. Classify image and Generate text (same as before)
                category, confidence = classify_image(image_data)
                description = generate_complaint_text(category)

                # 2. Save the image to a temporary file for Selenium to access
                # This is a new, necessary step for the form filler
                with open("temp_image.jpg", "wb") as f:
                    f.write(image_data.getbuffer())

                # 3. Call the REAL form filler function
                submission_success = submit_to_replica_form(
                    user_details={"name": st.session_state.user_name, "phone": st.session_state.phone_number},
                    complaint_details={"category": category, "description": description, "image_path": "temp_image.jpg"}
                )

                # 4. Store the results, including the success status
                st.session_state.results = {
                    "category": category,
                    "confidence": f"{confidence:.0%}",
                    "description": description,
                    "success": submission_success  # Store if it worked
                }
                st.session_state.image_processed = True
                
        st.rerun()

    # --- Display Final Results After Processing ---
    if st.session_state.get('image_processed', False):
        with col2:
            results = st.session_state.results
            
            # Show a success or error message based on the result
            if results["success"]:
                st.success("🎉 Your complaint has been submitted successfully!")
                st.balloons()
            else:
                st.error("⚠️ There was a problem submitting your complaint. Please check the terminal for errors.")
            
            st.subheader("Submission Summary")
            st.metric("Detected Issue", results['category'])
            st.metric("Confidence", results['confidence'])
            st.text_area("Submitted Complaint Text", results['description'], height=150)
            
            if st.button("File Another Complaint"):
                st.session_state.image_processed = False
                st.session_state.pop('results', None)
                st.rerun()


# --- Main Router ---
# --- NO CHANGES IN THIS SECTION ---
if not st.session_state.logged_in:
    display_login_page()
else:
    display_main_app()
