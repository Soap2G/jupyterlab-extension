import json
import tornado
from rucio_jupyterlab.rucio.authenticators import RucioAuthenticationException
from .base import RucioAPIHandler
from rucio_jupyterlab.metrics import prometheus_metrics

class ValidateConnectionHandler(RucioAPIHandler):
    @tornado.web.authenticated
    @prometheus_metrics
    def get(self):
        namespace = self.get_query_argument('namespace', default=None)
        auth_type = self.get_query_argument('auth_type', default=None)

        if not namespace or namespace == "undefined":
            self.set_status(400)
            self.finish(json.dumps({'success': False, 'error': 'Missing or invalid namespace'}))
            return

        try:
            rucio = self.rucio.for_instance(namespace)
            client = rucio.get_client(auth_type=auth_type) if auth_type else rucio.get_client()
            client.get_account(rucio.account)

            self.finish(json.dumps({'success': True}))
        except RucioAuthenticationException:
            self.set_status(401)
            self.finish(json.dumps({'success': False, 'error': 'authentication_error'}))
        except Exception as exc:
            self.set_status(400)
            self.finish(json.dumps({'success': False, 'error': str(exc)}))
