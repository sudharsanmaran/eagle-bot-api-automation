FROM python:3.11.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements /app/requirements

RUN pip3 install --upgrade pip && pip3 install --upgrade setuptools

RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . /app

RUN chmod +x alembic_upgrade.sh

RUN chmod +x start.sh

# CMD ["bash","alembic_upgrade.sh"]

CMD ["bash","start.sh"]