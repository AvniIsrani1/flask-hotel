INITIAL SETUP

CREATE VIRTUAL ENVIRONMENT
    python -m venv .venv   

ACTIVATE VIRTUAL ENVIRONMENT
    .venv\Scripts\activate

pip install flask
pip install flask-mysqldb
pip install flask-sqlalchemy
pip install flask-admin
pip install flask-mail     

pip install pymysql
pip install boto3
pip install flask-cors 
pip install transformers
pip install torch
pip install huggingface_hub
pip install pandas
pip install langchain-huggingface
pip install langchain-community
pip install faiss-cpu

TO RUN
flask --app hotel run --debug