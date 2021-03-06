#Credits to Kushal Bhavsar and his "Fruit & Vegetable Recognition"
#Source Github: https://github.com/Spidy20/Fruit_Vegetable_Recognition/blob/master/Fruits_Vegetable_Classification.py
#Youtube channel: https://www.youtube.com/watch?v=cF6rMXZcuCs&t=1171s

import streamlit as st
from PIL import Image
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.models import load_model
import requests
import datetime
import os
import altair as alt
import pandas as pd
from bs4 import BeautifulSoup
import tensorflow as tf
import tensorflow_hub as hub
from utils import *
import pyautogui
import sqlite3

conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

st.set_page_config(page_title="SG Snap Food",
                   page_icon="🍔")

labels = {0: 'Hainanese Chicken Rice', 1: 'apple', 2: 'bak kut teh', 3: 'banana', 4: 'char kway teow',
          5: 'chendol', 6: 'curry puff', 7: 'grapes', 8: 'kiwi', 9: 'laksa',
          10: 'mango', 11: 'nasi lemak', 12: 'orange', 13: 'oyster omelette', 14: 'pear',
          15: 'pineapple', 16: 'pomegranate', 17: 'roti prata', 18: 'satay', 19: 'watermelon'}

sgfood = ['Hainanese chicken rice', 'Bak kut teh', 'Char kway teow', 'Chendol', 'Curry puff', 'Laksa', 'Nasi lemak',
          'Oyster omelette', 'Roti prata', 'Satay']
fruit = ['Apple', 'Banana', 'Grapes', 'Kiwi', 'Mango', 'Orange', 'Pear', 'Pineapple', 'Pomegranate', 'Watermelon']

calories = get_calories()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS commentsdatabase(date INTEGER, correctness TEXT, picture TEXT,comments TEXT)")


def add_data(date, correctness, picture, comments):
    c.execute('INSERT INTO commentsdatabase(date,correctness,picture,comments) VALUES (?,?,?,?)',
              (date, correctness, picture, comments))
    conn.commit()


def fetch_calories(prediction):
    try:
        url = 'https://www.google.com/search?&q=calories in ' + prediction
        req = requests.get(url).text
        scrap = BeautifulSoup(req, 'html.parser')
        calories = scrap.find("div", class_="BNeawe iBp4i AP7Wnd").text
        return calories
    except Exception as e:
        st.error("Can't able to fetch the Calories")
        print(e)


@st.cache(suppress_st_warning=True)
def processed_img(img_path, model, class_names):
    img = load_img(img_path, target_size=(224, 224, 3))
    img = img_to_array(img)
    img = img / 255
    img = np.expand_dims(img, [0])
    answer = model.predict(img)
    print("answer is", answer)
    print("length of class_names", len(class_names))
    if int(len(class_names)) > 2:
        pred_class = class_names[tf.argmax(answer[0])]
        print("pred_class is", pred_class)
        pred_conf = tf.reduce_max(answer[0])
        print("pred_conf", pred_conf)
        top_5_i = sorted((answer.argsort())[0][-5:][::-1])
        print("top_5_i", top_5_i)
        values = answer[0][top_5_i] * 100
        print("values", values)
        labels = []
        for x in range(5):
            labels.append(class_names[top_5_i[x]])
            print("labels", labels)

        df = pd.DataFrame({"Top 5 Predictions": labels,
                           "F1 Scores": values,
                           'color': ['#d40b1f', '#720bd4', '#0b62d4', '#0bd4a5', '#0bd422']})
        df = df.sort_values('F1 Scores')
        print("df = ", df)
        st.success(f'Prediction : {pred_class} \n|| Confidence : {pred_conf * 100:.2f}%')
        st.write(alt.Chart(df).mark_bar().encode(
            x='F1 Scores',
            y=alt.X('Top 5 Predictions', sort=None),
            color=alt.Color("color", scale=None),
            text='F1 Scores'
        ).properties(width=600, height=400))
    else:
        pred_class = class_names[int(tf.round(answer))]
        print("pred_class is", pred_class)
        st.success(f'Prediction : {pred_class}')
    return pred_class.capitalize()


def run():
    st.image("https://github.com/DSstore/AIP/raw/main/snapfood.gif")
    app_mode = st.sidebar.selectbox("Choose the Classification Model",
                                    ["Binary Classification Model", "Multi-Class Classification Model",
                                     "EfficientNet Model_V1"])

    if app_mode == "Binary Classification Model":
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Loss", "0.088")
        col2.metric("Accuracy", "96.5%")
        col3, col4 = st.sidebar.columns(2)
        col3.metric("Val_Loss", "0.35")
        col4.metric("Val_ Acc", "89.6%")

        model = load_model('Binary_CNN_model_6.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        class_names = get_2_classes()
        st.sidebar.write("Number of identified food:  ", len(class_names))
        st.sidebar.table(class_names)
    elif app_mode == "Multi-Class Classification Model":
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Loss", "0.19")
        col2.metric("Accuracy", "94%")
        col3, col4 = st.sidebar.columns(2)
        col3.metric("Val_Loss", "0.80")
        col4.metric("Val_ Acc", "81.48%")

        model = load_model('Multi_class_model.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        class_names = get_10_classes()
        st.sidebar.write("Number of identified food:  ", len(class_names))
        st.sidebar.table(class_names)
    elif app_mode == "EfficientNet Model_V1":
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Loss", "0.19")
        col2.metric("Accuracy", "98%")
        col3, col4 = st.sidebar.columns(2)
        col3.metric("Val_Loss", "0.43")
        col4.metric("Val_ Acc", "88.6%")

        model = load_model('efficientnet_model_1.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        class_names = get_20_classes()
        st.sidebar.write("Number of identified food:  ", len(class_names))
        st.sidebar.table(class_names)

    st.sidebar.title("**Disclaimer**")
    st.sidebar.write(
        "Daily values are based on 2000 calorie diet and 155 lbs body weight.\nActual daily nutrient requirements might be different based on your age, gender, level of physical activity, medical history, and other factors.\nAll data displayed on this site is for general informational purposes only and should not be considered a substitute of a doctor's advice. Please consult with your doctor before making any changes to your diet.\nNutrition labels presented on this site is for illustration purposes only. Food images may show a similar or a related product and are not meant to be used for food identification.\nNutritional value of a cooked product is provided for the given weight of cooked food. \nData from USDA National Nutrient Database.")

    application_mode = st.radio(
        "Select your capture mode",
        ('Images', 'Camera'))
    if application_mode == 'Images':
        img_file = st.file_uploader("Choose an Image", type=["jpg", "png"])
    else:
        img_file = st.camera_input("Take a picture")

    if not img_file:
        st.warning("Please upload an image")
        st.stop()
    else:
        img = Image.open(img_file).resize((250, 250))
        st.image(img, use_column_width=False)
        save_image_path = img_file.name
        with open(save_image_path, "wb") as f:
            f.write(img_file.getbuffer())
        pred_button = st.button("Predict")

    if pred_button:
        pred_class = processed_img(save_image_path, model, class_names)

        if pred_class in sgfood:
            st.info('**Category : Singapore Local Dish**')
            st.image(calories[pred_class])

        else:
            st.info('**Category : Fruits**')
            cal = fetch_calories(pred_class)
            if cal:
                st.warning('**' + cal + '(100 grams)**')

    create_table()
    selection = st.selectbox("Is this image correct?", ("Select an option", "Yes", "No"))
    if selection == "Select an option":
        pass
    elif selection == "No":
        usercomment = st.text_input('What should the image be?')
        if usercomment:
            timingnow = datetime.datetime.now()
            add_data(date=timingnow, correctness="No", picture=save_image_path, comments=usercomment)
            st.write("Thank you for that, we'll use your help to make our model better!")
            pyautogui.hotkey("ctrl", "F5")
    elif selection == "Yes":
        timingnow = datetime.datetime.now()
        add_data(date=timingnow, correctness="Yes", picture=save_image_path, comments=None)
        st.write('Thank you for your feedback!')
        pyautogui.hotkey("ctrl", "F5")


run()