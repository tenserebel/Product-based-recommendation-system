# importing necessary libraries
import streamlit as st
import pandas as pd 
import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity 
from fastparquet import ParquetFile
import pymongo
from pymongo import MongoClient
import certifi

ca = certifi.where()
pf = ParquetFile('data.parq')
df = pf.to_pandas()
index_df=pd.read_csv('index.csv')

def to_low(strok:str):
    return strok.lower()

count_vec = CountVectorizer(stop_words='english')
count_matrix = count_vec.fit_transform(index_df['feature'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)
def cosine_recommender(nam:str,n):
    ind = index_df[index_df['name'] == nam].index.to_list()[0]
    cos_scor = list(enumerate(cosine_sim[ind]))
    cos_scor = sorted(cos_scor, key=lambda x: x[1], reverse=True)
    cos_scor = cos_scor[0:n+1]
    new_ind = [i[0] for i in cos_scor]
    return index_df['name'].iloc[new_ind]

@st.cache(hash_funcs={MongoClient: id})
def mongo_connect(url):
    return MongoClient(url,tlsCAFile=ca)

def mongo_upload():
  if db.name1.find_one({"user_name":name}):
    st.info("name already present")
  else:
        try:
            mongo_dump = { "user_name":name,
             }
            mongo_dump_result = db.name1.insert_one(mongo_dump)
            st.success("name added")
        except:
            st.error("some error occured")

st.title('Amazon Recommendation system')
client = mongo_connect("")# link for the mongodb connection.
db = client.name1
name=st.text_input("Enter your name here:")
if st.button("Enter data"):
  mongo_upload()
present_data=db.name1.find_one({"user_name":name})
try:
  present_data=present_data['product']
except (TypeError,KeyError):
  pass
input=st.selectbox('Enter the Product name:',df['name']) 
myquery = { "user_name": name}
newvalues = { "$set": { "product": input} }

int_val = st.number_input('Number of recommendation:', min_value=5, max_value=14, value=5, step=1)
st.caption('The Input number should be between 5 and 18.')
int_val=int(int_val)

st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
    color:blue;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<p class="big-font">OUTPUT:</p>', unsafe_allow_html=True)

def similar_prod(list_prod):
  if str(list_prod[0])==str(input):
      list_prod=list_prod[1:]
      return list_prod
  else:
      return list_prod

if st.button("Show Recommendation"):
  data2=db.name1.update_one({"user_name": name}, {"$set": { "product": input} }, upsert=False)
  st.write("Selected Model is Cosine Similarity")
  rec_output=[]
  cos=cosine_recommender(input,int_val)
  cos=cos.to_list()
  if present_data==input:
    st.write("same products")
    rec_output=cos.copy()
    rec_output=similar_prod(rec_output)
    st.write(rec_output)
  else:
    st.write("different products")
    cos=similar_prod(cos)
    cos1=cos[:int_val-2]
    for i in range(0,len(cos1)):
      rec_output.append(cos1[i])
    try:
      old_rec=cosine_recommender(present_data,int_val)
    except IndexError:
      st.write(cos)
    try:
      old_rec=old_rec.to_list()
      old_rec=old_rec[:2]
      for i in range(0,len(old_rec)):
        rec_output.append(old_rec[i])
      st.write(rec_output)
    except NameError:
      pass
  
