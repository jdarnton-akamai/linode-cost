import logging
import json
import requests
import sys
import datetime

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
    else:
        logging.info("Request failed.")
        logging.info("Status Code was ", response.status_code)
        logging.info("Response was ", response.content)
        sys.exit("instance_details() failed")

def transfer_details(api_token):

    url = "https://api.linode.com/v4/account/transfer"
    headers = { 
        'Authorization': 'Bearer ' + api_token 
        }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        transfer_data = response.json()
        return transfer_data
    else:
        logging.info("Request failed.")
        logging.info("Status Code was ", response.status_code)
        logging.info("Response was ", response.content)
        sys.exit("transfer_details() failed")

def percent_month_complete():

    today = datetime.date.today()
    days_in_month = datetime.date(today.year, today.month+1, 1) - datetime.date(today.year, today.month, 1)
    percent_complete = round((today.day / days_in_month.days),2)
    return percent_complete

my_hourly_price = 0
my_monthly_price = 0
my_transfer_quota = 0
my_transfer_used = 0
my_transfer_overage = 0
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

print ("Done! Getting network transfer")
my_transfer = transfer_details(my_token)
my_transfer_quota = my_transfer['quota']
my_transfer_used = my_transfer['used']
my_transfer_overage = my_transfer['billable']

print("All done!")

print("Your current hourly run rate for instances is: $", round(my_hourly_price,2))
print("Your monthly run rate for instances is: $", round(my_monthly_price,2))
print("Your egress quota for the month is:", my_transfer_quota, "GB")  
print("You have used", my_transfer_used, "GB egress so far this month")
print("You have", my_transfer_overage, "GB in egress overage so far this month")
projected_usage = round((my_transfer_used / percent_month_complete()),0)
print("You are projected to consume", projected_usage, "GB egress by the end of the month")
if projected_usage > my_transfer_quota:
    print("This may result in"), my_transfer_quota - projected_usage, "GB egress overage with a cost of $", round(.01 * (my_transfer_quota - projected_usage),2)
else:
    print("Which would not result in any egress overage")

# Log activity
logging.info("Complete!")