Cloudy
-----


To start clone the repository in a file::

	git clone git@github.com:maurope/cloudy.git

Then, start a new environment using python version 3.12::

	python3.12 -m venv venv

Initialize this environment::

	source venv/bin/activate

Install requirements.txt and download spacy models for english and spanish::

	pip install -r requirements.txt && python3 -m spacy download en_core_web_sm -m spacy download es_core_news_sm && python3 

