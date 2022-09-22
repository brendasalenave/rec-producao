FROM python:3.8

# EXPOSE 8501

WORKDIR /projeto_recomendacao

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . . 

CMD streamlit run ./0_📚_Página_principal.py --server.port $PORT