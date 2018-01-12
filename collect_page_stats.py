#!/usr/bin/python3
#   collect_page_stats.py
#   This script leverages the Google PageSpeed Insights API to check a given
#   URL for key performance metrics
#
#   ref:  https://developers.google.com/speed/pagespeed/insights/?url=[YOUR_URL_GOES_HERE]}
#
#-------------------------------------------------------------------------------
# Still-to-DO: 
#   This code is currently replicated to handle different URLs we track, 
#   this is HIGHLY inefficient and will result in version control problems.
#   -   Create an array of URLs to test and iterate through them, recording the 
#       results for each.
#   -   Iterate test for desktop and mobile
#   -   Perform error handling for site outages / API failures etc.
#   -   Do some avalibility checks and alert via email on failures / performance
#       baselines being exceeded
#-------------------------------------------------------------------------------

## Load Libraries
from influxdb import InfluxDBClient
import requests
import json
import time
import datetime

# Define what we want to return from the API
#-------------------------------------------------------------------------------
api_key = '[YOUR_API_KEY_GOES_HERE]' # Add API key. Found here: https://console.developers.google.com/apis/credentials/key/
base_url = 'https://[URL_TO_TEST_HERE]'
filter_3rd = 'true'
locale_code = 'en_NZ'
show_screenshot = 'false'
device_type = 'desktop' # or mobile

# Construct the parameters to pass to the API
api_parameters = {'url': base_url, 'filter_third_party_resources': filter_3rd, 'locale': locale_code, 'screenshot': show_screenshot, 'strategy': device_type, 'key': api_key}
api_url = 'https://www.googleapis.com/pagespeedonline/v2/runPagespeed'

## Capture run time
now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")
iso = time.ctime()

# Send the request to the API
req = requests.get(api_url, params=api_parameters)

## ToDo:    Some kind of error handling
#-------------------------------------------------------------------------------
#   ref:    http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes
#print(req.status_code)

## Show the result from the API call
#-------------------------------------------------------------------------------
#print(req.text)

## Convert to JSON
return_text = req.text
return_json = json.loads(return_text)

## Test JSON
#print(return_json)

## Assign values from PageSpeed Insights (psi) to variables for loading into database
#-------------------------------------------------------------------------------
page_score = return_json['ruleGroups']['SPEED']['score']
psi_numResources = return_json['pageStats']['numberResources']
psi_numHosts = return_json['pageStats']['numberHosts']
psi_totReqBytes = return_json['pageStats']['totalRequestBytes']
psi_numStatResources = return_json['pageStats']['numberStaticResources']
psi_htmlRespBytes = return_json['pageStats']['htmlResponseBytes']
psi_jsRespBytes = return_json['pageStats']['javascriptResponseBytes']
psi_otherRespBytes = return_json['pageStats']['otherResponseBytes']
psi_numJsResources = return_json['pageStats']['numberJsResources']

# Display retrieved results
print("="*80)
print("Results for "+base_url+" on a "+device_type+" platform")
print("Page Score: "+"\t\t"+str(page_score))
print("# Resources: "+"\t\t"+str(psi_numResources))
print("# Hosts: "+"\t\t"+str(psi_numHosts))
print("# Static Resources: "+"\t"+str(psi_numStatResources))
print("# JS Resources: "+"\t"+str(psi_numJsResources))
print("Total Request Bytes: "+"\t"+str(psi_totReqBytes))
print("HTML Response Bytes: "+"\t"+str(psi_htmlRespBytes))
print("JS Response Bytes: "+"\t"+str(psi_jsRespBytes))
print("Other Response Bytes: "+"\t"+str(psi_otherRespBytes))

## Setup connection for InfluxDB
#-------------------------------------------------------------------------------
# Set the InfluxDB connection variables
indb_host = "[IP_OR_HOSTNAME_OF_INFLUXDB_SERVER]"
indb_port = 8086
indb_user = "[USERNAME_GOES_HERE]"
indb_password = "[PASSWORD_GOES_HERE]"
indb_dbname = "[NAME_OF_INFLUXDB_HERE]"
# Sample period (s)
interval = 5

session = "Page_Speed"
now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")

print("Session: ", session)
print("runNo: ", runNo)

# Create the InfluxDB object
client = InfluxDBClient(indb_host, indb_port, indb_user, indb_password, indb_dbname)

## Construct JSON
#-------------------------------------------------------------------------------
json_body = [
{
    "measurement": session,
    "tags": {
        "run": runNo,
        "url": base_url,
        "platform": device_type
    },
    "time": iso,
    "fields": {
        "Page_Score" : page_score,
        "Num_Resources" : psi_numResources,
        "Num_Hosts" : psi_numHosts,
        "Num_StatResources" : psi_numStatResources,
        "Num_jsResources" : psi_numJsResources,
        "Tot_ReqBytes" : psi_totReqBytes,
        "htmlRespBytes" : psi_htmlRespBytes,
        "jsRespBytes" : psi_jsRespBytes,
        "otherRespBytes" : psi_otherRespBytes
    }
}
]

# Write JSON to InfluxDB
#-------------------------------------------------------------------------------
client.write_points(json_body)

## Double up of code!
# ==============================================================================
# This code re-runs the above test, but for the mobile platform
#

device_type = 'mobile'  # Desktop is handled above

# Construct the parameters to pass to the API
api_parameters = {'url': base_url, 'filter_third_party_resources': filter_3rd, 'locale': locale_code, 'screenshot': show_screenshot, 'strategy': device_type, 'key': api_key}
api_url = 'https://www.googleapis.com/pagespeedonline/v2/runPagespeed'

## Capture run time
now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")
iso = time.ctime()

# Send the request to the API
req = requests.get(api_url, params=api_parameters)
## Convert to JSON
return_text = req.text
return_json = json.loads(return_text)

## Test JSON
#print(return_json)

## Assign values from PageSpeed Insights (psi) to variables for loading into database
#-------------------------------------------------------------------------------
page_score = return_json['ruleGroups']['SPEED']['score']
psi_numResources = return_json['pageStats']['numberResources']
psi_numHosts = return_json['pageStats']['numberHosts']
psi_totReqBytes = return_json['pageStats']['totalRequestBytes']
psi_numStatResources = return_json['pageStats']['numberStaticResources']
psi_htmlRespBytes = return_json['pageStats']['htmlResponseBytes']
psi_jsRespBytes = return_json['pageStats']['javascriptResponseBytes']
psi_otherRespBytes = return_json['pageStats']['otherResponseBytes']
psi_numJsResources = return_json['pageStats']['numberJsResources']

# Display retrieved results
# Below print commands are only useful for bug testing as the script itself 
# runs from cron
print("-"*80)
print("Results for "+base_url+" on a "+device_type+" platform")
print("Page Score: "+"\t\t"+str(page_score))
print("# Resources: "+"\t\t"+str(psi_numResources))
print("# Hosts: "+"\t\t"+str(psi_numHosts))
print("# Static Resources: "+"\t"+str(psi_numStatResources))
print("# JS Resources: "+"\t"+str(psi_numJsResources))
print("Total Request Bytes: "+"\t"+str(psi_totReqBytes))
print("HTML Response Bytes: "+"\t"+str(psi_htmlRespBytes))
print("JS Response Bytes: "+"\t"+str(psi_jsRespBytes))
print("Other Response Bytes: "+"\t"+str(psi_otherRespBytes))

## Setup connection for InfluxDB  (DOUBTFUL THAT THIS NEEDS REPLICATION)
#-------------------------------------------------------------------------------
# Set the InfluxDB connection variables
indb_host = "[IP_OR_HOSTNAME_OF_INFLUXDB_SERVER]"
indb_port = 8086
indb_user = "[USERNAME_GOES_HERE]"
indb_password = "[PASSWORD_GOES_HERE]"
indb_dbname = "[NAME_OF_INFLUXDB_HERE]"
# Sample period (s)
interval = 5

session = "Page_Speed"
now = datetime.datetime.now()
runNo = now.strftime("%Y%m%d%H%M")

print("Session: ", session)
print("runNo: ", runNo)
print("="*80)

# Create the InfluxDB object
client = InfluxDBClient(indb_host, indb_port, indb_user, indb_password, indb_dbname)

## Construct JSON
#-------------------------------------------------------------------------------
json_body = [
{
    "measurement": session,
    "tags": {
        "run": runNo,
        "url": base_url,
        "platform": device_type
    },
    "time": iso,
    "fields": {
        "Page_Score" : page_score,
        "Num_Resources" : psi_numResources,
        "Num_Hosts" : psi_numHosts,
        "Num_StatResources" : psi_numStatResources,
        "Num_jsResources" : psi_numJsResources,
        "Tot_ReqBytes" : psi_totReqBytes,
        "htmlRespBytes" : psi_htmlRespBytes,
        "jsRespBytes" : psi_jsRespBytes,
        "otherRespBytes" : psi_otherRespBytes
    }
}
]

# Write JSON to InfluxDB
#-------------------------------------------------------------------------------
client.write_points(json_body)
