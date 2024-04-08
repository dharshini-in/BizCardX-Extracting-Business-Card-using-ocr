
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_to_text(path):

  input_img= Image.open(path)

  #convert img to arr format:
  image_arr=np.array(input_img)

  reader=easyocr.Reader(['en'])
  text=reader.readtext(image_arr, detail= 0)

  return text, input_img

from typing import Concatenate
def extracted_text(texts):

  extrd_dict={"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[],"EMAIL":[],
              "WEBSITE":[],"ADDRESS":[],"PINCODE":[]}

  extrd_dict["NAME"].append(texts[0])
  extrd_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):
    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extrd_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extrd_dict["EMAIL"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small=texts[i].lower()
      extrd_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extrd_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]',texts[i]):
      extrd_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,:]','',texts[i])
      extrd_dict["ADDRESS"].append(remove_colon)

  for key,value in extrd_dict.items():
    if len(value)>0:
      concadenate= " ".join(value)
      extrd_dict[key]= [concadenate]

    else:
      value="NA"
      extrd_dict[key]=[value]

  return extrd_dict



#streamlit part

st.set_page_config(layout="wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH OCR")

with st.sidebar:
  select=option_menu("main menu",["HOME","UPLOAD & MODIFY","DROP"])

if select =="HOME":
 # Introduction
  st.title("Business Card Information Extraction App")
  st.write("Welcome to our Streamlit application development project! This app allows you to upload a business card image and extract relevant information from it.")

  # Problem Statement
  st.header("Problem Statement")
  st.write("You have been tasked with developing a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR. The extracted information should include the company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pin code. The extracted information should then be displayed in the application's graphical user interface (GUI). In addition, the application should allow users to save the extracted information into a database along with the uploaded business card image.")

  # Approach
  st.header("Approach")
  st.write("To achieve this, we will use Python, Streamlit, easyOCR, and SQLite for database management. The application will have a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information. The extracted information will be displayed in a clean and organized manner, and users will be able to easily add it to the database with the click of a button. Additionally, users will have the ability to read, update, and delete data through the Streamlit UI.")

elif select== "UPLOAD & MODIFY":
  img=st.file_uploader("upload the image",type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img,width=300)

    text_image, input_img = image_to_text(img)

    text_dict= extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    df=pd.DataFrame(text_dict)

    #convert img to bytes
    Image_bytes= io.BytesIO()
    input_img.save(Image_bytes, format="PNG")

    image_data= Image_bytes.getvalue()

    #create dict:
    data={"IMAGE": [image_data]}

    df_1= pd.DataFrame(data)

    concat_df=pd.concat([df,df_1],axis=1)

    st.dataframe(concat_df)

    button_1= st.button("save",use_container_width=True)

    if button_1:

        mydb = sqlite3.connect("bizcard.db")
        cursor= mydb.cursor()

        #table
        create_table_query= '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                          designation varchar(225),
                                                                          company_name varchar(225),
                                                                          contact varchar(225),
                                                                          email varchar(225),
                                                                          website text,
                                                                          address text,
                                                                          pincode varchar(225),
                                                                          image text)'''

        cursor.execute(create_table_query)
        mydb.commit()

        #insert query

        insert_query = '''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                        values(?,?,?,?,?,?,?,?,?)'''

        datas= concat_df.values.tolist()[0]
        cursor.execute(insert_query,datas)
        mydb.commit()

        st.success("saved successfully")

  method= st.radio("select the method",["None","Preview","Modify"])

  if method== "None":
    st.write("")

  if method == "Preview":

    mydb = sqlite3.connect("bizcard.db")
    cursor= mydb.cursor()
    #select query
    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()
    table_df= pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                            "WEBSITE","ADDRESS","PINCODE","IMAGE"))
    st.dataframe(table_df)

  elif method == "Modify":
    mydb = sqlite3.connect("bizcard.db")
    cursor= mydb.cursor()
    #select query
    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()
    table_df= pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                            "WEBSITE","ADDRESS","PINCODE","IMAGE"))
    col1,col2 = st.columns(2)
    with col1:
      selected_name = st.selectbox("select the name",table_df["NAME"])

    df_3= table_df[table_df["NAME"]== selected_name]

    df_4 = df_3.copy()

    col1,col2 = st.columns(2)
    with col1:
      mod_name = st.text_input("Name",df_3["NAME"].unique()[0])
      mod_desi = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
      mod_com_name = st.text_input("company_name",df_3["COMPANY_NAME"].unique()[0])
      mod_contact = st.text_input("contact",df_3["CONTACT"].unique()[0])
      mod_email = st.text_input("email",df_3["EMAIL"].unique()[0])

      df_4["NAME"]= mod_name
      df_4["DESIGNATION"] = mod_desi
      df_4["COMPANY_NAME"]= mod_com_name
      df_4["CONTACT"]= mod_contact
      df_4["EMAIL"] = mod_email

    with col2:
      mod_website = st.text_input("website",df_3["WEBSITE"].unique()[0])
      mod_address = st.text_input("address",df_3["ADDRESS"].unique()[0])
      mod_pincode = st.text_input("pincode",df_3["PINCODE"].unique()[0])
      mod_image = st.text_input("image",df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"]= mod_website
      df_4["ADDRESS"] = mod_address
      df_4["PINCODE"]= mod_pincode
      df_4["IMAGE"]= mod_image

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:
      button_3 = st.button("Modify", use_container_width=True)
    if button_3:
        mydb = sqlite3.connect("bizcard.db")
        cursor= mydb.cursor()

        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
        mydb.commit()

        #insert query

        insert_query = '''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                          values(?,?,?,?,?,?,?,?,?)'''

        datas= df_4.values.tolist()[0]
        cursor.execute(insert_query,datas)
        mydb.commit()

        st.success("modified successfully")


elif select=="DROP":
  mydb = sqlite3.connect("bizcard.db")
  cursor= mydb.cursor()
  col1,col2 = st.columns(2)
  with col1:
    #select query
    select_query = "SELECT NAME FROM bizcard_details"

    cursor.execute(select_query)
    table1= cursor.fetchall()
    mydb.commit()
    names=[]
    for i in table1:
      names.append(i[0])

    name_select = st.selectbox("select the name",names)

  with col2:
    #select query
    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"

    cursor.execute(select_query)
    table2 = cursor.fetchall()
    mydb.commit()
    designations=[]
    for j in table2:
      designations.append(j[0])

    designation_select = st.selectbox("select the designation",designations)

  if name_select and designation_select:
    col1,col2,col3 = st.columns(3)

    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Selected Designations: {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("DROP",use_container_width=True)

      if remove:

        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{name_select}' AND DESIGNATION='{designation_select}'")
        mydb.commit()
        st.warning("DELETED")













