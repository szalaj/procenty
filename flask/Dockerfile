# start by pulling the python image
FROM python:3.8-slim

EXPOSE 5000/tcp

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip


# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app
