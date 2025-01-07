FROM python:3.10-slim

WORKDIR /app

# Install Poetry and dependencies
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get install -y build-essential libpq-dev

ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry configuration files
COPY pyproject.toml /app/
COPY poetry.lock /app/

# Install dependencies via Poetry and generate requirements.txt
RUN poetry export -f requirements.txt --without-hashes > requirements.txt

# Install dependencies using pip directly
RUN pip install -r requirements.txt

# Debug step: List installed packages to confirm if google-cloud is installed
RUN pip list

# Copy the application code and the config file
COPY day_2/components /app/day_2/components
COPY day_2/iris_pipeline.py /app/
COPY config.py /app/

# Expose port 8080 for Cloud Run
EXPOSE 8080

CMD ["python", "iris_pipeline.py"]
