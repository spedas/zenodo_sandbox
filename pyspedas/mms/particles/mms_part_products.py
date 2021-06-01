import logging
import numpy as np
from time import time

from pytplot import get_data

from pyspedas.particles.spd_part_products.spd_pgs_make_theta_spec import spd_pgs_make_theta_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_phi_spec import spd_pgs_make_phi_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_e_spec import spd_pgs_make_e_spec
from pyspedas.particles.spd_part_products.spd_pgs_make_tplot import spd_pgs_make_tplot
from pyspedas.particles.spd_part_products.spd_pgs_limit_range import spd_pgs_limit_range
from pyspedas.particles.spd_part_products.spd_pgs_progress_update import spd_pgs_progress_update

from pyspedas.mms.fpi.mms_get_fpi_dist import mms_get_fpi_dist
from pyspedas.mms.particles.mms_convert_flux_units import mms_convert_flux_units
from pyspedas.mms.particles.mms_pgs_clean_data import mms_pgs_clean_data

logging.captureWarnings(True)
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

def mms_part_products(in_tvarname, units='eflux', species='e', data_rate='fast', instrument='fpi', probe='1',
    output=['energy', 'theta', 'phi'], energy=None, phi=None, theta=None, pitch=None, gyro=None):
    """

    """

    units = units.lower()
    if isinstance(probe, int):
        probe = str(probe)

    data_in = get_data(in_tvarname)

    if data_in is None:
        logging.error('Error, could not find the variable: ' + in_tvarname)
        return None

    if isinstance(output, str):
        output = output.split(' ')

    dist_in = mms_get_fpi_dist(in_tvarname, species=species, probe=probe, data_rate=data_rate)
    out_energy = np.zeros((dist_in['n_times'], dist_in['n_energy']))
    out_energy_y = np.zeros((dist_in['n_times'], dist_in['n_energy']))
    out_theta = np.zeros((dist_in['n_times'], dist_in['n_theta']))
    out_phi = np.zeros((dist_in['n_times'], dist_in['n_phi']))
    out_theta_y = np.zeros((dist_in['n_times'], dist_in['n_theta']))
    out_phi_y = np.zeros((dist_in['n_times'], dist_in['n_phi']))

    out_vars = []
    last_update_time = None
    ntimes = len(data_in.times)

    for i in range(0, ntimes):
        last_update_time = spd_pgs_progress_update(last_update_time=last_update_time, current_sample=i, total_samples=ntimes, type_string=in_tvarname)

        dist_in = mms_get_fpi_dist(in_tvarname, index=i, species=species, probe=probe, data_rate=data_rate)

        data = mms_convert_flux_units(dist_in, units=units)

        clean_data = mms_pgs_clean_data(data)

        # Apply phi, theta, & energy limits
        if energy is not None or theta is not None or phi is not None:
            clean_data = spd_pgs_limit_range(clean_data, energy=energy, theta=theta, phi=phi)

        # Build energy spectrogram
        if 'energy' in output:
            out_energy_y[i, :], out_energy[i, :] = spd_pgs_make_e_spec(clean_data)

        # Build theta spectrogram
        if 'theta' in output:
            out_theta_y[i, :], out_theta[i, :] = spd_pgs_make_theta_spec(clean_data)

        # Build phi spectrogram
        if 'phi' in output:
            out_phi_y[i, :], out_phi[i, :] = spd_pgs_make_phi_spec(clean_data)

    if 'energy' in output:
        spd_pgs_make_tplot(in_tvarname+'_energy', x=data_in.times, y=out_energy_y, z=out_energy, units=units, ylog=True)
        out_vars.append(in_tvarname+'_energy')

    if 'theta' in output:
        spd_pgs_make_tplot(in_tvarname+'_theta', x=data_in.times, y=out_theta_y, z=out_theta, units=units)
        out_vars.append(in_tvarname+'_theta')

    if 'phi' in output:
        spd_pgs_make_tplot(in_tvarname+'_phi', x=data_in.times, y=out_phi_y, z=out_phi, units=units)
        out_vars.append(in_tvarname+'_phi')

    return out_vars