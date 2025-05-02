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
pip install reportlab 
pip install qrcode[pil]    
pip install plotly

pip install pytest
pip install pytest-flask

TO RUN
flask --app hotel run --debug


FOR DOCUMENTATION
pip install sphinx sphinx-autodoc-typehints

sphinx-quickstart docs
    y, HOTEL, Git Good, 1.0.0, en

add this to conf.py:
    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.napoleon', 
        'sphinx.ext.viewcode',  
    ]

    import os
    import sys
    sys.path.insert(0, os.path.abspath('../..'))

then create/edit index.rst file: docs/source/index.rst

    Welcome to HOTEL's documentation!
    =================================

    .. toctree::
    :maxdepth: 2
    :caption: Contents:

    modules

    Indices and tables
    ===================================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

then: 
    cd docs
    sphinx-apidoc -o source/ ../HOTEL/
    sphinx-build -b html source build/html

then:
    Go into index.html and run the live server
