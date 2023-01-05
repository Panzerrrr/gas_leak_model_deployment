FROM python:3.8.2-slim

WORKDIR /usr/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN mkdir /usr/app/data
RUN mkdir /usr/app/models
RUN mkdir /usr/app/assets
RUN apt-get update
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0
COPY app ./
COPY models /usr/app/models
COPY assets /usr/app/assets


CMD ["sh", "-c", "streamlit run --server.port $PORT /usr/app/app.py --logger.level=debug"]