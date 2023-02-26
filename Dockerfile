FROM python:3.9-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y wkhtmltopdf
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "bot" ]