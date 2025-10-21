FROM python:3.13.7

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy project source code
COPY . .

# Run the FastAPI app
CMD ["python", "run.py"]