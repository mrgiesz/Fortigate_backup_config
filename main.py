# Python fortigate config grabber
from pathlib import Path
import pandas as pd
import requests
import time
import urllib3

# disable ssl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def excel_to_df(filename):
    # Reading excel file, and creating dataframe
    df = pd.read_excel(filename)
    return df


def build_api_url(ip, port, api_key) -> str:
    # building url from variables
    built_api_url = f"https://{ip}:{port}/api/v2/monitor/system/config/backup/?scope=global&access_token={api_key}"
    return built_api_url


def write_config_to_file(received_config, name):
    timestr = time.strftime("%Y-%m-%d-%H%M%S")

    # creating subdirectory
    Path('Customers/' + name).mkdir(parents=True, exist_ok=True)

    # Writing received config file too a file
    open(f'Customers/{name}/{timestr}_{name}_config.txt', 'wb').write(received_config)
    print(f'Stored config from {name}')


def download_config_from_fortigate(name, generated_api_url):
    print(f'Requesting config from {name}')
    try:
        # Requesting data from the fortigate
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


def loop_through_dataframe(df):
    # loop through dataframe to get info for each fortigate
    for row in df.itertuples():
        # creating api url
        api_url = build_api_url(row.IP, row.Port, row.Api_Key)

        # requesting config from fortigate
        config = download_config_from_fortigate(row.Name, api_url)

        # Writing data to file
        if config:
            write_config_to_file(config, row.Name)
        else:
            print(f'No data received rom {row.Name}')


def main():
    # Excel file name with fortigate info
    filename = 'fortigate-list.xlsx'

    # generating dataframe from excel file
    df = excel_to_df(filename)

    # loop through dataframe, request en write config for each fortigate.
    loop_through_dataframe(df)


if __name__ == '__main__':
    main()
