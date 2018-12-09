import math
import os
import urllib
from time import sleep

import requests
from requests import HTTPError


FAIL_STATE = '4'


def build_url(endpoint, protocol='http', host='localhost', port='8000'):
    return '{protocol}://{host}:{port}/{endpoint}'.format(
        protocol=protocol,
        host=host,
        port=port,
        endpoint=endpoint
    )


def build_headers():
    return {
        'Content-Type': 'application/json'
    }


def assert_response_code(response, accepted_response_codes, message):
    if response.status_code not in accepted_response_codes:
        message = '{}: {}'.format(message, response.status_code)
        print(message)
        raise HTTPError(message)


def upload_test(file_name):
    # Create a GeneParser on the server
    print('Creating a Gene Parser for file {}'.format(file_name))
    response = requests.post(
        build_url('gene_parser/'),
        headers=build_headers(),
        json={
            'file_name': file_name
        }
    )
    assert_response_code(response, [201], 'Cannot create a GeneParser')
    response_json = response.json()
    gene_parser_id = response_json['id']
    source_put_url = response_json['source_put_url']

    # # # # # Upload file
    print('Uploading to {}'.format(source_put_url))
    with open('tests/{}'.format(file_name), 'rb') as data:
        response = requests.put(
            source_put_url,
            data=data,
        )
    assert_response_code(response, [200], 'Cannot upload file')

    # # # # # Mark file as uploaded and start processing
    print("Marking file as uploaded")
    response = requests.post(
        build_url('gene_parser/{}/file_uploaded/'.format(response_json['id'])),
        headers=build_headers()
    )
    assert_response_code(response, [201], 'Cannot start processing')
    response_json = response.json()
    async_job_id = response_json['async_job']['id']

    # # # # # Track progress
    while True:
        response = requests.get(
            build_url('async_job/{}/'.format(async_job_id)),
            headers=build_headers(),
        )
        assert_response_code(response, [200], 'Cannot get AsyncJob')
        response_json = response.json()

        if response_json['state'] == FAIL_STATE:
            print('Job failed...')
            break

        progress = response_json['progress_data'].get('completed', 0)
        print('Parsing progress {}%'.format(
            str(math.floor(progress * 100)))
        )
        sleep(1)
        if progress == 1:
            break

    # # # # # Download result
    response = requests.get(
        build_url('gene_parser/{}/'.format(gene_parser_id)),
        headers=build_headers(),
    )
    assert_response_code(response, [200], 'Cannot get GeneParser')
    response_json = response.json()

    try:
        os.mkdir('downloads')
    except FileExistsError:
        pass

    download_file_name = './downloads/{}'.format(response_json['id'])
    print('Downloading file to `{}`'.format(download_file_name))
    response = urllib.request.urlopen(response_json['processed_file_url'])
    with open(download_file_name, 'b+w') as f:
        f.write(response.read())

    print('FINISHED')


upload_test('demo_file.fasta')
upload_test('demo_file.csv')
