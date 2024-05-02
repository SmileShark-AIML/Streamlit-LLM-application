import streamlit as st
import boto3
from datetime import datetime
from pytz import timezone

import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY']
aws_secret_access_key = os.environ['AWS_SECRET_KEY']

def get_s3_list():
    s3_client = boto3.client('s3',
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,)
    bucket_name = 'sharkpt-kb-s3'
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if response['KeyCount'] != 0:
        contents = response['Contents']
        selected_columns = {'Key': '파일명', 'LastModified': '수정시간', 'Size': '파일크기(MB)', 'StorageClass': '저장소유형'}

        # 선택한 열과 새로운 열 이름으로 새로운 데이터 생성
        table_data = []
        for item in contents:
            row = {}
            for old_col, new_col in selected_columns.items():
                if old_col == 'LastModified':
                    # UTC 시간을 한국 시간으로 변환
                    utc_time = datetime.strptime(str(item[old_col]), '%Y-%m-%d %H:%M:%S+00:00')
                    kst_time = utc_time.replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Seoul'))
                    row[new_col] = kst_time.strftime('%Y년 %m월 %d일 %H:%M:%S')
                elif old_col == 'Size':
                    # 바이트를 MB로 변환
                    size_mb = item[old_col] / (1024 * 1024)
                    row[new_col] = f'{size_mb:.2f} MB'
                else:
                    row[new_col] = item[old_col]
            table_data.append(row)
        st.session_state.s3_table = table_data