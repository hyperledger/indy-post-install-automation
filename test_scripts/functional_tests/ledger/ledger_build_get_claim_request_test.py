"""
Created on Dec 21, 2017

@author: khoi.ngo

Implementing test case GetClaimRequest with valid value.
"""
import json

from indy import did, ledger, pool, anoncreds
import pytest

from utilities import common, constant, utils
from utilities.constant import seed_default_trustee, signature_type, \
    get_claim_response, json_template
from utilities.test_scenario_base import TestScenarioBase
from utilities.utils import perform, verify_json


class TestGetClaimRequest(TestScenarioBase):

    @pytest.mark.asyncio
    async def test(self):
        await  pool.set_protocol_version(2)

        # 1. Prepare pool and wallet. Get pool_handle, wallet_handle
        self.steps.add_step("Prepare pool and wallet")
        self.pool_handle, self.wallet_handle = await perform(
                                    self.steps, common.prepare_pool_and_wallet,
                                    self.pool_name, self.wallet_name, self.wallet_credentials,
                                    self.pool_genesis_txn_file)

        # 3. Create 'issuer_did'.
        self.steps.add_step("Create 'issuer_did'")
        issuer_did, issuer_vk = await utils.perform(self.steps,
                                                    did.create_and_store_my_did,
                                                    self.wallet_handle, "{}")

        # 4. Create 'submitter_did'.
        self.steps.add_step("Create 'submitter_did'")
        await utils.perform(self.steps,
                            did.create_and_store_my_did,
                            self.wallet_handle, "{\"seed\":\"000000000000000000000000Trustee1\"}")

        # 5. Add issuer to the ledger.
        self.steps.add_step("Add issuer to the ledger")
        req = await ledger.build_nym_request(
            constant.did_default_trustee, issuer_did, issuer_vk, alias=None, role='TRUSTEE')
        await utils.perform(self.steps,
                            ledger.sign_and_submit_request,
                            self.pool_handle, self.wallet_handle, constant.did_default_trustee, req)

        # 7. Build and send SCHEMA and CRED_DEF requests and push it to the ledger.
        self.steps.add_step("Build and send SCHEMA and CRED_DEF")
        schema_id, schema_json = await anoncreds.issuer_create_schema(
            issuer_did, constant.gvt_schema_name, "1.0", constant.gvt_schema_attr_names)
        schema_request = await ledger.build_schema_request(issuer_did, schema_json)
        schema_result = await utils.perform(self.steps,
                                            ledger.sign_and_submit_request,
                                            self.pool_handle, self.wallet_handle, issuer_did, schema_request)

        schema_json = json.loads(schema_json)
        schema_json['seqNo'] = json.loads(schema_result)['result']['txnMetadata']['seqNo']
        schema_json = json.dumps(schema_json)

        cred_def_id, cred_def_json = await \
            anoncreds.issuer_create_and_store_credential_def(self.wallet_handle, issuer_did, schema_json, constant.tag,
                                                             constant.signature_type, constant.config_true)
        cred_def_req = await ledger.build_cred_def_request(issuer_did, cred_def_json)

        # 4. send claim request
        self.steps.add_step("send claim request")
        await perform(self.steps, ledger.sign_and_submit_request,
                      self.pool_handle, self.wallet_handle,
                      issuer_did, cred_def_req)

        # 5. build GET_CLAIM request
        self.steps.add_step("build get_claim request")
        # origin = "origin"
        get_cred_req = json.loads(await perform(
                                self.steps, ledger.build_get_cred_def_request,
                                issuer_did, cred_def_id))

        # 6. Verify json get_claim request is correct.
        self.steps.add_step("Verify json get_claim request is correct.")
        err_msg = "Invalid request type"
        utils.check(self.steps, error_message=err_msg,
                    condition=lambda: get_cred_req['operation']['type'] == '108')
