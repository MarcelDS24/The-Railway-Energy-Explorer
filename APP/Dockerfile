# Dockerfile for Streamlit App
FROM python:3.13-slim

# Install uv
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .

# Use uv to install dependencies with proper system flag
RUN uv pip install --system -r requirements.txt

# Copy the entire app directory
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
