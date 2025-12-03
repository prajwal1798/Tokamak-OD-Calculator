import numpy as np
from .geometry_plasma import Shape, Ip_from_q95_PROCESS, greenwald_density, thermal_beta
from .tf_coils import TFCoils


def scan_A_Bt_grid(
    A_min, A_max,
    Bt_min, Bt_max,
    n_A, n_Bt,
    a, kappa, delta,
    q95, f_G,
    Te_eV, Ti_e_V,
    tf: TFCoils,
):
    A_vals = np.linspace(A_min, A_max, n_A)
    Bt_vals = np.linspace(Bt_min, Bt_max, n_Bt)

    A_grid, Bt_grid = np.meshgrid(A_vals, Bt_vals, indexing="ij")

    Ip_grid = np.zeros_like(A_grid)
    ne_grid = np.zeros_like(A_grid)
    Icoil_grid = np.zeros_like(A_grid)
    beta_grid = np.zeros_like(A_grid)
    R_grid = np.zeros_like(A_grid)
    feasible_mask = np.ones_like(A_grid, dtype=bool)

    for i in range(n_A):
        for j in range(n_Bt):
            A = A_grid[i, j]
            Bt = Bt_grid[i, j]
            R = A * a
            shape = Shape(R=R, a=a, kappa=kappa, delta=delta)

            Ip_MA = Ip_from_q95_PROCESS(Bt, q95, shape)
            _, ne = greenwald_density(Ip_MA, a, f_G)
            beta = thermal_beta(Bt, ne, Te_eV, Ti_e_V)

            Icoil = tf.coil_current(Bt, R)
            feasible = tf.feasible(Bt, R)

            Ip_grid[i, j] = Ip_MA
            ne_grid[i, j] = ne
            Icoil_grid[i, j] = Icoil
            beta_grid[i, j] = beta
            R_grid[i, j] = R
            feasible_mask[i, j] = feasible

    return {
        "A": A_grid,
        "Bt": Bt_grid,
        "Ip_MA": Ip_grid,
        "ne": ne_grid,
        "Icoil": Icoil_grid,
        "beta": beta_grid,
        "R": R_grid,
        "feasible": feasible_mask,
    }
