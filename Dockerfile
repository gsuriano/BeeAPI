FROM python:3.11-alpine

WORKDIR /app

COPY . .    

RUN pip install -r requirements.txt

EXPOSE 5000

# Define environment variable
ENV FLASK_APP=main.py
ENV URL_API="https://api.opensensemap.org/boxes/"

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]  
