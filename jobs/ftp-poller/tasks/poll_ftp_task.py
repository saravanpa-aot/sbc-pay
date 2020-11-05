# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service to manage PAYBC services."""
from datetime import datetime
from typing import List

from flask import current_app
from paramiko.sftp_attr import SFTPAttributes
from pay_api.services.queue_publisher import publish_response

from utils.minio import MinioService
from utils.sftp import SFTPService


class PollFtpTask:  # pylint:disable=too-few-public-methods
    """Task to Poll FTP."""

    @classmethod
    def poll_ftp(cls):
        """Poll SFTP.

        Steps:
        1. List Files.
        2. If file
        """
        ftp_dir: str = current_app.config.get('CAS_SFTP_DIRECTORY')
        sftp_client = SFTPService.get_connection()
        file_list: List[SFTPAttributes] = sftp_client.listdir_attr(ftp_dir)
        print('-------file_list', file_list)
        current_app.logger.info(f'Found {len(file_list)} to be copied.')
        payment_file_list: List[str] = []
        for file in file_list:
            file_name = file.filename
            file_full_name = ftp_dir + '/' + file_name
            current_app.logger.info(f'Processing file  {file_name} started-----.')
            file_size = file.st_size
            if PollFtpTask._is_valid_payment_file(file_full_name):
                with sftp_client.open(file_full_name) as f:
                    value_as_bytes = f.read()
                    MinioService.put_object(value_as_bytes, file_name, file_size)
                    payment_file_list.append(file_name)

        PollFtpTask._post_process(payment_file_list)

    @classmethod
    def _post_process(cls, payment_file_list: List[str]):
        """
        1.Move the file to backup folder
        2.Send a message to queue
        """
        cls.move_file_to_backup(payment_file_list)

    @classmethod
    def move_file_to_backup(cls, payment_file_list):
        sftp_client = SFTPService.get_connection()
        ftp_backup_dir: str = current_app.config.get('CAS_SFTP_BACKUP_DIRECTORY')
        ftp_dir: str = current_app.config.get('CAS_SFTP_DIRECTORY')
        for file_name in payment_file_list:
            sftp_client.rename(ftp_dir + '/' + file_name, ftp_backup_dir + '/' + file_name)

    @classmethod
    def _is_valid_payment_file(cls, file_name):
        sftp_client = SFTPService.get_connection()
        return sftp_client.isfile(file_name)


    @classmethod
    def publis_to_queue(cls, file_name , minio_location):
        # Publish message to the Queue, saying account has been created. Using the event spec.
        queue_data = {
            'fileName': file_name,
            'file_source': 'MINIO',
            'location': minio_location
        }

        payload = {
            'specversion': '1.x-wip',
            'type': 'bc.registry.payment.' + 'paymentFileTypeUploaded' ,
            'time': f'{datetime.now()}',
            'datacontenttype': 'application/json',
            'data': queue_data
        }

        try:
            publish_response(payload=payload,
                             client_name=current_app.config.get('NATS_ACCOUNT_CLIENT_NAME'),
                             subject=current_app.config.get('NATS_ACCOUNT_SUBJECT'))
        except Exception as e:  # pylint: disable=broad-except
            current_app.logger.error(e)
            current_app.logger.warning(
                f'Notification to Queue failed for the file '
                f': {file_name}',
                e)
            raise
