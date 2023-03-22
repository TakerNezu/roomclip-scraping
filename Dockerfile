FROM python:3.9

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 -
RUN mkdir /app
ADD ./roomclip-scraping /roomclip-scraping
RUN cd /roomclip-scraping && poetry install
