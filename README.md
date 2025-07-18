# ComplainGo – AI-Powered Road Complaint Assistant

*Jo Dikhe, Bol Do — On-the-Go!*

## About This Project

ComplainGo is a **concept prototype** that reimagines how citizens report road and infrastructure issues in India.
It’s designed as a **scalable model for government services**, automating the entire complaint process — from identifying the issue to filling the official forms.

The project focuses on **simplicity, accessibility, and speed**, aiming to remove barriers like complex forms, lack of awareness, and time-consuming processes.

---
# https://complaingo-team3.streamlit.app/ [Try it Here]

[Screencast from 07-18-2025 04:51:41 PM.webm](https://github.com/user-attachments/assets/3c8b0d52-ac32-47a8-a9d0-f743153c5e79)

## Why This Project?

### The Problem

India witnesses over **2,300 deaths and 6,800 accidents yearly** due to potholes, waterlogging, poor street lighting, and other infrastructure issues.
Yet, complaints often go unreported due to the following challenges:

1. **Don’t Know Where to Complain**
   Lack of awareness about official platforms like CPGRAMS or municipal apps.

2. **Too Time-Consuming**
   Filling forms online takes **10–15 minutes**, discouraging people with limited time.

3. **Too Many Categories**
   Users often don’t know which category their issue fits into (e.g., is a water leak "sanitation" or "drainage"?).

4. **Low Digital Literacy**
   Many citizens, especially elderly or rural users, find online systems difficult to navigate.

---

## Our Solution

ComplainGo solves these pain points with an AI-powered assistant:

- Users simply take or upload a photo of the issue with your phone.

- The system classifies the problem (e.g., "Damaged Road") using a custom Teachable Machine model.

- A Gemini LLM generates a formal complaint text automatically.

- The data is plugged into a replica of the official form via Selenium automation.

- Lightweight and optimized — the entire pipeline runs smoothly on mobile phones, ensuring accessibility on-the-go.

**The result: a complaint can be submitted in seconds — no confusion, no wasted time.**



---

## Technical Pipeline

### 1. **Frontend Interface (Streamlit)**

* Mobile-first, responsive design.
* Supports **image upload and webcam capture**.
* User session management for smooth experience.

### 2. **AI Inference Core (TFLite + Gemini)**

* **Visual Classification:** TensorFlow Lite CNN classifies road issues in real time.
* **Complaint Generation:** Google Gemini LLM generates formal complaint text using few-shot prompts.

### 3. **Robotic Process Automation (Selenium)**

* Automates filling out official complaint forms using headless Chromium.

### 4. **Deployment**

* Streamlit Cloud deployment with containerized dependencies (requirements.txt, packages.txt).
* Secure API key management via Streamlit Secrets.

---

## Future Scope

1. **Automatic Geolocation**
   Use GPS metadata or browser geolocation to auto-fill precise complaint locations.

2. **Firebase Issue Hub**
   Store reports (images, categories, timestamps) in Firestore for heatmaps and analytics.

3. **Repair Tracking**
   Track complaint status (Reported → In Progress → Resolved) with notifications to users.

4. **AI-Powered Route Planner**
   Use **AI path planning** by combining road-quality scores and traffic data to suggest detours around damaged roads.

---

## Contributing

We welcome contributions from developers, designers, and AI enthusiasts.

* Improve the classification model.
* Enhance UI/UX with better animations and themes.
* Add integrations for more government platforms.

To contribute:

1. Fork this repo.
2. Create a feature branch.
3. Submit a pull request with detailed notes.

---

## Tech Stack

* **Frontend:** Streamlit (with custom CSS)
* **AI Models:** Teachable Machine (TFLite), Google Gemini LLM
* **Automation:** Selenium with Chromium
* **Backend:** Serverless architecture on Streamlit Cloud
* **Other Tools:** Python, OpenAI/Hugging Face APIs, Firebase (future)

