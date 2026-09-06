import numpy as np

from src.antenna.ula import ula_power_gain_db, ula_power_gain_linear
from src.energy import dbm_to_watt, energy_per_delivered_bit_joule, transmit_energy_joule


def test_ula_boresight_gain_equals_n_elements():
    for n in [1, 2, 4, 8]:
        gain = float(ula_power_gain_linear(15.0, 15.0, n))
        assert np.isclose(gain, n, rtol=1e-12, atol=1e-12)


def test_ula_db_boresight_matches_10log10_n():
    gain_db = float(ula_power_gain_db(0.0, 0.0, 8))
    assert np.isclose(gain_db, 10.0 * np.log10(8.0))


def test_tx_energy_anchor():
    assert np.isclose(dbm_to_watt(30.0), 1.0)
    assert np.isclose(transmit_energy_joule(30.0, 0.5e-3, attempts=2), 1e-3)
    epb = energy_per_delivered_bit_joule(30.0, 0.5e-3, delivered_bits=1000, attempts=1)
    assert np.isclose(epb, 5e-7)
