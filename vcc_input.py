__author__ = 'Peter Eriksson @ KTH 2015'

import openpyxl
import xlrd
import numpy
import os

# Description:
# This file handles the inputs as well as hard coded parameters

# Constants
k = 273.15

def refrigerant(name):
    # Refrigerant data
    refrigerant_data = numpy.zeros(5, dtype=numpy.object)

    # Defined since predefined mixtures did not want to run under Mac...
    if name.find('R404A') > -1:
        refrigerant_data[0] = 'R404A'
        refrigerant_data[1] = 'REFPROP'
        refrigerant_data[2] = 'R125&R134A&R143A'
        refrigerant_data[3] = (0.357816784026318, 0.0382639950410712, 0.603919220932611)
        refrigerant_data[4] = 'REFPROP::R125[0.357816784026318]&R134A[0.0382639950410712]&R143A[0.603919220932611]'
    elif name.find('R448A') > -1:
        refrigerant_data[0] = 'R448A'
        refrigerant_data[1] = 'REFPROP'
        refrigerant_data[2] = 'R32&R125&R1234YF&R134A&R1234ZE'
        refrigerant_data[3] = (0.431218201988559, 0.186914131481992, 0.151319256485899, 0.177586673617217, 0.0529617364263329)
        refrigerant_data[4] = 'REFPROP::R32[0.431218201988559]&R125[0.186914131481992]&R1234YF[0.151319256485899]&R134A[0.177586673617217]&R1234ZE[0.0529617364263329]'
    elif name.find('R449A') > -1:
        refrigerant_data[0] = 'R449A'
        refrigerant_data[1] = 'REFPROP'
        refrigerant_data[2] = 'R32&R125&R1234YF&R134A'
        refrigerant_data[3] = (0.407364566995509, 0.179481207732065, 0.193480840388364, 0.219673384884062)
        refrigerant_data[4] = 'REFPROP::R32[0.407364566995509]&R125[0.179481207732065]&R1234YF[0.193480840388364]&R134A[0.219673384884062]'
    elif name.find('R407F') > -1:
        refrigerant_data[0] = 'R407F'
        refrigerant_data[1] = 'REFPROP'
        refrigerant_data[2] = 'R32&R125&R134A'
        refrigerant_data[3] = (0.473194694453358, 0.205109095413331, 0.321696210133311)
        refrigerant_data[4] = 'REFPROP::R32[0.473194694453358]&R125[0.205109095413331]&R134A[0.321696210133311]'
    else:
        refrigerant_data[0] = name
        refrigerant_data[1] = 'REFPROP'
        refrigerant_data[2] = name
        refrigerant_data[3] = [1.0]
        refrigerant_data[4] = 'REFPROP::' + name

    return refrigerant_data

# Sandbox input data
def manual():

    input_data = {}

    # Evaporator
    input_data["ev_temperature"] = -40 + k	        # [C] Evaporator temperature
    input_data["ev_super_heat"] = 7			        # [K] Evaporator outlet super heating
    #input_data["ev_super_heat"] = 8.8			        # [K] Evaporator outlet super heating
    input_data["ev_pressure_drop"] = 0e3		    # [Pa] Evaporator pressure drop

    # Suction line
    input_data["sl_temperature_change"] = 0	        # [K] Superheat (Suction line)
    input_data["sl_pressure_drop"] = 0e3		    # [Pa] Suction Line

    # Compressor
    input_data["capacity_volumetric"] = 1
    input_data["efficiency_isentropic"] = 0		    # [-] Isentropic Efficiency 0=Bitzer data
    input_data["efficiency_volymetric"] = 1		    # [-] Volymetric Efficiency

    # Discharge line
    input_data["dl_temperature_change"] = 0          # [K] Superheat (Suction line)
    input_data["dl_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    # Condenser
    input_data["co_temperature"] = 35 + k		        # [C] Temperature
    input_data["co_sub_cooling"] = 2		        # [K] Outlet super cooling
    #input_data["co_sub_cooling"] = 15.6		        # [K] Outlet super cooling
    input_data["co_pressure_drop"] = 0e3            # [Pa] Pressure drop

    # Liquid line
    input_data["ll_temperature_change"] = 0          # [K] Superheat (Suction line)
    input_data["ll_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    return input_data

# Data from real system
def real_system():

    input_data = {}

    # Evaporator
    input_data["ev_temperature"] = -15.4+ k	        # [C] Evaporator temperature
    input_data["ev_super_heat"] = 2.1			        # [K] Evaporator outlet super heating
    input_data["ev_pressure_drop"] = 0e3		    # [Pa] Evaporator pressure drop

    # Suction line
    input_data["sl_temperature_change"] = 0	        # [K] Superheat (Suction line)
    input_data["sl_pressure_drop"] = 0e3		    # [Pa] Suction Line

    # Compressor
    input_data["capacity_volumetric"] = 1
    input_data["efficiency_isentropic"] = 0.502		    # [-] Isentropic Efficiency 0=Bitzer data
    input_data["efficiency_volymetric"] = 1		    # [-] Volymetric Efficiency

    # Discharge line
    input_data["dl_temperature_change"] = 4          # [K] Superheat (Suction line)
    input_data["dl_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    # Condenser
    input_data["co_temperature"] = 41.8 + k		        # [C] Temperature
    input_data["co_sub_cooling"] = 8.8		        # [K] Outlet super cooling
    input_data["co_pressure_drop"] = 0e3            # [Pa] Pressure drop

    # Liquid line
    input_data["ll_temperature_change"] = 0          # [K] Superheat (Suction line)
    input_data["ll_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    return input_data

# Data from real system
def real_system2():

    input_data = {}

    # Evaporator
    input_data["ev_temperature"] = -37.4+ k	        # [C] Evaporator temperature
    input_data["ev_super_heat"] = 8.8			        # [K] Evaporator outlet super heating
    input_data["ev_pressure_drop"] = 0e3		    # [Pa] Evaporator pressure drop

    # Suction line
    input_data["sl_temperature_change"] = 0.3	        # [K] Superheat (Suction line)
    input_data["sl_pressure_drop"] = 0e3		    # [Pa] Suction Line

    # Compressor
    input_data["capacity_volumetric"] = 1
    input_data["efficiency_isentropic"] = 0.555		    # [-] Isentropic Efficiency 0=Bitzer data
    input_data["efficiency_volymetric"] = 1		    # [-] Volymetric Efficiency

    # Discharge line
    input_data["dl_temperature_change"] = 4.7          # [K] Superheat (Suction line)
    input_data["dl_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    # Condenser
    input_data["co_temperature"] = 30 + k		        # [C] Temperature
    input_data["co_sub_cooling"] = 15.6		        # [K] Outlet super cooling
    input_data["co_pressure_drop"] = 0e3            # [Pa] Pressure drop

    # Liquid line
    input_data["ll_temperature_change"] = 0          # [K] Superheat (Suction line)
    input_data["ll_pressure_drop"] = 0e3            # [K] Superheat (Suction line)

    return input_data

# Load function for xls files from Genetron
def load(filename):

    input_data = {}

    if os.path.isfile(os.path.join(os.getcwd(), 'input', filename)):
        if filename.split(".")[-1] == 'xls':
            workbook = xlrd.open_workbook(os.path.join(os.getcwd(), 'input', filename))
        elif filename.split(".")[-1] == 'xlsx':
            workbook = openpyxl.open_workbook(os.path.join(os.getcwd(), 'input', filename))
        else:
            print('Extension of file not allowed')
            pass
    else:
        print('File does not exist')
        pass

    worksheet = workbook.sheet_by_index(0)

    # Refrigerant
    input_data["refrigerant"] = worksheet.cell_value(22,3)

    # Evaporator
    input_data["ev_temperature"] = worksheet.cell_value(5,3) + k	        # [C] Evaporator temperature
    input_data["ev_super_heat"] = worksheet.cell_value(6,3)			        # [K] Evaporator outlet super heating
    input_data["ev_pressure_drop"] = worksheet.cell_value(7,3)*1e3		    # [Pa] Evaporator pressure drop

    # Suction line
    input_data["sl_temperature_change"] = worksheet.cell_value(8,3)	        # [K] Superheat (Suction line)
    input_data["sl_pressure_drop"] = worksheet.cell_value(9,3)*1e3		    # [Pa] Suction Line

    # Compressor
    input_data["capacity_volumetric"] = worksheet.cell_value(10,3)		    # [-] Isentropic Efficiency
    input_data["efficiency_isentropic"] = worksheet.cell_value(11,3)	    # [-] Isentropic Efficiency
    input_data["efficiency_volymetric"] = worksheet.cell_value(12,3)		# [-] Volymetric Efficiency

    # Discharge line
    input_data["dl_temperature_change"] = worksheet.cell_value(13,3)        # [K] Superheat (Suction line)
    input_data["dl_pressure_drop"] = worksheet.cell_value(14,3)*1e3         # [K] Superheat (Suction line)

    # Condenser
    input_data["co_temperature"] = worksheet.cell_value(15,3) + k		    # [C] Temperature
    input_data["co_sub_cooling"] = worksheet.cell_value(16,3)		        # [K] Outlet sub cooling
    input_data["co_pressure_drop"] = worksheet.cell_value(17,3)*1e3         # [Pa] Pressure drop

    # Liquid line
    input_data["ll_temperature_change"] = worksheet.cell_value(18,3)        # [K] Superheat (Suction line)
    input_data["ll_pressure_drop"] = worksheet.cell_value(19,3)*1e3         # [K] Superheat (Suction line)

    return input_data

# Function to import results from Genetron xls export for fast validation of the model coding
def reference(filename):

    reference_data = numpy.zeros((10,6), dtype=numpy.float)  # Temperature

    # Differenft functions depending of version of Excel
    if filename.split(".")[-1] == 'xls':
        workbook = xlrd.open_workbook(os.path.join(os.getcwd(), 'input', filename))
    elif filename.split(".")[-1] == 'xlsx':
        workbook = openpyxl.open_workbook(os.path.join(os.getcwd(), 'input', filename))
    else:
        print('Extension of file not allowed')
        pass

    # Set working sheet
    worksheet = workbook.sheet_by_index(0)

    # After suction line/ Before compressor
    reference_data[0, 0] = worksheet.cell_value(108,3)+k        # Temperature
    reference_data[0, 1] = worksheet.cell_value(109,3)*1e3      # Pressure
    reference_data[0, 2] = worksheet.cell_value(110,3)*1e3      # Enthalpy
    reference_data[0, 3] = worksheet.cell_value(111,3)*1e3      # Entropy
    reference_data[0, 4] = worksheet.cell_value(112,3)          # Density

    # After compressor / Before discharge line
    reference_data[1, 0] = worksheet.cell_value(108,4)+k        # Temperature
    reference_data[1, 1] = worksheet.cell_value(109,4)*1e3      # Pressure
    reference_data[1, 2] = worksheet.cell_value(110,4)*1e3      # Enthalpy
    reference_data[1, 3] = worksheet.cell_value(111,4)*1e3      # Entropy
    reference_data[1, 4] = worksheet.cell_value(112,4)          # Density

    # After discharge line / Condenser inlet
    reference_data[2, 0] = worksheet.cell_value(124,3)+k        # Temperature
    reference_data[2, 1] = worksheet.cell_value(125,3)*1e3      # Pressure
    reference_data[2, 2] = worksheet.cell_value(126,3)*1e3      # Enthalpy
    reference_data[2, 3] = worksheet.cell_value(127,3)*1e3      # Entropy
    reference_data[2, 4] = worksheet.cell_value(128,3)          # Density

    # Condenser dew point
    reference_data[3, 0] = worksheet.cell_value(130,3)+k        # Temperature

    # Condenser bubble point
    reference_data[4, 0] = worksheet.cell_value(130,4)+k        # Temperature

    # Condenser outlet / Before liquid line
    reference_data[5, 0] = worksheet.cell_value(124,4)+k        # Temperature
    reference_data[5, 1] = worksheet.cell_value(125,4)*1e3      # Pressure
    reference_data[5, 2] = worksheet.cell_value(126,4)*1e3      # Enthalpy
    reference_data[5, 3] = worksheet.cell_value(127,4)*1e3      # Entropy
    reference_data[5, 4] = worksheet.cell_value(128,4)          # Density

    # After liquid line / Before expansion valve
    reference_data[6, 0] = worksheet.cell_value(141,3)+k        # Temperature
    reference_data[6, 1] = worksheet.cell_value(142,3)*1e3      # Pressure
    reference_data[6, 2] = worksheet.cell_value(143,3)*1e3      # Enthalpy
    reference_data[6, 3] = worksheet.cell_value(144,3)*1e3      # Entropy
    reference_data[6, 4] = worksheet.cell_value(145,3)          # Density

    # After expansion valve / Evaporator inlet
    reference_data[7, 0] = worksheet.cell_value(47,3)+k        # Temperature
    reference_data[7, 1] = worksheet.cell_value(48,3)*1e3      # Pressure
    reference_data[7, 2] = worksheet.cell_value(49,3)*1e3      # Enthalpy
    reference_data[7, 3] = worksheet.cell_value(50,3)*1e3      # Entropy
    reference_data[7, 4] = worksheet.cell_value(51,3)          # Density
    reference_data[7, 5] = worksheet.cell_value(52,3)          # Vapor mass quality

    # Evaporator dew point
    reference_data[8, 0] = worksheet.cell_value(53,4)+k         # Temperature

    # Evaporator outlet / Before suction line
    reference_data[9, 0] = worksheet.cell_value(47,4)+k         # Temperature
    reference_data[9, 1] = worksheet.cell_value(48,4)*1e3       # Pressure
    reference_data[9, 2] = worksheet.cell_value(49,4)*1e3       # Enthalpy
    reference_data[9, 3] = worksheet.cell_value(50,4)*1e3       # Entropy
    reference_data[9, 4] = worksheet.cell_value(51,4)           # Density

    return reference_data
