__author__ = 'Peter Eriksson @ KTH 2015'

import vcc_functions
import vcc_input
import numpy

#filename = 'genetron/R448A.xls'
#filename = 'genetron/R448A.xls'
#filename = 'genetron/R407C-1.xls'

#input_data = vcc_input.load(filename)
#reference_data = vcc_input.reference(filename)

input_data = vcc_input.real_system2()

REF_R404A = vcc_input.refrigerant('R404A')
R404A = vcc_functions.Vcc(REF_R404A)
R404A.set_input_data(input_data)
R404A.set_compressor_data('R404A-4GE-30Y.xls')
R404A.calculate()

REF_R448A = vcc_input.refrigerant('R448A')
R448A = vcc_functions.Vcc(REF_R448A)
R448A.set_input_data(input_data)
R448A.set_compressor_data('R448A-4GE-30Y.xls')
R448A.calculate()

REF_R449A = vcc_input.refrigerant('R449A')
R449A = vcc_functions.Vcc(REF_R449A)
R449A.set_input_data(input_data)
R449A.set_compressor_data('R449A-4GE-30Y.xls')
R449A.calculate()


"""
print(R404A.cooling_capacity())
print(R404A._compressor._P)

print(R448A.cooling_capacity())
print(R448A._compressor._P)

print(R449A.cooling_capacity())
print(R449A._compressor._P)

print((1 - (R449A.cooling_capacity()-R404A.cooling_capacity())/R404A.cooling_capacity())*R449A._compressor._P)

"""

t_range = numpy.linspace(0,30, 10, dtype=numpy.float)

for t_act in t_range:
    R404A.set_super_heating(t_act)
    R404A.set_sub_cooling(t_act)
    R404A.calculate()

    R448A.set_super_heating(t_act)
    R448A.set_sub_cooling(t_act)
    R448A.calculate()

    R449A.set_super_heating(t_act)
    R449A.set_sub_cooling(t_act)
    R449A.calculate()


    print(R404A._refrigerant.conductivity())
    print(R404A._refrigerant.viscosity())
    print(R404A._refrigerant.acentric_factor())
    print(R404A.cooling_capacity())
    print(" ")
    print(R448A._refrigerant.conductivity())
    print(R448A._refrigerant.viscosity())
    print(R448A.cooling_capacity())
    print(" ")
    print(R449A._refrigerant.conductivity())
    print(R449A._refrigerant.viscosity())
    print(R449A.cooling_capacity())
    print("---")

    #print(R448A.cop_2())
    #print(R449A.cop_2())

