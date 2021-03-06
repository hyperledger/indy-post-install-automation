"""
Created on Dec 12, 2017

@author: nhan.nguyen

Verify that user cannot store 'their_did' with invalid did.
"""

import pytest
import json

from indy import did
from indy.error import ErrorCode
from utilities import utils, common
from test_scripts.functional_tests.did.signus_test_base \
    import DidTestBase


class TestStoreInvalidDidIntoWallet(DidTestBase):
    @pytest.mark.asyncio
    async def test(self):
        # 1. Create wallet.
        # 2. Open wallet.
        self.wallet_handle = await \
            common.create_and_open_wallet_for_steps(self.steps,
                                                    self.wallet_name,
                                                    self.pool_name,
                                                    credentials=self.wallet_credentials)

        # 4. Store an invalid did into wallet and
        # verify that invalid did cannot be stored.
        self.steps.add_step("Store an invalid did into wallet and"
                            " verify that invalid did cannot be stored")

        invalid_did_json = json.dumps({"did": "invalidDID"})
        error_code = ErrorCode.CommonInvalidStructure
        await utils.perform_with_expected_code(self.steps,
                                               did.store_their_did,
                                               self.wallet_handle,
                                               invalid_did_json,
                                               expected_code=error_code)
