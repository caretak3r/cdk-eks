# Kubernetes Fargate does not support arm64
# Alpine Linux is lightweight ubuntu distribution
FROM registry.silent.engineer/amd64/python:3.11.7-alpine3.19@sha256:6aa46819a8ff43850e52f5ac59545b50c6d37ebd3430080421582af362afec97

# Create directory for the app user
RUN mkdir -p /home/app

# Create the system group app and
RUN addgroup -S app
# Create app user assigned to the app group
RUN adduser -S -G app app

# Create the home directory
ENV HOME=/home/app
ENV APP_HOME=/home/app/web


RUN mkdir $APP_HOME

# Set the working directory in the docker container
WORKDIR $APP_HOME

# Install dependencies
# What is the alpine equivalent to build-essential?: 
# https://github.com/gliderlabs/docker-alpine/issues/24
# RUN apt-get update && apt-get install -y build-essential

# Copy requirements.txt
COPY requirements.txt requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt



# Copy project
COPY . $APP_HOME

# Chown all the files to the app user
RUN chown -R app:app $APP_HOME

# Change to the app user
USER app

# Expose the port the app runs in
EXPOSE 5000
ENV PYTHONUNBUFFERED=0

# Define the command to start the container
CMD ["python3", "app/app.py"]