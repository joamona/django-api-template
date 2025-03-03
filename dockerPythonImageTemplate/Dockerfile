# pull official base image
FROM python:3.12-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2, and geodjango dependencies in the Linux system
RUN apk update && apk add postgresql-dev g++ gcc musl-dev libpq-dev wget pango gdal-dev geos-dev proj-dev gcc musl-dev \
     libffi-dev python3-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
     libc-dev linux-headers 

# Update pip to the latest version
RUN pip install --upgrade pip

# Copy the requirements file to the working directory
COPY ./requirements.txt .

# Install the Python requirements
RUN pip3 install -r requirements.txt

# Copy the current directory, that contains the Django 
# API into the image at /usr/src/app
COPY . .

# Change the permissions of the initdb.sh file
# This file is used to create the supeuser and migrate the database
RUN chmod +x initdb.sh
