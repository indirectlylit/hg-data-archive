## Initial AC Data ##

`current.tsv` and `voltage.tsv` contain the numbers Jamie collected on the prototype AC sensor. In both files, the first column represents Multimeter measurements and the second column represents numbers reported from the micro controller. We consider the multimeter to be "correct", and try to find a way of predicting power (voltage x current) solely from sensor data.

A few models are compared. Initial investigation might imply that a reasonable model would be something along the lines of:

    estimated power = 7.6297 + 1.0312 * current * voltage - 0.8632 * current^2

where current and power are microprocessor sensor readings as in the data.
