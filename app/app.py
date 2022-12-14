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


########### DIR'S PATH ###########

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'models/my_model_3rd_iteration.h5')
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data')
PRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),r'data/pred.jpg')



########### LOAD MODEL AND DATA ###########

model_origin = load_model(MODEL_DIR)
l = 240
L = 320

print('BLOOP')

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
    # for i in os.listdir(SAVE_DIR):
    #         os.remove(os.path.join(SAVE_DIR, i))
    

    # ##### USE DATA'S SAVED WITH THE MODEL FOR PREDICT #####
    # predictions = model.predict(df.drop(columns=['Strength'],axis=1))
    # norm_list = check_norm(predictions)




