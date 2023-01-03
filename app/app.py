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

# Retrieve the secrets as environment variables
db_host = os.environ["DB_HOST"]
db_username = os.environ["DB_USERNAME"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

# Connect to the database using the secrets
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_username,
    password=db_password,
)


########### DIR'S PATH ###########

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'models/my_model_3rd_iteration.h5')
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data')
PRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data/pred.jpg')


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

import streamlit as st

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]

        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.write("Here goes your normal Streamlit app...")
    st.button("Click me")



    ########### HIDE BURGER MENU ###########

    st.markdown(""" <style>
    footer {visibility: hidden;}
    span {color: #1F2023;}
    </style> """, unsafe_allow_html=True)

    ########### CONDENSE LAYOUT ###########

    padding = 0
    st.markdown(f""" <style>
        .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;
        }} </style> """, unsafe_allow_html=True)


    ########### UPLOAD AND SAVE FILE ###########
    st.subheader('Detecter une Fuite de Gaz !')

    st.subheader('Veuillez charger un document compatible (format jpg)')

    def save_uploadedfile(uploadedfile):
        with open(os.path.join(SAVE_DIR,'pred.jpg'),"wb") as f:
            f.write(uploadedfile.getbuffer())
            
        return st.success("Image chargée !")


    datafile = st.file_uploader("Image jpg nécessaire",type=['jpg'])
    if datafile is not None:
        file_details = {"FileName":datafile.name,"FileType":datafile.type}
        save_uploadedfile(datafile)

        img = cv2.imread(PRED_FILE)
        img = np.array(img)
        img_resized = np.array(img).reshape(1,l,L,-1)
        prediction = model_origin.predict(img_resized,verbose=1)

        st.write(prediction)

        cursor = conn.cursor()
        # Save the prediction to the database
        cursor.execute("CREATE TABLE IF NOT EXISTS predictions  (id SERIAL PRIMARY KEY, input_data TEXT, prediction TEXT)")

        # Create the users table
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY UNIQUE, name TEXT UNIQUE, email TEXT UNIQUE)")

        # Add a foreign key to the predictions table
        cursor.execute("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)")

        # Insert a row into the users table
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("jean", "jean@example.com"))
        # Commit the changes
        conn.commit()

        # Retrieve the user's id
        cursor.execute("SELECT id FROM users WHERE name = %s", ("jean",))
        user_id = cursor.fetchone()[0]


        # cursor.execute("INSERT INTO predictions (input_data, prediction) VALUES (%s, %s)", (input_data, round_to_one_zero_after_decimal(float(prediction))))

        cursor.execute("INSERT INTO predictions (user_id, input_data, prediction) VALUES (%s, %s, %s)", (user_id, str(datafile), round_to_one_zero_after_decimal(float(prediction))))

        conn.commit()
        cursor.close()
        conn.close()

            # for i in os.listdir(SAVE_DIR):
            #         os.remove(os.path.join(SAVE_DIR, i))
            

            # ##### USE DATA'S SAVED WITH THE MODEL FOR PREDICT #####
            # predictions = model.predict(df.drop(columns=['Strength'],axis=1))
            # norm_list = check_norm(predictions)




