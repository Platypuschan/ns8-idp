#!/usr/bin/env python3
"""Additional client-policy behavior checks on disposable services.
"""
import contextlib
import copy
import io
import os
import runpy
import sys
import types
import json
from pathlib import Path
import secrets
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from run import ROOT, LoginTests, cmd, idpaccess, idprealm, requests


class DraftEvidence(LoginTests):
    def new_client(self, name):
        idprealm.ensure_client(self.kc, 'ad.test', name,
            redirect_uris=[self.vw_url+'/identity/connect/oidc-signin'])
        client = self.kc.find_client('ad.test', name)
        self.addCleanup(lambda: self.kc.delete('/ad.test/clients/'+client['id']))
        return client

    def redeem(self, target, verifier, client='vaultwarden1', secret=None):
        return requests.post(self.url+'/realms/ad.test/protocol/openid-connect/token', data={
            'grant_type':'authorization_code', 'client_id':client,
            'client_secret':secret or self.secret,
            'code':parse_qs(urlsplit(target).query)['code'][0],
            'redirect_uri':self.vw_url+'/identity/connect/oidc-signin',
            'code_verifier':verifier}, timeout=20)

    def test_17_failures_never_disable_the_client(self):
        client=self.new_client('review-failure')
        with self.assertRaises(idpaccess.PolicyError):
            idpaccess.set_policy(self.kc,'ad.test',copy.deepcopy(client),'missing-review-group')
        after=self.kc.find_client('ad.test','review-failure')
        self.assertTrue(after['enabled'])
        self.assertFalse(idpaccess.restricted(after))
        # Fail each change of the real policy procedure: the token gate, and
        # the client update that sets the policy
        put=self.kc.put
        def failing_put(path,data=None):
            if path.endswith('/clients/'+after['id']):
                raise RuntimeError('injected client update failure')
            return put(path,data)
        for label,patcher in [('token gate',patch.object(idpaccess,'_ensure_token_gate',side_effect=RuntimeError('injected mapper write failure'))),
                ('client update',patch.object(self.kc,'put',side_effect=failing_put))]:
            with self.subTest(label), patcher, self.assertRaisesRegex(RuntimeError,'injected'):
                idpaccess.set_policy(self.kc,'ad.test',copy.deepcopy(after),'services_vaultwarden')
            failed=self.kc.find_client('ad.test','review-failure')
            self.assertTrue(failed['enabled'],label)
            self.assertFalse(idpaccess.restricted(failed),label)
        # The client stays usable, as before the failed change
        _,_,target,_=self.auth('denied',client='review-failure')
        self.assertIn('code=',target or '')
        # Trying again completes the policy
        state=idpaccess.set_policy(self.kc,'ad.test',self.kc.find_client('ad.test','review-failure'),'services_vaultwarden')
        self.assertTrue(state['enforced'],state)
        self.assertTrue(self.kc.find_client('ad.test','review-failure')['enabled'])
        _,response,target,_=self.auth('denied',client='review-failure')
        self.assertIsNone(target)
        self.assertEqual(response.status_code,403)

    def test_18_grants_detected_and_registration_resets(self):
        client=self.new_client('review-grants')
        idpaccess.set_policy(self.kc,'ad.test',client,'services_vaultwarden')
        client=self.kc.find_client('ad.test','review-grants')
        flags=('directAccessGrantsEnabled','implicitFlowEnabled','serviceAccountsEnabled')
        self.assertTrue(all(client[k] is False for k in flags))
        for flag in flags: client[flag]=True
        self.kc.put('/ad.test/clients/'+client['id'],client)
        state=idpaccess.access_state(self.kc,'ad.test',self.kc.find_client('ad.test','review-grants'))
        self.assertFalse(state['enforced'])
        self.assertEqual(set(state['issues']),{k+'_set' for k in flags})
        idpaccess.reconcile(self.kc,'ad.test',[self.kc.find_client('ad.test','review-grants')])
        self.assertFalse(idpaccess.access_state(self.kc,'ad.test',self.kc.find_client('ad.test','review-grants'))['enforced'])
        idprealm.ensure_client(self.kc,'ad.test','review-grants',redirect_uris=[self.vw_url+'/identity/connect/oidc-signin'])
        client=self.kc.find_client('ad.test','review-grants')
        self.assertTrue(all(client[k] is False for k in flags))
        self.assertTrue(idpaccess.access_state(self.kc,'ad.test',client)['enforced'])

    def test_19_real_token_defaults_and_reset(self):
        self.assertEqual(self.kc.get('/ad.test')['accessTokenLifespan'],300)
        client=self.new_client('review-token')
        secret=self.kc.get('/ad.test/clients/'+client['id']+'/client-secret')['value']
        _,_,target,verifier=self.auth('allowed',client='review-token')
        response=self.redeem(target,verifier,client='review-token',secret=secret)
        self.assertEqual(response.status_code,200)
        self.assertGreaterEqual(response.json()['expires_in'],295)
        self.assertLessEqual(response.json()['expires_in'],300)
        idprealm.ensure_client(self.kc,'ad.test','review-token',
            redirect_uris=[self.vw_url+'/identity/connect/oidc-signin'],access_token_lifespan=600)
        idprealm.ensure_client(self.kc,'ad.test','review-token',
            redirect_uris=[self.vw_url+'/identity/connect/oidc-signin'],access_token_lifespan=None)
        _,_,target,verifier=self.auth('allowed',client='review-token')
        response=self.redeem(target,verifier,client='review-token',secret=secret)
        self.assertEqual(response.status_code,200)
        self.assertGreaterEqual(response.json()['expires_in'],295)
        self.assertLessEqual(response.json()['expires_in'],300)
    def test_21_local_only_account_denied(self):
        username='reviewlocal'
        self.kc.post('/ad.test/users',{'username':username,'enabled':True,'email':'reviewlocal@example.test',
            'emailVerified':True,'firstName':'Review','lastName':'Local','credentials':[{'type':'password','value':self.password,'temporary':False}]})
        user=self.kc.get('/ad.test/users',params={'username':username,'exact':'true'})[0]
        self.addCleanup(lambda:self.kc.delete('/ad.test/users/'+user['id']))
        # Even manually assigning the imported group locally is insufficient.
        group=self.kc.get('/ad.test/group-by-path/services_vaultwarden')
        self.kc.put('/ad.test/users/'+user['id']+'/groups/'+group['id'])
        _,_,target,_=self.auth(username,client='other1')
        self.assertIn('code=',target or '')
        _,response,target,_=self.auth(username)
        self.assertIsNone(target)
        self.assertEqual(response.status_code,403)

    def test_22_nested_and_deleted_ldap_groups(self):
        group='review-parent'
        cmd('podman','exec',self.samba,'samba-tool','group','add',group)
        self.addCleanup(lambda:cmd('podman','exec',self.samba,'samba-tool','group','delete',group,check=False))
        client=self.new_client('review-group')
        cmd('podman','exec',self.samba,'samba-tool','group','addmembers',group,'services_vaultwarden')
        idpaccess.set_policy(self.kc,'ad.test',client,group)
        _,response,target,_=self.auth('allowed',client='review-group')
        self.assertIsNone(target)
        self.assertEqual(response.status_code,403)
        cmd('podman','exec',self.samba,'samba-tool','group','addmembers',group,'allowed')
        session,_,target,_=self.auth('allowed',client='review-group')
        self.assertIn('code=',target or '')
        cmd('podman','exec',self.samba,'samba-tool','group','delete',group)
        _,response,target,_=self.auth('allowed',session=session,client='review-group',require_cookie=True)
        self.assertIsNone(target)
        self.assertEqual(response.status_code,403)
        # Run the actual get-client-access action against the real Keycloak.
        # Only NS8 caller identity/transport plumbing is substituted; the
        # LDAP group lookup asks the real Samba AD.
        state=self.run_get_client_access({'domain':'ad.test'},'module/review-group')
        # The structural check cannot see the deletion
        self.assertTrue(state['enforced'],state)
        self.assertEqual(state['issues'],[])
        self.assertNotIn('live',state)
        state=self.run_get_client_access({'domain':'ad.test','live':True},'module/review-group')
        self.assertTrue(state['enforced'],state)
        self.assertEqual(state['live'],{'ok':False,'ldap_connection':True,'group_in_ldap':False,
            'user_allowed':None,'issues':['group_not_in_ldap']})
        print('LDAP-deleted group: login denied, enforced=true, live reports group_not_in_ldap',flush=True)

    def run_get_client_access(self, request, caller):
        kcadmin=types.ModuleType('kcadmin')
        kcadmin.agent_client=lambda:self.kc
        kcadmin.managed_realms=lambda kc:['ad.test']
        ldapproxy=types.ModuleType('agent.ldapproxy')
        ldapproxy.Ldapproxy=lambda:types.SimpleNamespace(get_domain=lambda domain:{'schema':'ad'})
        ldapclient=types.ModuleType('agent.ldapclient')
        class NotFound(Exception): pass
        samba=self.samba
        class Client:
            def get_group(self, name):
                if cmd('podman','exec',samba,'samba-tool','group','show',name,check=False).returncode:
                    raise NotFound(name)
                return {'group':name}
        ldapclient.Ldapclient=types.SimpleNamespace(factory=lambda **kw:Client())
        ldapclient.LdapclientEntryNotFound=NotFound
        output=io.StringIO()
        with patch.dict(sys.modules,{'kcadmin':kcadmin,'agent.ldapproxy':ldapproxy,'agent.ldapclient':ldapclient}), \
                patch.object(sys.modules['agent'],'ldapproxy',ldapproxy,create=True), \
                patch.dict(os.environ,{'AGENT_TASK_USER':caller}), \
                patch.object(idprealm,'require_keycloak',return_value=None), \
                patch.object(sys,'stdin',io.StringIO(json.dumps(request))), \
                contextlib.redirect_stdout(output):
            runpy.run_path(str(ROOT/'imageroot/actions/get-client-access/20read'),run_name='__main__')
        return json.loads(output.getvalue())

    def test_23_live_state_with_real_services(self):
        state=self.run_get_client_access({'domain':'ad.test','client_id':'vaultwarden1','live':True,'user':'allowed'},'admin')
        self.assertTrue(state['enforced'],state)
        self.assertEqual(state['live'],{'ok':True,'ldap_connection':True,'group_in_ldap':True,'user_allowed':True,'issues':[]})
        user=idpaccess.find_user(self.kc,'ad.test','denied')
        sessions=lambda:sorted(x['id'] for x in self.kc.get('/ad.test/users/'+user['id']+'/sessions'))
        before=sessions()
        state=self.run_get_client_access({'domain':'ad.test','client_id':'vaultwarden1','live':True,'user':'denied'},'admin')
        self.assertTrue(state['live']['ok'],state)
        self.assertIs(state['live']['user_allowed'],False)
        # The example token check leaves no user session behind
        self.assertEqual(sessions(),before)
        # A user removed from the group is reported at once, with the cache on
        cmd('podman','exec',self.samba,'samba-tool','group','removemembers','services_vaultwarden','allowed')
        try:
            state=self.run_get_client_access({'domain':'ad.test','client_id':'vaultwarden1','live':True,'user':'allowed'},'admin')
            self.assertIs(state['live']['user_allowed'],False)
        finally:
            cmd('podman','exec',self.samba,'samba-tool','group','addmembers','services_vaultwarden','allowed')
        cmd('podman','pause',self.samba)
        try:
            state=self.run_get_client_access({'domain':'ad.test','client_id':'vaultwarden1','live':True},'admin')
        finally:
            cmd('podman','unpause',self.samba)
        self.assertFalse(state['live']['ok'])
        self.assertFalse(state['live']['ldap_connection'])
        self.assertIsNone(state['live']['group_in_ldap'])
        self.assertEqual(state['live']['issues'],['ldap_connection_failed'])


if __name__=='__main__':
    suite=unittest.TestSuite(DraftEvidence(name) for name in sorted(DraftEvidence.__dict__) if name.startswith('test_'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
