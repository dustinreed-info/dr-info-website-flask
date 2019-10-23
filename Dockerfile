FROM python:3.6-slim
ADD . /application
WORKDIR /application
RUN pip install flask python-dotenv flask-wtf gunicorn
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "application"]