import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenrator.utils import read_file,get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenrator.MCQGenrator import generate_evaluate_chain
from src.mcqgenrator.logger import logging


st.set_page_config(page_title='Agkiya- MC Quiz Genrator', layout = 'wide', page_icon = 'AgkiyaLogo.png', initial_sidebar_state = 'auto')
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

rfPath = os.getcwd() + "/Response.json"
with open(rfPath,'r') as file:
    RESPONSE_JSON = json.load(file)

# creating the title for the app
    st.header('Your custom quiz genrator :sunglasses:', divider='rainbow')


# create a form using st.form
    with st.form("user_inputs"):
        st.info('You can upload a .pdf or .txt file and we generate a quiz based on your uploaded file. You can specify that how many questions you want in your quiz and what could be the difficulty level of your quiz. We did not store any information in our system', icon="ℹ️")

        #File Upload
        uploaded_file=st.file_uploader("Upload a PDF or txt file to genrate your custom test.", type=['pdf', 'txt'], accept_multiple_files=False)
        
        
        #Input Fields
        mcq_count=st.number_input("No. of Questions in Quiz", min_value=1, max_value=50)

        #Subject
        subject=st.text_input("Quiz Topic", max_chars=60)

         #Quiz Tone
        tone =  st.selectbox('Complexity Level of Questions',
                            ('Easy', 'Medium', 'Hard'))

        #Add Button
        button=st.form_submit_button("Genrate Quiz")


        #Check if button is clicked and fileds have input
        if button and uploaded_file is not None and mcq_count and subject and tone:
            with st.spinner("loading...."): 
                try:
                    text=read_file(uploaded_file)
                    
                    #count token and cost of api call
                    with get_openai_callback() as cb:
                        response=generate_evaluate_chain(
                            {
                                "text": text,
                                "number": mcq_count,
                                "subject":subject,
                                "tone": tone,
                                "response_json": json.dumps(RESPONSE_JSON)
                            }      
                        )

                except Exception as e:
                    traceback.print_exception(type(e),e,e.__traceback__)
                    st.error("Error")

                else:
                    print(f"Total Token:{cb.total_tokens}")
                    print(f"Prompt Token:{cb.prompt_tokens}")
                    print(f"Copletion Token:{cb.completion_tokens}")
                    print(f"Total Cost:{cb.total_cost}")
                    if isinstance(response, dict):
                        #Extract the quiz data from the response
                        quiz=response.get("quiz", None)
                        if quiz is not None:
                            st.subheader('Here is quiz genrated based on your data.', divider='rainbow')
                            table_data=get_table_data(quiz)
                            if table_data is not None:
                                df=pd.DataFrame(table_data)
                                
                                df.index=df.index+1
                                st.table(df)

                                #Display the review in a textbox as well
                                st.text_area(label="Review of " + subject + " Quiz ", value=response["review"])
                            else:
                                st.error("Error in table data")
                        else:
                            st.write(response)




