import io
import json
import logging
import celery
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from minio.error import InvalidRange
from async_job.models import AsyncJob
from gene.models import Gene
from gene_parser.models import GeneParser
from gene_parser import parsers
from genobase.tools.s3_client import S3Client


logger = logging.getLogger(settings.DEFAULT_LOGGER)


s3_client = S3Client()


@celery.task(name='gene_parser.tasks.process_genes')
def process_genes(async_job_json_string):
    """
    Job that idempotently imports genes from an s3 file to the DB.
    Requires: AsyncJob.job_payload['gene_parser_id']
    """

    async_job_json = json.loads(async_job_json_string)
    async_job = AsyncJob.objects.get(pk=async_job_json['pk'])
    gene_parser = GeneParser.objects.get(pk=async_job.job_payload['gene_parser_id'])
    _process_in_file(async_job, gene_parser)


def _process_in_file(async_job, gene_parser, chunk_size=10):
    # Validate we can parse this file
    file_extension = gene_parser.file_name.split('.')[-1]
    if file_extension not in parsers.supported_file_types:
        Exception()

    # Edge case where job failed right after storing the file
    if gene_parser.is_file_processed:
        return

    stats = s3_client.stat_object(
        bucket_name=S3Client.in_bucket_name,
        object_name=str(gene_parser.id)
    )

    # Parse file
    chunk_offset = async_job.progress_data.get('chunk_offset', 0)
    file_done = False
    first_result = True
    parser_buffer = parsers.ParserBuffer(parser_type=file_extension)

    while True:
        try:
            parser_buffer.buffer.extend(
                _get_next_file_chunk(
                    gene_parser=gene_parser,
                    chunk_offset=chunk_offset,
                    chunk_size=chunk_size
                )
            )
        except InvalidRange:
            file_done = True

        chunk_offset += chunk_size

        parsed_results = parser_buffer.parse(file_done=file_done, first_result=first_result)

        # Used for visual progress
        with transaction.atomic():
            async_job.progress_data['completed'] = 0.9999 if file_done else (chunk_offset / stats.size)
            async_job.save()

        if parsed_results is None and file_done:
            break

        if parsed_results is None:
            continue

        for result in parsed_results:
            with transaction.atomic():
                first_result = False

                _store_result(
                    async_job=async_job,
                    gene_parser=gene_parser,
                    result=result,
                    chunk_offset=chunk_offset - len(parser_buffer.buffer) - 1,
                )

                if file_done:
                    s3_client.remove_object(
                        bucket_name=S3Client.in_bucket_name,
                        object_name=str(gene_parser.id)
                    )

        if file_done:
            break

    _send_to_s3(async_job=async_job, gene_parser=gene_parser)


def _get_next_file_chunk(gene_parser, chunk_offset, chunk_size):
    chunk_response = s3_client.get_partial_object(
        bucket_name=S3Client.in_bucket_name,
        object_name=str(gene_parser.id),
        offset=chunk_offset,
        length=chunk_size
    )

    chars_list = list()
    for data in chunk_response:
        chars_list.extend(data.decode('ascii'))

    return chars_list


def _store_result(async_job, gene_parser, result, chunk_offset):
    gene, created = Gene.objects.get_or_create(
        gene_parser=gene_parser,
        name=result.name,
    )
    if created:
        gene.sequence = result.sequence
        gene.save()

    async_job.progress_data['chunk_offset'] = chunk_offset
    async_job.save()

    logger.info('Saved gene: {}'.format(result))


def _send_to_s3(async_job, gene_parser):
    # NOTE: This could use S3's partial upload instead, which would be more memory efficient and support larger
    #       output files. However, Minio's Python client doesn't support this functionality.

    gene_qs = Gene.objects.filter(
        gene_parser=gene_parser
    ).order_by(
        'created_at'
    )

    # Iterate on database and build a dictionary
    genes_list = list()
    paginator = Paginator(gene_qs, 10)
    line_num = 1
    for page in range(1, paginator.num_pages + 1):
        for gene in paginator.page(page).object_list:
            genes_list.append(
                {
                    'line_number': line_num,
                    'gene_name': gene.name,
                    'sequence': gene.sequence
                }
            )
            line_num += 1

    genes_json_string = json.dumps(genes_list)
    genes_io = io.BytesIO(genes_json_string.encode())

    # Put in S3
    s3_client.put_object(
        bucket_name=S3Client.out_bucket_name,
        object_name=str(gene_parser.id),
        data=genes_io,
        length=genes_io.getbuffer().nbytes
    )

    with transaction.atomic():
        async_job.progress_data['completed'] = 1
        async_job.save()

        gene_parser.is_file_processed = True
        gene_parser.save()
