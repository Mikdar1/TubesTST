# Use an official Python runtime as the base image
FROM python:3

ADD healthcare.py .

COPY . /TubesTST
WORKDIR /TubesTST
RUN apt-get -y update && apt-get install -y curl gnupg

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list  \ 
> /etc/apt/sources.list.d/mssql-release.list

RUN exit
RUN apt-get -y update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN pip install scikit-learn numpy fastapi uvicorn pandas matplotlib pyodbc python-multipart python-jose[cryptography] passlib[bcrypt]
CMD ["uvicorn", "healthcare:app", "--host=0.0.0.0", "--port=80"]