# Business Intelligence Portfolio

The first project to discuss is my work in Artifical Intelligence (AI), specially Reinforcement Learning. I am attempting to create a control system 
for distributed energy resources (DERs) using AI. The first project was my initial attempt at a simple model: learn the optimal operating procedue for
a given solar/natural gas turbine, given multiple parameters. I created a simulator in Excel, to confirm the simulation idea worked. Then, I created a
Python script that will use reinforcement learning to find the optimal path. 

While the system is simple, it was an effective test to determine the feasibility of the idea. 

### Environment

|source|Variable            |Qty  |UoM       |
|------|--------------------|-----|----------|
|Solar |Cloud Coverage      |0.3  |% of area |
|Solar |St.D Cloud Coverage |0.1  |% of area |
|Solar |Irradiance          |7    |kJ/m2     |
|Solar |Area                |100  |m2        |
|NG    |Power               |70   |kW        |
|NG    |Up-Time             |0.95 |% runtime |

### Rules

|Variable        |Qty         |UoM   |
|----------------|------------|------|
|Goal            |50          |kWh   |
|Reward Function |[0, 50, 100]|points|
|Startup Time    |4           |hrs   |	
|Shutdown Time   |2           |hrs   |

**the reward is given at the end of each hour, for a 24 hour period. If the Goal (energy demand) was met and if zero emissions were produced, then the entire reward is given. If the Goal (energy demand) was met but emissions were produced, then half the reward is given. If the Goal (energy demand) was not met, no reward is given.*
