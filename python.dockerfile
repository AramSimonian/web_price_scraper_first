FROM python:3.9
LABEL author="Aram Simonian"

WORKDIR /app

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
#RUN pip install --upgrade pip

# install selenium
RUN pip3 install selenium

# install Beautiful Soup
RUN pip3 install bs4

# This should install all project references?
#RUN pip3 install -r /home/web_scraper/requirements.txt

# Copy files required to run the program
# RUN cp main.py
# RUN cp price_links.csv
COPY ./main.py /app/
COPY ./price_links.csv /app/


# Execute the program
#CMD python3 /app/main.py
ENTRYPOINT [ "/app/main.py" ]