# mortalKombat

## Analysis of past time mortality

The objective of this script is to analyse how life expectancy evolved throught the last 200 years.

Many say that life expectancy in the 1800s was lower than 50 years. This can indeed be simply obtained as the mean age of death during this period. However, a major contribution to this early death was infant mortality. Computing a mean death age during where a period where this mortality was still high may therefore a biased estimate. Indeed, once a human has reached adulthood, is life expectancy (knowing that he did not die a child) is actually higher. This is what we intend to compute in this script.

We study France as an example. Data is obtained from [mortality.org](https://www.mortality.org/Country/Country?cntr=FRACNP)

The script produces the following figure:

![Mortality in France](https://raw.githubusercontent.com/laurent90git/mortalKombat/main/mortality_france.png "Mortality in France")

We see that the curves without infant mortality (curves with no transparency) are much higher than with. Typically, the median (respectively mean) age of death around 1850 is 30 (resp. 35) with infant mortality, while it becomes 55 (resp. 57) when we discard deaths at ages lower than 15 years.

Thus, a person having reached adulthood would typically expect to live up to 55 years before passing away, which is more optimistic than what the global death analysis (including infant mortality) would produce !
