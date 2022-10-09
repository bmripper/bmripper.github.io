# Artificial Intelligence Project

The project discusses my work in Artifical Intelligence (AI), specially Reinforcement Learning. I am attempting to create a control system 
for distributed energy resources (DERs) using AI. The project was my initial attempt at a simple model: learn the optimal operating procedue for
a power plant with solar panels and a natural gas turbine. I created a [simulator in Excel](https://bmripper.github.io/General_Resume_2022_09.pdf) first, then implemented the simulator in Python. The script uses reinforcement learning to find the optimal path (operating procedure) for a 24 hour period. 

While the system is simple, it was an effective test to determine the feasibility of the control system idea. 

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
