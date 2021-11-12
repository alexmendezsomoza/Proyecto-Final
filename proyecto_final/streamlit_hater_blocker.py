import time
import streamlit as st
import time
import pandas as pd
from spacy import displacy
import spacy
import re
import mysql.connector as conn
from spacy.lang.es.stop_words import STOP_WORDS
#Crear pdf report
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
#Automatizar email
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sys
sys.path.append('../')
from src.track_function import *

from PIL import Image

#to write a title in our streamlit page we can use the magic command `write`

st.title ("""
# Hate Blocker
""")

st.header('''Hate Blocker te ayudará a disfrutar de las redes sociales sin recibir ningún tipo de acoso.''')

st.subheader("Creado por Álex Méndez")

user_input = st.text_input("text")

if user_input == 'Si':

    st.info('Estoy pensando')

if st.button('Enviar a mi correo'):

    st.write('Analizando...')
    mail()



# 4 authentication chains

from dotenv import load_dotenv
import os

load_dotenv()

consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_key = os.getenv("access_key")
access_secret = os.getenv("access_secret")

# authorize twitter, initialize tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

users = []
users_url = []
tweets_url = []
usuario = []
texto = []
count = 0

if st.button('Comenzar análisis de menciones.'):

    st.write('Analizando...')

    mentions = api.mentions_timeline(tweet_mode= 'extented')


    for tweet in mentions: # Entran los tweets

        count += 1

        users.append(tweet.user)

        for i in users:

            print(' ')

        filename = '/Users/alexmendezsomoza/Desktop/Ironhack/Proyecto-Final/proyecto_final/modeloNLP_Twitter'
        clf = pickle.load(open(filename, 'rb'))

        valoracion = clf.predict([tweet.text])

        if valoracion == 1: # Es positivo el tweet?

            st.write('No bloqueo al usuario. Guardado para entrenar.')

            print (' ')

            insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.


        elif valoracion == 0: # Es negativo el tweet?

            st.write('Voy a bloquear a ', tweet.user.screen_name, 'por el siguiente tweet:', tweet.text )

            answers = ['Si','No','Para']

            verif = st.selectbox('¿Qué hacemos?', ['Selecciona opción.'] + answers, key=count)

            if verif not in answers:

                time.sleep(0.1)

            else:

                if verif == 'Si': # Si

                    st.write('Bloqueado. Guardado para entrenar.')

                    st.write('Guardado para enviar a cliente. ')

                    api.create_block(tweet.user.screen_name)

                    insert(tweet, i, 0) # Metelo en sql los tweets con etiqueta 0 para entrenar.

                    bullies_to_sql(tweet, i) # Metelo en el listado de bullies para enseñarlo al cliente.

                    usuario.append(i.name)

                    texto.append(tweet.text)


                elif verif == 'No': # No

                    insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.

                    st.write ('Usuario no bloqueado. Guardado para entrenar')

                elif verif == 'Para': # Para

                    break
