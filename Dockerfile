# Base image
FROM python:3.10-slim

# Set timezone (India example)
ENV TZ=Asia/Kolkata
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean

# Set workdir
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Expose port (optional, if Render needs)
EXPOSE 8000

# Start bot
CMD ["python", "main.py"]
