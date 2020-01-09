#!/usr/bin/env python3
'''Scraper using BeautifulSoup'''
from datetime import timedelta, datetime
import requests
from bs4 import BeautifulSoup

def write_to_csv(date_outcome_dict):
    '''Writes output to CSV file'''
    with open('Example_output.csv', 'w') as file:
        for key in date_outcome_dict:
            file.write("%s,%s\n"%(key, date_outcome_dict[key]))

def get_all_dates(year):
    ''' Initialize the dictionary with all the dates from 1Jan2019 to 31Jan2019'''
    date_outcome_dict = {}
    sdate = datetime.strptime('01-01-' + str(year), '%d-%m-%Y')
    edate = datetime.strptime('31-12-' + str(year), '%d-%m-%Y')
    step = timedelta(days=1)
    while sdate <= edate:
        iso_format = sdate.isoformat()
        date_outcome_dict[iso_format] = 0
        sdate += step
    return date_outcome_dict

def scrape_data(url, year):
    ''' Scrapes table from the given URL for given year '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.find(id='mw-content-text').find('table',
                                                class_='wikitable').find('tbody').find_all('tr')
    date_outcome_dict = get_all_dates(year)
    for i in range(4, len(rows)):
        table_data = rows[i].find('td')
        if table_data is not None and table_data.has_attr('rowspan'):
            num_payloads = int(table_data['rowspan'])
            date = rows[i].find('span', class_='nowrap')
            [s.extract() for s in date('sup')]
            flag = False
            for j in range(1, num_payloads):
                subrows = rows[i + j].find_all('td')
                if len(subrows) >= 5:
                    outcome = subrows[5]
                    [s.extract() for s in outcome('sup')]
                    if outcome.text.strip() in ['Successful', 'Operational', 'En Route']:
                        flag = True
                        break
            if flag:
                fmt_date = datetime.strptime(date.text.strip()
                                             + ' ' + str(year), '%d %B %Y').isoformat()
                date_outcome_dict[fmt_date] += 1
            i = i + num_payloads
    return date_outcome_dict

def main():
    '''Main method'''
    print(f"Starting scraping data from wikipedia")
    url = 'https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches'
    date_outcome_dict = scrape_data(url, 2019)
    write_to_csv(date_outcome_dict)
    print(f"Scraping done, check result in outcome.csv")

if __name__ == "__main__":
    main()
