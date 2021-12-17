# A good order will make compose faster
# Create multple stages (from keyword) to divide work, and put only the 
#   needed file after build -> in js project
# TODO: docker scan

FROM python:3.9 as base

RUN apt-get -y update
RUN apt-get -y install gcc build-essential libpq-dev

# create a non root user
RUN groupadd -r dev && useradd -m -g dev dev
WORKDIR /home/dev/app
COPY . .
RUN mkdir -p "/uploads" 

COPY requirements.txt ./
RUN echo "gunicorn" >> requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# switch to dev user
RUN chown -R dev:dev /home/dev/app
USER dev

ENTRYPOINT ["gunicorn", "-w", "3", "Api:create_app('production')", "2", "-b :5000"]
