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

st.title('WhatsApp Group Analysis')
st.markdown('Analysis on Exported chats to understand texting patterns of users.')