import streamlit as st
from utils import clear_messages

def sidebar_UI(selected):
    if selected == "채팅":

        st.write("Histories")
        History_indices_to_remove = []
        for i, History in enumerate(st.session_state.Historys):
            cols = st.columns([5, 1])
            with cols[0]:
                if st.button(History, key=f"History_button_{i}"):
                    st.session_state.current_History = History
            with cols[1]:
                if st.button("x", key=f"delete_History_{i}"):
                    clear_messages(History)  # 대화 삭제 함수 호출
                    if st.session_state.current_History == History:
                        st.session_state.current_History = ""

        st.write("도큐먼트 업로더")
        if st.session_state.current_History not in st.session_state.history_files:
            st.session_state.history_files[st.session_state.current_History] = []

        history_files = st.file_uploader("Choose a file", label_visibility="collapsed", accept_multiple_files=True, key=f"history_files_{st.session_state.current_History}")

        if history_files:
            st.session_state.history_files[st.session_state.current_History] = history_files
            dat = [f.name for f in st.session_state.history_files[st.session_state.current_History]]
            st.session_state.messages[st.session_state.current_History].append({"role": "assistant", "content": "참고문서에 변동이 있습니다.\n\n"+str(dat)})

        if st.session_state.history_files[st.session_state.current_History]:
            st.write("도큐먼트")
            for i, file in enumerate(st.session_state.history_files[st.session_state.current_History]):
                cols = st.columns([3,1])
                cols[0].write(file.name)
                if cols[1].button("삭제", key=f"delete_file_{i}_{st.session_state.current_History}"):
                    del st.session_state.history_files[st.session_state.current_History][i]
                    dat = [f.name for f in st.session_state.history_files[st.session_state.current_History]]
                    st.session_state.messages[st.session_state.current_History].append({"role": "assistant", "content": "참고문서에 변동이 있습니다.\n\n"+str(dat)})
                    st.experimental_rerun()