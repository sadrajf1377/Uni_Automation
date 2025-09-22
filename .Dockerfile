FROM python:3.11.4-alpine

WORKDIR /app
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV PATH=".PY/BIN/:$PATH"

COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . /app



