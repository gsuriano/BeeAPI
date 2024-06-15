FROM python:3.11-alpine

WORKDIR /app

COPY . .    

RUN pip install -r requirements.txt

EXPOSE 5000

# Define environment variable
ENV FLASK_APP=main.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]  
