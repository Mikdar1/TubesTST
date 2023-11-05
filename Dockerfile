# Use an official Python runtime as the base image
FROM python:3

ADD healthcare.py .

COPY . /Belajar-api
WORKDIR /Belajar-api
RUN pip install scikit-learn numpy fastapi uvicorn pandas matplotlib
CMD ["uvicorn", "healthcare:app", "--host=0.0.0.0", "--port=80"]