import streamlit as st

def session_init() :

    if "s3_table" not in st.session_state:
        st.session_state['s3_table'] = ""

    if "messages" not in st.session_state:
        st.session_state.messages = {}

    if "Historys" not in st.session_state:
        st.session_state.Historys = ["History 1", "History 2", "History 3", "History 4", "History 5"]

    if "history_files" not in st.session_state:
        st.session_state.history_files = {}

    if "current_History" not in st.session_state:
        st.session_state.current_History = st.session_state.Historys[0]