# Artificial Intelligence Project

The project discusses my work in Artifical Intelligence (AI), specially Reinforcement Learning. I am attempting to create a control system 
for distributed energy resources (DERs) using AI. The project was my initial attempt at a simple model: learn the optimal operating procedue for
a power plant with solar panels and a natural gas turbine. I created a [simulator in Excel](https://bmripper.github.io/Power_Plant_Simulator.xlsx) first, then recreated the simulator in Python. The script uses reinforcement learning to find the optimal path (operating procedure) for a 24 hour period. 

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

### Python program
```ruby
import numpy as np
import pylab as plt
from scipy import stats
```

```ruby
goal = 50                   #kWh, goal for the system to reach
s_avg_cc = 0.3              # as decimal percentage of sky, average cloud cover
s_std_cc = 0.1              # as decimal percentage of sky, standard deviation cloud cover
s_irr = 7                   # kj/m2, solar irradiance
s_area = 100                # m2, solar panel area
ng_power = 70               # kW, natural gas power generation
ng_avg_uptime = 0.95        # as decimal percentage of an hour, average up-time of equipment
ng_std_uptime = 0.01        # as decimal percentage of an hour, standard deviation up-time of equipment
ng_emissions_per_kWh = 0.4127691    # emissions per kWh when an ng turbine is running
ng_startup_time = 4         # hours, time to start-up natural gas turbine
ng_shutdown_time = 2        # hours, time to shutdown natural gas turbine
reward_function = [0,50,100]
```

```ruby
# Create Simulation
def simulation(actions):
    reward = []
    for idx, ng_on in enumerate(actions):
        s_kWh = (s_irr * stats.norm.pdf((idx-12)/2.738612788, 0, 1) / \
                stats.norm.pdf((12-12)/2.738612788, 0, 1) ) * \
                (1-np.random.normal(s_avg_cc, s_std_cc, 1)[0]) * s_area
        ng_kWh = ng_on * np.random.normal(ng_avg_uptime, ng_std_uptime,1)[0] * ng_power
        ng_emissions = ng_kWh * ng_emissions_per_kWh
        if s_kWh >= goal and ng_emissions < 1:
            r = reward_function[2]
        elif s_kWh + ng_kWh >= goal:
            r = reward_function[1]
        else:
            r = reward_function[0]
        reward.append(r)
    return reward

# Test Simulation
actions_guess = np.ones(24)
actions_guess *= -1
for i in range(24):
        actions_guess[i] = round(np.random.uniform(0,1),0)
        
actions_guess = [int(a) for a in actions_guess]
rewards = simulation(actions_guess)
print(rewards)
```
