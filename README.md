# BizCardX-Extracting-Business-Card-Data-with-OCR

BizCardReader BizCardX: Extracting Business Card Data with OCR using easyOCR,streamlit GUI, SQL,Data Extraction

Objective BizCardX - A Streamlit Application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.

The extracted information can be edited for its correctness and saved to MySQL Databases. 
All the Business card details with a preview of the uploaded card is available for the user to View and Delete it as required.


Prerequisties MySQL DB. 
Install the below python packages 
mysql.connector  streamlit  easyOcr Image Setup  
Pull the Home.py, pages,data folder 
Create the MySQL DB and 1 table bizcard_data. 
change the mysql root username and password in the python scripts. 
Run the Application Go to Command Prompt Change the working directory to the Directory where the code is pulled to Start the mySQL DB Run the command. 
The Bizcard application will open up with 3 menus in the sidebar to navigate to different python script in the pages folder. 
streamlit run app.py
