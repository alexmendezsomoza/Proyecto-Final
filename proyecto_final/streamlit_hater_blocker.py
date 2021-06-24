import streamlit as st
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

consumer_key = 'Qbxaw0OrPeZSFljKEp6SHI19M'
consumer_secret = 'kva4UfB6cK2Z6P70MGV8LAM0MMOu3SAHjuUl5t7bWxpegkCHGl'
access_key = '902474996-eLIpuPP1uqYZoTWtprZuiL2FmehUURAZHT8ZBReU'
access_secret = 'CkVPZlMz5Lk4EMYDZzmNM2zJQHGE0ze6CA0auHqnYtEhU'

# authorize twitter, initialize tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

users = []
users_url = []
tweets_url = []
usuario = []
texto = []

if st.button('Comenzar análisis de menciones.'):

    st.write('Analizando...')

    mentions = api.mentions_timeline(tweet_mode= 'extented')

    for tweet in mentions: # Entran los tweets

        users.append(tweet.user)

        for i in users:

            print(' ')

        clf = modelo()

        valoracion = clf.predict([tweet.text])

        if valoracion == 1: # Es positivo el tweet?

            st.write('No bloqueo al usuario. Guardado para entrenar.')

            print (' ')

            insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.


        elif valoracion == 0: # Es negativo el tweet?

            st.write('Voy a bloquear a ', tweet.user.screen_name, 'por el siguiente tweet:', tweet.text )

            verif = st.text_input("¿Deseas bloquear a este usuario?")

            if verif == 'Si': # Si

                api.create_block(tweet.user.screen_name)

                insert(tweet, i, 0) # Metelo en sql los tweets con etiqueta 0 para entrenar.

                bullies_to_sql(tweet, i) # Metelo en el listado de bullies para enseñarlo al cliente.

                st.write('Bloqueado. Guardado para entrenar.')

                st.write('Guardado para enviar a cliente. ')

                usuario.append(i.name)

                texto.append(tweet.text)


            elif verif == 'No': # No

                insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.

                st.write ('Usuario no bloqueado. Guardado para entrenar')

            elif verif == 'Para': # Para

                break