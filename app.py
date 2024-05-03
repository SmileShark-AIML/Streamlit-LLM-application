import streamlit as st
from streamlit_option_menu import option_menu
from config import session_init
from data import get_s3_list

from sidebar import sidebar_UI 
from chat import chat_UI
from kb import kb_UI
from experimental import experimental_UI
from dashboard import dashboard_UI
from comparison import comparison_UI

st.set_page_config(layout="wide", page_icon=":shark:", page_title="SmileShark LLM APP Demo (Bedrock)")

session_init()

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {visibility: hidden;height: 0%;position: fixed;}
                div[data-testid="stDecoration"] {visibility: hidden;height: 0%;position: fixed;}
                div[data-testid="stStatusWidget"] {visibility: hidden;height: 0%;position: fixed;}
                #MainMenu {visibility: hidden;height: 0%;}
                header {visibility: hidden;height: 0%;}
                footer {visibility: hidden;height: 0%;}
                section.main[class*="st-emotion-cache-"] > div[class^="st-emotion-cache-"] > div > div > div {
                    border: 0px solid #265E9A;border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    height: 50px;display: flex;align-items: center; outline: none;}
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

with st.sidebar:
    button_style = """
        <style>
        div.stButton > button {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    selected = option_menu("Bedrock Chat", ["채팅", 'LLM 비교', 'KB관리', 'Dashboard', 'Experimental'], 
        icons=['chat-left-dots', 'layers-half', 'sliders','graph-up' , 'cone-striped'], menu_icon="send", default_index=0)
    
    sidebar_UI(selected)

if selected == "채팅":
    chat_UI()

if selected == "KB관리": 
    get_s3_list()
    kb_UI()

if selected == "LLM 비교": 
    comparison_UI()

if selected == "Dashboard":
    dashboard_UI()

if selected == "Experimental":
    experimental_UI()