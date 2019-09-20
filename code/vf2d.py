"wrapper around pvfactors and bifacialvf"
# from .mypvfactors import merge_data, pvfactors_engine_run, debug_pvarray
# from .mybifacialvf import get_tmy3, bifacialvf_engine_run
import numpy as np
import math

chambery = {'Name':'Chambery', 'latitude': 45.637001, 'longitude': 5.881, 'Elevation': 235.0, 'TZ':-1.0}
surfaces_reflectivity = {'glass': 1.526, 'ARglass': 1.3}

def system_def(albedo=0.4, 
                row_type='first',
                n_modules_vertically=2, 
                module_size=(2.0, 1.0), 
                h_ground=1,
                surface_tilt=30,
                axis_azimuth=90,
                surface_azimuth=180,
                n_pvrows=1,
                rtr_spacing=9,
                frontSurface = "glass",
                backSurface = "glass",
                back_measure_points = 7,
                tracking=False,
                gps_data=chambery,
                ):
    
    w_m, h_m = module_size  #width x height of module
    slope = (n_modules_vertically * h_m) #lenght of the installation plane            
    
    #pvfactors variables
    gcr = slope/rtr_spacing  #ground coverage ratio

    def compute_rho(n2): return math.pow((n2 - 1.0) / (n2 + 1.0), 2.0)
    rho_front_pvrow =  compute_rho(surfaces_reflectivity[frontSurface])
    rho_back_pvrow =  compute_rho(surfaces_reflectivity[backSurface])
    #bifacialvf variables
    C = h_ground/slope #compute normalized ground_height 
    rtr = rtr_spacing/slope #normalized rtr spacing
    rowType = row_type       # RowType(first interior last single)
    transFactor = 0.013         # TransmissionFactor(open area fraction)
    cellRows = back_measure_points              # CellRows(# hor rows in panel)   
                                #This is the number of irradiance values returned along module chord
    
    # phisical
    if not tracking:
        h_center = h_ground + np.sin(2*np.pi*surface_tilt/360)*h_m
    else:
        h_center = h_ground
    
    
    pvarray_parameters = {'pvfactors': {
                                        'n_pvrows': n_pvrows,            # number of pv rows
                                        'pvrow_height': h_center,        # height of pvrows (measured at center / torque tube)
                                        'pvrow_width': n_modules_vertically * h_m,         # width of pvrows
                                        'tracking':tracking,
                                        'axis_azimuth': axis_azimuth,       # azimuth angle of rotation axis
                                        'surface_tilt': surface_tilt,      # tilt of the pv rows
                                        'surface_azimuth': surface_azimuth,   # azimuth of the pv rows front surface
                                        'albedo':albedo,
                                        'gcr': gcr,               # ground coverage ratio,
                                        'rho_front_pvrow': rho_front_pvrow,  # pv row front surface reflectivity
                                        'rho_back_pvrow': rho_back_pvrow,    # pv row back surface reflectivity
                                        'cut':{
                                            i: {'front': 1,'back': back_measure_points} for i in range(n_pvrows) # discretize the front  PV row into 3 segments and back in 5
                                            }
                                        },
                        'bifacialvf':  {'beta': surface_tilt,
                                        'sazm': surface_azimuth,
                                        'C': C,
                                        'rtr': rtr,
                                        'rowType': rowType,
                                        'transFactor': transFactor,
                                        'cellRows': cellRows,
                                        'PVfrontSurface': frontSurface,
                                        'PVbackSurface': backSurface,
                                        'albedo':albedo,
                                        'tracking': tracking
                                        },
                        'gps_data': gps_data
    }
    return pvarray_parameters

# def run_simulation(data, pvarray_parameters, engine='pvfactors'):
#     merged_data = merge_data(data.meteo, data.sunpos, pvarray_parameters['pvfactors'])
#     if engine == 'pvfactors':   
#         # idx = data.index.get_loc('9h 21 Dec 2017')
#         # print(f'Viewing the PV plant at index {idx}:\n{merged_data.iloc[idx]}')
#         idx = 10
#         debug_pvarray(merged_data, pvarray_parameters['pvfactors'], idx=idx)
#         res = pvfactors_engine_run(merged_data, pvarray_parameters['pvfactors'], parallel=8)
#     if engine == 'bifacialvf':
#         res = bifacialvf_engine_run(merged_data, pvarray_parameters['bifacialvf'], gps_data=pvarray_parameters['gps_data'])
#     return res
