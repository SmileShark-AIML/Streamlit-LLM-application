import streamlit as st
import boto3
from datetime import datetime
from pytz import timezone

from dotenv import load_dotenv
import os

load_dotenv()

dataSourceId = os.getenv('DATASOURCE_ID')
knowledgeBaseId = os.getenv('KNOWLEDGEBASE_ID')

def utc_to_kst(utc_time):
    """
    UTC 시간을 한국 시간으로 변환하는 함수
    :param utc_time: UTC 시간 문자열 (format: '%Y-%m-%d %H:%M:%S.%f+00:00')
    :return: 한국 시간 문자열 (format: '%Y년 %m월 %d일 %H:%M:%S')
    """
    utc_time = datetime.strptime(str(utc_time), '%Y-%m-%d %H:%M:%S.%f+00:00')
    kst_time = utc_time.replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Seoul'))
    return kst_time.strftime('%Y년 %m월 %d일 %H:%M:%S')

def clear_messages(History):
    if History in st.session_state.messages:
        st.session_state.messages[History] = []
    if History in st.session_state.history_files:
        st.session_state.history_files[History] = []

def set_current_History(History_name, index):
    st.session_state.current_History = History_name
    st.session_state.Historys[index] = History_name

def s3_button_click(s3, uploaded_file):
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        try:
            s3.put_object(Bucket='sharkpt-kb-s3', Key=uploaded_file.name, Body=file_content)
            st.toast("업로드 성공! 동기화를 원하시면 진행해주세요")
        except:
            st.toast("업로드 실패...")
    else:
        st.toast("파일이 선택되지 않았습니다.")

def kb_sync_click(bedrock_agent):
    try:
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId= knowledgeBaseId ,
            dataSourceId= dataSourceId
        )
        st.toast("동기화 진행")
    except:
        st.toast("error")

def update_History_name():
    History = st.session_state.current_History
    History_name_input = st.session_state[f"History_name_input_{History}"]
    if History_name_input != History:
        index = st.session_state.Historys.index(History)
        st.session_state.Historys[index] = History_name_input
        st.session_state.current_History = History_name_input
        if History in st.session_state.history_files:
            st.session_state.history_files[History_name_input] = st.session_state.history_files.pop(History)
    st.experimental_rerun()

def upload_s3():
    container = st.container()
    col1, col2 = st.columns([4,1])

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


    with container:
        with col1:
            s3 = boto3.client('s3')
            bedrock_agent = boto3.client( 'bedrock-agent' , region_name="us-west-2")
            uploaded_file = st.file_uploader("파일 선택", type=["txt", "md", "html", "doc", "docx", "csv", "xls", "xlsx", "pdf"], label_visibility="visible")
            
        with col2:
            st.write("")
            st.markdown(button_style, unsafe_allow_html=True)
            if st.button("S3 업로드"):
                if uploaded_file:
                    s3_button_click(s3, uploaded_file)
            if st.button("KB 동기화"):
                if uploaded_file:
                    kb_sync_click(bedrock_agent)