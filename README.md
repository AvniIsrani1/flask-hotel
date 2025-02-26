INITIAL SETUP

CREATE VIRTUAL ENVIRONMENT
    python -m venv .venv   

ACTIVATE VIRTUAL ENVIRONMENT
    .venv\Scripts\activate

pip install flask
pip install flask-mysqldb


TO RUN
flask --app hotel run --debug