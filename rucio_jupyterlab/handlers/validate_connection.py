# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Giovanni Guerrieri, giovanni.guerrieri@cern.ch, 2025

import json
import tornado
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics

class ValidateConnectionHandlerImpl:
    def __init__(self, namespace, rucio):
        self.namespace = namespace
        self.rucio = rucio

    def validate(self, account=None):
        """
        Trivial connection check using Rucio client.
        """
        try:
            # Use the account from the Rucio instance's config or parameter
            account_to_check = account or self.rucio.account
            client = self.rucio.get_client()
            # This will raise if the connection/auth is not valid
            client.get_account(account_to_check)
            return {"success": True}
        except Exception as exc:
            return {"success": False, "error": str(exc)}


class ValidateConnectionHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def post(self):
        namespace = self.get_query_argument('namespace')
        rucio = self.rucio.for_instance(namespace)
        handler = ValidateConnectionHandlerImpl(namespace, rucio)

        try:
            # Optionally, get account from POST body or use default
            data = self.get_json_body() or {}
            account = data.get('account', None)
            result = handler.validate(account)
            if result["success"]:
                self.finish(json.dumps(result))
            else:
                self.set_status(400)
                self.finish(json.dumps(result))
        except RucioAuthenticationException:
            self.set_status(401)
            self.finish(json.dumps({'success': False, 'error': 'authentication_error'}))
        except Exception as exc:
            self.set_status(500)
            self.finish(json.dumps({'success': False, 'error': str(exc)}))
