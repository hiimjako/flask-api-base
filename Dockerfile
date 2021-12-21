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

# RUN pip install --no-cache-dir -r requirements.txt
# RUN pipenv install $(test "$FLASK_ENV" == production || echo "--dev") --system --deploy --ignore-pipfile
RUN pip install pipenv  \
    && pipenv lock --keep-outdated --requirements > requirements.txt \
    && echo "gunicorn" >> requirements.txt \
    && pip install -r requirements.txt

# switch to dev user
RUN chown -R dev:dev /home/dev/app
USER dev

ENTRYPOINT ["gunicorn", "-w", "3", "Api:create_app()", "2", "-b :5000"]
