FROM python:latest
RUN pip install --upgrade pip

COPY "./code/" "/app"
WORKDIR /app

COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt
#RUN pip3 install opencv-python


CMD [ "python","-u", "run.py" ]