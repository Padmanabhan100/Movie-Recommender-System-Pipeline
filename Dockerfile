FROM python:3.9.13-slim-buster

# Run update command
RUN apt update -y

# Gets GCC compiler and essential tools
RUN apt install build-essential -y


# Set app as working directory
WORKDIR /app

# Move all content to the working directory
COPY . /app

# install dependencies  
RUN pip install --upgrade pip  

# Install the requirements
RUN pip install -r requirements.txt

# Expose at port 8080. 
EXPOSE 8080

# Run the web app
CMD ["python", "movieflix/manage.py", "runserver", "0.0.0.0:8080"]