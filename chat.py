import streamlit as st

st.set_page_config(page_title="소득세 챗봇", page_icon=":shark:")

st.title("소득세 챗봇")
st.caption("소득세 관련 질문에 답해드립니다.")

def get_ai_message(user_message):
    

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_question := st.chat_input("질문을 입력하세요"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.chat_message("ai"):
        st.write('ai message here')
    st.session_state.message_list.append({"role": "ai", "content": 'ai message here'})
