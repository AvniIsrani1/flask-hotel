INITIAL SETUP

CREATE VIRTUAL ENVIRONMENT
    python -m venv .venv   

ACTIVATE VIRTUAL ENVIRONMENT
    .venv\Scripts\activate

pip install flask
pip install flask-mysqldb
pip install flask-sqlalchemy
pip install flask-admin
pip install pymysql
pip install boto3




TO RUN
flask --app hotel run --debug