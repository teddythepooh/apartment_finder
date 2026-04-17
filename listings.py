base_url = "https://www.bjbproperties.com"

IDS = [
    # East Lakeview
    "east-lakeview-apartments/2850-n-Sheridan/",
    "east-lakeview-apartments/2828-n-Pinegrove/",
    "east-lakeview-apartments/426-w-Surf/",
    "east-lakeview-apartments/517-w-Oakdale/",
    "east-lakeview-apartments/734-w-Oakdale/",
    "east-lakeview-apartments/420-w-Surf/",
    # Gold Coast
    "gold-coast-apartments/1036-n-Dearborn/",
    "gold-coast-apartments/18-e-Elm/",
    "gold-coast-apartments/11-w-Division/",
    "gold-coast-apartments/25-e-Delaware/",
    "gold-coast-apartments/211-e-Delaware/",
    "gold-coast-apartments/244-e-Pearson/",
    # Lakeview
    "lakeview-apartments/1022-w-Dakin/",
    "lakeview-apartments/3141-n-Sheffield/",
    "lakeview-apartments/660-w-Barry/",
    "lakeview-apartments/4100-n-Marine/",
    "lakeview-apartments/925-w-Dakin/",
    "lakeview-apartments/3838-n-Broadway/",
    "lakeview-apartments/3834-n-Sheffield/",
    "lakeview-apartments/721-w-Belmont/",
    # Lincoln Park
    "lincoln-park-apartments/443-w-Wrightwood/",
    "lincoln-park-apartments/424-w-Diversey/",
    "lincoln-park-apartments/839-w-Diversey/",
    "lincoln-park-apartments/742-w-Fullerton/",
    "lincoln-park-apartments/2244-n-Cleveland/",
    "lincoln-park-apartments/482-w-Deming/",
    "lincoln-park-apartments/1215-w-Diversey/",
    "lincoln-park-apartments/1157-w-Diversey/",
    "lincoln-park-apartments/828-w-Fullerton/",
    "lincoln-park-apartments/629-w-Deming/",
    "lincoln-park-apartments/451-w-Wrightwood/",
    # Mag Mile
    "mag-mile-apartments/320-n-michigan/",
    # Rogers Park
    "rogers-park-apartments/1135-w-Pratt/",
    "rogers-park-apartments/1258-W-Loyola/",
    "rogers-park-apartments/6616-n-Glenwood/",
    "rogers-park-apartments/1063-w-Columbia/",
    "rogers-park-apartments/1101-w-Columbia/",
    "rogers-park-apartments/6720-n-Sheridan/",
    "rogers-park-apartments/1246-w-Pratt/",
    "rogers-park-apartments/1331-w-Loyola/",
    "rogers-park-apartments/6710-n-Sheridan/",
    "rogers-park-apartments/6701-n-Glenwood/",
    "rogers-park-apartments/6822-n-Wayne/",
    # Roscoe Village
    "roscoe-village-apartments/1837-w-Patterson/",
    "roscoe-village-apartments/1632-w-Belmont/",
    # South Lincoln Park
    "south-lincoln-park-apartments/2051-n-Sedgwick/",
    "south-lincoln-park-apartments/1939-n-Lincoln/",
    "south-lincoln-park-apartments/2046-n-Orleans/",
    # West Loop
    "west-loop-apartments/180-w-Adams/",
    "west-loop-apartments/768-w-Jackson/",
]

URLS = [f"{base_url}/{id}" for id in IDS]
