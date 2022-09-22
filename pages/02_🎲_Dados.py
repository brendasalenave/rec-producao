import streamlit as st
from streamlit.logger import get_logger
import os

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="🎲",
    )

    st.write("# Dados 🎲")

    # st.sidebar.success("Select a demo above.")

    st.image('./img/skoob.png',width=70)
    
    st.markdown(
        """
       No desenvolvimento desse projeto utilizamos dados do [Skoob](https://www.skoob.com.br). O Skoob é atualmente a maior rede social do Brasil voltada a livros. Esta rede social funciona tal qual uma estante virtual, onde é possível organizar leituras realizadas e pretendidas, bem como compartilhar resenhas e avaliar livros. Adicionalmente, esta plataforma também possibilita fazer trocas de livros, participar de sorteios e ganhar cortesias.
       
       Entretanto não foram encontrados datasets disponíveis que atendessem as necessidades do projeto.
       Assim, foi desenvolvido um script em Python para extração de um conjunto de dados como desejado.
       - Id do livro
       - Autor
       - Título
       - Sinopse
       - Avaliação (nota)
       - Total de avaliações
       - Gênero literário
       - Data lançamento
       - Leram
       - Lendo
       - Querem ler
       - Relendo
       - Abandonos
       - Total de Resenhas
       - Resenha
         - Autor
         - Título
         - Texto da resenha
         - Avaliação individual (nota)

       ### Pré processamento
       Inicialmente o conjunto de dados extraídos possuia:

       - Total de livros: 76.981
       - Total de autores: 33.411
       - Total de resenhas: 1.078.959

       Entretanto parte desses dados eram de livros em inglês, que não estavam no escopo do projeto. Assim, fizemos uma filtragem por idioma da descrição do livro buscando manter apenas obras escritas em português.

       - Total de livros: 49.806
       - Total de autores: 24.394 
       - Total de resenhas: 758.177

    Outra etapa importante do pré processamento se derivou da observação de dados faltantes. Diversos livros não continham informações relacionadas ao gênero literário.
    """
    )
    st.image('./img/dados_faltantes.png')
    st.markdown(
    """
    Essa questão foi resolvida de forma manual, preenchendo o gênero para os livros que não tinham essa informação disponível.
    """
    )

    st.image('./img/genero.png')

    st.markdown(
    """
    ### Dashboard
    
    Explore os dados: [Dashboard](https://app.powerbi.com/view?r=eyJrIjoiMjVmZjBlYjMtOTI3Ny00ZWNmLTg3OTQtMzQxNDBkMWE3ZGZhIiwidCI6IjU3NjY5YTY4LWFhODctNDcyYS1iZWFkLTQ1MjU4NGRjMzkzYiJ9)


    """
    )


if __name__ == "__main__":
    run()
