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

"""Tests to assure the CORS utilities.

Test-Suite to ensure that the CORS decorator is working as expected.
"""
from datetime import datetime

from pay_api.utils.date_util import get_nearest_business_day


def test_next_business_day(session):
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    x = datetime(2021, 1, 1)
    d = get_nearest_business_day(x)
    print(d)
    assert d.date() == datetime(2021, 1, 4)

    x = datetime(2021, 2, 15)
    d = get_nearest_business_day(x)
    print(d)
    assert d.date() == datetime(2021, 2, 16, 0, 0)
