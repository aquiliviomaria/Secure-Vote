FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*


    
# Instalar dependências Python
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "sv_config.wsgi"]