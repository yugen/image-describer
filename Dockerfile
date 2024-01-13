# syntax=docker/dockerfile:1
# Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon

FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip \
    pip install -r requirements.txt
COPY . /code/