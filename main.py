import streamlit as st
from langchain_helper import get_qa_chain, create_vector_db

st.title("Ecommerce FAQ Chatbot Q&A 🌱")
btn = st.button("Create Knowledgebase")
if btn:
    create_vector_db()
    pass

question = st.text_input("Question: ")

if question:
    chain = get_qa_chain()
    response = chain(question)
    st.header("Answer")
    st.write(response["result"])
