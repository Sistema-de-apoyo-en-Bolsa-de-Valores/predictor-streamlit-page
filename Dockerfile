FROM python:3.11 
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY app.py /app/app.py
CMD ["streamlit", "run", "app.py"]