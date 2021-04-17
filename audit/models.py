from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

# Create your models here.


class Host(models.Model):
    hostname = models.CharField(max_length=64)
    ip_addr = models.GenericIPAddressField(unique=True)
    idc = models.ForeignKey('IDC', on_delete=models.CASCADE)
    enabled = models.BooleanField()

    def __str__(self):
        return '%s(%s)' % (self.hostname, self.ip_addr)


class IDC(models.Model):
    idc_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return '%s' % self.idc_name


class BindHost(models.Model):
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    host_user = models.ForeignKey('HostUser', on_delete=models.CASCADE)

    def __str__(self):
        return '%s: %s' % (self.host, self.host_user)


class HostGroup(models.Model):
    group_name = models.CharField(max_length=64, unique=True)
    bind_hosts = models.ManyToManyField('BindHost', blank=True)

    def __str__(self):
        return self.group_name


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True
    )
    password = models.CharField(_('password'), max_length=128)

    name = models.CharField(max_length=32)
    host_group = models.ManyToManyField('HostGroup', blank=True)
    bind_hosts  =models.ManyToManyField('BindHost', blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = '账号表'

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class HostUser(models.Model):
    type = ((0, 'ssh-password'), (1, 'ssh-key'))
    type_choice = models.SmallIntegerField(choices=type, default=0)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        unique_together = ('type_choice', 'username')
