import torch
from modelforge.potential.painn import PaiNN


def test_PaiNN_forward(single_batch_with_batchsize_64):
    """Test initialization of the PaiNN neural network potential."""
    # read default parameters
    from modelforge.tests.test_models import load_configs

    # read default parameters
    config = load_configs("painn_without_ase", "qm9")

    # Extract parameters
    potential_parameter = config["potential"].get("potential_parameter", {})

    painn = PaiNN(**potential_parameter)
    assert painn is not None, "PaiNN model should be initialized."

    nnp_input = single_batch_with_batchsize_64.nnp_input.to(dtype=torch.float32)
    energy = painn(nnp_input)["E"]
    nr_of_mols = nnp_input.atomic_subsystem_indices.unique().shape[0]

    assert (
        len(energy) == nr_of_mols
    )  # Assuming energy is calculated per sample in the batch


def test_painn_interaction_equivariance(single_batch_with_batchsize_64):
    from modelforge.potential.painn import PaiNN
    from dataclasses import replace
    import torch

    from modelforge.tests.test_models import load_configs

    # read default parameters
    config = load_configs("painn_without_ase", "qm9")

    # Extract parameters
    potential_parameter = config["potential"].get("potential_parameter", {})

    # define a rotation matrix in 3D that rotates by 90 degrees around the z-axis
    # (clockwise when looking along the z-axis towards the origin)
    rotation_matrix = torch.tensor(
        [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]], dtype=torch.float64
    )

    painn = PaiNN(**potential_parameter).to(torch.float64)
    methane_input = single_batch_with_batchsize_64.nnp_input.to(dtype=torch.float64)
    perturbed_methane_input = replace(methane_input)
    perturbed_methane_input.positions = torch.matmul(
        methane_input.positions, rotation_matrix
    )

    # prepare reference and perturbed inputs
    pairlist_output = painn.input_preparation.prepare_inputs(methane_input)
    reference_prepared_input = painn.core_module._model_specific_input_preparation(
        methane_input, pairlist_output
    )

    reference_d_ij = reference_prepared_input.d_ij
    reference_r_ij = reference_prepared_input.r_ij
    reference_dir_ij = reference_r_ij / reference_d_ij
    reference_f_ij = (
        painn.core_module.representation_module.radial_symmetry_function_module(
            reference_d_ij
        )
    )

    pairlist_output = painn.input_preparation.prepare_inputs(perturbed_methane_input)
    perturbed_prepared_input = painn.core_module._model_specific_input_preparation(
        perturbed_methane_input, pairlist_output
    )

    perturbed_d_ij = perturbed_prepared_input.d_ij
    perturbed_r_ij = perturbed_prepared_input.r_ij
    perturbed_dir_ij = perturbed_r_ij / perturbed_d_ij
    perturbed_f_ij = (
        painn.core_module.representation_module.radial_symmetry_function_module(
            perturbed_d_ij
        )
    )

    # check that the invariant properties are preserved
    # d_ij is the distance between atom i and j
    # f_ij is the radial basis function of d_ij
    assert torch.allclose(reference_d_ij, perturbed_d_ij)
    assert torch.allclose(reference_f_ij, perturbed_f_ij)

    # what shoudl not be invariant is the direction
    assert not torch.allclose(reference_dir_ij, perturbed_dir_ij)

    # Check for equivariance
    # rotate the reference dir_ij
    rotated_reference_dir_ij = torch.matmul(reference_dir_ij, rotation_matrix)
    # Compare the rotated original dir_ij with the dir_ij from rotated positions
    assert torch.allclose(rotated_reference_dir_ij, perturbed_dir_ij)

    # Test that the interaction block is equivariant
    # First we test the transformed inputs
    reference_tranformed_inputs = painn.core_module.representation_module(
        reference_prepared_input
    )
    perturbed_tranformed_inputs = painn.core_module.representation_module(
        perturbed_prepared_input
    )

    assert torch.allclose(
        reference_tranformed_inputs["q"], perturbed_tranformed_inputs["q"]
    )
    assert torch.allclose(
        reference_tranformed_inputs["mu"], perturbed_tranformed_inputs["mu"]
    )

    painn_interaction = painn.core_module.interaction_modules[0]

    reference_r = painn_interaction(
        reference_tranformed_inputs["q"],
        reference_tranformed_inputs["mu"],
        reference_tranformed_inputs["filters"][0],
        reference_dir_ij,
        reference_prepared_input.pair_indices,
    )

    perturbed_r = painn_interaction(
        perturbed_tranformed_inputs["q"],
        perturbed_tranformed_inputs["mu"],
        reference_tranformed_inputs["filters"][0],
        perturbed_dir_ij,
        perturbed_prepared_input.pair_indices,
    )

    perturbed_q, perturbed_mu = perturbed_r
    reference_q, reference_mu = reference_r

    # mu is different, q is invariant
    assert torch.allclose(reference_q, perturbed_q)
    assert not torch.allclose(reference_mu, perturbed_mu)

    mixed_reference_q, mixed_reference_mu = painn.core_module.mixing_modules[0](
        reference_q, reference_mu
    )
    mixed_perturbed_q, mixed_perturbed_mu = painn.core_module.mixing_modules[0](
        perturbed_q, perturbed_mu
    )

    # q is a scalar property and invariant
    assert torch.allclose(mixed_reference_q, mixed_perturbed_q, atol=1e-2)
    # mu is a vector property and should not be invariant
    assert not torch.allclose(mixed_reference_mu, mixed_perturbed_mu)


import torch
from modelforge.tests.test_schnet import setup_single_methane_input


def setup_spk_painn_representation(
    cutoff, nr_atom_basis, number_of_gaussians, nr_of_interactions
):
    # ------------------------------------ #
    # set up the schnetpack Painn representation model
    from schnetpack.nn import GaussianRBF, CosineCutoff
    from schnetpack.representation import PaiNN as schnetpack_PaiNN
    from openff.units import unit

    radial_basis = GaussianRBF(
        n_rbf=number_of_gaussians, cutoff=cutoff.to(unit.angstrom).m
    )
    return schnetpack_PaiNN(
        n_atom_basis=nr_atom_basis,
        n_interactions=nr_of_interactions,
        radial_basis=radial_basis,
        cutoff_fn=CosineCutoff(cutoff.to(unit.angstrom).m),
    )


def setup_modelforge_painn_representation(
    cutoff, nr_atom_basis, number_of_gaussians, nr_of_interactions
):
    # ------------------------------------ #
    # set up the modelforge Painn representation model
    # which means that we only want to call the
    # _transform_input() method
    from modelforge.potential.painn import PaiNN

    return PaiNN(
        max_Z=100,
        number_of_atom_features=nr_atom_basis,
        number_of_interaction_modules=nr_of_interactions,
        number_of_radial_basis_functions=number_of_gaussians,
        cutoff=cutoff,
        shared_interactions=False,
        shared_filters=False,
        processing_operation=[],
        readout_operation=[
            {
                "step": "from_atom_to_molecule",
                "mode": "sum",
                "in": "E_i",
                "index_key": "atomic_subsystem_indices",
                "out": "E",
            }
        ],
    )


def test_painn_representation_implementation():
    # ---------------------------------------- #
    # setup the PaiNN model
    # ---------------------------------------- #
    from openff.units import unit
    from .precalculated_values import load_precalculated_painn_results

    cutoff = unit.Quantity(5.0, unit.angstrom)
    nr_atom_basis = 8
    number_of_gaussians = 5
    nr_of_interactions = 3
    torch.manual_seed(1234)

    modelforge_painn = setup_modelforge_painn_representation(
        cutoff, nr_atom_basis, number_of_gaussians, nr_of_interactions
    ).double()
    # ------------------------------------ #
    # set up the input for the Painn model
    input = setup_single_methane_input()
    spk_input = input["spk_methane_input"]
    mf_nnp_input = input["modelforge_methane_input"]

    modelforge_painn.input_preparation._input_checks(mf_nnp_input)
    pairlist_output = modelforge_painn.input_preparation.prepare_inputs(mf_nnp_input)
    pain_nn_input_mf = modelforge_painn.core_module._model_specific_input_preparation(
        mf_nnp_input, pairlist_output
    )

    # ---------------------------------------- #
    # test forward pass
    # ---------------------------------------- #

    # reset filter parameters
    torch.manual_seed(1234)
    modelforge_painn.core_module.representation_module.filter_net.reset_parameters()

    modelforge_results = modelforge_painn.core_module.forward(
        pain_nn_input_mf, pairlist_output
    )
    schnetpack_results = load_precalculated_painn_results()

    # check that the scalar and vector representations are the same
    # start with scalar representation
    assert (
        schnetpack_results["scalar_representation"].shape
        == modelforge_results["q"].shape
    )

    scalar_spk = schnetpack_results["scalar_representation"].double()
    scalar_mf = modelforge_results["q"].double()

    assert torch.allclose(scalar_spk, scalar_mf, atol=1e-4)
    # check vector representation
    assert (
        schnetpack_results["vector_representation"].shape
        == modelforge_results["mu"].shape
    )

    assert torch.allclose(
        schnetpack_results["vector_representation"].double(),
        modelforge_results["mu"].double(),
        atol=1e-4,
    )
