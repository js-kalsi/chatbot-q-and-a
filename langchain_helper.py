from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from const import (
    LLM_MODEL_NAME,
    LLM_MODEL_TEMP,
    LLM_BASE_URL,
    EMBEDDING_MODEL_NAME,
    VECTOR_DB_FILE_PATH,
    VECTOR_RETRIVAL_TEMP,
    DB_PATH,
)


llm = ChatOllama(
    model=LLM_MODEL_NAME, temperature=LLM_MODEL_TEMP, base_url=LLM_BASE_URL
)

instructor_embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def create_vector_db():
    """
    Creates a vector database from the JSON data and saves it locally.

    Parameters:
        file_path (str): The file path of the JSON data.
        embedding (dict): A dictionary containing the embeddings for the questions.

    Returns:
        None

    Raises:
        ValueError: If the JSON data could not be loaded or the file path was invalid.
    """
    loader = JSONLoader(
        file_path=DB_PATH,
        jq_schema=".questions[]",
        text_content=False,
    )
    data = loader.load()
    vectordb = FAISS.from_documents(documents=data, embedding=instructor_embeddings)
    vectordb.save_local(VECTOR_DB_FILE_PATH)


def get_qa_chain():
    """
    Creates a QA chain that retrieves answers from a vector database based on user input.

    Parameters:
        None

    Returns:
        A QA chain object.

    Raises:
        ValueError: If the JSON data could not be loaded or the file path was invalid.
    """
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(
        VECTOR_DB_FILE_PATH, instructor_embeddings, allow_dangerous_deserialization=True
    )

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=VECTOR_RETRIVAL_TEMP)

    prompt_template = """Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "response" section in the source document context 
    without making much changes. If the answer is not found in the context, kindly state "I don't know." 
    Don't try to make up an answer.

    CONTEXT: {context}

    QUESTION: {question}"""

    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        input_key="query",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return chain
