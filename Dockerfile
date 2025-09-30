# Dockerfile, Python 3.12 slim image
FROM python:3.12-slim

#Working Directory
WORKDIR /app

#File copy
COPY app.py .

#Port exposure
EXPOSE 8000

#App excution
CMD ["python", "app.py"]
