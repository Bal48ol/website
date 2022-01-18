#-alpine
FROM python:3.8
#app
WORKDIR /website
#app, copy
ADD . /website
#EXPOSE 5000
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
