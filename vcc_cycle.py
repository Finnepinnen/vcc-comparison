__author__ = 'Peter Eriksson @ KTH 2015'

import vcc_input
import vcc_functions

# Description:
# This file describes the vcc cycle for the introduction

# Scientific parameters
k = 273.15
folder = '../../Report/LaTeX/data/'

# Load input data from file
input_data = {}

# Evaporator
input_data["ev_temperature"] = -20 + k	        # [C] Evaporator temperature
input_data["ev_super_heat"] = 20			        # [K] Evaporator outlet super heating
input_data["ev_pressure_drop"] = 100e3		    # [Pa] Evaporator pressure drop

# Suction line
input_data["sl_temperature_change"] = 20	        # [K] Superheat (Suction line)
input_data["sl_pressure_drop"] = 10e3		    # [Pa] Suction Line

# Compressor
input_data["capacity_volumetric"] = 1
input_data["efficiency_isentropic"] = 0.8		    # [-] Isentropic Efficiency 0=Bitzer data
input_data["efficiency_volymetric"] = 1		    # [-] Volymetric Efficiency

# Discharge line
input_data["dl_temperature_change"] = 40          # [K] Superheat (Suction line)
input_data["dl_pressure_drop"] = 100e3            # [K] Superheat (Suction line)

# Condenser
input_data["co_temperature"] = 40 + k		        # [C] Temperature
input_data["co_sub_cooling"] = 15		        # [K] Outlet super cooling
input_data["co_pressure_drop"] = 600e3            # [Pa] Pressure drop

# Liquid line
input_data["ll_temperature_change"] = 8          # [K] Superheat (Suction line)
input_data["ll_pressure_drop"] = 300e3            # [K] Superheat (Suction line)

# Set refrigerant data
ref_R404A = vcc_input.refrigerant("R449A")

# Instatiate system data for refrigerant respectively
R404A = vcc_functions.Vcc(ref_R404A)
R404A.set_input_data(input_data)
#R404A.set_compressor_data('R449A-4FES-5Y.xls')
R404A.set_compressor_data(input_data["efficiency_isentropic"])

R404A.calculate()
envelope = R404A.build_envelope()

# Write the envelope
file_envelope = open(str("%s%s.dat" % (folder, 'Nomenclature-envelope')), 'w+')
file_envelope.write("ethalpy pressure\n")

for f in range(0, len(envelope['p'])):
    file_envelope.write(str("%f %f\n" % (envelope['h'][f], envelope['p'][f])))

file_envelope.close()

# Write the cycle
file_cycle = open(str("%s%s.dat" % (folder, 'Nomenclature-cycle')), 'w+')
file_cycle.write("ethalpy pressure\n")

for f in range(-1, 10):
    file_cycle.write(str("%f %f\n" % (R404A._h[f]/1e3, R404A._p[f]/1e5)))

file_cycle.close()


# Write the hs
file_hs = open(str("%s%s.dat" % (folder, 'Nomenclature-hs')), 'w+')
file_hs.write("ethalpy pressure\n")

file_hs.write(str("%f %f\n" % (R404A._h[7]/1e3, R404A._p[7]/1e5)))
file_hs.write(str("%f %f\n" % (R404A._h[7]/1e3, 0.5)))

file_hs.close()

# Write the h2k
file_h1k = open(str("%s%s.dat" % (folder, 'Nomenclature-h1k')), 'w+')
file_h1k.write("ethalpy pressure\n")

file_h1k.write(str("%f %f\n" % (R404A._h[1]/1e3, R404A._p[1]/1e5)))
file_h1k.write(str("%f %f\n" % (R404A._h[1]/1e3, 0.5)))

file_h1k.close()

# Write the h2k
file_h2k = open(str("%s%s.dat" % (folder, 'Nomenclature-h2k')), 'w+')
file_h2k.write("ethalpy pressure\n")

file_h2k.write(str("%f %f\n" % (R404A._h[0]/1e3, R404A._p[0]/1e5)))
file_h2k.write(str("%f %f\n" % (R404A._h[0]/1e3, 0.5)))

file_h2k.close()

# Write the h1kis-line
file_h1kis_line = open(str("%s%s.dat" % (folder, 'Nomenclature-h1kis-line')), 'w+')
file_h1kis_line.write("ethalpy pressure\n")

file_h1kis_line.write(str("%f %f\n" % (R404A._h[0]/1e3, R404A._p[0]/1e5)))
file_h1kis_line.write(str("%f %f\n" % (R404A._h1k_is/1e3, R404A._p[1]/1e5)))

file_h1kis_line.close()


# Write the h1kis
file_h1kis = open(str("%s%s.dat" % (folder, 'Nomenclature-h1kis')), 'w+')
file_h1kis.write("ethalpy pressure\n")

file_h1kis.write(str("%f %f\n" % (R404A._h1k_is/1e3, R404A._p[1]/1e5)))
file_h1kis.write(str("%f %f\n" % (R404A._h1k_is/1e3, 0.5)))

file_h1kis.close()


# Write the p1m
file_p1m = open(str("%s%s.dat" % (folder, 'Nomenclature-p1m')), 'w+')
file_p1m.write("ethalpy pressure\n")

file_p1m.write(str("%f %f\n" % ((R404A.h(3)+R404A.h(4))/2e3, (R404A.p(3)+R404A.p(4))/2e5-0.1)))
file_p1m.write(str("%f %f\n" % (50, (R404A.p(3)+R404A.p(4))/2e5-0.1)))

file_p1m.close()

# Write the p1m
file_p2m = open(str("%s%s.dat" % (folder, 'Nomenclature-p2m')), 'w+')
file_p2m.write("ethalpy pressure\n")

file_p2m.write(str("%f %f\n" % ((R404A.h(7)+R404A.h(8))/2e3, (R404A.p(7)+R404A.p(8))/2e5-0.05)))
file_p2m.write(str("%f %f\n" % (50, (R404A.p(7)+R404A.p(8))/2e5-0.05)))

file_p2m.close()