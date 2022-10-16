# Supervised Learning: Classification

This project is an example of using classification techniques to determine which group data points are part of. If we do this accurately, when we continue to receive points in the future without knowing what groups they belong too, we can properly classify them. In the example, we use linear discrimany analysis, quadratic discriminant analysis, and naive bayes. I build a model that predicts the type of plant given datapoints with sepal width, sepal length, pedal width, and pedal length. 
<br><br>

|header |value|
|-------|-------------------|
|author:|Brent Ripperger|
|date:  |14 April 2020|

<br>

### Preamble: Loading packages and data

```{r, message=FALSE}
library(ggplot2)
library(ISLR)
library(MASS)
library(klaR)  # You may need to install this one
library(knitr)
library(glmnet)
library(plyr)
library(gam)
library(caret)
library(tidyverse)

set.seed(14504008)

cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

options(scipen = 4)

Adulthood data
n.obs <- 3000
age <- pmin(pmax(rnorm(n.obs, mean = 30, sd = 10), 5), 50)
is.adult <- as.numeric(age >= 18)
age.data <- data.frame(age = age, is.adult = as.factor(is.adult))
```



### Linear Discriminant Analysis, Quadratic Discriminant Analysis, Naive Bayes

> This problem introduces you to the `klaR` library, which provides a set of useful model fitting and visualization tools. You will also use some fitting functions from the `MASS` library.

> You may find the tutorial at [this link](http://www.statmethods.net/advstats/discriminant.html) helpful for solving this problem.

> We're going to use Fisher's famous `iris` data set for this problem.  This data set comes pre-loaded with R.  You can learn more about it by looking at the helpfile `?iris`.  It's fair to say that everyone who has ever learned Data Mining in R has encountered the iris data at one point or another

##### **(a)** Use the `lda` function from the `MASS` library to build an LDA classifier predicting `Species` from the 4 measurements in the `iris` data.  Call this fit `iris.lda`.  

```{r}
iris.lda <- lda(Species~.,data=iris)
```

##### Explore the `iris.lda` object to answer the following:  What are the group means and prior probabilities for each class?  

```{r}
iris.lda$means
iris.lda$prior
```

|description|Sepal.Length|Sepal.Width|Petal.Length|Petal.Width|
|-----------|------------|-----------|------------|-----------|
|setosa     | 5.006|       3.428   |     1.462  |     0.246|
|versicolor    |    5.936      | 2.770      |  4.260   |    1.326|
|virginica      |   6.588  |     2.974    |    5.552      | 2.026|


##### Run the `plot()` command on your `iris.lda` object.  This produces what is called a discriminant plot.  When we have $K$ possible classes, we get $K-1$ so-called linear discriminants.  You should think of these as "derived features" that provide a helpful low-dimensional representation of the data.  The more spread out the classes appear in these discriminant plots, the better the LDA method performs (and vice versa).  You may supply the argument `col = as.numeric(iris$Species)` to colour the points based on the true class label.

```{r}
plot(iris.lda,col = as.numeric(iris$Species))
```

<br>
![](https://bmripper.github.io/plot_lda.PNG)
<br>

#####  **(b)** Using the `predict` function, calculate the 3x3 confusion matrix for the lda classifier.  What is the overall misclassification rate of the LDA classifier?  Does LDA perform well on this problem?

```{r}
pred2 <- predict(iris.lda,iris)
pred_conf <- ifelse(pred2$class=="setosa","x1", ifelse(pred2$class=="versicolor","x2","x3"))

truth2 <- iris$Species
truth_conf <- ifelse(truth2=="setosa","x1", ifelse(truth2=="versicolor","x2","x3"))
table(pred_conf,truth_conf)
```
*prediction rows, actual columns*

| |x1| x2| x3|
|--------|---|---|---|
|        x1| 50 | 0 | 0|
|        x2|  0| 48 | 1|
|        x3  |0  |2 |49|

<font color="#157515">

- **(2+1)/150 == 1/50 == 2% misclassification rate. Yes! I'd say the LDA does very well. Correct 98% of the time, with only 4 inputs needed.**

</font>

##### Again using the `predict()` function:  What are the estimated posterior class probabilities for the 120th observation?  You should run `zapsmall()` on the vector of posterior probabilities to get it to display nicely.

```{r}
# pred2$posterior[120,]
# zapsmall(pred2$posterior)
zapsmall(pred2$posterior[120,])
```

##### **(c)** Use the `partimat()` function from the `klaR` package with `method = "lda"` to get bivariate plots showing the LDA decision boundaries.  Misclassifications are indicated by red text.  

```{r, cache = TRUE, fig.width = 10, fig.height = 6}
partimat(Species~.,data=iris,method="lda")
```

<br>
![](https://bmripper.github.io/predict_lda.PNG)
<br>

##### Two of the classes begin with the letter v, which makes the above plot hard to interpret.  The following code produces a new data frame, where the Species column has been transformed according to: `S = setosa`, `C = versicolor`, `N = verginica`.  Try constructing the plot again.  Do all 2-variable combinations of the inputs do an equally good job of separating the three classes?  

```{r, cache = TRUE, fig.width = 10, fig.height = 6}
iris2 <- transform(iris, Species = mapvalues(Species, c("setosa", "versicolor", "virginica"),
                                             c("S", "C", "N")))
partimat(Species~.,data=iris2,method="lda")
```

<font color="#157515">

- **Most have an error rate around 3-5%, however Sepal Width has an error rate at 20%. So 5/6 do equally well, but 1/6 does fairly poorly.**

</font>

##### **(d)**  Using the `iris2` data frame, run the `partimat` command again, this time with `method = "qda"`.  Does it look like allowing quadratic boundaries changes much?  

```{r, cache = TRUE, fig.width = 10, fig.height = 6}
partimat(Species~.,data=iris2,method="qda")
```

<br>
![](https://bmripper.github.io/predict_qda.PNG)
<br>

<font color="#157515">

- **Sepal Width and Petal Width both change substaintially. The others don't change much, or if they do it is mostly at the outlier points. The error rates didn't change much between lda and qda also.**

</font>

##### **(e)**  Using the `geom = "density"` or `geom_density()` functionality in `ggplot2`, construct density plots for the 4 input variables.  Your density plots should look similar to the ones shown for `income` and `balance` in Lecture 8.  There are 3 classes in the iris data instead of two, so your plots should have 3 densities overlaid.  The `alpha` argument may be used to change the transparency.  

##### Based on these plots, does it look like Naive Bayes will be an effective classifier for the iris data?  Explain.  

```{r}
ggplot(data=iris,aes(Sepal.Length,fill=Species, alpha=1/2)) + geom_density() + ggtitle("Sepal Length")
ggplot(data=iris,aes(Sepal.Width,fill=Species, alpha=1/2)) + geom_density() + ggtitle("Sepal Width")
ggplot(data=iris,aes(Petal.Length,fill=Species, alpha=1/2)) + geom_density() + ggtitle("Petal Length")
ggplot(data=iris,aes(Petal.Width,fill=Species, alpha=1/2)) + geom_density() + ggtitle("Petal Width")
```

<br>
![](https://bmripper.github.io/plot_naive_sl.PNG)
![](https://bmripper.github.io/plot_naive_sw.PNG)
![](https://bmripper.github.io/plot_naive_pl.PNG)
![](https://bmripper.github.io/plot_naive_pw.PNG)
<br>


<font color="#157515">

- **Looking at the partition plots above, we can see that these 4 variables group pretty well. There aren't scenarios where, for example versicolor, groups in two different areas on one plot. When looking at the plots we just generated, we can also see that the Petal plots are fairly distinct. While the sepal plots do overlap (therefore bad for Naive Bayes), petal classifications should be able to help carry the classification predictor. However, I don't love that Naive Bayes will assume independence because Sepal and Petal are not independent.**

</font>

##### **(f)** Use the `NaiveBayes()` command with `usekernel = TRUE` to fit a Naive Bayes classifier to the `iris` data.  Save your output as `iris.nb`.  Produce a confusion matrix for the Naive Bayes classifier.   What is the misclassification rate of Naive Bayes on this problem?  How does the performance of Naive Bayes compare to that of LDA in this example?

```{r}
iris.nb <- NaiveBayes(Species ~ ., data = iris, usekernel = TRUE)
pred3 <- predict(iris.nb,iris)
pred3_conf <- ifelse(pred3$class=="setosa","x1", ifelse(pred3$class=="versicolor","x2","x3"))

truth3 <- iris$Species
truth3_conf <- ifelse(truth3=="setosa","x1", ifelse(truth3=="versicolor","x2","x3"))
table(pred3_conf,truth3_conf)
```

*prediction rows, actual columns*

| |x1| x2| x3|
|--------|---|---|---|
|        x1| 50 | 0 | 0|
|        x2|  0| 47 | 3|
|        x3  |0  |3 |47|

<font color="#157515">

- **The misclassification rate here is 6/150 == 4%. Therefore this is 2x worse than the LDA predictor, however still 96% accuracy seems acceptable.**

</font>

##### **(g)**  What is the true class of the 120th observation? What are the estimated posterior probabilities for the 120th observation according to Naive Bayes?  Are they similar to those estimated by LDA?  Do LDA and Naive Bayes result in the same classification for this observation?  Does either method classify this observation correctly?

```{r}
#LDA
zapsmall(pred2$posterior[120,])
#Naive Bayes
zapsmall(pred3$posterior[120,])
#Truth
truth3[120]
```

<font color="#157515">

- **My Naive Bayes prediction states 95% probability of Versicolor when really the answer is in the 5% Virginica. My LDA prediction states 78% probability of Virginica, which is actually correct if the threshold is 50%.**

</font>
