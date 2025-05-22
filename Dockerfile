FROM python:3.13
WORKDIR /app
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libx11-xcb1 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libatk1.0-0 \
    libasound2 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install firefox
CMD ["python", "main.py"]