import streamlit as st
import boto3
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import calendar
import altair as alt
from itertools import cycle

CLOUDWATCH_NAMESPACE = 'AWS/Bedrock'
CLOUDWATCH_METRIC_NAMES = ['Invocations', 'InvocationLatency', 'OutputTokenCount', 'InputTokenCount']
CLOUDWATCH_PERIOD = 60
CLOUDWATCH_LATENCY_STAT = 'Average'
CLOUDWATCH_OTHER_STAT = 'Sum'
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY']
aws_secret_access_key = os.environ['AWS_SECRET_KEY']

def dashboard_UI():
    KST = timezone('Asia/Seoul')
    cloudwatch = boto3.client('cloudwatch',
                              region_name="us-west-2",
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,)
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    months = [datetime(current_year, m, 1).strftime('%Y-%m') for m in range(1, 13)]
    
    st.write("##### (예상) 비용확인")
    selected_month = st.selectbox('해당월 비용 확인', months, index=current_month - 1, label_visibility="collapsed")  # 현재 월을 디폴트로 선택
    
    if selected_month:
        # 선택한 월의 시작일과 종료일 계산
        year, month = map(int, selected_month.split('-'))
        start_time = datetime(year, month, 1, tzinfo=timezone('UTC'))
        end_time = start_time + timedelta(days=calendar.monthrange(year, month)[1])


        # CloudWatch 데이터 가져오기
        metric_data_queries = [
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Bedrock',
                        'MetricName': 'InputTokenCount',
                        'Dimensions': [
                            {
                                "Name": "ModelId",
                                "Value": MODEL_ID
                            }
                        ]
                    },
                    'Period': 3600,  # 1시간 단위로 집계
                    'Stat': 'Sum',
                },
                'ReturnData': True
            },
            {
                'Id': 'm2',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Bedrock',
                        'MetricName': 'OutputTokenCount',
                        'Dimensions': [
                            {
                                "Name": "ModelId",
                                "Value": MODEL_ID
                            }
                        ]
                    },
                    'Period': 3600,  # 1시간 단위로 집계
                    'Stat': 'Sum',
                },
                'ReturnData': True
            }
        ]

        response = cloudwatch.get_metric_data(
            MetricDataQueries=metric_data_queries,
            StartTime=start_time,
            EndTime=end_time
        )

        # 예상 비용 계산
        input_tokens = sum(response['MetricDataResults'][0]['Values'])
        output_tokens = sum(response['MetricDataResults'][1]['Values'])
        # total_tokens = input_tokens + output_tokens
        input_token_price = 0.003  # 예시로 토큰당 가격을 0.0001로 설정 (실제 가격은 다를 수 있음)
        output_token_price = 0.015  # 예시로 토큰당 가격을 0.0001로 설정 (실제 가격은 다를 수 있음)

        estimated_cost = (input_tokens / 1000 * input_token_price) + (output_tokens / 1000 * output_token_price)

        st.write("계산공식 : (Input Tokens / 1000 × Input Token Price ) + (Input Tokens / 1000 × Input Token Price )")
        st.write(f"사용된 총 Input Tokens : {input_tokens:,.0f}")
        st.write(f"사용된 총 Output Tokens : {output_tokens:,.0f}")
        st.write(f"계산: (${input_tokens:,.0f} / 1000 × ${input_token_price:,.4f}) + (${output_tokens:,.0f} / 1000 × ${output_token_price:,.4f}) = ${estimated_cost:,.4f}")
        st.write(f"예상 총 비용 : ${estimated_cost:,.3f}")

        now = datetime.now(KST)
        start_time = now - timedelta(hours=24)
        end_time = now.astimezone(timezone('UTC'))
        start_time = start_time.astimezone(timezone('UTC'))

        metric_names = ['Invocations', 'InvocationLatency', 'OutputTokenCount', 'InputTokenCount']
        metric_data_queries = []

        for i, metric_name in enumerate(CLOUDWATCH_METRIC_NAMES, 1):
            stat = CLOUDWATCH_OTHER_STAT
            if metric_name == 'InvocationLatency':
                stat = CLOUDWATCH_LATENCY_STAT

            metric_data_queries.append({
                'Id': f'm{i}',
                'MetricStat': {
                    'Metric': {
                        'Namespace': CLOUDWATCH_NAMESPACE,
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                "Name": "ModelId",
                                "Value": MODEL_ID
                            }
                        ]
                    },
                    'Period': CLOUDWATCH_PERIOD,
                    'Stat': stat,
                },
                'ReturnData': True
            })

        response = cloudwatch.get_metric_data(
            MetricDataQueries=metric_data_queries,
            StartTime=start_time,
            EndTime=end_time
        )

        # 2x2 그리드를 위한 열 생성
        col1, col2 = st.columns(2)
        columns = cycle([col1, col2])

        for dat in response['MetricDataResults']:
            timestamps = dat['Timestamps']
            values = dat['Values']
            chart_data = pd.DataFrame({'Timestamp': timestamps, 'Value': values})
            chart_data = chart_data.set_index('Timestamp')
            
            # 연속된 분과 불연속적인 분 구분
            chart_data['minute'] = chart_data.index.minute
            chart_data['diff'] = chart_data['minute'].diff().fillna(0)
            chart_data['is_continuous'] = (chart_data['diff'] == 1) | (chart_data['diff'] == -59)
            
            # 메트릭 이름 가져오기
            metric_name = dat['Label']
            
            # Altair 차트 생성
            chart = alt.Chart(chart_data.reset_index()).mark_line(
                point=alt.OverlayMarkDef(filled=False, fill='white')
            ).encode(
                x=alt.X('Timestamp:T', axis=alt.Axis(format='%H:%M')),  # 시간 형식 변경
                y='Value:Q',
                strokeDash=alt.condition(
                    alt.datum.is_continuous,
                    alt.value([0]),  # 연속된 분은 실선
                    alt.value([5, 5])  # 불연속적인 분은 점선
                )
            ).properties(
                # title=metric_name,  # 차트 제목 설정
                height=200  # 차트 높이 설정
            )
            
            # 차트를 expander로 감싸기
            with next(columns).expander(metric_name, expanded=True):
                st.altair_chart(chart, use_container_width=True)