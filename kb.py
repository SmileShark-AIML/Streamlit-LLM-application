import streamlit as st
from pytz import timezone
from datetime import datetime
import boto3
from utils import upload_s3
import pandas as pd
from utils import utc_to_kst
from dotenv import load_dotenv
import os

load_dotenv()

dataSourceId = os.getenv('DATASOURCE_ID')
knowledgeBaseId = os.getenv('KNOWLEDGEBASE_ID')

def kb_UI():
    st.markdown("### KB데이터 관리")
    s3_table_data = st.session_state.s3_table
    if s3_table_data :
        st.write("데이터 리스트")
        df = pd.DataFrame(s3_table_data)
        df.index += 1
        st.table(df)
        
    st.write("###### KB에 추가하고싶은 파일을 업로드하세요")
    upload_s3()


    st.write("###### KB동기화 이력")
    bedrock_agent = boto3.client( 'bedrock-agent' , region_name="us-west-2")
    response = bedrock_agent.list_ingestion_jobs(
        dataSourceId=dataSourceId,
        knowledgeBaseId=knowledgeBaseId,
        maxResults=5,
        sortBy={
            'attribute': 'STATUS',
            'order': 'DESCENDING'
        }
    )
    jobs = response["ingestionJobSummaries"]
    selected_columns = {'knowledgeBaseId': 'KB아이디', 'startedAt': '시작시간', 'updatedAt': '업데이트시간', 'status': '상태'}

    # 선택한 열과 새로운 열 이름으로 새로운 데이터 생성
    table_data = []
    for item in jobs:
        row = {}
        for old_col, new_col in selected_columns.items():
            if old_col in ['startedAt', 'updatedAt']:
                row[new_col] = utc_to_kst(item[old_col])  # 시간 변환 함수 사용
            else:
                row[new_col] = str(item[old_col])
        table_data.append(row)

    st.table(table_data)