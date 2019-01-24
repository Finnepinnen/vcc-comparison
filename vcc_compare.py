__author__ = 'PeterE-Mac'

import vcc_input
import vcc_functions
import numpy
import time
import pprint
import matplotlib.pyplot as pyplot
import scipy

start = time.time()

input_data = vcc_input.real_system2()

k = 273.15

# Evaluation range condenser
t_cond_mid = 35 + k     # Fix temperature middle
#t_cond_mid = 30 + k     # Fix temperature middle
t_cond_high = 55 + k    # Fix temperature high

t_cond_min = 10 + k     # Range from
t_cond_max = 55 + k     # Range to
t_cond_res = 10         # Range resolution
t_cond = numpy.linspace(t_cond_min, t_cond_max, t_cond_res)

# Evaluation range evaporator
t_evap_mid = -5 + k     # Fix temperature middle
t_evap_low = -35 + k    # Fix temperature high

t_evap_min = -40 + k    # Range from
t_evap_max = 0 + k      # Range to
t_evap_res = 30         # Range resolution
t_evap = numpy.linspace(t_evap_min, t_evap_max, t_evap_res)

# Refrigerants to compare
refs = ["R404A", "R448A", "R449A"]
#compressor_extension = '-4FES-5Y.xls'
compressor_extension = '-4GE-30Y.xls'

# Operations of comparison
ops = [
        # <--- Middle temperature --->

        # Coefficient of performance
        {
            'name':'COP2_M',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".cop_2()"',
            'calc_intersect':True
        },
        {
            'name':'COP2_MR',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".cop_2()-VCC_"+ref+".cop_2())/VCC_"+ref+".cop_2()*1e2"'
        },



        # Volumetric refrigerating effect
        {
            'name':'Volumetric-cooling-capacity_M',
            'xlabel':'evaporator',
            'ylabel':'volumetric',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".volumetric_cooling_capacity()/1e3"',
            'calc_intersect':True
        },
        {
            'name':'Volumetric-cooling-capacity_MR',
            'xlabel':'evaporator',
            'ylabel':'volumetric',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".volumetric_cooling_capacity()-VCC_"+ref+".volumetric_cooling_capacity())/VCC_"+ref+".volumetric_cooling_capacity()*1e2"'
        },

        # Discharge temperature
        {
            'name':'Discharge-temperature_M',
            'xlabel':'evaporator',
            'ylabel':'discharge',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".discharge_temperature() - k"'
        },
        {
            'name':'Discharge-temperature_MR',
            'xlabel':'evaporator',
            'ylabel':'discharge',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".discharge_temperature()-VCC_"+ref+".discharge_temperature())/(VCC_"+ref+".discharge_temperature()-k)*1e2"'
        },

        # Mass flow rate
        {
            'name':'Mass-flow-rate_M',
            'xlabel':'evaporator',
            'ylabel':'massflowrate',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".mass_flow_rate()*3600"'
        },
        {
            'name':'Mass-flow-rate_MR',
            'xlabel':'evaporator',
            'ylabel':'massflowrate',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".mass_flow_rate()-VCC_"+ref+".mass_flow_rate())/VCC_"+ref+".mass_flow_rate()*1e2"'
        },

        # Volumetric flow rate
        {
            'name':'Volumetric-flow-rate_M',
            'xlabel':'evaporator',
            'ylabel':'volumetricflowrate',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".volumetric_flow_rate()*3600"'
        },
        {
            'name':'Volumetric-flow-rate_MR',
            'xlabel':'evaporator',
            'ylabel':'volumetricflowrate',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".volumetric_flow_rate()-VCC_"+ref+".volumetric_flow_rate())/VCC_"+ref+".volumetric_flow_rate()*1e2"'
        },

        # Isentropic efficiency
        {
            'name':'Isentropic-efficiency_M',
            'xlabel':'evaporator',
            'ylabel':'isentropic',
            'tc':t_cond_mid,
            'xfunc':'"VCC_"+aref+".p(1)/VCC_"+aref+".p(0)"',
            'yfunc':'"VCC_"+aref+".isentropic_efficiency()"',
            'calc_intersect':True
        },
        {
            'name':'Isentropic-efficiency_MR',
            'xlabel':'evaporator',
            'ylabel':'isentropic',
            'tc':t_cond_mid,
            'xfunc':'"VCC_"+aref+".p(1)/VCC_"+aref+".p(0)"',
            'yfunc':'"(VCC_"+aref+".isentropic_efficiency()-VCC_"+ref+".isentropic_efficiency())/VCC_"+ref+".isentropic_efficiency()*1e2"'
        },

        # Specific power
        {
            'name':'Specific-power_M',
            'xlabel':'evaporator',
            'ylabel':'enthaplyrise',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+"._compressor.specific_power()"',
            'calc_intersect':True
        },
        {
            'name':'Specific-power_MR',
            'xlabel':'evaporator',
            'ylabel':'enthaplyrise',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+"._compressor.specific_power()-VCC_"+ref+"._compressor.specific_power())/VCC_"+ref+"._compressor.specific_power()*1e2"'
        },

        # Cooling capacity
        {
            'name':'Cooling-capacity_M',
            'xlabel':'evaporator',
            'ylabel':'refrigeratingcapacity',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".cooling_capacity()/1e3"',
            'calc_intersect':True
        },
        {
            'name':'Cooling-capacity_MR',
            'xlabel':'evaporator',
            'ylabel':'refrigeratingcapacity',
            'tc':t_cond_mid,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".cooling_capacity()-VCC_"+ref+".cooling_capacity())/VCC_"+ref+".cooling_capacity()*1e2"'
        },

        # <--- High temperature --->

        # Coefficient of performance
        {
            'name':'COP2_H',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'tc':t_cond_high,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".cop_2()"',
            'calc_intersect':True
        },
        {
            'name':'COP2_HR',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'tc':t_cond_high,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".cop_2()-VCC_"+ref+".cop_2())/VCC_"+ref+".cop_2()*100"'
            #'yfunc':'"VCC_"+aref+".cop_2()/VCC_"+ref+".cop_2()"'
        },

        # Isentropic efficiency
        {
            'name':'Isentropic-efficiency_H',
            'xlabel':'evaporator',
            'ylabel':'isentropic',
            'tc':t_cond_high,
            'xfunc':'"VCC_"+aref+".p(1)/VCC_"+aref+".p(0)"',
            'yfunc':'"VCC_"+aref+".isentropic_efficiency()"',
            'calc_intersect':True
        },

        # Isentropic efficiency
        {
            'name':'Isentropic-efficiency_HR',
            'xlabel':'evaporator',
            'ylabel':'isentropic',
            'tc':t_cond_high,
            'xfunc':'"VCC_"+aref+".p(1)/VCC_"+aref+".p(0)"',
            'yfunc':'"(VCC_"+aref+".isentropic_efficiency()-VCC_"+ref+".isentropic_efficiency())/VCC_"+ref+".isentropic_efficiency()*1e2"'
        },

        # Cooling capacity
        {
            'name':'Cooling-capacity_H',
            'xlabel':'evaporator',
            'ylabel':'refrigeratingcapacity',
            'tc':t_cond_high,
            'xfunc':'te+"-"+k',
            'yfunc':'"VCC_"+aref+".cooling_capacity()/1e3"',
            'calc_intersect':True
        },
        {
            'name':'Cooling-capacity_HR',
            'xlabel':'evaporator',
            'ylabel':'refrigeratingcapacity',
            'tc':t_cond_high,
            'xfunc':'te+"-"+k',
            'yfunc':'"(VCC_"+aref+".cooling_capacity()-VCC_"+ref+".cooling_capacity())/VCC_"+ref+".cooling_capacity()*1e2"'
        },

      ]

values = dict()

folder = '../../Report/LaTeX/data/'
#folder = './test/'

# Instantiate Vcc:s for each refrigerant
for r in range(0, len(refs)):
    locals()["REF_" + refs[r]] = vcc_input.refrigerant(refs[r])
    locals()["VCC_" + refs[r]] = vcc_functions.Vcc(locals()["REF_" + refs[r]])

    locals()["VCC_" + refs[r]].set_input_data(input_data)

    locals()["VCC_" + refs[r]].set_compressor_data(refs[r] + compressor_extension)
    #locals()["VCC_" + refs[r]].set_compressor_data(1.0)


#locals()["VCC_" + refs[1]].set_super_heating(input_data['ev_super_heat']-0.8/3)
#locals()["VCC_" + refs[2]].set_super_heating(input_data['ev_super_heat']-0.8/3)

# Open file streams and write first row
for r in range(0, len(refs)):
    values[refs[r]] = dict()

    for o in range(0, len(ops)):
        filename = str("%s_%s" % (ops[o]['name'], refs[r]))
        path = str("%s%s.dat" % (folder, filename))
        #print("Opened file: " + filename)

        locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))] = open(path, 'w+')
        locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))].write(ops[o]['xlabel']+" "+ops[o]['ylabel']+"\n")

        values[refs[r]][o] = {
                            'xvalue': numpy.zeros(t_evap_res),
                            'yvalue': numpy.zeros(t_evap_res),
                             }

    #print(" ")

# Loop through condenser temperatures
for t_cond_act in [t_cond_mid, t_cond_high]:
    print("Tc: " + str(t_cond_act))
    # Loop through evaporator temperatures
    for e in range(0, len(t_evap)):
        print("  Te: " + str(t_evap[e]))
        # Loop through refrigerants
        for r in range(0, len(refs)):
            # Set condenser temperature
            locals()["VCC_" + refs[r]].set_condenser_temperature(t_cond_act)

            # Set evaporator temperature
            locals()["VCC_" + refs[r]].set_evaporator_temperature(t_evap[e])

            # Calculate Vcc
            locals()["VCC_" + refs[r]].calculate()

            # Loop through all operations
            for o in range(0, len(ops)):
                if ops[o]['tc'] == t_cond_act:
                    xvalue = eval(eval(ops[o]['xfunc'], {}, {'te': str(t_evap[e]), 'k': str(k), 'ref': refs[0], 'aref': refs[r]}))
                    yvalue = eval(eval(ops[o]['yfunc'], {}, {'ref': refs[0], 'aref': refs[r]}))

                    locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))].write(
                        str("%f %f\n" % (xvalue, yvalue))
                    )

                    values[refs[r]][o]['xvalue'][e] = xvalue
                    values[refs[r]][o]['yvalue'][e] = yvalue


# Calculate intersections
# Loop through all operations
for o in range(0, len(ops)):
    if ops[o].has_key('calc_intersect'):
        if ops[o]['calc_intersect']:
            for r in range(1, len(refs)):
                print('Intersection of ' + ops[o]['name'] + '_' + refs[r])

                vcc_functions.data_intersect(values[refs[0]][o]['xvalue'], values[refs[0]][o]['yvalue'],
                                             values[refs[r]][o]['xvalue'], values[refs[r]][o]['yvalue'])


# Close file streams
for r in range(0, len(refs)):
    for op in ops:
        locals()[str("FILE_%s_%s" % (op['name'], refs[r]))].close()

end = time.time()
print("Time required: " + str(end - start))

