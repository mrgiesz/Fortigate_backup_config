# Python Fortigate config grabber
from pathlib import Path
import pandas as pd
import requests
import time
import urllib3

# disable ssl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_url(ip, port, api_key):
    # building url from variables
    built_api_url = f"https://{ip}:{port}/api/v2/monitor/system/config/backup/?scope=global&access_token={api_key}"
    return built_api_url


def write_data(received_config, name):
    timestr = time.strftime("%Y-%m-%d-%H%M%S")
    # creating subdirectory
    Path('Customers/' + name).mkdir(parents=True, exist_ok=True)
    # Writing received config file too a file
    open(f'Customers/{name}/{timestr}_{name}_config.txt', 'wb').write(received_config)
    print(f'Stored config from {name}')


def get_data_from_fortigate(name, generated_api_url):
    print(f'Requesting config from {name}')
    try:
        # Requesting data from the Fortigate
        response = requests.get(generated_api_url, verify=False)
        if response.status_code == 200:
            print(f'Received config from {name}')
        else:
            raise ConnectionError(f"Status code was not 200 but : {response.status_code}")
        return response.content
    except requests.exceptions.HTTPError as errh:
        print(f'A Http Error with {name}', errh)
    except requests.exceptions.ConnectionError as errc:
        print(f'Error Connecting with {name}', errc)
    except requests.exceptions.Timeout as errt:
        print(f'Timeout Error occurred with {name}', errt)
    except requests.exceptions.RequestException as err:
        print(f'Something Else occurred with {name}', err)


if __name__ == '__main__':

    # Reading excel, and creating device list
    df = pd.read_excel('fortigate-list.xlsx')

    # loop through excel file, and send data to function.
    for row in df.itertuples():
        # creating api url
        api_url = build_url(row.IP, row.Port, row.Api_Key)
        # requesting config from Fortigate
        config = get_data_from_fortigate(row.Name, api_url)
        # Writing data to file
        if config:
            write_data(config, row.Name)
        else:
            print(f'No data received rom {row.Name}')
