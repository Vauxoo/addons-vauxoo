Configure printers to send Directly to them
===========================================

**NOTE:** This module needs to be migrated to v8.0

Any contribution/comment is welcome until now no customer requires
migration.

Print reports directly to printers

Configuring your server:
------------------------

- Install pycups::

    # aptitude install python-cups
    # apt-get install system-config-printer

- Edit the cups's config file (/etc/cups/cupsd.conf) y modificar:

  - In Section: Only listen for connections from the local machine::

      Listen 631
      Listen /var/run/cups/cups.sock

  - In Section: Default authentication type, when authentication is required...::

      DefaultAuthTypeDigest
      DefaultEncryptionRequired
      DefaultEncryption Never

  - In Section: Restrict access to the server...::

      <Location />
      Allow all
      </Location>

  - In Section: Restrict access to the admin pages...::

      <Location /admin>
      Allow all
      </Location>

  - In Section: Restrict access to configuration files...::

      <Location /admin/conf>
      AuthType Default
      Require user @SYSTEM
      Order allow,deny
      </Location>

-  Restart cups::

    # /etc/init.d/cups restart

-  Install::

    # aptitude install lpr #NO INSTALAR (por ahora)

-  Install::

    # aptitude install cups cups-driver-gutenprint gutenprint-locales foomatic-db foomatic-db-gutenprint foomatic-db-engine foomatic-filters foomatic-db-hpijs cups-bsd foo2zjs

- Add your printer normally as any printer in cups
- Go to (asistant web printers): http://ip.server.with.cups:631/.
- Add the printer there.

TODO:

- Explain odoo's side, but it will be done in the rewrite to v8.0.
- Migrate to v8.0.
- autodiscover printers.

**Make a PR with your new features or make a bug on github.**
