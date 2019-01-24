__author__ = 'Peter Eriksson @ KTH 2015'

import numpy as numpy
import CoolProp.CoolProp as CoolProp

# Description:
# This file illustrates the zeotropic behaviour of temperature glide

# Initiate CoolProp with AbstractState meaning low-level interface
refrigerant = CoolProp.AbstractState("REFPROP","R125&R1234yf")
pressure = 101.325e3

k = 273.15
x = numpy.linspace(0,1,25)

# Open files
file_1 = open('../../Report/LaTeX/data/zeotropic_bubble.dat', 'w+')
file_2 = open('../../Report/LaTeX/data/zeotropic_dew.dat', 'w+')
file_3 = open('../../Report/LaTeX/data/zeotropic_diff.dat', 'w+')

file_1.write("mixture temperature\n")
file_2.write("mixture temperature\n")
file_3.write("mixture temperature\n")

for i in range(0, len(x)):

    # Set mole fractions
    refrigerant.set_mole_fractions([x[i], 1-x[i]])

    refrigerant.update(CoolProp.PQ_INPUTS, pressure, 0)
    file_1.write(str("%f %f\n" % (x[i], refrigerant.T()-k)))

    if x[i]==0.5:
        file_3.write(str("%f %f\n" % (x[i], refrigerant.T()-k)))

    refrigerant.update(CoolProp.PQ_INPUTS, pressure, 1)
    file_2.write(str("%f %f\n" % (x[i], refrigerant.T()-k)))

    if x[i]==0.5:
        file_3.write(str("%f %f\n" % (x[i], refrigerant.T()-k)))


# Close files
file_1.close()
file_2.close()
file_3.close()