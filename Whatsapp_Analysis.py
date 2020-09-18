import streamlit as st
import pandas as pd 
import numpy as np 
import re
import emoji
import plotly.express as px 
from collections import Counter
import matplotlib.pyplot as plt 
from os import path 
from PIL import Image 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import regex
import time
import sys
import inspect
import datetime
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

st.title('WhatsApp Group Analysis')
st.markdown('Analysis Grup WhatsApp Sederhana menggunakan Python & Pyplot')
st.set_option('deprecation.showfileUploaderEncoding', False)

st.sidebar.title('About:')
st.sidebar.markdown('Aplikasi ini digunakan untuk menganalisis Whatsapp Group Chat yang di eksport tanpa media.')

st.sidebar.markdown('[![IdSundev]\
                    (https://img.shields.io/badge/Author-@IdSundev-gray.svg?colorA=gray&colorB=dodgerblue&logo=github)]\
                    (https://github.com/IdSundev/Analysing-WhatsApp-Group-using-Streamlit/)')

st.sidebar.markdown('**Cara Export group chat (Not Available on WhatApp Web)**')
st.sidebar.text('1) Pilih group chat.')
st.sidebar.text('2) Pilih options > More > Export chat.')
st.sidebar.text('3) Pilih export without media.')
st.sidebar.markdown('**FAQs**')
st.sidebar.markdown('Data yang diupload tidak akan disimpan dimanapun baik di situs ini maupun di third party seperti local storage(DB/FileSystem/Logs)')

st.sidebar.markdown('**REFERENCE**')
st.sidebar.markdown('[![Saiteja Kura]\
                    (https://img.shields.io/badge/Reference-@SaitejaKura-gray.svg?colorA=gray&colorB=dodgerblue&logo=github)]\
                    (https://github.com/kurasaiteja/Whatsapp-Group-Chat--Analyzer-Web-App/)')

# menampilkan grafik untuk emoji
def visualize_emoji(data):
  total_emojis_list = list([a for b in messages_df.emoji for a in b])
  emoji_dict = dict(Counter(total_emojis_list))
  emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
  emoji_df = pd.DataFrame(emoji_dict, columns=['emoji','count'])
  fig = px.pie(emoji_df, values='count', names='emoji')
  fig.update_traces(textposition='inside', textinfo='percent+label')
  fig.update_layout(
    margin=dict(
      l=5,
      r=5,
    )
  )
  fig.update(layout_showlegend=False)
  return fig

# Fungsi untuk melihat pada tgl berapa saja group paling ramai
def messages_as_time_moves_on(messages_df):
  date_df = messages_df.groupby('Date').sum()
  date_df['MessageCount'] = messages_df.groupby('Date').size().values
  date_df.reset_index(inplace=True)
  fig = px.line(date_df, x='Date', y='MessageCount')
  fig.update_layout(
    margin=dict(
      l=5,
      r=5,
    )
  )
  return fig

# Chatter Award
def chatteraward(messages_df):
  auth = messages_df.groupby('Author').sum()
  auth['MessageCount'] = messages_df.groupby('Author').size().values
  auth.reset_index(inplace=True)
  fig = px.bar(
    auth, 
    x='Author', 
    y='MessageCount', 
    color='Author', 
    orientation='v',
    color_discrete_sequence=['red','green','blue','goldenrod','magenta'],
    title='Chatter Award' )
  fig.update(layout_showlegend=False)
  fig.update_layout(
    margin=dict(
      l=5,
      r=5,
    )
  )
  return fig

# Top 10 Times of the day at which the most number of messages were sent
def time_active(messages_df):
  messages_df['Time'].value_counts().head(10).plot.barh()
  plt.xlabel('Number of messages')
  plt.ylabel('Time')
  plt.tight_layout()

# Menampilkan Word Cloud
def words(messages_df):
  text = ' '.join(review for review in messages_df.Message)
  stopwords = set(STOPWORDS)
  stopwords_sastrawi = StopWordRemoverFactory().get_stop_words()
  stopwords.update(stopwords_sastrawi)
  path='content/id.stopwords.txt'
  f = open(path)
  stopwords_masdevin = [x.rstrip() for x in f]
  f.close()
  stopwords.update(stopwords_masdevin)
  update_stopwords = ['mba','mas','mbak','bu','klo','yaa','ga','aja','mbak','udah','nih','nya','lu','gw','gak','bang','bro','wkwk','wkwkwk','bg','nih','yg','kalo','gue','kak','Iya','si','btw','tau','yaaa','kalo','orang','dah','Terima kasih','sdg','yah','utk','bgmn','lgss','sdh','dlm','jg','smg']
  stopwords.update(update_stopwords)
  wordcloud = WordCloud(stopwords=stopwords, background_color='white', height=640, width=800).generate(text)
  # Display the generated image the matplotlib way:
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.xticks([])
  plt.yticks([])
  plt.tight_layout()

# The most happening day was
def day(messages_df):
  messages_df['Date'].value_counts().head(10).plot.barh()
  plt.xlabel('Number of Messages')
  plt.ylabel('Date')
  plt.tight_layout()

# counting emoji
def split_count(text):
  emoji_list = []
  data = regex.findall(r'\X', text)
  for word in data:
    if any(char in emoji.UNICODE_EMOJI for char in word):
      emoji_list.append(word)
  return emoji_list

# takes input as data and return number of messages and total emojis in chat.
def stats(data):
  total_messages = data.shape[0]
  media_messages = data[data['Message'] == '<Media omitted>'].shape[0]
  emojis = sum(data['emoji'].str.len())

  return "Total Messages 💬: {} \n Total Media 🎬: {} \n Total Emoji's 😂: {}".format(total_messages, media_messages, emojis)

# Exports dari Android
def startsWithDateAndTimeAndroid(s):
  pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9])(, | )([0-9]+)(:|.)([0-9]+)([" AM"|" PM"]*) -'
  result = re.match(pattern, s)
  if result:
    return True
  return False

# Exports dari ios
def startsWithDateAndTimeios(s):
  pattern = '^\[([0-9]+)([\/-])([0-9]+)([\/-])([0-9]+)[,]? ([0-9]+):([0-9][0-9]):([0-9][0-9])?[ ]?(AM|PM|am|pm)?\]' 
  result = re.match(pattern, s)
  if result:
    return True
  return False

# Find Author
def FindAuthor(s):
  s=s.split(":")
  if len(s)==2:
    return True
  else:
    return False

def handleTimeAndroid(line):
  splitTime = line.split(':')
  if line[-2:] == 'PM':
    pm = dict(zip(range(12), range(12,24)))
    pm[12] = 0
    time = str(pm[int(splitTime[0])])+':'+splitTime[1][:2]
  else:
    if int(splitTime[0]) < 10:
      time = '0'+splitTime[0]+':'+splitTime[1][:2]
    else:
      time = splitTime[0]+':'+splitTime[1][:2]
  return time


def getDataPointAndroid(line):
  splitline = line.split(' - ')
  dateTime = splitline[0]
  if (dateTime[-2:] == 'AM') | (dateTime[-2:] == 'PM'):
    date, time = dateTime.split(', ')
    time = handleTimeAndroid(time)
  else:
    if dateTime[8] == ' ':
      date, time = dateTime.split(' ')
    else:
      date, time = dateTime.split(', ')
  message = ' '.join(splitline[1:])
  if FindAuthor(message):
    splitMessage = message.split(': ')
    author = splitMessage[0]
    message = ' '.join(splitMessage[1:])
  else:
    author = None
  return date, time, author, message

def getDataPointios(line):
  splitline = line.split('] ')
  dateTime = splitline[0]
  if ',' in dateTime:
    date, time = dateTime.split(',')
  else:
    date, time = dateTime.split(' ')
  message = ' '.join(splitline[1:])
  if FindAuthor(message):
    splitMessage = message.split(': ')
    author = splitMessage[0]
    message = ' '.join(splitMessage[1:])
  else:
    author = None
  if time[5] == ':':
    print(time)
    time = time[:5]+time[-3:]
  else:
    if 'AM' in time or 'PM' in time:
      time = time[:6]+time[-3:]
    else:
      time = time[:6]
  return date, time, author, message

# untuk keperluan date di ios
def dateconv(date):
  year = ''
  if '-' in date:
    year = date.split('-')[2]
    if len(year) == 4:
      return datetime.datetime.strptime(date, "[%d-%m-%Y").strftime("%Y-%m-%d")
    elif len(year) ==2:
      return datetime.datetime.strptime(date, "[%d-%m-%y").strftime("%Y-%m-%d")
  elif '/' in date:
    year = date.split('/')[2]
    if len(year) == 4:
      return datetime.datetime.strptime(date, "[%d/%m/%Y").strftime("%Y-%m-%d")
    if len(year) ==2:
      return datetime.datetime.strptime(date, "[%d/%m/%y").strftime("%Y-%m-%d")

# Upload File
uploaded_file = st.file_uploader('Upload Your Whatsap Chat.(.txt file only!)', type='txt')
st.markdown('**Format:**')
st.text('(Tgl/Bln/Thn) (Jam.Menit) - (Author): (Message) Atau')
st.text('(Tgl/Bln/Thn), (Jam:Menit) - (Author): (Message) Atau')
st.text('(Tgl/Bln/Thn), (Jam:Menit AM|PM) - (Author): (Message)')
if uploaded_file is not None:
  @st.cache(allow_output_mutation=True)
  def load_data(uploaded_file):
    device=''
    if '[' in next(uploaded_file):
      device = 'ios'
    else:
      device = 'android'
    next(uploaded_file)
    parsedData = []
    messageBuffer = []
    date, time, author = None, None, None
    for i in uploaded_file:
      line = i
      if not line:
        break
      if device == 'ios':
        line = line.strip()
        if startsWithDateAndTimeios(line):
          if len(messageBuffer) > 0:
            parsedData.append([date, time, author, ' '.join(messageBuffer)])
          messageBuffer.clear()
          date, time, author, message = getDataPointios(line)
          messageBuffer.append(message)
        else:
          line = (line.encode('ascii', 'ignore')).decode('utf-8')
          if startsWithDateAndTimeios(line):
            if len(messageBuffer) > 0:
              parsedData.append([date, time, author, ' '.join(messageBuffer)])
            messageBuffer.clear()
            date, time, author, message = getDataPointios(line)
            messageBuffer.append(message)
          else:
            messageBuffer.append(line)
      else:
        line = line.strip()
        if startsWithDateAndTimeAndroid(line):
          if len(messageBuffer) > 0:
            parsedData.append([date, time, author, ' '.join(messageBuffer)])
          messageBuffer.clear()
          date, time, author, message = getDataPointAndroid(line)
          messageBuffer.append(message)
        else:
          messageBuffer.append(line)

    if device == 'android':
      df = pd.DataFrame(parsedData, columns=['Date', 'Time','Author','Message'])
      df['Date'] = pd.to_datetime(df['Date'])
      # hapus data yang mengandung NA
      df = df.dropna()
      # hapus Message dengan isi: 'Pesan ini telah dihapus' atau 'This message was deleted'
      indexNames = df[(df['Message'] == 'Pesan ini telah dihapus') | (df['Message'] == 'This message was deleted')].index
      df.drop(indexNames, inplace=True)
      df['emoji'] = df['Message'].apply(split_count)
      URLPATTERN = r'(https?://\S+)'
      df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
      return df
    else:
      df = pd.DataFrame(parsedData, columns=['Date','Time','Author','Message'])
      df = df.dropna()
      df['Date'] = df['Date'].apply(dateconv)
      df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
      df['emoji'] = df['Message'].apply(split_count)
      URLPATTERN = r'(https?://\S+)'
      df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
      return df
  data = load_data(uploaded_file)
  authorlist = list(data.Author.unique())
  authorlist.insert(0, 'All')
  st.subheader("**Who's Stats do you want to see?**")
  option = st.selectbox("", authorlist)
  if option == 'All':
    name='Group'
    total_messages = data.shape[0]
    link_messages = data[data['urlcount']>0]
    deleted_messages=data[(data["Message"] == " You deleted this message")| (data["Message"] == " This message was deleted")| (data["Message"] == " This message was deleted.")|(data["Message"] == " You deleted this message.")]
    print(deleted_messages.shape[0])
    media_messages = data[(data['Message'] == '<Media tidak disertakan>')|(data['Message'] == '<Media omitted>')|(data['Message'] == 'image omitted')|(data['Message'] == 'video omitted')|(data['Message'] == 'sticker omitted')].shape[0]
    emojis = sum(data['emoji'].str.len())
    links = np.sum(data.urlcount)
    st.subheader("**%s's total messages 💬**"% name)
    st.markdown(total_messages)
    st.subheader("**%s's total media 🎬**"% name)
    st.markdown(media_messages)
    st.subheader("**%s's total emojis 😂**"% name)
    st.markdown(emojis)
    st.subheader("**%s's total links**"% name)
    st.markdown(links)
    media_messages_df = data[(data['Message'] == '<Media tidak disertakan>')|(data['Message'] == '<Media omitted>')|(data['Message'] == 'image omitted')|(data['Message'] == 'video omitted')|(data['Message'] == 'sticker omitted')]
    messages_df = data.drop(media_messages_df.index)
    messages_df = messages_df.drop(deleted_messages.index)
    messages_df = messages_df.drop(link_messages.index)
    messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
    messages_df['MessageCount'] = 1
    messages_df['emojicount'] = messages_df['emoji'].str.len()
    config={'responsive': True}
    st.header("**Some more Stats**")
    st.subheader("**%s's emoji distribution 😂**"% name)
    st.text("Hover on Chart to see details.")
    st.plotly_chart(visualize_emoji(data),use_container_width=True)
    st.subheader("**%s's messages as time moves on**"% name)
    st.text("Hover on Chart to see details.")
    st.plotly_chart(messages_as_time_moves_on(messages_df),use_container_width=True)
    st.subheader("**And the Chatter Award in the group goes to - **")
    st.text("Hover on Chart to see details.")
    st.plotly_chart(chatteraward(messages_df),use_container_width=True)
    st.subheader("**When is the %s most active?**"% name)
    time_active(messages_df)
    st.pyplot()
    time.sleep(0.2)
    st.subheader("**The most happening day for the %s was - **"% name)
    day(messages_df)
    st.pyplot()
    time.sleep(0.2)
    st.subheader("**%s's WordCloud **"% name)
    words(messages_df)
    st.pyplot()
  else:
    data = data[data.Author.eq(option)]
    total_messages = data.shape[0]
    link_messages= data[data['urlcount']>0]
    deleted_messages=data[(data["Message"] == " You deleted this message")| (data["Message"] == " This message was deleted.")|(data["Message"] == " You deleted this message.")]
    print(deleted_messages.shape[0])
    media_messages = data[(data['Message'] == '<Media tidak disertakan>')|(data['Message'] == '<Media omitted>')|(data['Message'] == 'image omitted')|(data['Message'] == 'video omitted')|(data['Message'] == 'sticker omitted')].shape[0]
    emojis = sum(data['emoji'].str.len())
    links = np.sum(data.urlcount)
    st.subheader("**%s's total messages 💬**"% option)
    st.markdown(total_messages)
    st.subheader("**%s's total media 🎬**"% option)
    st.markdown(media_messages)
    st.subheader("**%s's total emojis 😂**"% option)
    st.markdown(emojis)
    st.subheader("**%s's total links**"% option)
    st.markdown(links)
    media_messages_df = data[(data['Message'] == '<Media tidak disertakan>')|(data['Message'] == '<Media omitted>')|(data['Message'] == 'image omitted')|(data['Message'] == 'video omitted')|(data['Message'] == 'sticker omitted')]
    messages_df = data.drop(media_messages_df.index)
    messages_df = messages_df.drop(deleted_messages.index)
    messages_df = messages_df.drop(link_messages.index)
    messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
    messages_df["MessageCount"]=1
    messages_df["emojicount"]= messages_df['emoji'].str.len()
    st.header("**Some more Stats**")
    st.subheader("**%s's emoji distribution 😂**"% option)
    st.text("Hover on Chart to see details.")
    st.plotly_chart(visualize_emoji(data),use_container_width=True)
    st.subheader("**%s's messages as Time moves on**"% option)
    st.text("Hover on Chart to see details.")
    st.plotly_chart(messages_as_time_moves_on(messages_df),use_container_width=True)
    st.subheader("**When is %s most active?**"% option)
    time_active(messages_df)
    st.pyplot()
    time.sleep(0.2)
    st.subheader("**The most happening day for %s was - **"% option)
    day(messages_df)
    st.pyplot()
    time.sleep(0.2)
    st.subheader("** %s's WordCloud **"% option)
    words(messages_df)
    st.pyplot()