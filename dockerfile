FROM python:alpine3.12  

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN python -m venv gaspricesenv
RUN apk update && apk add libpq
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install psycopg2
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script and other necessary files
COPY app/gasprices.py ./  
COPY app/scheduler.py ./


# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Run your script
CMD ["python", "scheduler.py"] 