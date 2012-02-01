import re

from nose.tools import assert_equal

import ckan.model as model
from ckan.lib.create_test_data import CreateTestData
from ckan.logic import NotAuthorized
        

from ckan.tests import *
from ckan.tests import setup_test_search_index
from base import FunctionalTestCase
from ckan.tests import search_related, is_search_supported

        
class TestPublisherGroups(FunctionalTestCase):

    @classmethod
    def setup_class(self):                        
        from ckan.tests.mock_publisher_auth import MockPublisherAuth
        self.auth = MockPublisherAuth()

        model.Session.remove()
        CreateTestData.create(auth_profile='publisher')
        self.groupname = u'david'
        self.packagename = u'testpkg'
        model.repo.new_revision()
        model.Session.add(model.Package(name=self.packagename))
        model.repo.commit_and_remove()

    @classmethod
    def teardown_class(self):
        model.Session.remove()
        model.repo.rebuild_db()
        model.Session.remove()

    def _run_fail_test( self, username, action):
        grp = model.Group.by_name(self.groupname)        
        context = { 'group': grp, 'model': model, 'user': username }
        try:
            self.auth.check_access(action,context, {})
            assert False, "The user should not have access"
        except NotAuthorized, e:
            pass
    
    def _run_success_test( self, username, action):    
        userobj = model.User.get(username)
        grp = model.Group.by_name(self.groupname)        
        f = model.User.get_groups
        def gg(*args, **kwargs):
            return [grp]
        model.User.get_groups = gg
    
        context = { 'group': grp, 'model': model, 'user': username }
        try:
            self.auth.check_access(action, context, {})
        except NotAuthorized, e:
            assert False, "The user should have %s access: %r." % (action, e.extra_msg)
        model.User.get_groups = f
        
    def test_new_success(self):
        self._run_success_test( 'russianfan', 'group_create' )
        
    def test_new_fail(self):
        self._run_fail_test( 'russianfan', 'group_create' )

    def test_new_anon_fail(self):
        self._run_fail_test( '', 'group_create' )

    def test_new_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'group_create' )
    
    def test_edit_success(self):
        """ Success because user in group """
        self._run_success_test( 'russianfan', 'group_update' )
        
    def test_edit_fail(self):
        """ Fail because user not in group """
        self._run_fail_test( 'russianfan', 'group_update' )
        
    def test_edit_anon_fail(self):
        """ Fail because user is anon """
        self._run_fail_test( '', 'group_update' )

    def test_edit_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'group_update' )

    def test_delete_success(self):
        """ Success because user in group """
        self._run_success_test( 'russianfan', 'group_delete' )
        
    def test_delete_fail(self):
        """ Fail because user not in group """
        self._run_fail_test( 'russianfan', 'group_delete' )
        
    def test_delete_anon_fail(self):
        """ Fail because user is anon """
        self._run_fail_test( '', 'group_delete' )

    def test_delete_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'group_delete' )
        

class TestPublisherGroupPackages(FunctionalTestCase):

    @classmethod
    def setup_class(self):                        
        from ckan.tests.mock_publisher_auth import MockPublisherAuth
        self.auth = MockPublisherAuth()

        model.Session.remove()
        CreateTestData.create(auth_profile='publisher')
        self.groupname = u'david'
        self.packagename = u'testpkg'
        model.repo.new_revision()
        model.Session.add(model.Package(name=self.packagename))
        model.repo.commit_and_remove()

    @classmethod
    def teardown_class(self):
        model.Session.remove()
        model.repo.rebuild_db()
        model.Session.remove()

    def _run_fail_test( self, username, action):
        context = { 'package': self.packagename, 'model': model, 'user': username }
        try:
            self.auth.check_access(action, context, {})
            assert False, "The user should not have access"
        except NotAuthorized, e:
            pass
    
    def _run_success_test( self, username, action):    
        userobj = model.User.get(username)
        grp = model.Group.by_name(self.groupname)     

        f = model.User.get_groups
        g = model.Package.get_groups
        def gg(*args, **kwargs):
            return [grp]
        model.User.get_groups = gg
        model.Package.get_groups = gg
    
        context = { 'package': self.packagename, 'model': model, 'user': username }
        try:
            self.auth.check_access(action, context, {})
        except NotAuthorized, e:
            assert False, "The user should have %s access: %r." % (action, e.extra_msg)
        model.User.get_groups = f
        model.Package.get_groups = g
        
    def test_new_success(self):
        self._run_success_test( 'russianfan', 'package_create' )
     
    # Currently valid to have any logged in user succeed    
    #def test_new_fail(self):
    #    self._run_fail_test( 'russianfan', 'package_create' )

    def test_new_anon_fail(self):
        self._run_fail_test( '', 'package_create' )

    def test_new_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'package_create' )
    
    def test_edit_success(self):
        """ Success because user in group """
        self._run_success_test( 'russianfan', 'package_update' )
        
    def test_edit_fail(self):
        """ Fail because user not in group """
        self._run_fail_test( 'russianfan', 'package_update' )
        
    def test_edit_anon_fail(self):
        """ Fail because user is anon """
        self._run_fail_test( '', 'package_update' )

    def test_edit_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'package_update' )

    def test_delete_success(self):
        """ Success because user in group """
        self._run_success_test( 'russianfan', 'package_delete' )
        
    def test_delete_fail(self):
        """ Fail because user not in group """
        self._run_fail_test( 'russianfan', 'package_delete' )
        
    def test_delete_anon_fail(self):
        """ Fail because user is anon """
        self._run_fail_test( '', 'package_delete' )

    def test_delete_unknown_fail(self):
        self._run_fail_test( 'nosuchuser', 'package_delete' )
        