__author__ = 'Peter Eriksson @ KTH 2015'

import numpy as numpy
import CoolProp.CoolProp as CoolProp
import xlrd as xlrd
import os
import six
from matplotlib import pyplot

# Description:
# This file contains the main class Vcc. The Vcc instance is a complete vapor compression cycle.

# The instance is created with refrigerant data as input, which are generated in vcc_input.refrigerant(name)
# The refrigerant data is in the init because of recommendation from CoolProp,
# since an instance should not change refrigerant over time

# Next the input data must be set. The input data can be completely changed during calculations.as
# Or partially through the many set_ functions e.g set_condenser_temperature()

# The last input is the compressor data. From bitzer csv files can be downloaded for specific compressors and
# refrigerants. https://www.bitzer.de/websoftware/Calculate.aspx Make sure to convert the csv files to xls files and
# remove excess letters from condenser and evaporator range fields.

# To excecute the instance write instance.calculate()
# Afterwards all cycle data are made available.
# Plots can be made and points of interest retrieved

# Example:
# import vcc_functions
# import vcc_input
#
# input_data = vcc_input.manual()
# refrigerant_data = vcc_input.refrigerant('R404A')
# R404A = vcc_functions.Vcc(refrigerant_data)
# R404A.set_input_data(input_data)
# R404A.set_compressor_data('R404A-4FES-5Y.xls')
# R404A.calculate()
#
# print(R404A.p(0))
# R404A.output_list()
# R404A.plot_hlogp()

# <--- File begin --->

# Constants
k = 273.15

# Vapor compression cycle class
class Vcc:

    # Initiate class with definition of all variables specific to the instance
    def __init__(self, refrigerant_data):
        # Create instances of results
        self._T = numpy.zeros(10, dtype=numpy.float)  # Temperature
        self._p = numpy.zeros(10, dtype=numpy.float)  # Pressure
        self._h = numpy.zeros(10, dtype=numpy.float)  # Enthlapy
        self._s = numpy.zeros(10, dtype=numpy.float)  # Entropy
        self._d = numpy.zeros(10, dtype=numpy.float)  # Density
        self._x = numpy.zeros(10, dtype=numpy.float)  # Vapor mass quality
        self._h1k_is = 0

        # Points of interest
        self._description = numpy.zeros(10, dtype=numpy.object)
        self._description[0] = 'After suction line/ Before compressor'
        self._description[1] = 'After compressor / Before discharge line'
        self._description[2] = 'After discharge line / Condenser inlet'
        self._description[3] = 'Condenser dew point'
        self._description[4] = 'Condenser bubble point'
        self._description[5] = 'Condenser outlet / Before liquid line'
        self._description[6] = 'After liquid line / Before expansion valve'
        self._description[7] = 'After expansion valve / Evaporator inlet'
        self._description[8] = 'Evaporator dew point'
        self._description[9] = 'Evaporator outlet / Before suction line'

        # Evaporator
        self._ev_temperature = 0
        self._ev_super_heat = 0
        self._ev_pressure_drop = 0

        # Suction line
        self._sl_temperature_change = 0
        self._sl_pressure_drop = 0

        # Compressor
        self._capacity_volumetric = 0
        self._efficiency_isentropic = 0
        self._efficiency_volymetric = 0

        # Retrieved from "Analysis based on EU Regulation No 517/2014 of new HFC/HFO mixtures
        # as alternatives of high GWP refrigerants in refrigeration and HVAC systems"
        self._volumetric_flow_rate = 0.00653

        # Discharge line
        self._dl_temperature_change = 0
        self._dl_pressure_drop = 0

        # Condenser
        self._co_temperature = 0
        self._co_sub_cooling = 0
        self._co_pressure_drop = 0

        # Liquid line
        self._ll_temperature_change = 0
        self._ll_pressure_drop = 0

        # Data changed
        self._recalculate_condenser = True
        self._recalculate_evaporator = True

        # Initiate CoolProp with AbstractState meaning low-level interface
        self._refrigerant = CoolProp.AbstractState(refrigerant_data[1], refrigerant_data[2])

        # Set mole fractions
        self._refrigerant.set_mole_fractions(refrigerant_data[3])

        # Build custom composition envelope
        self._refrigerant.build_phase_envelope(refrigerant_data[0])

        # Instantiate compressor
        self._compressor = Compressor()

    def calculate_condenser(self):
        # Calculating the pressure in the middle of the condensator

        # Find a start point for the pressure in the middle of the evaporator
        self._refrigerant.update(CoolProp.QT_INPUTS, 0.5, self._co_temperature)
        p_co_mid = self._refrigerant.p()

        # Start value of the error term
        p_co_corr = 1e5

        # Error of 1 Pascal
        while abs(p_co_corr) > 1:
            # Inlet and outlet is symetric arround the evaporator middle
            p_co_inlet = p_co_mid+self._co_pressure_drop/2
            p_co_outlet = p_co_mid-self._co_pressure_drop/2

            # Inlet data
            self._refrigerant.update(CoolProp.PQ_INPUTS, p_co_inlet, 1)
            t_co_inlet = self._refrigerant.T()

            # Outlet data
            self._refrigerant.update(CoolProp.PQ_INPUTS, p_co_outlet, 0)
            t_co_outlet = self._refrigerant.T()

            # Objective, minimize following
            # This is the temperature difference, since the temperature drop is almos linear it applys to all points
            # As well inlet as outlet and mid
            t_co_diff = t_co_inlet/2 + t_co_outlet/2 - self._co_temperature

            # Evaluate the pressure at the inlet generated given the temperature correction
            self._refrigerant.update(CoolProp.QT_INPUTS, 1, t_co_inlet - t_co_diff)
            p_co_corr = self._refrigerant.p() - p_co_inlet

            # Correct the pressure
            p_co_mid += p_co_corr

            #print 'Pg', p_co_mid, 'Ti', t_co_inlet-k, 'To', t_co_outlet-k, ' Td', t_co_diff, ' Pc', p_co_corr

        # Condenser inlet
        self._p[3] = p_co_mid+self._co_pressure_drop/2
        self._refrigerant.update(CoolProp.PQ_INPUTS, self._p[3], 1)
        self._T[3] = self._refrigerant.T()
        self._h[3] = self._refrigerant.hmass()
        self._s[3] = self._refrigerant.smass()
        self._d[3] = self._refrigerant.rhomass()

        # Condenser outlet
        self._p[4] = p_co_mid-self._co_pressure_drop/2
        self._refrigerant.update(CoolProp.PQ_INPUTS, self._p[4], 0)
        self._T[4] = self._refrigerant.T()
        self._h[4] = self._refrigerant.hmass()
        self._s[4] = self._refrigerant.smass()
        self._d[4] = self._refrigerant.rhomass()

        # Condenser outlet / Before liquid line
        # Same pressure as at bubble point in condenser
        self._p[5] = self._p[4]

        # The temperature is relative to the on at the bubble point
        self._T[5] = self._T[4] - self._co_sub_cooling

        #  If sub cooling is the case,  switch point from the envelope with the specified sub cooling
        if self._co_sub_cooling != 0:
            self._refrigerant.update(CoolProp.PT_INPUTS, self._p[5], self._T[5])

        self._h[5] = self._refrigerant.hmass()
        self._s[5] = self._refrigerant.smass()
        self._d[5] = self._refrigerant.rhomass()

        # After liquid line / Before expansion valve
        self._p[6] = self._p[5] - self._ll_pressure_drop
        self._T[6] = self._T[5] - self._ll_temperature_change

        if self._ll_pressure_drop != 0 or self._ll_temperature_change != 0:
            self._refrigerant.update(CoolProp.PT_INPUTS, self._p[6], self._T[6])

        self._h[6] = self._refrigerant.hmass()
        self._s[6] = self._refrigerant.smass()
        self._d[6] = self._refrigerant.rhomass()

        self._recalculate_condenser = False

        return True

    def calculate_evaporator(self):
        # The enthalpy before expansion valve is the same as after the valve because the expansion valve
        # doesn't perform any thermodynamic work. It's just a trade in specific volume, pressure and temperature.
        self._h[7] = self._h[6]

        # Start by guessing at Q = 0.667 since according to the Honeywell recommendation the temperature in the evaporator
        # is 1/3 of bubble temperature and 2/3 och dew temperature for a given pressure.

        # This gives an estimated pressure in the middle of the evaporator
        self._refrigerant.update(CoolProp.QT_INPUTS, 0.667, self._ev_temperature)
        p_ev_mid = self._refrigerant.p()

        # Start value of the error term
        p_ev_corr = 1e5

        # Error of 1 Pascal allowed
        while abs(p_ev_corr) > 1:

            # Inlet and outlet pressure is symmetric around the evaporator middle pressure
            p_ev_inlet = p_ev_mid+self._ev_pressure_drop/2
            p_ev_outlet = p_ev_mid-self._ev_pressure_drop/2

            # Inlet data
            self._refrigerant.update(CoolProp.HmassP_INPUTS, self._h[7], p_ev_inlet)
            q_ev_inlet = self._refrigerant.Q()
            t_ev_inlet = self._refrigerant.T()

            # Outlet data
            self._refrigerant.update(CoolProp.PQ_INPUTS, p_ev_outlet, 1)
            t_ev_outlet = self._refrigerant.T()

            # Objective, minimize following:

            # This is the temperature difference, since the temperature drop along the vapor mass quality property is almost
            # linear it applies to all points, as well inlet as outlet and mid
            t_ev_diff = t_ev_inlet/2 + t_ev_outlet/2 - self._ev_temperature

            # Evaluate the pressure at the inlet generated given the temperature correction
            self._refrigerant.update(CoolProp.QT_INPUTS, q_ev_inlet, t_ev_inlet - t_ev_diff)
            p_ev_corr = self._refrigerant.p() - p_ev_inlet

            # Correct the pressure
            p_ev_mid += p_ev_corr

            #print 'Pg', p_ev_mid, 'Ti', t_ev_inlet-k, 'To', t_ev_outlet-k, ' Td', t_ev_diff, ' Qg', q_ev_inlet, ' Pc', p_ev_corr

        # Assign pressures
        self._p[7] = p_ev_mid+self._ev_pressure_drop/2

        # This code line makes more sence since it follows the logic of the condenser
        self._p[8] = p_ev_mid-self._ev_pressure_drop/2

        # TODO The following two lines makes the output identical with the Genetron software but I'm not able to
        # motivate these lines. For future work these remain but for now i go further with what I can motivate.
        #self._p[8] = p_ev_mid
        #self._p[9] = p_ev_mid-self._ev_pressure_drop/2

        #  With pressure and enthalpy know the rest of the states is known.
        self._refrigerant.update(CoolProp.HmassP_INPUTS, self._h[7], self._p[7])
        self._T[7] = self._refrigerant.T()
        self._s[7] = self._refrigerant.smass()
        self._d[7] = self._refrigerant.rhomass()
        self._x[7] = self._refrigerant.Q()

        # <--- Evaporator dew point --->
        self._refrigerant.update(CoolProp.PQ_INPUTS, self._p[8], 1)
        self._T[8] = self._refrigerant.T()
        self._h[8] = self._refrigerant.hmass()
        self._s[8] = self._refrigerant.smass()
        self._d[8] = self._refrigerant.rhomass()

        # <--- Evaporator outlet / Before suction line --->
        # TODO The following line comes with the above stated issue of genetron inequality that I can't motivate
        #self._T[9] = self._T[8] + self._ev_super_heat

        # I'm using these lines instead
        self._p[9] = self._p[8]
        self._T[9] = self._T[8] + self._ev_super_heat

        #  Now calculate the rest of the properties. All though it must be
        #  decided whether it is a super heating or not. Otherwise the calculation
        #  comes to close to the dividing accuracy and the calculation fails.
        #  In other word, calculate as the point is on the envelope when 0
        #  super heating is the case.
        if self._ev_super_heat == 0:
            self._refrigerant.update(CoolProp.PQ_INPUTS, self._p[9], 1)
        else:
            self._refrigerant.update(CoolProp.PT_INPUTS, self._p[9], self._T[9])

        #  Oh again? Yes every time...
        self._h[9] = self._refrigerant.hmass()
        self._s[9] = self._refrigerant.smass()
        self._d[9] = self._refrigerant.rhomass()

        # The evaporator is done calculated until changes that affects the data calls for recalculation
        self._recalculate_evaporator = False

        return True

    def calculate(self):
        # Begin calculations

        # <---- Condenser ---->
        if self._recalculate_condenser:
            self.calculate_condenser()

        # <---- Evaporator ---->
        if self._recalculate_evaporator:
            self.calculate_evaporator()

        # <---- Compressor inlet / Suction line outlet ---->
        #  The effects of the suction line are applied
        self._p[0] = self._p[9] - self._sl_pressure_drop
        self._T[0] = self._T[9] + self._sl_temperature_change

        #  To close values to the envelope returns errors. As mentioned before.
        if self._ev_super_heat == 0 and self._sl_temperature_change == 0:
            self._refrigerant.update(CoolProp.QT_INPUTS, 1, self._T[0])
        else:
            self._refrigerant.update(CoolProp.PT_INPUTS, self._p[0], self._T[0])

        # Oh here we go again...
        self._h[0] = self._refrigerant.hmass()
        self._s[0] = self._refrigerant.smass()
        self._d[0] = self._refrigerant.rhomass()

        # <---- Compressor outlet / Discharge line inlet ---->
        self._p[1] = self._p[3] + self._dl_pressure_drop

        #  Now it's interesting. The entropy before the compressor and the
        #  pressure afterwards results in the isentropic state after the compressor.
        self._refrigerant.update(CoolProp.PSmass_INPUTS, self._p[1], self._s[0])
        self._h[1] = self._h1k_is = self._refrigerant.hmass()

        # Calculate compressor performance
        self._compressor.calculate(self._ev_temperature, self._co_temperature)

        # If a compressor file is loaded and read proceed
        if self._compressor.EN12900:
            # Real compressor data
            self._h[1] = self._h[0] + self._compressor.specific_power()
        else:
            if self._compressor.set_efficiency != 0:
                #  With known isentropic efficency and enthalpy before and after the
                #  compressor, the enthalpy can be calculated.
                self._h[1] = (self._h1k_is - self._h[0]) / self._compressor.set_efficiency + self._h[0]

        # With the enthalpy and pressure know: give me the values knoooow!
        self._refrigerant.update(CoolProp.HmassP_INPUTS, self._h[1], self._p[1])
        self._T[1] = self._refrigerant.T()
        self._s[1] = self._refrigerant.smass()
        self._d[1] = self._refrigerant.rhomass()

        # <---- Discharge line outlet / Condenser inlet ---->
        # Pressure is the same as at the condenser inlet
        self._p[2] = self._p[3]

        # Subtract the temperature from the compressor outlet temperature
        self._T[2] = self._T[1] - self._dl_temperature_change

        # Calculate
        self._refrigerant.update(CoolProp.PT_INPUTS, self._p[2], self._T[2])

        # Assign results
        self._h[2] = self._refrigerant.hmass()
        self._s[2] = self._refrigerant.smass()
        self._d[2] = self._refrigerant.rhomass()

        return True

    # <--- Performance data --->

    def discharge_temperature(self):

        return self._T[1]

    def mass_flow_rate(self):
        # Is the compressor modeled with polynomial or fixed value
        if self._compressor.EN12900:
            # m dot from compressor
            return self._compressor.mass_flow_rate()
        else:
            # m dot theoretical
            return self._volumetric_flow_rate * self._d[0]

    def compressor_power(self):

        return self.compressor_specific_power() * self.mass_flow_rate()

    def compressor_specific_power(self):

        if self._compressor.EN12900:
            return self._compressor.specific_power()
        else:
            return self._h[1]-self._h[0]

    def volumetric_flow_rate(self):
        # V dot index 2
        return self.mass_flow_rate() / (self._d[0])

    def cooling_capacity(self):
        # Q dot
        return self.mass_flow_rate() * (self._h[0] - self._h[6])

    def volumetric_cooling_capacity(self):
        # enthalpy at the compressor inlet - enthalpy at evaporator inlet / specific volume at compressor inlet
        return (self._h[0] - self._h[6]) * self._d[0]

    def cop_1(self):
        # Heating COP1
        # Enthalpy(Expansion valve to Compressor outlet) / (Compressor intel to outlet)
        return (self._h[1] - self._h[6]) / (self._h[1] - self._h[0])

    def cop_2(self):
        # Cooling COP2
        # Enthalpy(Expansion valve to Compressor inlet) / (Compressor intel to outlet)
        return (self._h[0] - self._h[7]) / (self._h[1] - self._h[0])

    def isentropic_efficiency(self):
        # Isentropic
        return (self._h1k_is - self._h[0])/(self._h[1] - self._h[0])

    # <--- Print data --->

    def output_list(self, mode=0):
        # Print
        print('   id       t          p        h          s          d         x')

        for i in range(0,10):
            if (i not in (3, 4, 8) and mode == 1) or mode == 0:
                print('%6s %6.2f %10.4f %8.2f %10.4f %10.4f %10.1f   %s' %
                    (
                        i,
                        self._T[i]-k,
                        self._p[i]/1e3,
                        self._h[i]/1e3,
                        self._s[i]/1e3,
                        self._d[i],
                        self._x[i]*1e2,
                        self._description[i]
                    ))

    def compare_list(self, reference_data):
        # Print
        print('   id       t          p        h          s          d         x')

        for i in range(0,10):
            if i not in (3, 4, 8):
                print('%6s %6.2f %10.4f %8.2f %10.4f %10.4f %10.1f   %s' %
                    (
                        i,
                        abs((self._T[i] - reference_data[i, 0]) / reference_data[i, 0])*1e2,
                        abs((self._p[i] - reference_data[i, 1]) / reference_data[i, 1])*1e2,
                        abs((self._h[i] - reference_data[i, 2]) / reference_data[i, 2])*1e2,
                        abs((self._s[i] - reference_data[i, 3]) / reference_data[i, 3])*1e2,
                        abs((self._d[i] - reference_data[i, 4]) / reference_data[i, 4])*1e2,
                        abs(self._x[i] - reference_data[i, 5])*1e2 if (i == 7) else 0,
                        self._description[i]
                    ))

    # <--- Plot --->

    def build_envelope(self, resolution=40):

        # Get the temperature at minimum pressure at 1 bar
        # Below is uninteresting since during leakage the air would leak in instead of refrigerant out.
        self._refrigerant.update(CoolProp.PQ_INPUTS, 0.5e5, 0)
        self.temperature_min = self._refrigerant.T()

        # Get the critical temperature, top of the two-phase plot
        self.temperature_critical = self._refrigerant.true_critical_point()[0]

        # Create a vector with temperatures
        self.temperature_range = numpy.linspace(self.temperature_min, self.temperature_critical, resolution)

        # The data matrix
        bubble_h, bubble_p = [], []
        dew_h, dew_p = [], []

        # Loop through all temperatures
        for i in range(0, len(self.temperature_range)):
            # Calculate the envelope for Q = 0
            self._refrigerant.update(CoolProp.QT_INPUTS, 0, self.temperature_range[i])
            bubble_h.append(self._refrigerant.hmass()/1e3)
            bubble_p.append(self._refrigerant.p()/1e5)

            # Calculate the envelope for Q = 1
            self._refrigerant.update(CoolProp.QT_INPUTS, 1, self.temperature_range[i])
            dew_h.append(self._refrigerant.hmass()/1e3)
            dew_p.append(self._refrigerant.p()/1e5)

        # Repair top
        repair_h = numpy.array([bubble_h[-2], bubble_h[-1], dew_h[-1], dew_h[-2]])
        repair_p = numpy.array([bubble_p[-2], bubble_p[-1], dew_p[-1], dew_p[-2]])
        repair_func = numpy.poly1d(numpy.polyfit(repair_h, repair_p, 3))

        # The gap range
        repair_from = bubble_h[-1]
        repair_to = dew_h[-1]
        repair_range = numpy.linspace(repair_from, repair_to, 10)

        # Add pressures and enthalpies calculated for the gap
        for r in range(1, len(repair_range)-1):
            bubble_h.append(repair_range[r])
            bubble_p.append(repair_func(repair_range[r]))

        # Return a combined bubble and dew boundary in enthalpy and pressure, with the repaired top
        return {'h': numpy.append(bubble_h, numpy.flipud(dew_h), 1), 'p': numpy.append(bubble_p, numpy.flipud(dew_p), 1)}

    def plot_hlogp(self):
        # Initialize
        ax = pyplot.subplot()
        ax.set_yscale('log')

        # Retrieve envelope
        envelope = self.build_envelope()

        # Plot the saturation curves
        pyplot.plot(envelope['h'], envelope['p'], '-k')

        # Plot the process
        pyplot.plot([self._h[9]/1e3, self._h[8]/1e3, self._h[7]/1e3, self._h[6]/1e3,
                     self._h[5]/1e3, self._h[4]/1e3, self._h[3]/1e3, self._h[2]/1e3,
                     self._h[1]/1e3, self._h[0]/1e3, self._h[9]/1e3],
                    [self._p[9]/1e5, self._p[8]/1e5, self._p[7]/1e5, self._p[6]/1e5,
                     self._p[5]/1e5, self._p[4]/1e5, self._p[3]/1e5, self._p[2]/1e5,
                     self._p[1]/1e5, self._p[0]/1e5, self._p[9]/1e5], '-or')

        # Plot the isentropic efficiency
        pyplot.plot([self._h[0]/1e3, self._h1k_is/1e3], [self._p[0]/1e5, self._p[1]/1e5],'--')

        # Labels
        pyplot.xlabel("Enthalpy [kJ/kg]")
        pyplot.ylabel("Pressure [bar]")

        # Add grid
        pyplot.grid()

        # And display!
        pyplot.show()

        return True

    def plot_sT(self):

        # Initialize plot
        fig = pyplot.figure()
        ax = fig.add_subplot(111)

        # Get the temperature at minimum pressure at 1 bar
        # Below is uninteresting since during leakage the air would leak in instead of refrigerant out.
        self._refrigerant.update(CoolProp.PQ_INPUTS, 1e5, 0)
        temperature_min = self._refrigerant.T()

        # Get the critical temperature, top of the two-phase plot
        temperature_critical = self._refrigerant.true_critical_point()[0]

        # Create a vector with temperatures
        temperature_range = numpy.linspace(temperature_min, temperature_critical, 40)

        # The data matrix
        bubble, dew = [], []

        for i in range(0, len(temperature_range)):
            # Calculate the envelope for Q = 0
            self._refrigerant.update(CoolProp.QT_INPUTS, 0, temperature_range[i])
            bubble.append(self._refrigerant.smass()/1e3)

            # Calculate the envelope for Q = 1
            self._refrigerant.update(CoolProp.QT_INPUTS, 1, temperature_range[i])
            dew.append(self._refrigerant.smass()/1e3)

        # Plot the saturation curves
        ax.plot(bubble, temperature_range-k, '-k')
        ax.plot(dew, temperature_range-k, '-k')

        # Plot the process
        ax.plot([self._s[9]/1e3, self._s[8]/1e3, self._s[7]/1e3, self._s[6]/1e3,
                 self._s[5]/1e3, self._s[4]/1e3, self._s[3]/1e3, self._s[2]/1e3,
                 self._s[1]/1e3, self._s[0]/1e3, self._s[9]/1e3],
                [self._T[9]-k, self._T[8]-k, self._T[7]-k, self._T[6]-k,
                 self._T[5]-k, self._T[4]-k, self._T[3]-k, self._T[2]-k,
                 self._T[1]-k, self._T[0]-k, self._T[9]-k], '-or')

        # Labels
        pyplot.xlabel("Entropy [kJ/kgK]")
        pyplot.ylabel("Temperature [C]")

        # Add grid
        ax.grid()

        # And action!
        pyplot.show()

        return True

    # <--- Set data --->

    def set_input_data(self, input_data):

        # Evaporator
        self._ev_temperature = input_data["ev_temperature"]
        self._ev_super_heat = input_data["ev_super_heat"]
        self._ev_pressure_drop = input_data["ev_pressure_drop"]

        # Suction line
        self._sl_temperature_change = input_data["sl_temperature_change"]
        self._sl_pressure_drop = input_data["sl_pressure_drop"]

        # Compressor
        self._capacity_volumetric = input_data["capacity_volumetric"]
        self._efficiency_isentropic = input_data["efficiency_isentropic"]
        self._efficiency_volymetric = input_data["efficiency_volymetric"]

        # Discharge line
        self._dl_temperature_change = input_data["dl_temperature_change"]
        self._dl_pressure_drop = input_data["dl_pressure_drop"]

        # Condenser
        self._co_temperature = input_data["co_temperature"]
        self._co_sub_cooling = input_data["co_sub_cooling"]
        self._co_pressure_drop = input_data["co_pressure_drop"]

        # Liquid line
        self._ll_temperature_change = input_data["ll_temperature_change"]
        self._ll_pressure_drop = input_data["ll_pressure_drop"]

        return True

    def set_volumetric_flow_rate(self, value):

        if float(value) == value:
            if self._volumetric_flow_rate != value:
                self._volumetric_flow_rate = value

        return True

    def set_compressor_data(self, compressor_data):

        self._compressor.set(compressor_data)

        self._recalculate_evaporator = True
        self._recalculate_condenser = True

        return True

    def set_sub_cooling(self, value):
        if float(value) == value:
            if self._co_sub_cooling != value:
                self._recalculate_condenser = True
                self._recalculate_evaporator = True
                self._co_sub_cooling = value

    def set_super_heating(self, value):
        if float(value) == value:
            if self._ev_super_heat != value:
                self._recalculate_evaporator = True
                self._ev_super_heat = value

    def set_condenser_temperature(self, value):
        if float(value) == value:
            if self._co_temperature != value:
                self._recalculate_condenser = True
                self._recalculate_evaporator = True
                self._co_temperature = value

    def set_evaporator_temperature(self, value):
        if float(value) == value:
            if self._ev_temperature != value:
                self._recalculate_evaporator = True
                self._ev_temperature = value

    # <--- get variables --->
    def T(self, index):
        return self._T[index]

    def p(self, index):
        return self._p[index]

    def h(self, index):
        return self._h[index]

    def s(self, index):
        return self._s[index]

    def d(self, index):
        return self._d[index]

    def x(self, index):
        return self._x[index]

class Compressor:

    def __init__(self):
        self.parameters = numpy.zeros((4,10), numpy.float)
        self.EN12900 = False

        self.set_efficiency = 0

        self._tc_min = 0
        self._tc_max = 0
        self._to_min = 0
        self._to_max = 0

        self._Q = 1000
        self._P = 1000
        self._m = 3600
        self._I = 10

        self._refrigerant_name = ""

    def set(self, object):
        # object=filename or isentropic efficiencyt as float

        if isinstance(object, six.string_types):
            if os.path.isfile(os.path.join(os.getcwd(), 'input', 'compressor', object)):
                # https://www.bitzer.de/websoftware/Calculate.aspx
                workbook = xlrd.open_workbook(os.path.join(os.getcwd(), 'input', 'compressor', object))
                print('Loaded compressor data: ' + object)

                # Set working sheet
                worksheet = workbook.sheet_by_index(0)

                # Refrigerant name
                self._refrigerant_name = worksheet.cell_value(12,3)

                # Polynomial parameters
                for r in range(0,4):
                    for c in range(0,10):
                        self.parameters[r,c] = worksheet.cell_value(27+r,1+c)

                # Boundaries
                self._tc_min = worksheet.cell_value(35, 3) + k
                self._tc_max = worksheet.cell_value(35, 5) + k

                self._to_min = worksheet.cell_value(34, 3) + k
                self._to_max = worksheet.cell_value(34, 5) + k

                self.EN12900 = True

            else:
                print(os.path.join(os.getcwd(), 'input', 'compressor', object))
                print('Crompressor xls file no found, continuing with isentropic efficiency of: 1')
                self.EN12900 = False
        elif isinstance(object, float):
            self.set_efficiency = object
            self.EN12900 = False

        else:
            print('Crompressor set: Error')

    def calculate(self, ev_temperature, co_temperature):
        if self.EN12900:
            if ev_temperature <= self._to_max and ev_temperature >= self._to_min:
                if co_temperature <= self._tc_max and co_temperature >= self._tc_min:
                    self._Q = self.core(0, ev_temperature, co_temperature)
                    self._P = self.core(1, ev_temperature, co_temperature)
                    self._m = self.core(2, ev_temperature, co_temperature)
                    self._I = self.core(3, ev_temperature, co_temperature)

                    return True
                else:
                    print(self._refrigerant_name + " compressor error: Condenser temperature out of range")
                    print("Min: " + str(self._tc_min-k) + " Is: " + str(co_temperature-k) + " Max: " + str(self._tc_max-k))
            else:
                print(self._refrigerant_name + " compressor error: Evaporator temperature out of range")
                print("Min: " + str(self._to_min-k) + " Is: " + str(ev_temperature-k) + " Max: " + str(self._to_max-k))
        else:

            return True

        return False

    def core(self, mode, ev_temperature, co_temperature):
        # EN 12900
        # y = c1 + c2*to + c3*tc + c4*to^2 + c5*to*tc + c6*tc^2 + c7*to^3 + c8*tc*to^2 + c9*to*tc^2 + c10*tc^3
        to = ev_temperature-k
        tc = co_temperature-k
        return self.parameters[mode, 0] + \
               self.parameters[mode, 1]*to + \
               self.parameters[mode, 2]*tc + \
               self.parameters[mode, 3]*numpy.power(to, 2) + \
               self.parameters[mode, 4]*to*tc + \
               self.parameters[mode, 5]*numpy.power(tc, 2) + \
               self.parameters[mode, 6]*numpy.power(to, 3) + \
               self.parameters[mode, 7]*tc*numpy.power(to, 2) + \
               self.parameters[mode, 8]*to*numpy.power(tc, 2) + \
               self.parameters[mode, 9]*numpy.power(tc, 3)

    def mass_flow_rate(self):
        # Unit: kg/s
        return self._m / 3600

    def specific_power(self):
        # Unit: j/kg
        return self._P / self.mass_flow_rate()

def data_intersect(a_x, a_y, b_x, b_y):

    # Combined x vector
    c_x = numpy.union1d(a_x, b_x)

    # Shift register
    a_i = [0, 0]
    a_s = 0
    b_i = [0, 0]
    b_s = 0

    # Loop through all x values
    for i in range(0, len(c_x)):

        # Search for instance of x value
        a_w = numpy.where(a_x==c_x[i])[0]
        b_w = numpy.where(b_x==c_x[i])[0]

        # In vector a?
        if len(a_w) > 0:
            # Shift the array index
            a_i[0] = a_i[1]
            a_i[1] = a_w[0]
            a_s += 1

        # In vector b?
        if len(b_w) > 0:
            # Shift the array index
            b_i[0] = b_i[1]
            b_i[1] = b_w[0]
            b_s += 1

        # Is there ar flip of values?
        # Meaning that the shif registers indicates a intersection
        if a_s >= 2 and b_s >= 2:
            if (a_y[a_i[0]] > b_y[b_i[0]] and a_y[a_i[1]] < b_y[b_i[1]]) or \
               (a_y[a_i[0]] < b_y[b_i[0]] and a_y[a_i[1]] > b_y[b_i[1]]):

                a_s = 0
                b_s = 0

                p_a = numpy.polyfit([a_x[a_i[0]], a_x[a_i[1]]], [a_y[a_i[0]], a_y[a_i[1]]], 1)
                p_b = numpy.polyfit([b_x[b_i[0]], b_x[b_i[1]]], [b_y[b_i[0]], b_y[b_i[1]]], 1)
                p_c = p_a - p_b

                print("intersection at: " + str(numpy.roots(p_c)[0]))

                val_a = numpy.polyval(p_a, c_x)
                val_b = numpy.polyval(p_b, c_x)

                #pyplot.plot(a_x, a_y, '*r')
                #pyplot.plot(c_x, val_a, '-r')

                #pyplot.plot(b_x, b_y, '*b')
                #pyplot.plot(c_x, val_b, '-b')
                #pyplot.show()
