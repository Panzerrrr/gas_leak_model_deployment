import streamlit as st
import pandas as pd
import numpy as np
import os
########### PREDICT ###########


from tensorflow.keras.models import load_model
import cv2
from tensorflow.keras.utils import img_to_array
from tensorflow import convert_to_tensor
import pandas as pd
import numpy as np
from PIL import Image
import psycopg2
import math
import os
from pathlib import Path
from conf import *


# Retrieve the secrets as environment variables
db_host = os.getenv("DB_HOST") or DB_HOST
db_username = os.getenv("DB_USERNAME") or DB_USERNAME
db_password = os.getenv("DB_PASSWORD") or DB_PASSWORD
db_name = os.getenv("DB_NAME") or DB_NAME

# Connect to the database using the secrets
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_username,
    password=db_password,
)


########### DIR'S PATH ###########

# MODEL_DIR =  os.path.join(os.path.dirname(os.path.abspath(__file__)),r'models/my_model_3rd_iteration.h5')
MODEL_DIR = Path(BASE_DIR,r'models/my_model_3rd_iteration.h5')
# SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data')
SAVE_DIR = Path(BASE_DIR,r'data')
# PRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data/pred.jpg')
PRED_FILE = Path(BASE_DIR,r'data/pred.jpg')
print(type(PRED_FILE))

LOGO = Path(BASE_DIR,Image.open(r'assets/logo_transparent.png'))

########### CUSTOMIZING PAGE TITLE AND FAVICON ###########

st.set_page_config(page_title='GasLeakDetector', page_icon=LOGO)

########### IMG INTRO ###########

col4, col5, col6 = st.columns([1,2.5,1])

with col4:
    st.write("")
with col5:
    st.image(LOGO,width=400)
with col6:
    st.write("")



########### LOAD MODEL AND DATA ###########

model_origin = load_model(MODEL_DIR)
l = 240
L = 320

def round_to_one_zero_after_decimal(n):
    if n == 0:
        return 0
    sgn = -1 if n < 0 else 1
    scale = int(-math.floor(math.log10(abs(n))))
    if scale < 0:
        scale = 1
    factor = 10**scale
    return sgn*math.floor(abs(n)*factor)/factor

# streamlit_app.py

########### HIDE BURGER MENU ###########

st.markdown(""" <style>
footer {visibility: hidden;}
span {color: #1F2023;}
</style> """, unsafe_allow_html=True)

########### CONDENSE LAYOUT ###########

padding = 5
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)


########### UPLOAD AND SAVE FILE ###########


st.subheader('Veuillez charger un document compatible (format jpg)')

def save_uploadedfile(uploadedfile):
    with open(os.path.join(SAVE_DIR,'pred.jpg'),"wb") as f:
        f.write(uploadedfile.getbuffer())
        
    return st.success("Image chargée !")


datafile = st.file_uploader("Image jpg nécessaire",type=['jpg'])
if datafile is not None:
    file_details = {"FileName":datafile.name,"FileType":datafile.type}
    save_uploadedfile(datafile)

    img = cv2.imread(str(PRED_FILE))
    img = np.array(img)
    img_resized = np.array(img).reshape(1,l,L,-1)
    prediction = model_origin.predict(img_resized,verbose=1)


    image = Image.open(datafile)

    col1, col2, col3 = st.columns([1,2.5,1])

    with col1:
        st.write("")
    with col2:
        st.image(image, caption='Image passée au model')
        st.write(f"Score du model : {float(prediction)}")
        if float(prediction) >= 0.5 :
            st.subheader("Pas de fuites de gaz !")
        elif float(prediction) < 0.5:
            st.subheader("Fuite de gaz !")

    with col3:
        st.write("")



    cursor = conn.cursor()
    # Save the prediction to the database
    cursor.execute("CREATE TABLE IF NOT EXISTS predictions  (id SERIAL PRIMARY KEY, input_data TEXT, prediction TEXT)")

    # Create the users table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY UNIQUE, name TEXT UNIQUE)")

    # Add a foreign key to the predictions table
    cursor.execute("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)")

    # Define the values to insert
    name = "Nidal"

    # Create the INSERT statement
    sql = """
    INSERT INTO users (name)
    SELECT * FROM (SELECT %s) AS tmp
    WHERE NOT EXISTS (
        SELECT name FROM users WHERE name = %s
    ) LIMIT 1;
    """
    cursor.execute(sql, (name, name))
    # Commit the changes
    conn.commit()

    # Retrieve the user's id
    cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
    user_id = cursor.fetchone()[0]



    cursor.execute("INSERT INTO predictions (user_id, input_data, prediction) VALUES (%s, %s, %s)", (user_id, str(datafile), round_to_one_zero_after_decimal(float(prediction))))

    conn.commit()
    cursor.close()
    conn.close()



