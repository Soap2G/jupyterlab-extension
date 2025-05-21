import json
import tornado
import traceback

from rucio_jupyterlab.rucio.authenticators import (
    authenticate_userpass,
    authenticate_x509,
    authenticate_oidc,
    RucioAuthenticationException,
)
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics


class ValidateConnectionHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument("namespace", default=None)
        auth_type = self.get_query_argument("auth_type", default=None)

        if not namespace or namespace == "undefined":
            self.set_status(400)
            self.finish(json.dumps({"success": False, "error": "Missing or invalid namespace"}))
            return

        try:
            rucio = self.rucio.for_instance(namespace)
            base_url = rucio.instance_config.get("rucio_base_url")
            account = rucio.instance_config.get("account")
            vo = rucio.instance_config.get("vo")
            app_id = rucio.instance_config.get("app_id")
            rucio_ca_cert = rucio.instance_config.get("rucio_ca_cert", False)

            config = rucio.auth_config

            if auth_type == "userpass":
                username = config.get("username")
                password = config.get("password")
                authenticate_userpass(base_url, username, password, account, vo, app_id, rucio_ca_cert)

            elif auth_type == "x509":
                cert_path = config.get("cert")
                key_path = config.get("key")
                authenticate_x509(base_url, cert_path, key_path, account, vo, app_id, rucio_ca_cert)

            elif auth_type == "x509_proxy":
                proxy_path = config.get("client_x509_proxy")
                account = config.get("account")
                authenticate_x509(base_url, proxy_path, account, vo, app_id, rucio_ca_cert)

            elif auth_type == "oidc":
                oidc_auth = config.get("oidc_auth")
                oidc_auth_source = config.get("oidc_auth_source")
                authenticate_oidc(base_url, oidc_auth, oidc_auth_source, rucio_ca_cert)

            else:
                raise RucioAuthenticationException(f"Unsupported auth_type: {auth_type}")

            self.finish(json.dumps({"success": True}))

        except RucioAuthenticationException as auth_exc:
            self.set_status(401)
            self.finish(json.dumps({"success": False, "error": str(auth_exc)}))

        except Exception as exc:
            traceback.print_exc()
            self.set_status(400)
            self.finish(json.dumps({"success": False, "error": str(exc)}))
