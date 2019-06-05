# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to assure the Receipt Service.

Test-Suite to ensure that the Receipt Service is working as expected.
"""

from datetime import datetime

from pay_api.models import Invoice, Payment, PaymentAccount
from pay_api.services.receipt import Receipt as ReceiptService


def factory_payment_account(corp_number: str = 'CP1234', corp_type_code='CP', payment_system_code='PAYBC'):
    """Factory."""
    return PaymentAccount(corp_number=corp_number, corp_type_code=corp_type_code,
                          payment_system_code=payment_system_code)


def factory_payment(payment_system_code: str = 'PAYBC', payment_method_code='CC', payment_status_code='DRAFT'):
    """Factory."""
    return Payment(payment_system_code=payment_system_code, payment_method_code=payment_method_code,
                   payment_status_code=payment_status_code, created_by='test', created_on=datetime.now())


def factory_invoice(payment_id: str, account_id: str):
    """Factory."""
    return Invoice(payment_id=payment_id,
                   invoice_status_code='DRAFT',
                   account_id=account_id,
                   total=0, created_by='test', created_on=datetime.now())


def test_receipt_saved_from_new(session):
    """Assert that the receipt is saved to the table."""
    payment_account = factory_payment_account()
    payment = factory_payment()
    payment_account.save()
    payment.save()
    i = factory_invoice(payment_id=payment.id, account_id=payment_account.id)
    i.save()
    receipt_service = ReceiptService()
    receipt_service.receipt_number = '1234567890'
    receipt_service.invoice_id = i.id
    receipt_service.receipt_date = datetime.now()
    receipt_service.receipt_amount = 100
    receipt_service = receipt_service.save()

    receipt_service = ReceiptService.find_by_id(receipt_service.id)

    assert receipt_service is not None
    assert receipt_service.id is not None
    assert receipt_service.receipt_date is not None
    assert receipt_service.invoice_id is not None

    receipt_service = ReceiptService.find_by_invoice_id_and_receipt_number(i.id, receipt_service.receipt_number)

    assert receipt_service is not None
    assert receipt_service.id is not None


def test_receipt_invalid_lookup(session):
    """Test invalid lookup."""
    receipt = ReceiptService.find_by_id(999)

    assert receipt is not None
    assert receipt.id is None

    receipt = ReceiptService.find_by_invoice_id_and_receipt_number(999, '1234567890')

    assert receipt is not None
    assert receipt.id is None
