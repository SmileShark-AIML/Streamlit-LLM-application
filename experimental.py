import streamlit as st
import boto3

def experimental_UI():
    st.write("Experimental Function")

    bedrock_client = boto3.client(service_name="bedrock", region_name="us-west-2")
    fm_list = bedrock_client.list_foundation_models()
    fm_list = fm_list['modelSummaries']
    st.write(fm_list)