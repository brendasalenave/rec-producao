import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Recomendação de Livros",
        page_icon="	☕",
    )
    st.write('###### DATA SCIENCE & MACHINE LEARNING')

    st.title('Recomendação de Livros 📚')
    # st.image('./tera.jpg',width=70)

    # st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        #### Objetivo
        Proporcionar ao usuário recomendações de leitura conforme sua preferência no momento através de um sistema de recomendação capaz de sugerir com base em alguns parâmetros informados pelo usuário no momento da recomendação (e.g., livros lidos previamente similares ao que se pretende), quais livros poderiam ser escolhidos como sua próxima leitura. 

        Utilizar descrição e resenha de livros como base da recomendação na busca novas por experiências literárias.

    """
    )


if __name__ == "__main__":
    run()