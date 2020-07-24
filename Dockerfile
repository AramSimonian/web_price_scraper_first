FROM joyzoursky/python-chromedriver

#upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip

#creating app directory in container (linux machine)
RUN mkdir c:\home\web_scraper

#copying main.py from local directory to container's app directory
COPY main.py /home/web_scraper/main.py
COPY requirements.txt /home/web_scraper/requirements.txt
COPY price_links.csv /home/web_scraper/price_links.csv

#updating project references
#CMD pip install bs4
#CMD pip install selenium
#CMD pip install urllib3
RUN pip install -r /home/web_scraper/requirements.txt

#running main.py in container
CMD python /home/web_scraper/main.py