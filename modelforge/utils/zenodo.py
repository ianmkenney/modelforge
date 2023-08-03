"""Module for fetching datafiles from zenodo"""

import requests
from typing import Optional

def fetch_record_id_from_doi(doi: str, timeout: Optional[int]= 10) -> str:
    """Retrieve URL associated with a DOI.

    Parameters
    ----------
    doi : str, required
        The DOI to be considered.  This can be formatted as a URL.
    timeout : int, optional, default=10
        The number of seconds to wait to establish a connection

    Returns
    -------
    url : str
        The target URL linked to the DOI.
    """

    doi_org_url = 'https://dx.doi.org/'
    if doi.startswith('http'):
        input_url = doi
    else:
        input_url = doi_org_url + doi

    try:
        response = requests.get(input_url, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        raise Exception('Fetching url for DOI timed out.')

    if not response.ok:
        raise Exception(f'{doi} could not be accessed.')

    # the record id is stored at the end of the url
    # e.g., https://zenodo.org/record/3588339
    return response.url.split('/')[-1]

def get_zenodo_datafiles(record_id: str, file_extension: str, timeout: Optional[int]= 10)-> str:
    """Retrieve link(s) to datafiles on zenodo with a given extension.

    Parameters
    ----------
    record_id : str, required
        zenodo.org record id
    file_extension : str, required
        Return file(s) with extensions that match file_extension
    timeout : int, optional, default=10
        The number of seconds to wait to establish a connection

    Returns
    -------
    data_urls : list-like object, dtype=str
        Direct links to files with the given file extension.
    """

    zenodo_base = 'https://zenodo.org/api/records/'
    zenodo_api_url = zenodo_base + record_id

    try:
        data_request = requests.get(zenodo_api_url, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        raise Exception('Attempt to access Zenodo timed out')

    if not data_request.ok:
        raise Exception(f'Record id {record_id} could not be accessed.')

    # grab the data from zenodo
    json_content = data_request.json()
    files = json_content['files']

    # search through the list of files to find those with desired extension
    data_urls = []
    for file in files:
        if file['links']['self'].endswith(file_extension):
            data_urls.append(file['links']['self'])

    return data_urls

def hdf5_from_zenodo_doi(doi: str)->str:
    """For a given zenodo DOI, return links to all hdf5 files.

    Parameters
    ----------
    doi : str, required
        The Zenodo DOI to be considered.  This can be formatted as a URL.
    Returns
    -------
    data_urls : list-like object, dtype=str
        Direct links to files with the given file extension.
    """
    record_id = fetch_record_id_from_doi(doi)
    data_urls = get_zenodo_datafiles(record_id, file_extension='hdf5.gz')

    return data_urls
