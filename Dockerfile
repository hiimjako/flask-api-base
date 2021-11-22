# A good order will make compose faster
# Create multple stages (from keyword) to divide work, and put only the 
#   needed file after build -> in js project
# TODO: docker scan

FROM python:3.9 as base

WORKDIR /app

# create a non root user
RUN groupadd -r dev && useradd -g dev dev
RUN chown -R dev:dev /app
# switch to dev user
USER dev

RUN mkdir "/uploads" 

RUN apt-get -y update
RUN apt-get -y install gcc build-essential libpq-dev

COPY requirements.txt ./
RUN echo "gunicorn" >> requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
ENTRYPOINT ["gunicorn", "-w", "3", "OpenDrive:create_app('production')", "2", "-b :5000"]
