# Argo Ocean Data Analysis

## UMICH SIADS 591-592 Project
## Authors: Claire-Isabelle Carlier, Sharon Sung

## Motivation

Our proposed project was to use Argo data (a data set of ocean floats that collect variables such as salinity and 
temperature in oceans around the world), map the change of salinity and temperature in the Estuary and 
Gulf of St. Lawrence, and identify potential correlations to fish populations totals in the same area. 

The Estuary and Gulf of St. Lawrence (the “Gulf”) is an incredibly diverse and complex marine and estuary 
ecosystem and is one of the largest of its kind in the world. The area is made up of freshwater from the Canadian 
Shield, the Great Lakes basin and the St. Lawrence River system emptying out into the Atlantic Ocean, where it 
combines with the cold Labrador Current from the Arctic and the warm Gulf Stream from the tropics. These 
currents merge in a semi-enclosed and mostly shallow area, creating perfect conditions for an incredible diversity 
of life. The Gulf of St. Lawrence is the most important source of fish on the Atlantic side for the commercial 
fishing industry in both the U.S. and Canada, both top exporters of fish and seafood in the world . By studying and 
reporting about this ecosystem and the species that depend on it, we hope to better inform others about its 
critical importance. 

This project aimed to answer the following questions:

<ul>
<li>How have ocean properties such as temperature and salinity changed over a period of ten years in the Gulf?</li>
<li>How have pelagic fish populations changed in the Gulf within the same time period?</li>
<li>Is there a meaningful correlation between ocean properties and fish population evolutions that merits further study?</li>
</ul>

## Data Sources
<ul>
<li>Argo: Argo is an international program that collects information about Earth’s oceans using a fleet of robotic 
instruments that drift with the ocean currents and move between the surface and mid-water level. For the scope of this 
project, we used Atlantic Ocean data between latitude 38 to 59 and longitude -70 to -35 (corresponding to a large zone 
including the St Lawrence Gulf).</li>
<li>Global Temperature and Salinity Profile Programme (GTSPP): Data from the Global Temperature and Salinity Profile 
Programme (GTSPP), a joint international cooperative effort supporting the World Climate Research Programme, was used 
to supplement ARGO data for the same time period (2009-2019). Similar to Argo data, GTSPP data also collects sea 
measurements such as salinity and temperature in the Earth’s oceans, but instead of floats, data is collected from 
both ships and buoys. Measurements are not quite as deep as Argo data, as depth measurements max out typically well 
before a thousand meters.</li>
<li>Government of Canada’s Department of Fisheries and Oceans (DFO) – Quebec Coastal Thermograph Network
DFO’s dataset was used to supplement both the Argo float and GTSPP dataset at the surface level, as we were not 
sure we would have sufficient measurement points for the Gulf from the first two datasets. Data are collected from 
buoys and, unlike both Argo and GTSPP data, strictly surface level data only (less than 100 meters).</li>
<li>Government of Canada’s Department of Fisheries and Oceans (DFO) – Pelagic Fish Populations in the Gulf: The
Canadian Department of Fisheries and Ocean conducts annual multidisciplinary surveys of the Northern and Southern 
Gulf of St. Lawrence to capture information on groundfish and invertebrates’ abundance, spatial distribution and 
diversity. The pelagic species represented in the dataset are: Arctic Cod, Atlantic Argentine, Atlantic Herring, 
Atlantic Mackerel, Atlantic Soft Pout, Capelin, Lumpfish, Pollock, Rainbow Smelt, Sand Lances, Silver Hake, 
Threespine Stickleback and White Barracudina.
</li>
</ul>