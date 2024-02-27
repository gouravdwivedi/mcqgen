import os
import json
import traceback
import PyPDF2

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
        
        except Exception as e:
            raise Exception("Error while reading the pdf file.")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception("Unsupported file format, onle pdf and text file are supported.")
    
def get_table_data(quiz_str):
    try:

        # data cleaning for pdf
        quiz_str = remove_text_before_first_occurrence(quiz_str, "{")

        # convert the quiz from a str to dict
        quiz_dict=json.loads(quiz_str)
        quiz_table_data=[]

        #iterate over the quiz dictionary and extact the required information
        for key,value in quiz_dict.items():
            mcq=value["mcq"]
            options=" || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                ]
            )

            correct=value["correct"]
            quiz_table_data.append({"Question" : mcq,"Choices": options, "Correct Response": correct})

        return quiz_table_data


    except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        return False
    
def remove_text_before_first_occurrence(text, delimiter):
    index = text.find(delimiter)
    if index != -1:
        return text[index:]
    else:
        return text
    
# Function to insert new line after '|'
def insert_newline(text):
    return text.replace('||', '<br>')


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')