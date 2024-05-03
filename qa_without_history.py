import streamlit as st
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import time
import random

import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY']
aws_secret_access_key = os.environ['AWS_SECRET_KEY']
dataSourceId = os.environ['DATASOURCE_ID']
knowledgeBaseId = os.environ['KNOWLEDGEBASE_ID']

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
def run_qa(question, model):
    if model == "Claude 3 Sonnet" : 
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        query_template = """
        You are a solution architect with competent AWS domain knowledge.
        Make sure to answer in Korean after excluding emoticons.
        답변은 인사로 시작합니다, 안녕하세요, 스마일샤크 AI SA입니다.
        단락의 시작 부분에 대한 사용자의 질문에 대한 요약을 풀어서 설명합니다.
        구어를 쓰되 형식적인 표현은 피하세요.
        마지막으로 감사하다는 답변이 불만족스러우시면 스마일샤크 테크 지원센터를 이용해달라고 전해주시기 바랍니다.

        <DOCUMENTS>
        문서 : {context}
        </DOCUMENTS>

        <INSTRUCTIONS>
        질문: {question}
        </INSTRUCTIONS>
        """
        model_kwargs = {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 2048,
        }

    if model == "Claude 3 Opus":
        model_id="anthropic.claude-3-opus-20240229-v1:0"
        query_template = """
        You are a solution architect with competent AWS domain knowledge.
        Make sure to answer in Korean after excluding emoticons.
        답변은 인사로 시작합니다, 안녕하세요, 스마일샤크 AI SA입니다.
        단락의 시작 부분에 대한 사용자의 질문에 대한 요약을 풀어서 설명합니다.
        구어를 쓰되 형식적인 표현은 피하세요.
        마지막으로 감사하다는 답변이 불만족스러우시면 스마일샤크 테크 지원센터를 이용해달라고 전해주시기 바랍니다.

        <DOCUMENTS>
        문서 : {context}
        </DOCUMENTS>

        <INSTRUCTIONS>
        질문: {question}
        </INSTRUCTIONS>
        """
        model_kwargs = {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 2048,
        }

    if model == "Llama 3 70B Instruct" :
        model_id="meta.llama3-70b-instruct-v1:0"
        query_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

        Make sure to answer in Korean after excluding emoticons.
        You are a solution architect with competent AWS domain knowledge.
        대답은 인사로 시작합니다, 안녕하세요, 스마일샤크 AI SA입니다.
        구어를 쓰되 형식적인 표현은 피하세요. 문서 : {context}<|eot_id|><|start_header_id|>user<|end_header_id|>

        질문: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """

        model_kwargs={
        "top_p": 0.9,
        "temperature": 0.1,
        "max_gen_len": 2048,
        }
        
    if model == "Mistral Large" :
        model_id="mistral.mistral-large-2402-v1:0"
        query_template = """
        <s>[INST]
        You are a solution architect with competent AWS domain knowledge.
        Make sure to answer in Korean after excluding emoticons.
        답변은 인사로 시작합니다, 안녕하세요, 스마일샤크 AI SA입니다.
        단락의 시작 부분에 대한 사용자의 질문에 대한 요약을 풀어서 설명합니다.
        구어를 쓰되 형식적인 표현은 피하세요.
        마지막으로 감사하다는 답변이 불만족스러우시면 스마일샤크 테크 지원센터를 이용해달라고 전해주시기 바랍니다.

        문서 : {context}

        질문: {question}
        [/INST]
        </s>
        """

        model_kwargs = {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 2048,
        }

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=knowledgeBaseId,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
        region_name="us-west-2"
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=query_template,
    )

    llm = ChatBedrock(
        model_id=model_id,
        region_name="us-west-2",
        model_kwargs=model_kwargs,
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    res = qa({"query": question})
    print("=====================================================================")
    print(model)
    print("=====================================================================")
    print(res)
    return res['result'] + "\n"