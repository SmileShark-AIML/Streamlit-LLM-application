import streamlit as st
from utils import clear_messages
from qa import run_qa


def chat_UI():
    History = st.session_state.current_History
    st.write("### Chat")
    c1, c2 = st.columns([5, 1])
    if History:
        with c1.form(key=f"History_form_{History}"):
            col1, col2 = st.columns([5, 1])
            History_name_input = col1.text_input("Modify History", value=History, key=f"History_name_input_{History}", label_visibility="collapsed")
            submit_button = col2.form_submit_button(label="Update")
            if submit_button:
                if History_name_input != History:
                    index = st.session_state.Historys.index(History)
                    if History_name_input == "":
                        History_name_input = "None"
                    st.session_state.Historys[index] = History_name_input
                    st.session_state.current_History = History_name_input
                    if History in st.session_state.messages:
                        st.session_state.messages[History_name_input] = st.session_state.messages.pop(History)
                    st.experimental_rerun()
        if History_name_input != History:
            st.session_state.Historys = [History_name_input if r == History else r for r in st.session_state.Historys]
            st.session_state.current_History = History_name_input
            if History in st.session_state.messages:
                st.session_state.messages[History_name_input] = st.session_state.messages.pop(History)
        c2.write("")
        # 삭제 버튼 추가
        if c2.button("초기화", key=f"clear_messages_{History}"):
            clear_messages(History)
                
    else:
        st.write("채팅방을 선택해주세요.")

    if st.session_state.current_History not in st.session_state.messages:
        st.session_state.messages[st.session_state.current_History] = []

    for message in st.session_state.messages[st.session_state.current_History]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메시지를 입력하세요."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages[st.session_state.current_History].append({"role": "user", "content": prompt})

        with st.spinner("답변 생성 중..."):
            answer = "echo"
            answer = run_qa(prompt)

        response = answer

        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages[st.session_state.current_History].append({"role": "assistant", "content": response})

        print(st.session_state.messages[st.session_state.current_History])
