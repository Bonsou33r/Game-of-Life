# Use Python slim image for smaller size while maintaining compatibility
FROM python:3.11-slim

# Install system dependencies for pygame and GUI support
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy game files
COPY game_of_life_pygame.py .
COPY launcher.py .

# Set environment variables for GUI support
ENV DISPLAY=:0
ENV SDL_VIDEODRIVER=x11

# Create a non-root user for security
RUN useradd -m gameuser && chown -R gameuser:gameuser /app
USER gameuser

# Set the entry point to run the launcher
CMD ["python", "launcher.py"]
