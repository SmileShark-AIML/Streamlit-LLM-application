import streamlit as st
import os
from qa_without_history import run_qa
from concurrent.futures import ThreadPoolExecutor

aws_access_key_id = os.environ['AWS_ACCESS_KEY']
aws_secret_access_key = os.environ['AWS_SECRET_KEY']
dataSourceId = os.environ['DATASOURCE_ID']
knowledgeBaseId = os.environ['KNOWLEDGEBASE_ID']

def comparison_UI():
    st.write("### LLM 답변비교")

    if "comparison_msg" not in st.session_state:
        st.session_state.comparison_msg = []

    if prompt := st.chat_input("메시지를 입력하세요."):
        # Clear previous chat history
        st.session_state.comparison_msg = []
        
        # Display user message
        st.write(f"**질문**: {prompt}")
        
        # Add user message to chat history
        st.session_state.comparison_msg.append({"role": "user", "content": prompt})

        with st.spinner("답변 생성 중..."):
            models = ["Claude 3 Sonnet", "Claude 3 Opus", "Llama 3 70B Instruct", "Mistral Large"]
            with ThreadPoolExecutor() as executor:
                answers = list(executor.map(run_qa, [prompt] * len(models), models))

            # 각 답변을 별도의 변수에 할당
            answer1, answer2, answer3, answer4 = answers

            # Display the table with HTML formatting and no borders
            table_html = """
            <table style="border-collapse: collapse; width: 100%;">
            <tr>
            <td style="background-color: #f0f0f0; padding: 10px; font-weight: bold; text-align: center; border: none; width: 50%;">{}</td>
            <td style="background-color: #f0f0f0; padding: 10px; font-weight: bold; text-align: center; border: none; width: 50%;">{}</td>
            </tr>
            <tr>
            <td style="vertical-align: top; padding: 10px; border: none; white-space: pre-wrap; width: 50%;">{}</td>
            <td style="vertical-align: top; padding: 10px; border: none; white-space: pre-wrap; width: 50%;">{}</td>
            </tr>
            <tr>
            <td style="background-color: #f0f0f0; padding: 10px; font-weight: bold; text-align: center; border: none; width: 50%;">{}</td>
            <td style="background-color: #f0f0f0; padding: 10px; font-weight: bold; text-align: center; border: none; width: 50%;">{}</td>
            </tr>
            <tr>
            <td style="vertical-align: top; padding: 10px; border: none; white-space: pre-wrap; width: 50%;">{}</td>
            <td style="vertical-align: top; padding: 10px; border: none; white-space: pre-wrap; width: 50%;">{}</td>
            </tr>
            </table>
            """.format(models[0], models[1], answer1, answer2, models[2], models[3], answer3, answer4)

            st.markdown(table_html, unsafe_allow_html=True)

            # Add assistant responses to chat history
            for i, answer in enumerate(answers):
                st.session_state.comparison_msg.append({"role": f"assistant_{models[i]}", "content": answer})

        print(st.session_state.comparison_msg)