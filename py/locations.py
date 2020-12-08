import sys
import json
import requests
from bs4 import BeautifulSoup


site_types = {
    'rv' : '31',
    'group' : '33',
    'cabin' : '101',
    'dispersed' : '34'
}

camp_site_urls = []
camp_site_titles = []
camp_site_lat_lon = []
all_camp_site_urls = []
camp_site_locations = []
site_url_root = 'https://www.fs.usda.gov'
site_url_path = '/activity/mtnf/recreation/camping-cabins/?recid=21644&actid='

# build list of all campsite page urls
def get_all_site_urls(site_type):
    try:
        all_sites = requests.get(site_url_root + site_url_path + site_type)
        all_sites_soup = BeautifulSoup(all_sites.text, 'html.parser')
        all_sites.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    site_links = all_sites_soup.find_all("li", {"style": ["clear:both;margin:0 0 0 25px", "clear:both;margin:0 0 0 50px"]})
    for link in site_links:
        links = link.findChildren("a" , recursive=False)
        for l in links:
            camp_site_urls.append(site_url_root + l.get('href'))
    make_site_soup(camp_site_urls, site_type) 
 
# scrape name, lat, lon for each campsite
def make_site_soup(camp_site_urls, site_type):
    for url in camp_site_urls:
        try:
            single_site = requests.get(url)
            single_site_soup = BeautifulSoup(single_site.text, 'html.parser')  
            single_site.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)   
        camp_site_titles.append(single_site_soup.title.text.split('-')[1].strip(' \t\n\r\xa0'))
        lat_lon = single_site_soup.find_all("div", {"style": ["font-size:0.85em;position:relative;float:right;margin-right:12px"]})    
        for i in lat_lon: 
            camp_site_locations.append(float(i.text.strip(' \t\n\r\xa0')))
    camp_site_lat_lon = [list(x) for x in zip(camp_site_titles, camp_site_locations[:-1:2], camp_site_locations[1::2])]
    camp_site_json = json.dumps(camp_site_lat_lon)
    with open('../data/' + sys.argv[1] + '.json', 'w') as outfile:
        json.dump(camp_site_json, outfile)

def check_input():
    if len(sys.argv) > 1 and sys.argv[1] in site_types.keys():
        site_type = site_types.get(sys.argv[1])
        get_all_site_urls(site_type)
    else:
        print('Invalid or missing argument.')   
        
check_input()