__author__ = 'Peter Eriksson @ KTH 2015'

import numpy as numpy
import CoolProp.CoolProp as CoolProp
import vcc_input

# Description:
# This file illustrates the non-linear behaviour of temperature glide.

refrigerant_data = vcc_input.refrigerant('R448A')

# Initiate CoolProp with AbstractState meaning low-level interface
refrigerant = CoolProp.AbstractState(refrigerant_data[1], refrigerant_data[2])

 # Set mole fractions
refrigerant.set_mole_fractions(refrigerant_data[3])

pressure = 4e5
k = 273.15

x = numpy.linspace(0,1,10)

t = numpy.zeros(len(x), numpy.float)

file_1 = open('../../Report/LaTeX/data/Glide-non-linear.dat', 'w+')
file_2 = open('../../Report/LaTeX/data/Glide-linear.dat', 'w+')
file_3 = open('../../Report/LaTeX/data/Glide-diff.dat', 'w+')

file_1.write("vapormassquality temperature\n")
file_2.write("vapormassquality temperature\n")
file_3.write("vapormassquality temperature\n")

t_min = 0
t_max = 0

# Loop through all temperatures
for i in range(0, len(x)):

    refrigerant.update(CoolProp.PQ_INPUTS, pressure, x[i])
    file_1.write(str("%f %f\n" % (x[i], refrigerant.T()-k)))

    if i==0:
        t_min = refrigerant.T()-k
        file_2.write(str("%f %f\n" % (x[i], t_min)))


    if i==len(x)-1:
        t_max=refrigerant.T()-k
        file_2.write(str("%f %f\n" % (x[i], t_max)))

refrigerant.update(CoolProp.PQ_INPUTS, pressure, 0.5)
file_3.write(str("%f %f\n" % (0.5, (t_min+t_max)/2)))
file_3.write(str("%f %f\n" % (0.5, refrigerant.T()-k)))

file_1.close()
file_2.close()
file_3.close()