import pandas as pd
import streamlit as st
import mysql.connector as sql
from PIL import Image
from streamlit_option_menu import option_menu
import re
import easyocr
import os
import cv2
import matplotlib.pyplot as plt

#setting page configuration
icon=Image.open(rb'C:\Users\Lenovo\Desktop\Shiva\GUVI\bizcardimage.jpg')
img=Image.open(rb'C:\Users\Lenovo\Desktop\Shiva\GUVI\ocrimage.png')
st.set_page_config(page_title='BizCardX: Extracting Business Card Data with OCR',page_icon=icon)

#setting option_menu
with st.sidebar:
    selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                        icons=["house","cloud-upload","pencil-square"],
                        default_index=0,
                        orientation="vertical",
                        styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                                "icon": {"font-size": "20px"},
                                "container" : {"max-width": "6000px"},
                                "nav-link-selected": {"background-color": "#6495ED"}})

#Initialising the easyocr reader
reader=easyocr.Reader(['en'])

#connection with mysql
mydb=sql.connect(host='localhost', user='root', password='root', db='bizcard')
mycursor = mydb.cursor(buffered=True)

#table creation:
mycursor.execute("""CREATE TABLE IF NOT EXISTS card_data(ID INT AUTO_INCREMENT PRIMARY KEY,
                  COMPANY_NAME VARCHAR(50),
                  CARD_HOLDER VARCHAR(40),
                  DESIGNATION VARCHAR(40),
                  MOBILE_NUMBER LONGTEXT,
                  EMAIL VARCHAR(40),
                  WEBSITE VARCHAR(35),
                  AREA VARCHAR(35),
                  CITY VARCHAR(30),
                  STATE VARCHAR(35),
                  PINCODE VARCHAR(12),
                  IMAGE LONGBLOB)""")
#Home 
if selected == "Home":
    st.header('BizCardX: Extracting Business Card Data with OCR')
    with st.container():
        st.markdown(''':yellow[**Technologies Used :**] :white[Python,easy OCR, Streamlit, SQL, Pandas]''')
        st.markdown(''':yellow[**Overview :**] :white[In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. 
                    You can view, modify or delete the extracted data in this app. 
                    This app would also allow users to save the extracted information into a database along with the uploaded business card image. 
                    The database would be able to store multiple entries, each with its own business card image and extracted information.]''')
    st.image(img)

#upload and extract 
if selected == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards",uploaded_card.name),'wb') as f:
                f.write(uploaded_card.getbuffer())
        save_card(uploaded_card)

        def image_preview(image,res):
            for(bbox,text,prob) in res:
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)

        #displaying the uploaded card:
        col1,col2=st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)
        #displaying the card with highlights
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                #print(res)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image,res))  
        #easy OCR
        saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)
        print(result)

        #converting image to binary:
        def img_to_binary(file):
            with open(file,'rb') as file:
                binaryData=file.read()
            return binaryData
        
        data={'COMPANY_NAME' :[],
              'CARD_HOLDER':[],
              'DESIGNATION':[],
              'MOBILE_NUMBER':[],
              'EMAIL':[],
              'WEBSITE':[],
              'AREA':[],
              'CITY':[],
              'STATE':[],
              'PINCODE':[],
              'IMAGE':img_to_binary(saved_img)}
        
        def get_data(res):
            for ind,i in enumerate(res):

                #to get website url:
                if 'www' in i.lower() or 'www.' in i.lower():
                    data["WEBSITE"].append(i)
                elif 'WWW' in i:
                    data["WEBSITE"]=res[4]+'.'+res[5]

                #to get email id:
                elif '@' in i:
                    data["EMAIL"].append(i)
                
                #to get mobile_number:
                elif '-' in i:
                    data["MOBILE_NUMBER"].append(i)
                    if len(data["MOBILE_NUMBER"])==2:
                        data["MOBILE_NUMBER"]='&'.join(data['MOBILE_NUMBER'])

                #to get comapny_name:
                elif ind == len(res)-1:
                    data["COMPANY_NAME"].append(i)

                #to get a cardholder name:
                elif ind==0:
                    data["CARD_HOLDER"].append(i)

                #to get designatation:
                elif ind==1:
                    data["DESIGNATION"].append(i)

                #to get area:
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["AREA"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["AREA"].append(i)

                #to get city name:
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["CITY"].append(match1[0])
                elif match2:
                    data["CITY"].append(match2[0])
                elif match3:
                    data["CITY"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["STATE"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["STATE"].append(i.split()[-1])
                if len(data["STATE"])== 2:
                    data["STATE"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["PINCODE"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["PINCODE"].append(i[10:])
        get_data(result)

        #function to create dataframe:
        def create_df(data):
            df=pd.DataFrame(data)
            return df
        df=create_df(data)
        st.success("Data extracted!")
        st.write(df)

        if st.button("Upload to database"):
            for i,row in df.iterrows():
                #here %S means string values
                sql = """INSERT INTO card_data(COMPANY_NAME, CARD_HOLDER, DESIGNATION, MOBILE_NUMBER, EMAIL, WEBSITE, AREA, CITY, STATE, PINCODE, IMAGE)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
            st.success("#### Uploaded to database successfully!")
#Modify menu:
if selected=="Modify":
    col1,col2,col3=st.columns([3,3,2])
    col2.markdown("Alter or Delete the dataframe")
    column1,column2=st.columns(2,gap="large")

    with column1:
        mycursor.execute("SELECT CARD_HOLDER FROM card_data")
        result = mycursor.fetchall()
        business_cards={}
        for row in result:
            business_cards[row[0]]=row[0]
        selected_card=st.selectbox("Select a card holder name to update",list(business_cards.keys()))
        st.markdown("Update or modify any data below")
        mycursor.execute('SELECT COMPANY_NAME, CARD_HOLDER, DESIGNATION, MOBILE_NUMBER, EMAIL, WEBSITE, AREA, CITY, STATE, PINCODE FROM card_data where CARD_HOLDER=%s',(selected_card,))
        result=mycursor.fetchone()

        #displaying all the informations
        COMPANY_NAME=st.text_input("COMPANY_NAME",result[0])
        CARD_HOLDER=st.text_input("CARD_HOLDER",result[1])
        DESIGNATION=st.text_input("DESIGNATION",result[2])
        MOBILE_NUMBER=st.text_input("MOBILE_NUMBER",result[3])
        EMAIL=st.text_input('EMAIL',result[4])
        WEBSITE=st.text_input("WEBSITE",result[5])
        AREA=st.text_input("AREA",result[6])
        CITY=st.text_input('CITY',result[7])
        STATE=st.text_input('STATE',result[8])
        PINCODE=st.text_input("PINCODE",result[9])

        if st.button ("commit changes in Database"):
            # Update the information for the selected business card in the database
            mycursor.execute("""UPDATE card_data SET COMPANY_NAME=%s, CARD_HOLDER=%s, DESIGNATION=%s, MOBILE_NUMBER=%s, EMAIL=%s, WEBSITE=%s, AREA=%s, CITY=%s, STATE=%s, PINCODE=%s WHERE CARD_HOLDER=%s""",
                (COMPANY_NAME, CARD_HOLDER, DESIGNATION, MOBILE_NUMBER, EMAIL, WEBSITE, AREA, CITY, STATE, PINCODE, selected_card,))
            mydb.commit()
            st.success("Information updated in data successfully")

    with column2:
        mycursor.execute("SELECT CARD_HOLDER FROM card_data")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
        st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
        st.write("#### Proceed to delete this card?")

        if st.button("Yes Delete Business Card"):
            mycursor.execute(f"DELETE FROM card_data WHERE CARD_HOLDER='{selected_card}'")
            mydb.commit()
            st.success("Business card information deleted from database.")


if st.button("View updated data"):
    mycursor.execute("SELECT COMPANY_NAME, CARD_HOLDER, DESIGNATION, MOBILE_NUMBER, EMAIL, WEBSITE, AREA, CITY, STATE, PINCODE FROM card_data")
    updated_df=pd.DataFrame(mycursor.fetchall(),columns=["COMPANY_NAME","CARD_HOLDER","DESIGNATION","MOBILE_NUMBER","EMAIL","WEBSITE","AREA","CITY","STATE","PINCODE"])
    st.write(updated_df)