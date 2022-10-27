#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import ssl
from re import search
import os
import sys

hdr = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
}

link = "https://www.nationsonline.org/oneworld/IATA_Codes/airport_code_list.htm"
page = requests.get(link, headers=hdr).content
soup = BeautifulSoup(page, "html.parser")

## substrings created for removal in next step
substring = "<strong>"
substring2 = "<colgroup>"
substring3 = "colspan"

# initialising empty lists for each column of the table
country = []
city = []
IATA = []

## First we'll grab only the elements that we want by removing the <strong> tagged
## Alphabetical category markers from the table along with the colgroup/span format tags

# Loop through all tables - each letter of alphabet is its' own table! :S
for table in soup.find_all("table"):
    # then loop through the rows
    for row in table.find_all("tr"):
        # filter the alphabet letter rows, and the column span/group rows
        if (
            not search(substring, str(row))
            and not search(substring2, str(row))
            and not search(substring3, str(row))
        ):
            # find all 'td' tags and toss the text into a list
            td = row.find_all("td")
            city.append(td[0].text)
            country.append(td[1].text)
            IATA.append(td[2].text)

#%%

## zip the three lists, then convert to a dataframe
iatacode = list(zip(city, country, IATA))
iatacodes = pd.DataFrame(iatacode, columns=["City", "Country", "IATA"])

#%%
iatacodes

#%%

## test that the dataframe is filled by returning all the airports in Australia
iatacodes.loc[iatacodes["Country"] == "Australia"]


#%%
# Save the codes to a txt file
with open(
    os.path.join(sys.path[0], "iata_codes.csv"), "a", encoding="utf-8"
) as csvfile:
    iatacodes.to_csv(
        csvfile,
        index=False,
        line_terminator="\n",
        header=csvfile.tell() == 0,
        na_rep="NaN",
    )
