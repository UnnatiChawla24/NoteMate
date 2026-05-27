import streamlit as st

# Dictionary defining multiple UI themes with colors for background, sidebar, and text
themes = {
    "Classic Light": {
        "bg": "#f5f5f5",  # Light background color
        "sidebar": "#e0e0e0",  # Light sidebar background
        "text": "#000000",  # Black text color
    },
    "Classic Dark": {
        "bg": "#1e1e1e",  # Dark background color
        "sidebar": "#121212",  # Dark sidebar background
        "text": "#A9A9A9",  # Gray text color
    },
    "Midnight Neon": {
        "bg": "#1a1a2e",  # Deep blue background
        "sidebar": "#16213e",  # Dark blue sidebar
        "text": "#00feba",  # Neon cyan text color
    },
    "Desert Sand": {
        "bg": "#f7f4ef",  # Soft sand-like background
        "sidebar": "#d9cbbd",  # Muted sand sidebar
        "text": "#6e5c4a",  # Brownish text color
    },
    "Ocean Breeze": {
        "bg": "#c9f0f2",  # Light aqua background
        "sidebar": "#5bc0be",  # Teal sidebar
        "text": "#013a44",  # Dark teal text color
    },
}


def apply_theme(theme):
    # Extract individual color settings from the selected theme dictionary
    bg_color = theme["bg"]
    sidebar_color = theme["sidebar"]
    text_color = theme["text"]

    # Inject CSS styles into Streamlit app to customize appearance dynamically
    st.markdown(
        f"""
        <style>
            /* Set main app background color and smooth transition */
            .stApp {{
                background-color: {bg_color};
                transition: background-color 1.5s ease, color 1.5s ease;
            }}

            /* Style the sidebar with background, padding, rounded corners, and transition */
            section[data-testid="stSidebar"]  {{
                background-color: {sidebar_color};
                padding: 1rem,2rem,10rem,2rem;
                border-radius: 10px;
                transition: background-color 1.5s ease, color 1.5s ease;
            }}

            /* Set the color for all main HTML elements and form controls */
            html, body, h1, h2, h3, h4, h5, h6, p, span, div, li, ul, ol, a, label, button, input, select, textarea {{
                color: {text_color} !important;
            }}

            /* Force all elements inside the app container to use the text color */
            .stApp  * {{
                color : {text_color} !important;
            }}

            /* Force all elements inside the sidebar to use the text color */
            .section[data-testid="stSidebar"]  * {{
                color : {text_color} !important;
            }}

        </style>
        """,
        unsafe_allow_html=True,
    )
