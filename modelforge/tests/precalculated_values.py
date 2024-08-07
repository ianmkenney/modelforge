import torch


def setup_single_methane_input():
    import torch

    # ------------------------------------ #
    # set up the input for the spk Painn model
    methan_spk = {
        "_idx": torch.tensor([0]),
        "dipole_moment": torch.tensor([0.0], dtype=torch.float64),
        "energy_U0": torch.tensor([-40.4789], dtype=torch.float64),
        "energy_U": torch.tensor([-40.4761], dtype=torch.float64),
        "_n_atoms": torch.tensor([5]),
        "_atomic_numbers": torch.tensor([6, 1, 1, 1, 1]),
        "_positions": torch.tensor(
            [
                [-1.2698e-02, 1.0858e00, 8.0010e-03],
                [2.1504e-03, -6.0313e-03, 1.9761e-03],
                [1.0117e00, 1.4638e00, 2.7657e-04],
                [-5.4082e-01, 1.4475e00, -8.7664e-01],
                [-5.2381e-01, 1.4379e00, 9.0640e-01],
            ],
            dtype=torch.float64,
        ),
        "_cell": torch.tensor(
            [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]], dtype=torch.float64
        ),
        "_pbc": torch.tensor([False, False, False]),
        "_offsets": torch.tensor(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=torch.float64,
        ),
        "_idx_i": torch.tensor(
            [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        ),
        "_idx_j": torch.tensor(
            [1, 2, 3, 4, 0, 2, 3, 4, 0, 1, 3, 4, 0, 1, 2, 4, 0, 1, 2, 3]
        ),
        "_Rij": torch.tensor(
            [
                [1.4849e-02, -1.0918e00, -6.0249e-03],
                [1.0244e00, 3.7795e-01, -7.7244e-03],
                [-5.2812e-01, 3.6172e-01, -8.8464e-01],
                [-5.1112e-01, 3.5213e-01, 8.9840e-01],
                [-1.4849e-02, 1.0918e00, 6.0249e-03],
                [1.0096e00, 1.4698e00, -1.6995e-03],
                [-5.4297e-01, 1.4536e00, -8.7862e-01],
                [-5.2596e-01, 1.4440e00, 9.0442e-01],
                [-1.0244e00, -3.7795e-01, 7.7244e-03],
                [-1.0096e00, -1.4698e00, 1.6995e-03],
                [-1.5525e00, -1.6225e-02, -8.7692e-01],
                [-1.5355e00, -2.5819e-02, 9.0612e-01],
                [5.2812e-01, -3.6172e-01, 8.8464e-01],
                [5.4297e-01, -1.4536e00, 8.7862e-01],
                [1.5525e00, 1.6225e-02, 8.7692e-01],
                [1.7001e-02, -9.5940e-03, 1.7830e00],
                [5.1112e-01, -3.5213e-01, -8.9840e-01],
                [5.2596e-01, -1.4440e00, -9.0442e-01],
                [1.5355e00, 2.5819e-02, -9.0612e-01],
                [-1.7001e-02, 9.5940e-03, -1.7830e00],
            ],
            dtype=torch.float64,
        ),
    }
    # ------------------------------------ #

    # ------------------------------------ #
    # set up the input for the modelforge Painn model
    atomic_numbers = torch.tensor([6, 1, 1, 1, 1], dtype=torch.int64)

    positions = (
        torch.tensor(
            [
                [-1.2698e-02, 1.0858e00, 8.0010e-03],
                [2.1504e-03, -6.0313e-03, 1.9761e-03],
                [1.0117e00, 1.4638e00, 2.7657e-04],
                [-5.4082e-01, 1.4475e00, -8.7664e-01],
                [-5.2381e-01, 1.4379e00, 9.0640e-01],
            ],
            dtype=torch.float64,
            requires_grad=True,
        )
        / 10
    )
    E = torch.tensor([0.0], requires_grad=True)
    atomic_subsystem_indices = torch.tensor([0, 0, 0, 0, 0], dtype=torch.int32)
    from modelforge.dataset.dataset import NNPInput

    modelforge_methane = NNPInput(
        atomic_numbers=atomic_numbers,
        positions=positions,
        atomic_subsystem_indices=atomic_subsystem_indices,
        total_charge=torch.tensor([0], dtype=torch.int32),
    )
    # ------------------------------------ #

    return {
        "spk_methane_input": methan_spk,
        "modelforge_methane_input": modelforge_methane,
    }


def load_precalculated_painn_results():
    results = {
        "_idx": torch.tensor([0]),
        "dipole_moment": torch.tensor([0.0]),
        "energy_U0": torch.tensor([-40.4789], dtype=torch.float64),
        "energy_U": torch.tensor([-40.4761], dtype=torch.float64),
        "_n_atoms": torch.tensor([5]),
        "_atomic_numbers": torch.tensor([6, 1, 1, 1, 1]),
        "_positions": torch.tensor(
            [
                [-1.2698e-02, 1.0858e00, 8.0010e-03],
                [2.1504e-03, -6.0313e-03, 1.9761e-03],
                [1.0117e00, 1.4638e00, 2.7657e-04],
                [-5.4082e-01, 1.4475e00, -8.7664e-01],
                [-5.2381e-01, 1.4379e00, 9.0640e-01],
            ],
            dtype=torch.float64,
        ),
        "_cell": torch.tensor(
            [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]], dtype=torch.float64
        ),
        "_pbc": torch.tensor([False, False, False]),
        "_offsets": torch.tensor(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=torch.float64,
        ),
        "_idx_i": torch.tensor(
            [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        ),
        "_idx_j": torch.tensor(
            [1, 2, 3, 4, 0, 2, 3, 4, 0, 1, 3, 4, 0, 1, 2, 4, 0, 1, 2, 3]
        ),
        "_Rij": torch.tensor(
            [
                [1.4849e-02, -1.0918e00, -6.0249e-03],
                [1.0244e00, 3.7795e-01, -7.7244e-03],
                [-5.2812e-01, 3.6172e-01, -8.8464e-01],
                [-5.1112e-01, 3.5213e-01, 8.9840e-01],
                [-1.4849e-02, 1.0918e00, 6.0249e-03],
                [1.0096e00, 1.4698e00, -1.6995e-03],
                [-5.4297e-01, 1.4536e00, -8.7862e-01],
                [-5.2596e-01, 1.4440e00, 9.0442e-01],
                [-1.0244e00, -3.7795e-01, 7.7244e-03],
                [-1.0096e00, -1.4698e00, 1.6995e-03],
                [-1.5525e00, -1.6225e-02, -8.7692e-01],
                [-1.5355e00, -2.5819e-02, 9.0612e-01],
                [5.2812e-01, -3.6172e-01, 8.8464e-01],
                [5.4297e-01, -1.4536e00, 8.7862e-01],
                [1.5525e00, 1.6225e-02, 8.7692e-01],
                [1.7001e-02, -9.5940e-03, 1.7830e00],
                [5.1112e-01, -3.5213e-01, -8.9840e-01],
                [5.2596e-01, -1.4440e00, -9.0442e-01],
                [1.5355e00, 2.5819e-02, -9.0612e-01],
                [-1.7001e-02, 9.5940e-03, -1.7830e00],
            ],
            dtype=torch.float64,
        ),
        "scalar_representation": torch.tensor(
            [
                [0.1628, 0.9060, -1.7949, -2.2348, -1.5576, 0.0653, -1.8837, 0.0704],
                [-0.2524, 0.6174, -0.1448, 0.1231, -0.6103, -1.6204, -0.1701, -0.9315],
                [-0.2524, 0.6174, -0.1448, 0.1231, -0.6103, -1.6204, -0.1701, -0.9315],
                [-0.2524, 0.6174, -0.1448, 0.1231, -0.6103, -1.6204, -0.1701, -0.9315],
                [-0.2524, 0.6174, -0.1448, 0.1231, -0.6103, -1.6204, -0.1701, -0.9315],
            ],
            dtype=torch.float64,
        ),
        "vector_representation": torch.tensor(
            [
                [
                    [
                        3.1709e-06,
                        -1.8076e-07,
                        -5.1120e-06,
                        2.3066e-06,
                        -2.5445e-06,
                        5.7499e-07,
                        1.3830e-06,
                        2.2221e-06,
                    ],
                    [
                        -2.4997e-06,
                        2.2083e-07,
                        3.9980e-06,
                        -2.0408e-06,
                        1.1304e-06,
                        3.2887e-07,
                        -1.1924e-06,
                        -1.5206e-06,
                    ],
                    [
                        -2.4008e-07,
                        1.2919e-07,
                        -6.7643e-08,
                        -3.3288e-07,
                        -2.0324e-07,
                        2.8985e-07,
                        -1.9070e-07,
                        -2.2505e-07,
                    ],
                ],
                [
                    [
                        -5.5289e-04,
                        1.4046e-04,
                        4.2147e-03,
                        -2.3912e-03,
                        4.2472e-03,
                        -1.1341e-03,
                        -1.4090e-03,
                        -2.1828e-03,
                    ],
                    [
                        4.0891e-02,
                        -1.0310e-02,
                        -3.1037e-01,
                        1.7599e-01,
                        -3.1260e-01,
                        8.3624e-02,
                        1.0368e-01,
                        1.6052e-01,
                    ],
                    [
                        2.2560e-04,
                        -5.6923e-05,
                        -1.7126e-03,
                        9.7115e-04,
                        -1.7250e-03,
                        4.6145e-04,
                        5.7210e-04,
                        8.8581e-04,
                    ],
                ],
                [
                    [
                        -3.8371e-02,
                        9.6760e-03,
                        2.9121e-01,
                        -1.6513e-01,
                        2.9330e-01,
                        -7.8460e-02,
                        -9.7277e-02,
                        -1.5061e-01,
                    ],
                    [
                        -1.4156e-02,
                        3.5694e-03,
                        1.0744e-01,
                        -6.0925e-02,
                        1.0821e-01,
                        -2.8948e-02,
                        -3.5890e-02,
                        -5.5567e-02,
                    ],
                    [
                        2.8971e-04,
                        -7.3015e-05,
                        -2.1964e-03,
                        1.2454e-03,
                        -2.2120e-03,
                        5.9190e-04,
                        7.3367e-04,
                        1.1356e-03,
                    ],
                ],
                [
                    [
                        1.9780e-02,
                        -4.9889e-03,
                        -1.5013e-01,
                        8.5131e-02,
                        -1.5121e-01,
                        4.0447e-02,
                        5.0148e-02,
                        7.7643e-02,
                    ],
                    [
                        -1.3547e-02,
                        3.4161e-03,
                        1.0283e-01,
                        -5.8307e-02,
                        1.0356e-01,
                        -2.7704e-02,
                        -3.4346e-02,
                        -5.3180e-02,
                    ],
                    [
                        3.3135e-02,
                        -8.3570e-03,
                        -2.5148e-01,
                        1.4260e-01,
                        -2.5328e-01,
                        6.7753e-02,
                        8.4001e-02,
                        1.3006e-01,
                    ],
                ],
                [
                    [
                        1.9144e-02,
                        -4.8287e-03,
                        -1.4529e-01,
                        8.2391e-02,
                        -1.4634e-01,
                        3.9145e-02,
                        4.8532e-02,
                        7.5143e-02,
                    ],
                    [
                        -1.3187e-02,
                        3.3258e-03,
                        1.0010e-01,
                        -5.6760e-02,
                        1.0082e-01,
                        -2.6968e-02,
                        -3.3434e-02,
                        -5.1770e-02,
                    ],
                    [
                        -3.3650e-02,
                        8.4877e-03,
                        2.5538e-01,
                        -1.4482e-01,
                        2.5722e-01,
                        -6.8804e-02,
                        -8.5305e-02,
                        -1.3208e-01,
                    ],
                ],
            ],
            dtype=torch.float64,
        ),
    }

    return results


def load_precalculated_schnet_results():
    schnetpack_results = {
        "_idx": torch.tensor([0]),
        "dipole_moment": torch.tensor([0.0], dtype=torch.float64),
        "energy_U0": torch.tensor([-40.4789], dtype=torch.float64),
        "energy_U": torch.tensor([-40.4761], dtype=torch.float64),
        "_n_atoms": torch.tensor([5]),
        "_atomic_numbers": torch.tensor([6, 1, 1, 1, 1]),
        "_positions": torch.tensor(
            [
                [-1.2698e-02, 1.0858e00, 8.0010e-03],
                [2.1504e-03, -6.0313e-03, 1.9761e-03],
                [1.0117e00, 1.4638e00, 2.7657e-04],
                [-5.4082e-01, 1.4475e00, -8.7664e-01],
                [-5.2381e-01, 1.4379e00, 9.0640e-01],
            ],
            dtype=torch.float64,
        ),
        "_cell": torch.tensor(
            [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]], dtype=torch.float64
        ),
        "_pbc": torch.tensor([False, False, False]),
        "_offsets": torch.tensor(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=torch.float64,
        ),
        "_idx_i": torch.tensor(
            [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4]
        ),
        "_idx_j": torch.tensor(
            [1, 2, 3, 4, 0, 2, 3, 4, 0, 1, 3, 4, 0, 1, 2, 4, 0, 1, 2, 3]
        ),
        "_Rij": torch.tensor(
            [
                [1.4849e-02, -1.0918e00, -6.0249e-03],
                [1.0244e00, 3.7795e-01, -7.7244e-03],
                [-5.2812e-01, 3.6172e-01, -8.8464e-01],
                [-5.1112e-01, 3.5213e-01, 8.9840e-01],
                [-1.4849e-02, 1.0918e00, 6.0249e-03],
                [1.0096e00, 1.4698e00, -1.6995e-03],
                [-5.4297e-01, 1.4536e00, -8.7862e-01],
                [-5.2596e-01, 1.4440e00, 9.0442e-01],
                [-1.0244e00, -3.7795e-01, 7.7244e-03],
                [-1.0096e00, -1.4698e00, 1.6995e-03],
                [-1.5525e00, -1.6225e-02, -8.7692e-01],
                [-1.5355e00, -2.5819e-02, 9.0612e-01],
                [5.2812e-01, -3.6172e-01, 8.8464e-01],
                [5.4297e-01, -1.4536e00, 8.7862e-01],
                [1.5525e00, 1.6225e-02, 8.7692e-01],
                [1.7001e-02, -9.5940e-03, 1.7830e00],
                [5.1112e-01, -3.5213e-01, -8.9840e-01],
                [5.2596e-01, -1.4440e00, -9.0442e-01],
                [1.5355e00, 2.5819e-02, -9.0612e-01],
                [-1.7001e-02, 9.5940e-03, -1.7830e00],
            ],
            dtype=torch.float64,
        ),
        "scalar_representation": torch.tensor(
            [
                [
                    0.1254,
                    -0.9284,
                    -0.6935,
                    2.2096,
                    -0.0555,
                    -0.1595,
                    -1.1804,
                    0.6562,
                    -0.3001,
                    -0.4318,
                    1.0901,
                    -0.0626,
                ],
                [
                    -0.0200,
                    -1.9309,
                    0.5967,
                    -0.3637,
                    0.2486,
                    0.1331,
                    -0.7700,
                    -1.4115,
                    -0.1196,
                    0.5523,
                    0.0644,
                    -0.4112,
                ],
                [
                    -0.0200,
                    -1.9309,
                    0.5967,
                    -0.3637,
                    0.2486,
                    0.1331,
                    -0.7700,
                    -1.4115,
                    -0.1196,
                    0.5523,
                    0.0645,
                    -0.4112,
                ],
                [
                    -0.0200,
                    -1.9309,
                    0.5967,
                    -0.3637,
                    0.2486,
                    0.1331,
                    -0.7700,
                    -1.4115,
                    -0.1196,
                    0.5523,
                    0.0645,
                    -0.4112,
                ],
                [
                    -0.0200,
                    -1.9309,
                    0.5967,
                    -0.3637,
                    0.2486,
                    0.1331,
                    -0.7700,
                    -1.4115,
                    -0.1196,
                    0.5523,
                    0.0645,
                    -0.4112,
                ],
            ],
            dtype=torch.float64,
        ),
    }
    return schnetpack_results
