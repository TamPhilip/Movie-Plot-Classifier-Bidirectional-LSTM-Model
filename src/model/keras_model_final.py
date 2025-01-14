# -*- coding: utf-8 -*-
# TODO:  Create a Model class
import h5py
import time
import numpy as np
import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

#
# from numpy import array
# from numpy import argmax
# from keras.utils import to_categorical
# from numpy import array
# from numpy import argmax
# from keras.utils import to_categorical
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics import confusion_matrix
# from sklearn.preprocessing import normalize
# from keras.preprocessing.sequence import pad_sequences
# from keras.utils.np_utils import to_categorical
from keras.callbacks import EarlyStopping
from keras.preprocessing.text import Tokenizer
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from keras.models import Sequential
from nltk.corpus import stopwords
from keras.layers import Bidirectional
import matplotlib.pyplot as plt
import tensorflow as tf
# import numpy
sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
path = os.path.abspath(os.curdir)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print(path)
df_co = pd.read_csv('{}/../csv-data/movie-data-cleaned.csv'.format(path))
df_co.drop(['Unnamed: 0'], axis=1, inplace=True)
df_im = pd.read_csv('{}/../csv-data/movies_genres.csv'.format(path), delimiter='\t')

df_im.head()

imdb_genres = df_im.drop(['plot', 'title', 'Sci-Fi','Documentary', 'Reality-TV', 'Animation'], axis=1)
counts = []
categories = list(imdb_genres.columns.values)
for i in categories:
    counts.append((i, imdb_genres[i].sum()))
df_stats_imdb = pd.DataFrame(counts, columns=['genre', '#movies'])

df_stats_imdb = df_stats_imdb[df_stats_imdb['#movies'] > 8000]
df_stats_imdb
# df_stats_imdb['genre'].values

df_co.head()

corpus_genres = df_co.drop(['Title', 'Summary', 'Horror'], axis=1)
counts = []
categories = list(corpus_genres.columns.values)
for i in categories:
  counts.append((i, corpus_genres[i].sum()))
df_stats_corpus = pd.DataFrame(counts, columns=['genre', '#movies'])
df_stats_corpus

cs = []

for index, category in enumerate(df_stats_imdb['genre']):
  current_index_b = 0
  for index_b, category_b in enumerate(df_stats_corpus['genre']):
    if category == category_b:
      current_index_b = index_b
      cs.append((category, df_stats_corpus['#movies'].values[index_b] + df_stats_imdb['#movies'].values[index]))
  if not (category, df_stats_corpus['#movies'].values[current_index_b] + df_stats_imdb['#movies'].values[index]) in cs:
      cs.append((category, df_stats_imdb['#movies'].values[index]))

df_stats = pd.DataFrame(cs, columns=['genre', '#movies'])
df_stats

df_im = df_im.drop(['Sci-Fi','Documentary', 'Reality-TV', 'Animation'], axis=1)
df_co = df_co.drop(['Horror'], axis=1)

df_co.rename(index=str, columns={"Title": "title", "Summary": "plot"}, inplace=True)

print(df_im.head())
print(df_co.head())

df_im.shape

df_final = df_im.append(df_co)
df_final.fillna(int(0), inplace=True)

df_final_plot = df_final[['plot']]
df_final_values = df_final[['Action',
                            'Adventure',
                            'Comedy',
                            'Crime',
#                             'Drama',
                            'Family',
                            'Mystery',
                            'Romance',
                            'Thriller']].astype(int)

df_final_plot['plot'] = df_final_plot['plot'].str.lower().replace('["\'#$%&()*+,-/:;<=>@[\\]^_`{|}~\t\n]',' ', regex=True)

df_final = pd.concat([df_final_plot, df_final_values], axis=1, join='inner')

df_final

movie_data = df_final[(df_final['Action'] == 1) |
                        (df_final['Comedy'] == 1) |
                        (df_final['Adventure'] == 1) |
                        (df_final['Thriller'] == 1) |
#                         (df_final['Drama'] == 1) |
                        (df_final['Mystery'] == 1) |
                         (df_final['Family'] == 1) |
                        (df_final['Romance'] == 1) |
                        (df_final['Crime'] == 1)]

print(len(movie_data))

print(" \n SELECT DATA \n")

counat = 0
def check(r,
          a,
          dr,
          co,
          th,
          ad,
          my,
          fa,
          cr):
    genres = ['Action',
              'Comedy',
              'Drama',
              'Thriller',
              'Family',
              'Adventure',
              'Mystery',
              'Romance',
              'Crime']
    movie = movie_data[
        (movie_data['Romance'] == r)
        & (movie_data['Action'] == a)
#             & (movie_data['Drama'] == dr)
            & (movie_data['Comedy'] == co)
            & (movie_data['Thriller'] == th)
            & (movie_data['Family'] == fa)
            & (movie_data['Adventure'] == ad)
            & (movie_data['Mystery'] == my)
            & (movie_data['Crime'] == cr)
    ]
    if r == 0:
        genres.remove('Romance')
    if a ==0:
        genres.remove('Action')
    if dr == 0:
        genres.remove('Drama')
    if co == 0:
        genres.remove('Comedy')
    if th == 0:
        genres.remove('Thriller')
    if ad == 0:
        genres.remove('Adventure')
    if cr == 0:
        genres.remove('Crime')
    if my == 0:
        genres.remove('Mystery')
    if fa == 0:
        genres.remove('Family')
    if len(movie) > 1000:
      print(" {} : {}".format(genres, len(movie)))
    return len(movie)

for r in range(2):
    for a in range(2):
        for dr in range(1):
            for co in range(2):
                for th in range(2):
                    for fa in range(2):
                        for cr in range(2):
                            for ad in range(2):
                              for my in range(2):
                                counat += check(r, a, dr, co, th, ad, my, fa, cr)
print(counat)
movie_data.to_csv('final_data.csv')

#%%
movie_data = pd.read_csv('{}/../csv-data/final_data.csv'.format(path))
df_final = movie_data

df_final.drop(['Unnamed: 0'], axis=1, inplace=True)
print(df_final.columns)

df_final.shape

stop_words = set(stopwords.words('english'))
stop_words = {x.replace("'","") for x in stop_words if re.search("[']", x.lower())}

vectorizer = TfidfVectorizer(max_features=2500, ngram_range=(1, 2))
print("Here")
movie_data = np.split(df_final, [1], axis=1)
y_data = movie_data[1]
features = movie_data[0]['plot'].values
X = vectorizer.fit_transform(features).toarray()
del features
del movie_data
del df_final

epochs = 10
emb_dim = 128
batch_size = 32

#%%

print(X.shape)

#%% Run Changes
def create_train_model(genre):
    y = y_data[genre]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

    print("here)")
    model = Sequential()
    model.add(Embedding(2500, emb_dim, input_length=X.shape[1]))
    model.add(SpatialDropout1D(0.7))
    model.add(Bidirectional(LSTM(30, recurrent_dropout=0.7)))
    model.add(Dense(1, activation='sigmoid'))
    print("Start")
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
    print(model.summary())
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,validation_data=(X_test, y_test),callbacks=[EarlyStopping(monitor='val_loss',patience=7, min_delta=0.0001)])

    #for genre, history in hist.items():
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy {}'.format(genre))
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train','test'], loc='upper left')
    plt.show()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss for {}'.format(genre))
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train','test'], loc='upper left')
    plt.show()

    return model
#%% Run Action
print("Starting")
action_model = create_train_model('Action')
action_model.save('action_model.h5')
#%% Run Adventure
adventure_model = create_train_model('Adventure')
adventure_model.save('adventure_model.h5')
#%% Run Comedy
comedy_model = create_train_model('Comedy')
comedy_model.save('comedy_model.h5')
#%% Run Thriller
thriller_model = create_train_model('Thriller')
thriller_model.save('thriller_model.h5')
#%% Run Family
family_model = create_train_model('Family')
family_model.save('family_model.h5')
#%% Run Mystery
mystery_model = create_train_model('Mystery')
mystery_model.save('mystery_model.h5')
#%% Run Crime
crime_model = create_train_model('Crime')
crime_model.save('crime_model.h5')
#%% Run Romance
romance_model = create_train_model('Romance')
romance_model.save('romance_model.h5')

