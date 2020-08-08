# argo_ocean_data_analysis
For use in the SIADS591 Milestone Project

Data sets/links:
* Argo User Manual: https://archimer.ifremer.fr/doc/00187/29825/
* FTP we could pull from: ftp://usgodae.org/pub/outgoing/argo
* NOAA Weather data services: https://www.ncei.noaa.gov/access, including Storm Event DB (https://www.ncdc.noaa.gov/stormevents/details.jsp?type=eventtype)

Database possibilities:
* AWS (RDS, DynamoDB): The free tier offers some level of service for each:
    * https://aws.amazon.com/rds/ (I'm most familiar with MariaDB from work, but we could go with Postgres like class!) 
    Free tier: https://aws.amazon.com/rds/free/
    * DynamoDB has 25 GB: https://aws.amazon.com/dynamodb/?did=ft_card&trk=ft_card . If we want to go with a non-relational, although
    I think this is less useful in a case where we'll be joining data... Still, there's no limit on pull requests like there is with RDS, 
    although they throttle on throughput.
    
Visualization possibilities:
* Bokeh
* Plotly (in this case we'd actually likely be using Dash instead for an online viz)
* Altair
* Tableau/PowerBi (they can do it!!! and you can host, haha)

Geographic needs/considerations for our viz:
* Mapbox 

Ideas:
- Impact of hurricanes/storms on salinity and phytoplankton (chlorophyll - may not be included in all sensors)
- Impact of precipitations on salinity, temperature and oxygen
- Impact of ship activity (ex: Panama canal)
    - https://www.northeastoceandata.org/data-download/ Under marine traffic there is AIS data for the NE ocean area from 2011 onward. 
    Appears to be ArcGIS data; maybe we can parse it into python somehow?
- Fish movements
- Comparing the salinity/temperature in the St-Laurent vs Atlantic Ocean - https://open.canada.ca/data/en/dataset/8a3dc9e5-f3af-4270-8c09-43fa2c25848b
- We can also merge the set with the bottom layer salinity, to see if depth changes salinity: https://open.canada.ca/data/en/dataset/9571b5fa-3311-44c8-a565-d5694f34afac
- We can also merge it with pelagic fish data!!! 
    - https://open.canada.ca/data/en/dataset/267e20aa-97e8-43da-8c23-1234376938bc 
    - https://open.canada.ca/data/en/dataset/f1fc359c-0ed1-4045-a421-adef2497b68d (this has the data dictionary + annual split)


Seems like there is a richness of data for the Estuary and Gulf of St Lawrence, and I think there is argo data for this area as well? 

TODO:
- Find EU data source for weather forecast and historical weather data
- Play with the data, choose a scope for Tuesday
- If we go with Gulf of St Lawrence data, double check to make sure Gulf data is in Argo data to have overlapping data sets.

UPDATES  - I guess we could read our commits, but this might be easier. :) 
- Started exploring the pelagic fish data (see pelagic_analysis.ipynb)
- Started filling out the proposal doc and changed up formatting a bit! Highlighted in yellow what is wanted from us to fill in the doc, the rest of the words are ours. 
- Added pelagic fish data to our data folder - we can use this as a repository for data as a copy to whatever we push to db.
- Added an etl folder (actually, set it up as a package) - so we can set up the code to push data into a database or pull out of it. Should also be where we house our API calls. 