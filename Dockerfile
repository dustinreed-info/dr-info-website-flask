FROM python:3.9-slim
ADD src requirements.txt /src/ 
ADD tests /src/tests/
WORKDIR /src
RUN pip install -r requirements.txt && py.test
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]