__author__ = 'Peter Eriksson @ KTH 2015'

import vcc_input
import vcc_functions
import numpy

# Description:
# This file exports all comparison files

# Scientific parameters
k = 273.15

# Evaluation range condenser
t_cond_mid = 35 + k     # Fix temperature middle
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

# Load input data from file
input_data = vcc_input.real_system2()

# Refrigerants to compare
refs = ["R404A", "R448A", "R449A"]
compressor_name = '-4GE-30Y'

sub_range = [5, 10, 15, 20, 25, 30]
super_range = [5, 10, 15, 20, 25, 30, 50]

# Operations of comparison
ops = [
        # Super heating
        {
            'name':'Super-heating',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'xfunc':'tch',
            'yfunc':'"VCC_"+aref+".cop_2()"',
            'sub_cooling':'input_data["co_sub_cooling"]',
            'super_heating':'t_range[t]',
            'prefix':'Super'
        },

        {
            'name':'Super-heating-specific-power',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'xfunc':'tch',
            'yfunc':'"VCC_"+aref+"._compressor.specific_power()"',
            'sub_cooling':'input_data["co_sub_cooling"]',
            'super_heating':'t_range[t]',
            'prefix':'Super'
        },

        {
            'name':'Super-heating-discharge-temperature',
            'xlabel':'evaporator',
            'ylabel':'dischargetemperature',
            'xfunc':'tch',
            'yfunc':'"VCC_"+aref+".T(1)-k"',
            'sub_cooling':'input_data["co_sub_cooling"]',
            'super_heating':'t_range[t]',
            'prefix':'Super'
        },

        {
            'name':'Super-heating-capacity',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'xfunc':'tch',
            'yfunc':'"VCC_"+aref+"._h[1]-VCC_"+aref+"._h[6]"',
            'sub_cooling':'input_data["co_sub_cooling"]',
            'super_heating':'t_range[t]',
            'prefix':'Super'
        },

        # Sub cooling
        {
            'name':'Sub-cooling',
            'xlabel':'evaporator',
            'ylabel':'COP2',
            'xfunc':'tch',
            'yfunc':'"VCC_"+aref+".cop_2()"',
            'sub_cooling':'t_range[t]',
            'super_heating':'input_data["ev_super_heat"]',
            'prefix':'Sub',
            'calc_intersect':True
        },

       ]

values = dict()

folder = '../../Report/LaTeX/data/'

# Instantiate Vcc:s for each refrigerant
for r in range(0, len(refs)):
    locals()["REF_" + refs[r]] = vcc_input.refrigerant(refs[r])
    locals()["VCC_" + refs[r]] = vcc_functions.Vcc(locals()["REF_" + refs[r]])

    locals()["VCC_" + refs[r]].set_input_data(input_data)


# Open file streams and write first row
for r in range(0, len(refs)):
    values[refs[r]] = dict()

    for o in range(0, len(ops)):
        filename = str("%s_%s" % (ops[o]['name'], refs[r]))
        path = str("%s%s.dat" % (folder, filename))
        print("Opened file: " + filename)

        locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))] = open(path, 'w+')
        locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))].write(ops[o]['xlabel']+" "+ops[o]['ylabel']+"\n")

        if ops[o]['prefix'] == 'Super':
            values[refs[r]][o] = {
                                'xvalue': numpy.zeros(len(super_range)),
                                'yvalue': numpy.zeros(len(super_range)),
                                 }
        else:
            values[refs[r]][o] = {
                                'xvalue': numpy.zeros(len(sub_range)),
                                'yvalue': numpy.zeros(len(sub_range)),
                                 }




# Calculate
# Loop through refrigerants
for r in range(0, len(refs)):

    for o in range(0, len(ops)):

        if ops[o]['prefix'] == 'Super':
            t_range = super_range
        else:
            t_range = sub_range

        # Loop through temperatures
        for t in range(0, len(t_range)):

            locals()["VCC_" + refs[r]].set_sub_cooling(eval(ops[o]['sub_cooling']))
            locals()["VCC_" + refs[r]].set_super_heating(eval(ops[o]['super_heating']))

            # Set compressor
            locals()["VCC_" + refs[r]].set_compressor_data(refs[r] + compressor_name + "-" + ops[o]['prefix'] + "-" + str(t_range[t]) + ".xls")
            locals()["VCC_" + refs[r]].calculate()

            xvalue = eval(eval(ops[o]['xfunc'], {}, {'tch': str(t_range[t]), 'k': str(k), 'ref': refs[0], 'aref': refs[r]}))
            yvalue = eval(eval(ops[o]['yfunc'], {}, {'ref': refs[0], 'aref': refs[r]}))

            locals()[str("FILE_%s_%s" % (ops[o]['name'], refs[r]))].write(
                str("%f %f\n" % (xvalue, yvalue))
            )

            values[refs[r]][o]['xvalue'][t] = xvalue
            values[refs[r]][o]['yvalue'][t] = yvalue

            print(locals()["VCC_" + refs[r]].T(1)-273.15)
            print(locals()["VCC_" + refs[r]]._compressor.specific_power())
            print(locals()["VCC_" + refs[r]].isentropic_efficiency())

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