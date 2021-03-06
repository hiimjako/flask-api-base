# flask-api-base

A base template for flask API with: JWT atuh, postgres, migrations and users models

# Develop

1. Fill the .env file with the demo:

   `cp .env.sample .env`

2. Install docker for development:

   `docker-compose -f docker-compose-dev.yml up`

   To develop also for local machine install pipenv environment:

   `pipenv install -d`

3. It is installed pre-commit, a package that runs lint and tests before commiting (can generate errors)

   `pre-commit install`

   Command that runs:

   - Code formatting with black:

     `black Api/ tests/`

   - Clean unused imports:

     `pycln Api/ tests/ -a`

     To avoid deleting unused inport use: `# noqa`

     e.g. `import not_used_import # noqa`

   To disable it run `pre-commit uninstall` (not recommended)

# Test api

`coverage run -m unittest discover`

To see coverage (after running the tests)

`coverage report -m` or `coverage html`

To ignore coverage in not coverable lines: `# pragma: no cover`

Run test without coverage package

`python unittest`

# Set linter

Vscode:

`python formatting provider` -> `black`

# Deploy

- Deploy docker for production:

  `docker-compose up -d`
