#%%
import pandas as pd
import numpy as np
import os
import sys

iata_codes = pd.read_csv("iata_codes.csv")
latlon = pd.read_csv(
    "GlobalAirportDatabase.csv",
    names=[
        "ICAO",
        "IATA",
        "Airport name",
        "City/Town",
        "Country",
        "Latitude degrees",
        "Latitude minutes",
        "Latitude seconds",
        "Latitude direction",
        "Longitude degrees",
        "Longitude minutes",
        "Longitude seconds",
        "Longitude direction",
        "Altitude",
        "Latitude Decimal Degrees",
        "Longitude Decimal Degrees",
    ],
)


#%%
latlon
#%%
iata_codes
#%%

dfc = pd.merge(iata_codes, latlon, on=["IATA"], how="left")
iata_codes = dfc[
    [
        "City",
        "Country_x",
        "IATA",
        "Latitude Decimal Degrees",
        "Longitude Decimal Degrees",
    ]
]
iata_codes.rename(
    columns={
        "Country_x": "Country",
        "Latitude Decimal Degrees": "Lat",
        "Longitude Decimal Degrees": "Lon",
    },
    inplace=True,
)

#%%
france = iata_codes.loc[iata_codes["Country"] == "France"]
italy = iata_codes.loc[iata_codes["Country"] == "Italy"]
uk = iata_codes.loc[iata_codes["Country"] == "United Kingdom"]

#%%
france

#%%
print(len(france))
print(len(uk))
print(len(italy))
#%%
iata_codes = iata_codes.loc[
    iata_codes["Country"].isin(["France", "Italy", "United Kingdom"])
]

#%%
iata_codes.drop([1840, 1388, 247, 1037])

#%%
with open(
    os.path.join(sys.path[0], "iata_codes_latlon.csv"), "a", encoding="utf-8"
) as csvfile:
    iata_codes.to_csv(
        csvfile,
        index=False,
        line_terminator="\n",
        header=csvfile.tell() == 0,
        na_rep="NaN",
    )
