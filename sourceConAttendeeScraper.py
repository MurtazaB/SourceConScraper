# Needed for Charles Proxy
from requests import Session

# Needed for basic requests
import requests
import json

# Needed for exporting attendee info to a csv
import csv

# Additional cipher needed for making these secure requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':ADH-AES256-SHA384'

# Setup for Charles Proxy
session = Session()
session.verify = "charles-ssl-proxying-certificate.pem"

# Headers scraped from Whova
headers = {
    'Host': 'whova.com',
    'Accept': '*/*',
    'User-Agent': 'Whova/200 (iPhone; iOS 10.2.1; Scale/2.00)',
    'Accept-Language': 'en-US;q=1',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYXV0aCIsImlzc3VlZF9hdCI6MTUzNjgxMjYzMCwidXNlcl9pZCI6Nzg1NjI4LCJlbWFpbCI6Im11cnRhemFAY2FyZWVyYmxpdHouaW8iLCJleHAiOjE1Mzc2NzY2MzB9.MRwFuR9iFVY6aXI8AUc52thhM88HqO_U76h90mpoclw',
}

# Parameters needed to make an attendee request
params = (
    ('api_version', '3'),
    ('event', 'sourc1_201809'),
    ('lang', 'en_US'),
)

# Making the request to get all attendees
response = requests.get('https://whova.com/event/attendees/v3/', headers=headers, params=params, verify=False)

# Turning the string response to json
all_attendees = json.loads(response.text)

# Parsing the full json result to just get a list of attendees
attendees = all_attendees.get('result', {}).get('list', [])

# Empty list to store each attendees personal id (set in Whova upon account creation)
pids = []

# Going through each attendee to get their personal id and adding it to `pids`
for attendee in attendees:
    pids.append(attendee.get('pid').split('_')[-1])


# Empty list to store profiles of users (just names and linkedin urls)
profile_info = []

# Going through each personal id we found
for pid in pids:

    this_profile = {}

    # Setting new parameters for making a profile information request to Whova
    # Notice that we're filling in `pid` with the personal id of the user
    params = (
        ('api_version', '3'),
        ('event', 'sourc1_201809'),
        ('lang', 'en_US'),
        ('pid', pid),
        ('source', 'attendee_list__'),
        ('version', 'iphone_5.8.0'),
    )

    # Making the request to Whova and getting the result in json
    response = requests.get('https://whova.com/mobile/pipldetail2/', headers=headers, params=params, verify=False)
    result = json.loads(response.text)

    # Getting the person's name and adding it a `this_profile` variable
    name = result.get('result', {}).get('profile', {}).get('name')
    this_profile['name'] = name

    # 
    social_urls = result.get('result', {}).get('profile', {}).get('urlclass', {}).get('social', [])
    
    # Checking to see if this person has a LinkedIn URL
    # If so, we add it to the person's profile
    linkedin_url = ""
    for url in social_urls:
        if url.get('type') == 'LinkedIn':
            linkedin_url = url.get('url', '')

    this_profile['linkedin'] = linkedin_url

    profile_info.append(this_profile)


# Opening up a csv file and dropping all our parsed information in it
with open('whova_info.csv', 'w', newline='') as csvfile:
    whova_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    whova_writer.writerow(['name', 'linkedin'])
    
    for profile in profile_info:
        whova_writer.writerow([profile.get('name'), profile.get('linkedin')])

print("All done -- check for the file 'whova_info.csv' to get the scraped information!")
print("Be sure to check out www.careerblitz.io/recruiting for more awesome recruiting tools!")


