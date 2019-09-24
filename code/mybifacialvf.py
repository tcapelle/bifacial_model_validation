from bifacialvf.bifacialvf import simulate_inner
import pandas as pd


def _get_tmy3(data):
    'Get columns needed for bifacialvf'
    tmy3 = (data[['dni', 'dhi', 'zenith', 'azimuth', 'elevation']]
            .rename(columns={'dni':'DNI', 'dhi':'DHI'}))
    return tmy3

def format_output(res, cuts): 
    'Formats the bifacialvf output to pvfactors output'
    front_cols = [f'No_{i+1}_RowFrontGTI' for i in range(cuts)]
    back_cols = [f'No_{i+1}_RowBackGTI' for i in range(cuts)]
    aux = pd.DataFrame(index=res.index)
    aux['qinc_front'] = res[front_cols].mean(axis=1)
    aux['qinc_back_mean'] = res[back_cols].mean(axis=1)
    aux[back_cols] = res[back_cols]
    aux =  aux.rename(columns=dict(zip(back_cols,[f'qinc_back_{i}' for i in range(cuts-1, -1, -1)] )))
    return aux[['qinc_front', 'qinc_back_mean']+[f'qinc_back_{i}' for i in range(cuts)]]

def bifacialvf_engine_run(data,  pvarray_parameters, gps_data, **kwargs):
    'Wrapper to run simulate using pvarray_parameters'
    tmy3 = _get_tmy3(data)
    outfile = 'output.csv'
    simulate_inner(tmy3, gps_data, outfile, **pvarray_parameters, sam_header=False, **kwargs)
    return (pd.read_csv(outfile, header=2, index_col='date', parse_dates=True)
            .pipe(format_output, cuts=pvarray_parameters['cellRows']))