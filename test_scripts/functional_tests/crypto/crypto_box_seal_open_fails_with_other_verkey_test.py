"""
Created on Jan 2, 2018

@author: nhan.nguyen

Verify that an anonymous encrypted message
cannot be decrypted with other verkey in wallet.
"""

import pytest
from indy import crypto
from indy.error import ErrorCode
from utilities import common, utils
from test_scripts.functional_tests.crypto.crypto_test_base \
    import CryptoTestBase


class TestCryptoBoxSealOpenWithOtherKey(CryptoTestBase):
    @pytest.mark.asyncio
    async def test(self):
        # 1. Create wallet.
        # 2. Open wallet.
        self.wallet_handle = await common.create_and_open_wallet_for_steps(
            self.steps, self.wallet_name, self.pool_name, credentials=self.wallet_credentials)

        # 3. Create 'my_verkey'.
        self.steps.add_step("Create 'my_verkey'")
        my_verkey = await utils.perform(self.steps, crypto.create_key,
                                        self.wallet_handle, "{}")

        # 4. Create other verkey.
        self.steps.add_step("Create other verkey")
        other_verkey = await utils.perform(self.steps, crypto.create_key,
                                           self.wallet_handle, "{}")

        # 4. Create sealed crypto box with 'my_verkey'.
        self.steps.add_step("Create sealed crypto box with 'my_verkey'")
        msg = "Test crypto".encode()
        encrypted_msg = await utils.perform(self.steps,
                                            crypto.anon_crypt,
                                            my_verkey, msg)

        # 5. Open sealed crypto box with other verkey and verify
        # that sealed crypto box cannot be opened.
        self.steps.add_step("Open sealed crypto box with other verkey and "
                            "verify that sealed crypto box cannot be opened")
        error_code = ErrorCode.CommonInvalidStructure
        await utils.perform_with_expected_code(self.steps,
                                               crypto.anon_decrypt,
                                               self.wallet_handle,
                                               other_verkey, encrypted_msg,
                                               expected_code=error_code)
