# -*- coding:utf-8 -*-
import sys

import csv
import json
from bs4 import BeautifulSoup
import js2xml
from lxml import etree

# Async model
import aiohttp
import asyncio
from aiohttp import ClientSession

# retry- setting
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
s = requests.Session()
retries = Retry(total=15,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
s.mount('https://', HTTPAdapter(max_retries=retries))

# write file section
async def RunmberCheck(outPutFile: str):

    conn = aiohttp.TCPConnector(limit=5)
    session = aiohttp.ClientSession(connector=conn)

    # start to read file
    csvFile = open('booking-token.csv', 'r')
    dict_reader = csv.DictReader(csvFile)

    # start to write a file
    with open(outPutFile, mode='w') as csv_write_file:
        fieldnames = ["Confirmation#", "GAR_Rnumber"]
        writer = csv.DictWriter(csv_write_file, fieldnames=fieldnames)
        writer.writeheader()

        # for loop Getaroom_reservation_token
        for row in dict_reader:
            # row["uuid"], this will be the parameter
            url = 'https://www.getaroom.com/reservations/%s' % (row["number"])

            try:
                response = s.get(
                    url, headers={'Accept-Encoding': 'compress'}, verify=True)
                
                soup = BeautifulSoup(response.text, 'lxml')
                src = soup.select('head script')[6].string
                src_text = js2xml.parse(src, debug=False)
                src_tree = js2xml.pretty_print(src_text)
                selector = etree.HTML(src_tree)
                
                # <property name="rv_confirmation_code">
                if len(selector.xpath("//property[@name = 'rv_confirmation_code']/string/text()")) > 0:
                    content = selector.xpath(
                        "//property[@name = 'rv_confirmation_code']/string/text()")[0]
                else:
                    content = "maybe invalid token"
                
            except OSError as reason:
                print('file have error')
                print('the reason is %s' % str(reason))
                content = str(reason)
            except TypeError as reason:
                print('function error?')
                print('the reason is %s' % str(reason))
                content = str(reason)

            writer.writerow({
                "Confirmation#": row["number"],
                "GAR_Rnumber": content
            })
            print("Just processed Getaroom_reservation_token: " +
                  row["number"])

    csvFile.close()


# excute function
loop = asyncio.get_event_loop()
loop.run_until_complete(
    RunmberCheck(
        outPutFile="Rnumber_4.17.2021.csv"
    )
)
loop.close()
