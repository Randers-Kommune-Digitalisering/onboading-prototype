FROM node:14-alpine AS frontend

WORKDIR /app

COPY vue/package*.json ./vue/
RUN cd vue && npm install

COPY vue/ ./vue/
RUN cd vue && npm run build

RUN cp -r vue/dist dist

RUN rm -rf vue

FROM python:3.10-alpine AS backend

WORKDIR /app

RUN apk update
RUN apk add musl-dev gcc libpq-dev mariadb-connector-c-dev postgresql-dev python3-dev

COPY python/src/requirements.txt ./python/src/
RUN pip install -r python/src/requirements.txt

COPY python/ ./python/

COPY --from=frontend /app/dist /app/frontend

EXPOSE 8000
CMD ["python", "python/src/main.py"]