__author__ = 'PeterE-Mac'

import vcc_functions
import vcc_input

input_data = vcc_input.real_system2()

compressor_extension = '-4GE-30Y.xls'
folder = '../../Report/LaTeX/data/'

k = 273.15
m = 10
L_annual = 0.125
n = 15
a_recovery = 0.95
beta = 0.405
time = 24 * 365 * 0.75

refs = [
    {
        'name':'R404A',
        'GWP':3922,
        'direct':0.0,
        'indirect':0.0,
        'e_annual':0.0
    },
    {
        'name':'R448A',
        'GWP':1273,
        'direct':0.0,
        'indirect':0.0,
        'e_annual':0.0
    },
    {
        'name':'R449A',
        'GWP':1282,
        'direct':0.0,
        'indirect':0.0,
        'e_annual':0.0
    },
]

TEWI_direct = open(str("%s%s.dat" % (folder, 'TEWI-direct')), 'w+')
TEWI_indirect = open(str("%s%s.dat" % (folder, 'TEWI-indirect')), 'w+')

TEWI_direct.write("CO2e refrigerant\n")
TEWI_indirect.write("CO2e refrigerant\n")

# Instantiate Vcc:s for each refrigerant
for r in range(0, len(refs)):
    locals()["REF_" + refs[r]['name']] = vcc_input.refrigerant(refs[r]['name'])
    locals()["VCC_" + refs[r]['name']] = vcc_functions.Vcc(locals()["REF_" + refs[r]['name']])

    locals()["VCC_" + refs[r]['name']].set_input_data(input_data)
    locals()["VCC_" + refs[r]['name']].set_compressor_data(refs[r]['name'] + compressor_extension)
    locals()["VCC_" + refs[r]['name']].calculate()


print("---")

print("REF   : Qdot2 : mdot : d0   : Qvol   : P     : P'      : etais : E_ann    : cop2   : DisT   : beta: TEWI")

for r in range(0, len(refs)):

    # The degraded real compressor efficiency
    degraded_efficiency = input_data['efficiency_isentropic'] * locals()["VCC_" + refs[r]['name']].isentropic_efficiency()/locals()["VCC_" + refs[0]['name']].isentropic_efficiency()



    # Set the degraded compressor efficiency
    # The volumetric flow rate from the real compressor data, same due to preserved mechanical properties
    locals()["VCC_" + refs[r]['name']].set_volumetric_flow_rate(locals()["VCC_" + refs[r]['name']].volumetric_flow_rate())
    locals()["VCC_" + refs[r]['name']].set_compressor_data(degraded_efficiency)
    locals()["VCC_" + refs[r]['name']].calculate()

    locals()["VCC_" + refs[r]['name']].plot_hlogp()


    # Cooling capacity compensation needed
    # Since the cooling capacity drops for the retrofit refrigerants the compressor must run more of the time
    rel_cool_cap = locals()["VCC_" + refs[r]['name']].cooling_capacity()/locals()["VCC_" + refs[0]['name']].cooling_capacity()

    P_compensated = locals()["VCC_" + refs[r]['name']].compressor_power() / rel_cool_cap

    # System dependent variables
    refs[r]['e_annual'] = P_compensated * time / 1e3

    # The parts of TEWI
    leakage = refs[r]['GWP'] * m * L_annual * n
    recovery = refs[r]['GWP'] * m * (1 - a_recovery)
    indirect = refs[r]['e_annual'] * beta * n

    refs[r]['direct'] = leakage + recovery
    refs[r]['indirect'] = indirect


    #print((refs[r]['GWP'] - refs[0]['GWP']) * m * L_annual * n)
    #print(refs[r]['GWP'] - refs[0]['GWP']) * m * (1 - a_recovery)
    #print((refs[0]['e_annual'] - refs[r]['e_annual']) * n)

    if r > 0:
        #beta_max = (refs[0]['direct']+refs[0]['indirect'] - refs[r]['direct']) / (refs[r]['e_annual'] * n)

        beta_max = (
                (refs[0]['GWP'] - refs[r]['GWP']) * m * L_annual * n +
                (refs[0]['GWP'] - refs[r]['GWP']) * m * (1 - a_recovery)
               ) / \
               (
                   (refs[r]['e_annual'] - refs[0]['e_annual']) * n
               )

    else:
        beta_max = 0

    tewi = leakage + recovery + indirect

    TEWI_direct.write(str("%f %s\n" % ((leakage + recovery)/1e3, refs[r]['name'])))
    TEWI_indirect.write(str("%f %s\n" % (indirect/1e3, refs[r]['name'])))

    print(locals()["VCC_" + refs[r]['name']].T(3)-273.15)

    print("%s : %.1f  : %.1f : %.0f  : %.1f  : %.2f  : %.2f  : %.2f  : %.3f : %.0f : %.2f : %.0f   : %.1f : %.1f" %
        (
        refs[r]['name'],
        locals()["VCC_" + refs[r]['name']]._h[0] - locals()["VCC_" + refs[r]['name']]._h[6],
        locals()["VCC_" + refs[r]['name']]._h[1] - locals()["VCC_" + refs[r]['name']]._h[0], #locals()["VCC_" + refs[r]['name']].cooling_capacity()/1e3,
        locals()["VCC_" + refs[r]['name']].mass_flow_rate()*3600,
        locals()["VCC_" + refs[r]['name']]._d[0],
        locals()["VCC_" + refs[r]['name']].volumetric_cooling_capacity()/1e3,
        locals()["VCC_" + refs[r]['name']].compressor_power()/1e3,
        P_compensated/1e3,
        degraded_efficiency,
        refs[r]['e_annual'],
        locals()["VCC_" + refs[r]['name']].cop_2(),
        locals()["VCC_" + refs[r]['name']].discharge_temperature()-k,
        beta_max,
        tewi
        )
    )

    # Reset the compressor
    locals()["VCC_" + refs[r]['name']].set_compressor_data(refs[r]['name'] + compressor_extension)
    locals()["VCC_" + refs[r]['name']].calculate()

    print(" ")
