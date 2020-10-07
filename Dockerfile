# For more information, please refer to https://aka.ms/vscode-docker-python
FROM ubuntu:18.04

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Update and install dependencies
RUN apt-get -y update && \
    apt-get -y install ffmpeg \
    python3 \
    python3-pip

COPY . /music_bot
WORKDIR /music_bot

# Install pip requirements
RUN python3 -m pip install -r requirements.txt

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd bot && chown -R bot /music_bot
USER bot

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python3", "-m", "music_bot", "config.ini"]
