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
- Fish movements
- Comparing the salinity/temperature in the St-Laurent vs Atlantic Ocean - https://open.canada.ca/data/en/dataset/8a3dc9e5-f3af-4270-8c09-43fa2c25848b

TODO:
- Find EU data source for weather forecast and historical weather data
- Play with the data, choose a scope for Tuesday

