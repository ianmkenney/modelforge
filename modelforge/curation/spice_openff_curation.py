from modelforge.utils.units import *

from modelforge.curation.curation_baseclass import *
from retry import retry
from tqdm import tqdm


class SPICE12OpenFFCuration(dataset_curation):
    """
    Routines to fetch and process the SPICE pubchem 1.2 dataset into a curated hdf5 file.


    Reference:
    Eastman, P., Behara, P.K., Dotson, D.L. et al. SPICE,
    A Dataset of Drug-like Molecules and Peptides for Training Machine Learning Potentials.
    Sci Data 10, 11 (2023). https://doi.org/10.1038/s41597-022-01882-6

    Dataset DOI:
    https://doi.org/10.5281/zenodo.8222043

    Parameters
    ----------
    hdf5_file_name, str, required
        name of the hdf5 file generated for the SPICE dataset
    output_file_dir: str, optional, default='./'
        Path to write the output hdf5 files.
    local_cache_dir: str, optional, default='./spice_dataset'
        Location to save downloaded dataset.
    convert_units: bool, optional, default=True
        Convert from [angstrom, hartree] (i.e., source units)
        to [nanometer, kJ/mol]

    Examples
    --------
    >>> spice_openff_data = SPICE_pubchem_1_2_openff_curation(hdf5_file_name='spice_pubchem_12_openff_dataset.hdf5',
    >>>                             local_cache_dir='~/datasets/spice12_openff_dataset')
    >>> spice_openff_data.process()

    """

    def _init_dataset_parameters(self):
        self.qcarchive_server = "ml.qcarchive.molssi.org"

        self.qm_parameters = {
            "geometry": {
                "u_in": unit.bohr,
                "u_out": unit.nanometer,
            },
            "dft_total_energy": {
                "u_in": unit.hartree,
                "u_out": unit.kilojoule_per_mole,
            },
            "dispersion_corrected_dft_total_energy": {
                "u_in": unit.hartree,
                "u_out": unit.kilojoule_per_mole,
            },
            "dft_total_gradient": {
                "u_in": unit.hartree / unit.bohr,
                "u_out": unit.kilojoule_per_mole / unit.angstrom,
            },
            "dispersion_corrected_dft_total_gradient": {
                "u_in": unit.hartree / unit.bohr,
                "u_out": unit.kilojoule_per_mole / unit.angstrom,
            },
            "mbis_charges": {
                "u_in": unit.elementary_charge,
                "u_out": unit.elementary_charge,
            },
            "scf_dipole": {
                "u_in": unit.elementary_charge * unit.bohr,
                "u_out": unit.elementary_charge * unit.nanometer,
            },
            "dispersion_correction_energy": {
                "u_in": unit.hartree,
                "u_out": unit.kilojoule_per_mole,
            },
            "dispersion_correction_gradient": {
                "u_in": unit.hartree / unit.bohr,
                "u_out": unit.kilojoule_per_mole / unit.angstrom,
            },
            "reference_energy": {
                "u_in": unit.hartree,
                "u_out": unit.kilojoule_per_mole,
            },
        }

    def _init_record_entries_series(self):
        # For data efficiency, information for different conformers will be grouped together
        # To make it clear to the dataset loader which pieces of information are common to all
        # conformers, or which pieces encode the series, we will label each value.
        # The keys in this dictionary correspond to the label of the entries in each record.
        # The value indicates if the entry contains series data (True) or a single common entry (False).
        # If the entry has a value of True, the "series" attribute in hdf5 file will be set to True; False, if False.
        # This information will be used by the code to read in the datafile to know how to parse underlying records.

        self._record_entries_series = {
            "name": False,
            "atomic_numbers": False,
            "n_configs": False,
            "reference_energy": False,
            "geometry": True,
            "dft_total_energy": True,
            "dft_total_gradient": True,
            "mbis_charges": True,
            "scf_dipole": True,
            "dispersion_correction_energy": True,
            "dispersion_correction_gradient": True,
            "dispersion_corrected_dft_total_gradient": True,
            "dispersion_corrected_dft_total_energy": True,
            "canonical_isomeric_explicit_hydrogen_mapped_smiles": False,
            "molecular_formula": False,
        }

    @retry(delay=1, jitter=1, backoff=2, tries=50, logger=logger, max_delay=10)
    def _fetch_singlepoint_from_qcarchive(
        self,
        dataset_type: str,
        dataset_name: str,
        specification_name: str,
        local_database_name: str,
        local_path_dir: str,
        pbar: tqdm,
        force_download: bool,
        unit_testing_max_records: Optional[int] = None,
    ):
        from sqlitedict import SqliteDict
        from loguru import logger

        ds = self.client.get_dataset(
            dataset_type=dataset_type, dataset_name=dataset_name
        )

        entry_names = ds.entry_names
        with SqliteDict(
            f"{local_path_dir}/{local_database_name}",
            tablename=specification_name,
            autocommit=True,
        ) as spice_db:
            # defining the db_keys as a set is faster for
            # searching to see if a key exists
            db_keys = set(spice_db.keys())
            to_fetch = []
            if force_download:
                for name in entry_names[0:unit_testing_max_records]:
                    to_fetch.append(name)
            else:
                for name in entry_names[0:unit_testing_max_records]:
                    if name not in db_keys:
                        to_fetch.append(name)
            pbar.total = pbar.total + len(to_fetch)
            pbar.refresh()

            # We need a different routine to fetch entries vs records with a give specification
            if len(to_fetch) > 0:
                if specification_name == "entry":
                    logger.debug(
                        f"Fetching {len(to_fetch)} entries from dataset {dataset_name}."
                    )
                    for entry in ds.iterate_entries(
                        to_fetch, force_refetch=force_download
                    ):
                        spice_db[entry.dict()["name"]] = entry
                        pbar.update(1)

                else:
                    logger.debug(
                        f"Fetching {len(to_fetch)} records for specification {specification_name} from dataset {dataset_name}."
                    )
                    for record in ds.iterate_records(
                        to_fetch,
                        specification_names=[specification_name],
                        force_refetch=force_download,
                    ):
                        spice_db[record[0]] = record[2]
                        pbar.update(1)

    def _calculate_reference_energy(self, smiles: str) -> float:
        from rdkit import Chem

        atom_energy = {
            "Br": {-1: -2574.2451510945853, 0: -2574.1167240829964},
            "C": {-1: -37.91424135791358, 0: -37.87264507233593, 1: -37.45349214963933},
            "Ca": {2: -676.9528465198214},
            "Cl": {-1: -460.3350243496703, 0: -460.1988762285739},
            "F": {-1: -99.91298732343974, 0: -99.78611622985483},
            "H": {-1: -0.5027370838721259, 0: -0.4987605100487531, 1: 0.0},
            "I": {-1: -297.8813829975981, 0: -297.76228914445625},
            "K": {1: -599.8025677513111},
            "Li": {1: -7.285254714046546},
            "Mg": {2: -199.2688420040449},
            "N": {
                -1: -54.602291095426494,
                0: -54.62327513368922,
                1: -54.08594142587869,
            },
            "Na": {1: -162.11366478783253},
            "O": {-1: -75.17101657391741, 0: -75.11317840410095, 1: -74.60241514396725},
            "P": {0: -341.3059197024934, 1: -340.9258392474849},
            "S": {-1: -398.2405387031612, 0: -398.1599636677874, 1: -397.7746615977658},
        }
        default_charge = {}
        for symbol in atom_energy:
            energies = [
                (energy, charge) for charge, energy in atom_energy[symbol].items()
            ]
            default_charge[symbol] = sorted(energies)[0][1]

        rdmol = Chem.MolFromSmiles(smiles, sanitize=False)
        total_charge = sum(atom.GetFormalCharge() for atom in rdmol.GetAtoms())
        symbol = [atom.GetSymbol() for atom in rdmol.GetAtoms()]
        charge = [default_charge[s] for s in symbol]
        delta = np.sign(total_charge - sum(charge))
        while delta != 0:
            best_index = -1
            best_energy = None
            for i in range(len(symbol)):
                s = symbol[i]
                e = atom_energy[s]
                new_charge = charge[i] + delta

                if new_charge in e:
                    if best_index == -1 or e[new_charge] - e[charge[i]] < best_energy:
                        best_index = i
                        best_energy = e[new_charge] - e[charge[i]]

            charge[best_index] += delta
            delta = np.sign(total_charge - sum(charge))

        return sum(atom_energy[s][c] for s, c in zip(symbol, charge))

    def _process_downloaded(
        self,
        local_path_dir: str,
        filename: str,
        unit_testing_max_records: Optional[int] = None,
    ):
        """
        Processes a downloaded dataset: extracts relevant information.

        Parameters
        ----------
        local_path_dir: str, required
            Path to the directory that contains the raw hdf5 datafile
        filename: str, required
            Name of the raw hdf5 file,
        unit_testing_max_records: int, optional, default=None
            If set to an integer ('n') the routine will only process the first 'n' records; useful for unit tests.

        Examples
        --------
        """
        from tqdm import tqdm
        import numpy as np
        from sqlitedict import SqliteDict
        from loguru import logger

        input_file_name = f"{local_path_dir}/{filename}"

        non_error_keys = []

        # identify the set of molecules that do not have errors
        with SqliteDict(
            input_file_name, tablename="spec_2", autocommit=False
        ) as spice_db_spec2:
            spec2_keys = list(spice_db_spec2.keys())

            with SqliteDict(
                input_file_name, tablename="spec_6", autocommit=False
            ) as spice_db_spec6:
                spec6_keys = list(spice_db_spec6.keys())
                # let us make sure that we do have the same keys
                assert np.all(spec2_keys == spec6_keys)

                for key in spec2_keys:
                    if (
                        spice_db_spec_2[key].status.value == "complete"
                        and spice_db_spec_6[key].status.value == "complete"
                    ):
                        non_error_keys.append(key)

        # sort the keys such that conformers are listed in numerical order
        # this is not strickly necessary, but will help to better retain
        # connection to the original QCArchive data
        sorted_keys = []

        # names of the pubchem molecules are of form  {numerical_id}-{conformer_number}
        # first sort by numerical_id
        pre_sort = sorted(non_error_keys, key=lambda x: int(x.split("-")[0]))

        # then sort each molecule by conformer_number
        current_val = pre_sort[0].split("-")[0]
        temp_list = []

        for val in pre_sort:
            name = val.split("-")[0]
            if name == current_val:
                temp_list.append(val)
            else:
                sorted_keys += sorted(temp_list, key=lambda x: int(x.split("-")[-1]))
                temp_list = []
                current_val = name
                temp_list.append(val)

        # dict to store the molecule name and an associated mol_id
        molecule_names = {}
        mol_id = 0

        # first read in molecules from entry
        with SqliteDict(
            input_file_name, tablename="entry", autocommit=False
        ) as spice_db:
            logger.debug(f"Processing {filename} entries.")
            for key in tqdm(sorted_keys):
                val = spice_db[key].dict()
                name = val["name"].split("-")[0]
                if not name in molecule_names.keys():
                    molecule_names[name] = mol_id
                    mol_id += 1

                    data_temp = {}
                    data_temp["name"] = name
                    atomic_numbers = []
                    for element in val["molecule"]["symbols"]:
                        atomic_numbers.append(
                            qcel.periodictable.to_atomic_number(element)
                        )
                    data_temp["atomic_numbers"] = atomic_numbers
                    data_temp["molecular_formula"] = val["molecule"]["identifiers"][
                        "molecular_formula"
                    ]
                    data_temp[
                        "canonical_isomeric_explicit_hydrogen_mapped_smiles"
                    ] = val["molecule"]["extras"][
                        "canonical_isomeric_explicit_hydrogen_mapped_smiles"
                    ]
                    data_temp["n_configs"] = 1
                    data_temp["geometry"] = val["molecule"]["geometry"].reshape(
                        1, -1, 3
                    )
                    data_temp["reference_energy"] = self._calculate_reference_energy(
                        data_temp["canonical_isomeric_explicit_hydrogen_mapped_smiles"]
                    )
                    self.data.append(data_temp)
                else:
                    index = molecule_names[name]
                    self.data[index]["n_configs"] += 1
                    self.data[index]["geometry"] = np.vstack(
                        (
                            self.data[index]["geometry"],
                            val["molecule"]["geometry"].reshape(1, -1, 3),
                        )
                    )
            # add units to the geometry
            for datapoint in data:
                datapoint["geometry"] = (
                    datapoint["geometry"] * self.qm_parameters["geometry"]["u_in"]
                )

        with SqliteDict(
            input_file_name, tablename="spec_2", autocommit=False
        ) as spice_db:
            logger.debug(f"Processing {filename} spec_2.")

            for key in tqdm(sorted_keys):
                name = key.split("-")[0]
                val = spice_db[key].dict()

                index = molecule_names[name]

                quantity = "dft total energy"
                quanity_o = "dft_total_energy"
                if not quanity_o in data[index].keys():
                    data[index][quanity_o] = val["properties"][quantity]
                else:
                    data[index][quanity_o] = np.vstack(
                        (data[index][quanity_o], val["properties"][quantity])
                    )

                quantity = "dft total gradient"
                quantity_o = "dft_total_gradient"
                if not quantity_o in data[index].keys():
                    data[index][quantity_o] = np.array(
                        val["properties"][quantity]
                    ).reshape(1, -1, 3)
                else:
                    data[index][quantity_o] = np.vstack(
                        (
                            data[index][quantity_o],
                            np.array(val["properties"][quantity]).reshape(1, -1, 3),
                        )
                    )

                quantity = "mbis charges"
                quantity_o = "mbis_charges"
                if not quantity_o in data[index].keys():
                    data[index][quantity_o] = np.array(
                        val["properties"][quantity]
                    ).reshape(1, -1)
                else:
                    data[index][quantity_o] = np.vstack(
                        (
                            data[index][quantity_o],
                            np.array(val["properties"][quantity]).reshape(1, -1),
                        )
                    )

                quantity = "scf dipole"
                quantity_o = "scf_dipole"
                if not quantity_o in data[index].keys():
                    data[index][quantity_o] = np.array(
                        val["properties"][quantity]
                    ).reshape(1, 3)
                else:
                    data[index][quantity_o] = np.vstack(
                        (
                            data[index][quantity_o],
                            np.array(val["properties"][quantity]).reshape(1, 3),
                        )
                    )

        with SqliteDict(
            input_file_name, tablename="spec_6", autocommit=False
        ) as spice_db:
            logger.debug(f"Processing {filename} spec_6.")

            for key in tqdm(sorted_keys):
                name = key.split("-")[0]
                val = spice_db[key].dict()
                index = molecule_names[name]

                # typecasting issue in there

                quantity = "dispersion correction energy"
                quantity_o = "dispersion_correction_energy"
                if not quantity_o in data[index].keys():
                    data[index][quantity_o] = float(val["properties"][quantity])
                else:
                    data[index][quantity_o] = np.append(
                        data[index][quantity_o], float(val["properties"][quantity])
                    )
                quantity = "dispersion correction gradient"
                quantity_o = "dispersion_correction_gradient"
                if not quantity_o in data[index].keys():
                    data[index][quantity_o] = np.array(
                        val["properties"][quantity]
                    ).reshape(1, -1, 3)
                else:
                    data[index][quantity_o] = np.vstack(
                        (
                            data[index][quantity_o],
                            np.array(val["properties"][quantity]).reshape(1, -1, 3),
                        )
                    )
        # assign units
        for datapoint in data:
            for key in datapoint.keys():
                if key in self.qm_parameters:
                    datapoint[key] = datapoint[key] * self.qm_parameters[key]["u_in"]

            datapoint["dispersion_corrected_dft_total_energy"] = (
                datapoint["dft_total_energy"]
                + datapoint["dispersion_correction_energy"]
            )
            datapoint["dispersion_corrected_dft_total_gradient"] = (
                datapoint["dft_total_gradient"]
                + datapoint["dispersion_correction_gradient"]
            )

        if self.convert_units:
            for datapoint in data:
                for key, val in datapoint.items():
                    if isinstance(val, pint.Quantity):
                        try:
                            datapoint[key] = val.to(
                                self.qm_parameters[key]["u_out"], "chem"
                            )
                        except Exception:
                            try:
                                # if the unit conversion can't be done
                                print(
                                    f"could not convert {key} with unit {val.u} to {self.qm_parameters[key]['u_out']}"
                                )
                            except Exception:
                                print(
                                    f"could not convert {key} with unit {val.u}. {val.u} not in the defined unit conversions."
                                )

    def process(
        self,
        force_download: bool = False,
        unit_testing_max_records: Optional[int] = None,
        n_threads=6,
    ) -> None:
        """
        Downloads the dataset, extracts relevant information, and writes an hdf5 file.

        Parameters
        ----------
        force_download: bool, optional, default=False
            If the raw data_file is present in the local_cache_dir, the local copy will be used.
            If True, this will force the software to download the data again, even if present.
        unit_testing_max_records: int, optional, default=None
            If set to an integer, 'n', the routine will only process the first 'n' records, useful for unit tests.

        Examples
        --------
        >>> spice_openff_data = SPICE_pubchem_1_2_openff_curation(hdf5_file_name='spice_pubchem_12_openff_dataset.hdf5',
        >>>                             local_cache_dir='~/datasets/spice12_openff_dataset')
        >>> spice_openff_data.process()

        """
        from qcportal import PortalClient
        from concurrent.futures import ThreadPoolExecutor, as_completed

        dataset_type = "singlepoint"
        dataset_names = [
            "SPICE PubChem Set 1 Single Points Dataset v1.2",
            "SPICE PubChem Set 2 Single Points Dataset v1.2",
            "SPICE PubChem Set 3 Single Points Dataset v1.2",
            "SPICE PubChem Set 4 Single Points Dataset v1.2",
            "SPICE PubChem Set 5 Single Points Dataset v1.2",
            "SPICE PubChem Set 6 Single Points Dataset v1.2",
        ]
        specification_names = ["spec_2", "spec_6", "entry"]
        self.client = PortalClient(self.qcarchive_server)

        # for dataset_name in dataset_names:
        #     for specification_name in specification_names:
        #         self._fetch_singlepoint_from_qcarchive(
        #             dataset_type=dataset_type,
        #             dataset_name=dataset_name,
        #             specification_name=specification_name,
        #             local_database_name=local_database_name,
        #             local_path_dir=self.local_cache_dir,
        #             unit_testing_max_records=unit_testing_max_records,
        #         )
        threads = []
        completed = 0
        local_database_names = []

        with tqdm() as pbar:
            pbar.total = 0
            with ThreadPoolExecutor(max_workers=n_threads) as e:
                for i, dataset_name in enumerate(dataset_names):
                    local_database_name = f"spice_pubchem{i+1}_12.sqlite"
                    local_database_names.append(local_database_name)
                    for specification_name in specification_names:
                        threads.append(
                            e.submit(
                                self._fetch_singlepoint_from_qcarchive,
                                dataset_type=dataset_type,
                                dataset_name=dataset_name,
                                specification_name=specification_name,
                                local_database_name=local_database_name,
                                local_path_dir=self.local_cache_dir,
                                pbar=pbar,
                                force_download=force_download,
                                unit_testing_max_records=unit_testing_max_records,
                            )
                        )

        self._clear_data()
        for local_database_name in local_database_names:
            self._process_downloaded(
                self.local_cache_dir, local_database_name, unit_testing_max_records
            )

        self._generate_hdf5()
