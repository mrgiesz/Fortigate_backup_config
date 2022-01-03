# Python Fortigate config grabber
from pathlib import Path
import pandas as pd
import requests
import time
import urllib3

# disable ssl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_data_from_fortigate(name, ip, port, api_key):
    api_url = 'https://' + str(ip) + ':' + str(
        port) + '/api/v2/monitor/system/config/backup/?scope=global&access_token=' + api_key
    print(f'requesting config from {name}')

    try:
        response = requests.get(api_url, verify=False)
        if response.status_code == 200:
            print(f'Received config from {name}')
            timestr = time.strftime("%Y-%m-%d-%H%M%S")
            # creating subdirectory
            Path(name).mkdir(exist_ok=True)
            # Writing output do file
            open(f'{name}/{timestr}_{name}_config.txt', 'wb').write(response.content)
        else:
            raise ConnectionError(f"Status code was not 200 but : {response.status_code}")
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
    df = pd.read_excel('customerlist.xlsx')

    # loop through excel file, and send data to function.
    for row in df.itertuples():
        get_data_from_fortigate(row.Name, row.IP, row.Port, row.Api_Key)
