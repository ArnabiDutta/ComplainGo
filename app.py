import streamlit as st
from PIL import Image
import time
import os

# --- Import our real AI and Form Filling functions ---
from ai_handler import classify_image, generate_complaint_text
from form_filler import submit_to_replica_form

# --- Page Configuration and CSS (No changes) ---
st.set_page_config(page_title="Complaingo", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');:root{--sage-green:#8A9A5B;--dark-sage:#556B2F;--light-ivory:#FFFFF0;--text-color:#36454F}html,body,[class*="st-"]{font-family:'Montserrat',sans-serif;color:var(--text-color)}.stApp{background-color:var(--light-ivory)}h1,h2,h3{color:var(--dark-sage);font-weight:700}.stButton>button{color:#FFFFFF;background-color:var(--sage-green);border:2px solid var(--sage-green);border-radius:50px;padding:12px 30px;font-weight:600;transition:all .3s ease-in-out;box-shadow:0 4px 14px 0 rgba(0,0,0,0.1)}.stButton>button:hover{background-color:var(--dark-sage);border-color:var(--dark-sage);transform:translateY(-3px);box-shadow:0 6px 20px 0 rgba(0,0,0,0.15)}[data-testid=stTextInput] input,[data-testid=stFileUploader]{border-radius:10px;border:2px solid var(--sage-green)}[data-testid=stSidebar]{background-color:#FFFFFF;border-right:2px solid #F0F0F0}</style>""", unsafe_allow_html=True)

# --- Session State (No changes) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.image_processed = False

# --- Login Page (No changes) ---
def display_login_page():
    # ... same as before
    st.title("Welcome to Complaingo 🌿")
    st.header("*Jo Dikhe, Bol Do — On-the-Go!*")
    st.markdown("---")
    with st.form("login_form"):
        st.session_state.user_name = st.text_input("Your Name", placeholder="e.g., Ananya Sharma")
        st.session_state.phone_number = st.text_input("Your Contact Number", placeholder="e.g., 9876543210")
        if st.form_submit_button("Start Complaining"):
            if st.session_state.user_name and st.session_state.phone_number:
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Please enter both your name and phone number.")

# --- Main App Page ---
def display_main_app():
    # ... Sidebar and Image Capture (No changes) ...
    with st.sidebar:
        st.title(f"Hi, {st.session_state.user_name.split(' ')[0]}!")
        st.markdown(f'<div style="text-align: center;"><img src="https://static.vecteezy.com/system/resources/previews/009/229/244/original/default-avatar-icon-of-social-media-user-vector.jpg" width="100" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
        if st.button("Logout"):
            for key in st.session_state.keys(): del st.session_state[key]
            st.rerun()
    st.title("Complaingo Dashboard")
    st.markdown("Just capture the issue. We'll handle the rest.")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📸 Capture the Issue")
        source_choice = st.radio("Choose source:", ("Upload Photo", "Use Webcam"), horizontal=True)
        image_data = None
        if source_choice == "Upload Photo":
            image_data = st.file_uploader("Select", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        else:
            image_data = st.camera_input("Point camera", label_visibility="collapsed")

    # --- Processing and Results ---
    if image_data and not st.session_state.image_processed:
        with col2:
            st.subheader("⚙️ AI Analysis & Submission in Progress...")
            st.image(image_data, caption="Analyzing this image...")
            with st.spinner("AI is working its magic..."):
                # --- THIS IS THE CHANGE ---
                # 1. Get the secret here in the main app script
                hf_token = st.secrets.get("HUGGING_FACE_API_KEY", "")

                # 2. Run classification (no change)
                category, confidence = classify_image(image_data)
                
                # 3. Pass the secret token to the generation function
                description = generate_complaint_text(category, hf_token)
                
                # --- (Rest of the logic is the same) ---
                with open("temp_image.jpg", "wb") as f:
                    f.write(image_data.getbuffer())
                submission_success = submit_to_replica_form(
                    user_details={"name": st.session_state.user_name, "phone": st.session_state.phone_number},
                    complaint_details={"category": category, "description": description, "image_path": "temp_image.jpg"}
                )
                st.session_state.results = {"category": category, "confidence": f"{confidence:.0%}", "description": description, "success": submission_success}
                st.session_state.image_processed = True
        st.rerun()

    # --- Display Final Results (No changes) ---
    if st.session_state.get('image_processed', False):
        with col2:
            results = st.session_state.results
            if results["success"]:
                st.success("🎉 Your complaint has been submitted successfully!"); st.balloons()
            else: st.error("⚠️ There was a problem submitting your complaint. Check the terminal for errors.")
            st.subheader("Submission Summary")
            st.metric("Detected Issue", results['category'])
            st.metric("Confidence", results['confidence'])
            st.text_area("Submitted Complaint Text", results['description'], height=150)
            if st.button("File Another Complaint"):
                st.session_state.image_processed = False
                st.session_state.pop('results', None); st.rerun()

# --- Main Router (No changes) ---
if not st.session_state.get('logged_in', False):
    display_login_page()
else:
    display_main_app()
