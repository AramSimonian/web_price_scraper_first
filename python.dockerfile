FROM python:3.9
LABEL author="Aram Simonian"

WORKDIR /app/
# RUN mkdir /app/output

# debian
# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
RUN unzip /tmp/chromedriver.zip chromedriver -d /app/

# set display port to avoid crash
ENV DISPLAY=:99
ENV PORT=5050
# EXPOSE $PORT
ENV PYTHONUNBUFFERED=1

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install --upgrade selenium

# install Beautiful Soup
RUN pip install bs4

# Copy files required to run the program
COPY ./main.py /app/
COPY ./price_links.csv /app/

# Execute the program
#CMD python3 /app/main.py
ENTRYPOINT [ "python3", "main.py" ]