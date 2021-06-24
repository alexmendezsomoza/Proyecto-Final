
import pandas as pd
import tweepy
import string #Quita todos los simbolos
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
import pickle
import mysql.connector as conn

#Automatizar email

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# cursor SQL

db = conn.connect(host='localhost', user='root', passwd='123456', database='hate_blocker')

cursor = db.cursor()

def insert(tweet, i, sentiment):
    insert_query = "insert into {} ({}) values {};" \
        .format('train_model', ','.join(['tweet_id', 'user', 'content', 'date', 'lang', 'sentiment']),
                tuple([tweet.id_str, i.id, tweet.text, str(tweet.created_at), 'es', sentiment]))

    cursor.execute(insert_query)

    db.commit()

    return


def bullies_to_sql(tweet, i):
    insert_query = "insert into {} ({}) values {};" \
        .format('listado_bullies', ','.join(['tweet_id', 'date', 'account', 'tweet_text', 'URL_account', 'URL_tweet']),
                tuple([tweet.id_str, str(tweet.created_at), i.screen_name, tweet.text,
                       'https://twitter.com/' + i.screen_name,
                       'https://twitter.com/' + i.screen_name + '/status/' + tweet.id_str]))

    cursor.execute(insert_query)

    db.commit()

    return


def mail(usuario,texto):
    # assign key email aspects to variables for easier future editing
    subject = "Hater Report"
    body = 'Hola, te envío el resumen de los usuarios bloqueados: \n'
    for i in range(len(usuario)):
        body += f"- He bloqueado al usuario *{usuario[i]}* por el tweet: {texto[i]} \n"

    sender_email = "ironhack.trabajo.final@gmail.com"
    receiver_email = "alexmendezsomoza@gmail.com"
    # file = "automate_report.pdf" # in the same directory as script
    password = "Ironhack2021"

    # Create the email head (sender, receiver, and subject)

    email = MIMEMultipart()
    email["From"] = sender_email
    email["To"] = receiver_email
    email["Subject"] = subject

    # Add body and attachment to email

    email.attach(MIMEText(body, "plain"))

    # attach_file = open(file, "rb") # open the file
    # report = MIMEBase("application", "octate-stream")
    # report.set_payload((attach_file).read())
    # encoders.encode_base64(report)

    # add report header with the file name

    # report.add_header("Content-Decomposition", "attachment", filename = file)
    # email.attach(report)

    # Create SMTP session for sending the mail

    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_email, password)  # login with mail_id and password
    text = email.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()

    return ('Mail Sent')


puntua = string.punctuation + "¡¿"
puntua


# Función para limpieza de datos
def text_data_cleaning(sentence):
    """
    :param sentence:
    :return: list de strings (stopwords)
    """
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(sentence)
    stopwords_spacy = list(STOP_WORDS)

    tokens = []
    for token in doc:
        if token.lemma_ != "-PRON-":
            temp = token.lemma_.strip()
        else:
            temp = token
        tokens.append(temp)

    clean_tokens = []
    for token in tokens:
        if token not in stopwords_spacy and token not in puntua:
            clean_tokens.append(token)

    return clean_tokens


def modelo():

    filename = 'modeloNLP_Twitter'
    modelo = pickle.load(open(filename, 'rb'))

    return modelo



def valoracion_block():

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


    mentions = api.mentions_timeline(tweet_mode= 'extented')

    for tweet in mentions: # Entran los tweets

        users.append(tweet.user)

        for i in users:

            print(' ')

        clf = modelo()
        valoracion = clf.predict([tweet.text])

        if valoracion == 1: # Es positivo el tweet?

            print ('No bloqueo al usuario. Guardado para entrenar.')

            print (' ')

            insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.


        elif valoracion == 0: # Es negativo el tweet?

            print('Voy a bloquear a ', tweet.user.screen_name, 'por el siguiente tweet:', tweet.text )

            verif = input ('¿Deseas bloquear a este usuario?') # Estas seguro que quieres bloquear?

            print (verif)

            if verif == 'Si': # Si

                api.create_block(tweet.user.screen_name)

                insert(tweet, i, 0) # Metelo en sql los tweets con etiqueta 0 para entrenar.

                bullies_to_sql(tweet, i) # Metelo en el listado de bullies para enseñarlo al cliente.

                print('Bloqueado. Guardado para entrenar.')

                print('Guardado para enviar a cliente. ')

                usuario.append(i.name)

                texto.append(tweet.text)

                #pdf(usuario, texto)



            elif verif == 'No': # No

                insert(tweet, i, 1) # Mete en sql los tweets con etiqueta 1 para entrenar.

                print ('Usuario no bloqueado. Guardado para entrenar')

            elif verif == 'Para': # Para

                break

    return usuario,texto

