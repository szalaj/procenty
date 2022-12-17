# start by pulling the python image
FROM python:3.8-buster

EXPOSE 5000/tcp


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

COPY requirements.txt .


RUN python -m pip install --upgrade pip

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . /app



CMD [ "python", "app.py" ]
