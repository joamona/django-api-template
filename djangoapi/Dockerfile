# pull official base image
FROM python:3.12-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
#pango es una dependencia de weasyprint
RUN apk update && apk add postgresql-dev gcc musl-dev libpq-dev wget pango  \
     gdal-dev geos-dev proj-dev gcc musl-dev \
     libffi-dev python3-dev zlib-dev jpeg-dev freetype-dev

RUN apk add --update --no-cache --virtual .tmp-build-deps \
     libc-dev linux-headers 

# install dependencies
RUN pip install --upgrade pip


COPY ./requirements.txt .

RUN pip3 install -r requirements.txt


# copy project
COPY . .
#RUN chmod +x migrate.sh
RUN chmod +x initdb.sh

#RUN echo "Collect static files"
#RUN python manage.py collectstatic --noinput

#ESTO NO SE PUEDE HACER AQUÍ, HAY QUE ENTRAR EN EN MODO INTERACTIVO Y HACERLO A MANO
#CUANDO CREAS DE NUEVO IMÁGENES Y CONTENEDORES, LA BBDD SE CONSERVA