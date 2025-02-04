
import psycopg2
import streamlit as st
import random
import os
import pandas as pd
import numpy as np
import operator

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
def calc_similarity(df_GT100_v2):
        # Create user-item matrix
        matrix = df_GT100_v2.pivot_table(index='titulo', columns='user_id', values='rating')
        matrix_norm = matrix.subtract(matrix.mean(axis=1), axis = 0)
        # Item similarity matrix using Pearson correlation
        item_similarity = matrix_norm.T.corr()
        return matrix_norm, item_similarity

def item_based_rec(item_similarity, picked_userid, matrix_norm, number_of_similar_items=5, number_of_recommendations =3):
    # books that the target user has not watched
    picked_userid_unwatched = pd.DataFrame(matrix_norm[picked_userid].isna()).reset_index()
    picked_userid_unwatched = picked_userid_unwatched[picked_userid_unwatched[picked_userid]==True]['titulo'].values.tolist()
    # books that the target user has watched

    picked_userid_watched = pd.DataFrame(matrix_norm[picked_userid].dropna(axis=0, how='all')\
                            .sort_values(ascending=False))\
                            .reset_index()\
                            .rename(columns={picked_userid:'rating'})
    # Dictionary to save the unwatched book and predicted rating pair
    rating_prediction ={}  
    # Loop through unwatched books          
    for picked_book in picked_userid_unwatched: 
        # Calculate the similarity score of the picked book iwth other books
        picked_book_similarity_score = item_similarity[[picked_book]].reset_index().rename(columns={picked_book:'similarity_score'})
        # Rank the similarities between the picked user watched book and the picked unwatched book.
        picked_userid_watched_similarity = pd.merge(left=picked_userid_watched, 
                                                    right=picked_book_similarity_score, 
                                                    on='titulo', 
                                                    how='inner')\
                                            .sort_values('similarity_score', ascending=False)[:number_of_similar_items]
        # Calculate the predicted rating using weighted average of similarity scores and the ratings from user 1
        predicted_rating = round(np.average(picked_userid_watched_similarity['rating'], 
                                            weights=picked_userid_watched_similarity['similarity_score']), 6)
        # Save the predicted rating in the dictionary
        rating_prediction[picked_book] = predicted_rating
    # Return the top recommended books
    return sorted(rating_prediction.items(), key=operator.itemgetter(1), reverse=True)[:number_of_recommendations]


def recommendation(item_similarity, user_id, matrix_norm, num_rec=3):
    rec = item_based_rec(item_similarity, user_id, matrix_norm, num_rec)
    print('\n\n\n* * * R E C O M E N D A C A O')
    # st.write("The following list won’t indent no matter what I try:")
    # for i in rec:
    #     print(i)
    #     # st.markdown(f"- {i}")
    return rec


def main():
    # path = os.getcwd() + '\common'
    # conn = create_connection(path+'\pythonsqlite.db')
    st.title("Recomendação de Leituras")
    st.markdown("Antes de avançarmos com a recomendação, precisamos que você nos indique pelo menos **3** livros do seu agrado.")
    st.markdown("Vamos começar?")
    
    emoji_list = ['🎉', '❤', '📖','📚']
        
    input_text_1 = ''
    input_text_2 = ''
    input_text_3 = ''
    book_1 = ''
    book_2 = ''
    book_3 = ''

    # if st.button('Bora!'):
    # print('PATH:',path + URI_SQLITE_DB)
    # st.write(path + URI_SQLITE_DB)
    conn = get_connection()
    print('CONN:',conn)
    input_text_1 = st.text_input('Livro 1',help='Digite o título de um livro que você tenha gostado.')
    if input_text_1:
        book_resp = select_search(conn, input_text_1)
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
        url = 'https://github.com/brendasalenave/recomendacao-livros/blob/main/df_GT100.parquet?raw=true'
        df_GT100 = pd.read_parquet(url, engine='auto')

        user_id = df_GT100.user_id.max()+1 # cria novo usuario
        print('user id: {user_id}')
        df_book_1 = df_GT100[(df_GT100.titulo == book_1[0]) & (df_GT100.autor == book_1[1])].iloc[[0]]
        df_book_2 = df_GT100[(df_GT100.titulo == book_2[0]) & (df_GT100.autor == book_2[1])].iloc[[0]]
        df_book_3 = df_GT100[(df_GT100.titulo == book_3[0]) & (df_GT100.autor == book_3[1])].iloc[[0]]
        df_books = pd.concat([df_book_1, df_book_2, df_book_3])
        
        df_books['rating'] = [5.0, 5.0, 5.0]
        df_books['user_id'] = [user_id, user_id, user_id]

        df_GT100_v2 = pd.concat([df_GT100, df_books])

        matrix_norm, item_similarity = calc_similarity(df_GT100_v2)
        rec = st.button('Recomendar')
        if rec:
            rec_list = recommendation(item_similarity, user_id, matrix_norm, num_rec=10)
            st.header("Livros recomendados para você:")
            for i in rec_list:
                book_resp = select_search(conn, i[0])
                # if len(book_resp) > 1: #se encontrar mais de um livro
                #     book = [file_selector(book_resp)]
                # else:
                book = [book_resp[0]]
                txt = book[0][0] +' - '+ book[0][1]
                st.markdown(f'- {txt}')

if __name__ == '__main__':
    main()