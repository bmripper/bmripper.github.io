# Geographic Information System Project

The project is my final output from a class in Geographic Information System (GIS). During the course, we used ArcGIS software. 

### Abstract

This project explored the relationship between economic performance (EP), social equity (SE), and walkability (W). The purpose was to answer the question: does walkability explain why certain census tracts both have high EP and high SE while other tracts have high EP but low SE. The project analyzed census tracts inside Allegheny County using data from the US Census Bureau, Environmental Protection Agency (EPA), and Western Pennsylvania Regional Data Center (WPRDC). The hypothesis is that high walkability is associated with places of high EP and high SE, while low walkability is associated with places of high EP and low SE. However, the results show the opposite being true. This analysis found that SE is negatively correlated with EP (𝑝𝑣𝑎𝑙𝑢𝑒 = <2𝑒−16,𝑅𝑠𝑞𝑢𝑎𝑟𝑒𝑑 = 0.19). Similarly, walkability is negatively correlated with EP (𝑝𝑣𝑎𝑙𝑢𝑒= <2𝑒−16,𝑅𝑠𝑞𝑢𝑎𝑟𝑒𝑑= 0.25). Considering both SE and W were negatively correlated with EP, there becomes a need to understand the relationship between W and SE. This analysis found that walkability is positively correlated with SE (𝑝𝑣𝑎𝑙𝑢𝑒 = 0.000218,𝑅𝑠𝑞𝑢𝑎𝑟𝑒𝑑 = 0.034). While the R-squared value is small, the implications for this are interesting and surprising. The positive relationship between W and SE justifies the need for further analysis by policy makers. These findings could provide the rationale to improve the walkability of targeted census tracts, expecting to drive an increase in SE. While the project didn’t prove that higher walkability explains why tracts have both high EP and high SE, the project was able to find a statistically significant, positive correlation between walkability and social equity.

### Environment

|source|variable            |qty  |UoM       |
|------|--------------------|-----|----------|
|Solar |Cloud Coverage      |0.3  |% of area |
|Solar |St.D Cloud Coverage |0.1  |% of area |
|Solar |Irradiance          |7    |kJ/m2     |
|Solar |Area                |100  |m2        |
|NG    |Power               |70   |kW        |
|NG    |Up-Time             |0.95 |% runtime |

### Rules

|variable        |qty         |UoM   |
|----------------|------------|------|
|Goal            |50          |kWh   |
|Reward Function |[0, 50, 100]|points|
|Startup Time    |4           |hrs   |	
|Shutdown Time   |2           |hrs   |

**the reward is given at the end of each hour, for a 24 hour period. If the Goal (energy demand) was met and if zero emissions were produced, then the entire reward is given. If the Goal (energy demand) was met but emissions were produced, then half the reward is given. If the Goal (energy demand) was not met, no reward is given.*
