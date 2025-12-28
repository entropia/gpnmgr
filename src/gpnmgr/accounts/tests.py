from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from gpnmgr.accounts.models import User, BaseUser


class FullAccessPermissionTest(TestCase):
    fixtures = ['users']

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='full-access-user')
        self.client.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')

    def testFullAccessPermissions(self):
        self.assertTrue(self.user.has_perm('donations.register_donation'))
        self.assertTrue(self.user.has_perm('donations.list_donations'))
        self.assertTrue(self.user.has_perm('log.view_log'))
        self.assertFalse(self.user.has_perm('invalid.absolute_garbage'))

class DonationRegistrationPermissionTest(TestCase):
    fixtures = ['users']
    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='register-user')
        self.client.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')

    def testDonationRegistrationPermissions(self):
        self.assertTrue(self.user.has_perm('donations.register_donation'))
        self.assertFalse(self.user.has_perm('donations.list_donations'))
        self.assertFalse(self.user.has_perm('log.view_log'))

        response = self.client.get(reverse('log_list'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('donation_create'))
        self.assertEqual(response.status_code, 200)

class DisabledUserPermissionTest(TestCase):
    fixtures = ['users']
    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='no-access-user')

    def testDisabledUserPermissions(self):
        self.assertFalse(self.user.has_perm('donations.register_donation'))

class InvalidPermissionTest(TestCase):
    fixtures = ['users']
    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='full-access-user')
        self.group = Group.objects.create(name='invalid-group')
        self.user.groups.add(self.group)
        Group.save(self.group)

    def testInvalidModulePermissions(self):
        self.assertFalse(self.user.has_module_perms('donations'))
        self.assertFalse(self.user.has_perm('donations.invalid-permission'))

class AnonymousUserPermissionTest(TestCase):
    pass

class UserPropertyTest(TestCase):
    fixtures = ['users']

    def testUserDisplayName(self):
        self.user = User.objects.get(username='full-access-user')
        self.base_user = BaseUser.objects.get(username='full-access-user')
        self.assertEqual(str(self.user), 'Full access user')
        self.assertEqual(str(self.base_user), 'Full access user')
        self.user = User.objects.get(username='register-user')
        self.base_user = BaseUser.objects.get(username='register-user')
        self.assertEqual(str(self.user), 'Ina Infodesk')
        self.assertEqual(str(self.base_user), 'Ina Infodesk')
        self.base_user = BaseUser.objects.get(username='base-user')
        self.assertEqual(str(self.base_user), 'Base User')

    def testUserProfileUrl(self):
        self.user = User.objects.get(username='full-access-user')
        self.assertEqual(self.user.get_absolute_url(), reverse('user_profile'))
