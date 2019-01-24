__author__ = 'Peter Eriksson @ KTH 2015'

import numpy as numpy
import CoolProp.CoolProp as CoolProp

# Description:
# This file generates data for LaTeX to render an illustration of the envelope, 2-phase region and the critical point

# Initiate CoolProp with AbstractState meaning low-level interface
refrigerant = CoolProp.AbstractState("REFPROP","R1234yf")

# Get the temperature at minimum pressure at 1 bar
# Below is uninteresting since during leakage the air would leak in instead of refrigerant out.
refrigerant.update(CoolProp.PQ_INPUTS, 1e5, 0)
temperature_min = refrigerant.T()

# Get the critical temperature, top of the two-phase plot
temperature_critical = refrigerant.true_critical_point()[0]

refrigerant.update(CoolProp.QT_INPUTS, 0, temperature_critical)
pressure_critical = refrigerant.p()
enthalpy_critical = refrigerant.hmass()

# Create a vector with temperatures
temperatures = numpy.linspace(temperature_min, temperature_critical, 50)

# Open files
file_1 = open('../../Report/LaTeX/data/envelope_bubble.dat', 'w+')
file_2 = open('../../Report/LaTeX/data/envelope_dew.dat', 'w+')
file_3 = open('../../Report/LaTeX/data/envelope_crit.dat', 'w+')

file_1.write("ethalpy pressure\n")
file_2.write("ethalpy pressure\n")
file_3.write("ethalpy pressure\n")

# Loop through all temperatures
for i in range(0, len(temperatures)):

    # Calculate the envelope for Q = 0
    refrigerant.update(CoolProp.QT_INPUTS, 0, temperatures[i])
    file_1.write(str("%f %f\n" % (refrigerant.hmass()/1e3, refrigerant.p()/1e5)))

    # Calculate the envelope for Q = 1
    refrigerant.update(CoolProp.QT_INPUTS, 1, temperatures[i])
    file_2.write(str("%f %f\n" % (refrigerant.hmass()/1e3, refrigerant.p()/1e5)))

file_2.write(str("%f %f\n" % (enthalpy_critical/1e3, pressure_critical/1e5)))
file_3.write(str("%f %f\n" % (enthalpy_critical/1e3, pressure_critical/1e5)))
file_3.write(str("%f %f\n" % (enthalpy_critical/1e3, 120)))

# Close files
file_1.close()
file_2.close()
file_3.close()
