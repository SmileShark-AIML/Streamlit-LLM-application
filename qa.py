import streamlit as st
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import time
import random

from dotenv import load_dotenv
import os

load_dotenv()

dataSourceId = os.getenv('DATASOURCE_ID')
knowledgeBaseId = os.getenv('KNOWLEDGEBASE_ID')

def retry_with_exponential_backoff_and_jitter(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    max_retries: int = 10,
    max_delay: float = 60,
    jitter_factor: float = 0.1,
):
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "ThrottlingException" not in str(e):
                    raise e
                num_retries += 1
                if num_retries > max_retries:
                    raise e
                delay = min(delay * exponential_base, max_delay)
                jitter = random.uniform(1 - jitter_factor, 1 + jitter_factor)
                delay *= jitter
                print(f"Retry {num_retries}/{max_retries} after {delay:.2f} seconds...")
                time.sleep(delay)

    return wrapper

def retry_with_fixed_delay(
    func,
    delay: float = 3,
    max_retries: int = 10,
):
    def wrapper(*args, **kwargs):
        num_retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "ThrottlingException" not in str(e):
                    raise e
                num_retries += 1
                if num_retries > max_retries:
                    raise e
                print(f"Retry {num_retries}/{max_retries} after {delay:.2f} seconds...")
                time.sleep(delay)

    return wrapper

@retry_with_fixed_delay
def run_qa(question):
    history = st.session_state.messages[st.session_state.current_History]
    string_history = '\n'.join([f"{item['role']}: {item['content']}" for item in history])

### 라마3 템플릿
#     query_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    
# Make sure to answer in Korean after excluding emoticons.
# You are a solution architect with competent AWS domain knowledge.
# Make sure to answer in Korean after excluding emoticons.
# Answer in the form of a category or a list of numbers.
# The answer begins with a greeting, Hello, I'am SmileShark AI SA.
# Provide a summary of the user's questions for the beginning of the paragraph.
# If you have had a previous conversation with the user, please refer to the conversation and answer.
# Use colloquial language, but avoid formal expressions.
# Finally, if you are dissatisfied with the answer with thank you, please tell them to use the SmileShark Tech Support Center. 유저와의 이전대화 : """ + string_history + """,문서 : {context}<|eot_id|><|start_header_id|>user<|end_header_id|>

# 질문: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
# """
    query_template = """
Make sure to answer in Korean after excluding emoticons.
You are a solution architect with competent AWS domain knowledge.
Make sure to answer in Korean after excluding emoticons.
Answer in the form of a category or a list of numbers.
The answer begins with a greeting, Hello, I'am 스마일샤크 AI SA.
Provide a summary of the user's questions for the beginning of the paragraph.
If you have had a previous conversation with the user, please refer to the conversation and answer.
Use colloquial language, but avoid formal expressions.
Finally, if you are dissatisfied with the answer with thank you, please tell them to use the 스마일샤크 Tech Support Center.

<CONVERSATION_HISTORY>
유저와의 이전대화 : """ + string_history + """
</CONVERSATION_HISTORY>

<DOCUMENTS>
문서 : {context}
</DOCUMENTS>

<INSTRUCTIONS>
질문: {question}
</INSTRUCTIONS>
"""

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=knowledgeBaseId,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
        region_name="us-west-2"
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=query_template,
    )
    
    model_kwargs={
        "top_p": 0.9,
        "temperature": 0.1,
        "max_gen_len": 2048,
        }
    
    llm = ChatBedrock(
        # model_id="meta.llama3-70b-instruct-v1:0",
        # model_id="anthropic.claude-3-opus-20240229-v1:0",
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        # model_kwargs=model_kwargs,
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    res = qa({"query": question})
    print(res['result'])
    return res['result']