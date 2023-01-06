FROM python:3.8.2-slim

WORKDIR /usr

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN mkdir data
RUN apt-get update
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0
COPY app app
COPY models models
COPY assets assets


CMD ["sh", "-c", "streamlit run --server.port $PORT /usr/app/app.py --logger.level=debug"]