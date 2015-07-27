Analytic Entry Line Split Unit Amount
=====================================

This module adds a new field named split_unit_amount which will accordingly
spread the values in the analytic entry lines the amount which was set in the
Journal Entry Line

The following example illustrated the use of this module.

Hey, Pancho, Sell 10 Barrels of Oil, each one costs 100 USD, Give each of your
boys (4 boys) 60% Iraq, 30% Venezuela, 20%Saudi Arabia and 10%Kuwait,

What you are expected to have in your reports is

600 USD, 6 Barrels, Iraq
300 USD, 3 Barrels, Venezuela
200 USD, 2 Barrels, Saudi Arabia
100 USD, 1 Barrels, Kuwait

This is what is reported without this module

600 USD, 10 Barrels, Iraq
300 USD, 10 Barrels, Venezuela
200 USD, 10 Barrels, Saudi Arabia
100 USD, 10 Barrels, Kuwait