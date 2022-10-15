# Advanced Business Analytics

The project demonstrates my work in advanced business analytics, specially applying statistics and distribution models to business data. In this project, I show how one can use distribution formluas to "fill-in" data gaps due to only having collected limited data. In order to do this, we first determine a theoretical/reasonable data distribution using domain knowledge. For example, for filling in height data one would assume a normal distribution. Another example, for counting the number of hurricanes in Florida one would assume a Poisson distribution. Once we determine the theoretical model, we learn the constants that minimize probability error [MLE](https://towardsdatascience.com/probability-concepts-explained-maximum-likelihood-estimation-c7b4342fdbb1). We then get a continuous data distribution that we can use to predict likely outcomes from unseen data.

<br>

|header            |value                                                                              |
|------------------|-----------------------------------------------------------------------------------|
|Program:          |                                                                                   |
|Author:           |Ripperger, Brent                                                                   |
|Date Created:     |28 November 2021                                                                   |

<br>

## Example Project

In the exaple project, we look at USA divorce data. We are going to show the probability of a divorce over time from a sample of people, the years they've been married/divorced, and if they divorced. Your first thought might be, why are we using non-business data? For example purposes, this dataset is easy to explain and quick to grasp. The results are also intuitive. However, a business example for this exact same problem would be: predict when a piece of equipment will breakdown. Say we had a dataset of equipment IDs, the amount of time the equipment has been operational, and is it running or not. We are going to determine the hazard curve for this dataset (i.e., what is the probability a piece of equipment breaks down each year in operation). We are doing all these steps for divorce data as our example. 

|Metadata  |                      |
|----------|----------------------|
|Title     |Divorce data in USA   |
|Dimensions|3367 rows x 3 columns |

top 4 rows:

|ID |time between marriage and divorce or end of observation|divorce or not|
|---|-------------------------------------------------------|--------------|
|9  |10                                                     |No            |
|11 |34                                                     |No            |
|13 |2                                                      |Yes           |
|15 |17                                                     |Yes           |

### Aggregate Data

We need to compute the actual hazard rate at each year. Therefore, we aggregate the IDs into a countdown of remaining population at each year in the dataset (0-73 years). 

|time|population at t|actual hazard ratio|
|----|---------------|--------------|
|1   |3367           |0.027621028   |
|2   |3147           |0.020972355   |
|3   |3005           |0.020965058   |
|4   |2869           |0.025095852   |

<div class='tableauPlaceholder' id='viz1665852226463' style='position: relative'><noscript><a href='#'><img alt='Hazard Curve, USA Divorce ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;ha&#47;hazard_ratio&#47;Sheet2&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='hazard_ratio&#47;Sheet2' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;ha&#47;hazard_ratio&#47;Sheet2&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>
