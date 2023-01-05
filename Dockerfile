FROM python:3.8.2-slim

WORKDIR /usr/app/src

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN mkdir /usr/app/src/data
RUN mkdir /usr/app/src/models
RUN mkdir /usr/app/src/assets
RUN apt-get update
RUN apt-get install -y --no-install-recommends libgl1 libglib2.0-0
COPY app ./
COPY models /usr/app/src/models

CMD ["sh", "-c", "streamlit run --server.port $PORT /usr/app/src/app.py --logger.level=debug"]