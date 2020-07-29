# argo_ocean_data_analysis
For use in the SIADS591 Milestone Project

Data sets/links:
* Argo User Manual: https://archimer.ifremer.fr/doc/00187/29825/
* FTP we could pull from: ftp://usgodae.org/pub/outgoing/argo

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