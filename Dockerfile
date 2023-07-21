FROM python:3.9-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y wkhtmltopdf libsndfile1
RUN pip3 install pysoundfile
RUN pip3 install soundfile
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "bot" ]