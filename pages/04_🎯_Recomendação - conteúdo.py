# import nltk
# nltk.download('stopwords')
import psycopg2
import streamlit as st
import random
import os
import pandas as pd
import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
import operator
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from nltk.corpus import stopwords
from spacy.lang.pt.stop_words import STOP_WORDS

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

def get_connection():
    """Put the connection in cache to reuse if path does not change between Streamlit reruns.
    NB : https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
    """
    conn = psycopg2.connect(os.getenv('DATABASE_URI'))
    return conn

def select_all_books(conn,book):
    cur = conn.cursor()
    query = f"SELECT * FROM book_tb WHERE title ILIKE \'%{book}%\'"
    print(query)
    cur.execute(query)

    rows = cur.fetchall()
    return rows

def select_author(conn, author_id):
    cur = conn.cursor()
    query = f"SELECT author_name FROM author_tb WHERE author_id={author_id}"
    print(query)
    cur.execute(query)

    rows = cur.fetchall()
    return rows[0][0]

def select_search(conn, query_search):
    cur = conn.cursor()
    query = f"""
    SELECT title, author_name
    FROM book_tb
    INNER JOIN author_tb ON book_tb.author_id=author_tb.author_id
    WHERE title ILIKE \'%{query_search}%\' OR author_name ILIKE \'%{query_search}%\';
    """
    cur.execute(query)
    rows = cur.fetchall()
    print(query)
    print(rows)
    return rows

def file_selector(books_list):
    selected = st.selectbox('Selecione o livro desejado:', ['']+books_list)
    if selected:
        emoji_list = ['🎉', '❤', '📖','📚', '✨']
        st.success('Ótima escolha! '+random.choice(emoji_list))
        return selected
    else:
        st.warning('No option is selected')

@st.cache
def calc_similarity(df_GT100_livros):
        customized_sw = ['pra'] 
        stop_words = list(set(stopwords.words('portuguese') + list(STOP_WORDS) + customized_sw))
        tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words=stop_words)
        tfidf_matrix = tf.fit_transform(df_GT100_livros['text'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        return cosine_sim

def getUserRead(df_GT100_livros, df_GT100_completo, user_id):
    BooksRead = df_GT100_completo[df_GT100_completo['user_id'] == user_id]['index'].to_list()
    print('O usuário selecionado leu os livros:\n')
    for posicao in range(len(df_GT100_livros.iloc[BooksRead])):
        autor, livro = df_GT100_livros.iloc[BooksRead][['autor', 'titulo']].values[posicao]
        print('{} - {}'.format(livro, autor))
    return BooksRead

def get_recommendations(df_GT100_livros, df_GT100_completo, user_id, cosine_sim):
    id = getUserRead(df_GT100_livros, df_GT100_completo, user_id) # id = book_index 
    
    sim_scores = []
    for idx in id:
        sim_scores = sim_scores + list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        book_ids = [i[0] for i in sim_scores]
    return df_GT100_livros.iloc[book_ids][len(id):]

@st.cache
def get_df_livros(df_GT100):
    df_GT100_livros = df_GT100.drop_duplicates(subset=['text']).reset_index(drop=True).reset_index().copy()
    df_GT100_livros = df_GT100_livros[['id', 'index', 'autor', 'titulo', 'text']]
    return df_GT100_livros


def main():
    st.title("Recomendação de Leituras")
    st.subheader('Abordagem: baseada em conteúdo')
    st.markdown("Antes de avançarmos com a recomendação, precisamos que você nos indique pelo menos **3** livros do seu agrado.")
    st.markdown("Vamos começar?")
    
    emoji_list = ['🎉', '❤', '📖','📚']
        
    input_text_1 = ''
    input_text_2 = ''
    input_text_3 = ''
    book_1 = ''
    book_2 = ''
    book_3 = ''

    conn = get_connection()
    input_text_1 = st.text_input('Livro 1',help='Digite o título de um livro que você tenha gostado.')
    if input_text_1:
        book_resp = select_search(conn, input_text_1)
        print('BOOK RESP:', book_resp)
        if not book_resp:
            st.error(f"Desculpe, não encontramos o livro '{input_text_1}' em nossa base de dados. Por favor tente buscar outro livro.", icon="😕")
            input_text_1 = None
            book = None
        
        elif len(book_resp) > 1: #se encontrar mais de um livro
            book = [file_selector(book_resp)]
        else:
            book = [book_resp[0]]
            st.success('Ótima escolha! '+random.choice(emoji_list))
        try:
            if book[0]:         
                txt = book[0][0] +' - '+ book[0][1]
                book_1 = (book[0][0],book[0][1])
                st.text(f'Livro selecionado: {txt}')
        except:
            pass

    if input_text_1:
        input_text_2 = st.text_input('Livro 2',help='Digite o título de outro livro que você tenha gostado.')
        if input_text_2:
            book_resp = select_search(conn, input_text_2)
            if not book_resp:
                st.error(f"Desculpe, não encontramos o livro '{input_text_2}' em nossa base de dados. Por favor tente buscar outro livro.", icon="😢")
                input_text_2 = None
                book = None
            elif len(book_resp) > 1: #se encontrar mais de um livro
                book = [file_selector(book_resp)]
            else:
                book = [book_resp[0]]
                st.success('Ótima escolha! '+random.choice(emoji_list))
            try:
                if book[0]:         
                    txt = book[0][0] +' - '+ book[0][1]
                    book_2 = (book[0][0],book[0][1])
                    st.text(f'Livro selecionado: {txt}')
            except:
                pass

    if input_text_2:
        input_text_3 = st.text_input('Livro 3', help='Digite o título de algum outro livro que você tenha gostado.')
        if input_text_3:
            book_resp = select_search(conn, input_text_3)
            if not book_resp:
                st.error(f"Desculpe, não encontramos o livro '{input_text_3}' em nossa base de dados. Por favor tente buscar outro livro.", icon="😩")
                input_text_2 = None
                book = None
            elif len(book_resp) > 1: #se encontrar mais de um livro
                book = [file_selector(book_resp)]
            else:
                print(book_resp)
                book = [book_resp[0]]
                st.success('Ótima escolha! '+random.choice(emoji_list))
            
            try: 
                if book[0]: 
                    txt = book[0][0] +' - '+ book[0][1]
                    book_3 = (book[0][0],book[0][1])
                    st.text(f'Livro selecionado: {txt}')
            except:
                pass

    if input_text_1 and input_text_2 and input_text_3:
        # df_GT100 = pd.read_csv('df_GT100.csv')
        # file_dir = os.path.dirname(__file__)
        # csv_path = os.path.join(file_dir,"..","common","df_GT100.parquet")
        url = 'https://github.com/brendasalenave/recomendacao-livros/blob/main/df_GT100.parquet?raw=true'
        df_GT100 = pd.read_parquet(url, engine='auto')

        df_GT100["generos_str"] = [' '.join(literal_eval(l)) for l in df_GT100["generos"]]
        df_GT100["text"] = df_GT100["autor"] + ' ' + df_GT100["titulo"] + ' ' + df_GT100["generos_str"] + ' ' + df_GT100['descricao']
        df_GT100["text"] = df_GT100["text"].str.lower()

        df_GT100_livros = get_df_livros(df_GT100)

        df_GT100_completo = pd.merge(df_GT100, df_GT100_livros[['id', 'index']], on='id')

        user_id = df_GT100_completo.user_id.max()+1 # cria novo usuario
        print('user id: {user_id}')
        df_book_1 = df_GT100_completo[(df_GT100_completo.titulo == book_1[0]) & (df_GT100_completo.autor == book_1[1])].iloc[[0]]
        df_book_2 = df_GT100_completo[(df_GT100_completo.titulo == book_2[0]) & (df_GT100_completo.autor == book_2[1])].iloc[[0]]
        df_book_3 = df_GT100_completo[(df_GT100_completo.titulo == book_3[0]) & (df_GT100_completo.autor == book_3[1])].iloc[[0]]
        df_books = pd.concat([df_book_1, df_book_2, df_book_3])
        
        df_books['user_id'] = [user_id, user_id, user_id]

        df_GT100_completo_v2 = pd.concat([df_GT100_completo, df_books])

        cosine_sim = calc_similarity(df_GT100_livros)

        rec = st.button('Recomendar')#, on_click=recommendation,args=(item_similarity,user_id, matrix_norm))
        if rec:
            st.header("Livros recomendados para você:")
            df_rec = get_recommendations(df_GT100_livros, df_GT100_completo_v2, user_id, cosine_sim).head(20)
            df_rec.drop_duplicates(inplace=True)

            i = 0
            for index, row in df_rec.iterrows():
                if i == 10:
                    break
                txt = row['titulo'] +' - '+ row['autor']
                st.markdown(f'- {txt}')
                i+=1


if __name__ == '__main__':
    main()