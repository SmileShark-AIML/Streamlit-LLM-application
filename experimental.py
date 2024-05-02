import streamlit as st
import boto3

import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY']
aws_secret_access_key = os.environ['AWS_SECRET_KEY']

def experimental_UI():
    st.write("Experimental Function")

    bedrock_client = boto3.client(service_name="bedrock", 
                                  region_name="us-west-2", 
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,)
    fm_list = bedrock_client.list_foundation_models()
    fm_list = fm_list['modelSummaries']
    st.write(fm_list)