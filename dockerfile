FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY requirements.txt /tmp
# RUN pip install --upgrade pip
# RUN apt-get update -y && apt-get upgrade -y

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /tmp/requirements.txt
WORKDIR /app
COPY ./app .

EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]