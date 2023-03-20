import logging
import json
import requests
import sys

# Set up logging
logging.basicConfig(filename='./linode_cost.log', level=logging.DEBUG)

def get_pricing():

    pricing_data = {}

    url = "https://api.linode.com/v4/linode/types"

    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        for i in json_data['data']:
            id = i['id']
            hourly = i['price']['hourly']
            monthly = i['price']['monthly']
            pricing_data[id] = {}
            pricing_data[id]['hourly'] = hourly
            pricing_data[id]['monthly'] = monthly
        return pricing_data
    else:
        logging.info("Request failed.")
        logging.info("Status Code was ", response.status_code)
        logging.info("Response was ", response.content)
        sys.exit("get_pricing() failed")

def get_instances(api_token):

    url = "https://api.linode.com/v4/linode/instances"
    headers = { 
        'Authorization': 'Bearer ' + api_token 
        }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        instance_data = response.json()
        return instance_data
    else:
        logging.info("Request failed.")
        logging.info("Status Code was ", response.status_code)
        logging.info("Response was ", response.content)
        sys.exit("get_instances() failed")

def instance_details(instance_id, api_token):

    url = "https://api.linode.com/v4/linode/instances/" + str(instance_id)
    headers = { 
        'Authorization': 'Bearer ' + api_token 
        }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        detail_data = response.json()
        return detail_data

my_hourly_price = 0
my_monthly_price = 0
print("Input your API token: ")
my_token = input()
print("Got it! Getting current instance pricing...")
my_pricing = get_pricing()
print("Done! Getting a list of instances...")
my_instances = get_instances(my_token)
print("Done! Getting details on", len(my_instances['data']), "instances...")
for i in my_instances['data']:
    my_details = instance_details(i['id'],my_token)
    my_type = my_details['type']
    my_hourly_price = my_hourly_price + my_pricing[my_type]['hourly']
    my_monthly_price = my_monthly_price + my_pricing[my_type]['monthly']
print ("Done!")
print("Your current hourly run rate for instances  is: $", round(my_hourly_price,2))
print("Your monthly run rate for instances is: $", round(my_monthly_price,2))

# Log activity
logging.info("Complete!")