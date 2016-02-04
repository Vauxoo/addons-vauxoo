Reporting Issues
----------------

1. Make sure you've actually read the error message if there is one, it may really help
2. No need to create an issue if you're [making a PR](#making-pull-requests) to fix it. Describe the issue in the PR, it's the same as an issue, but with higher priority!
2. Double-check that the issue still occurs with the latest version of Odoo (you can easily test this on [Runbot](http://runbot.vauxoo.com))
3. [Search](https://github.com/vauxoo/addons-vauxoo/issues) for similar issues before reporting anything
4. If you're a programmer, try investigating/fixing yourself, and consider making a Pull Request instead
5. If you really think a new issue is useful, keep in mind that it will be treated with a much lower priority than a Pull Request or an Vauxoo Enterprise support ticket

If later on you create a pull request solving an opened issue, do not forget to reference it in your pull request (e.g.: "This patch fixes issue #42").

When reporting an issue or creating a pull request, please **use the following template**:

```
**Quantity field is ignored in a sale order**

Impacted versions:

 - 8.0

Steps to reproduce:

 1. create a new sale order
 2. add a line with product 'Service', quantity 2, unit price 10.0
 3. validate the sale order

Current behavior:

 - Total price of 10.0

Expected behavior:

 - Total price of 20.0 (2 * 10 = 20)
```

Hacking this set of modules.
---

The main idea is create a little how-to commit by commit to know how to improve
this modules in a clean way and help us to help you, then if you are including
your new concepts try to be explicit and helpful in your commit messages.

How add a new feature:
---

0. Clone this repository:

    ```bash
    $ git clone git@github.com:vauxoo/addons-vauxoo.git -b 8.0
    $ cd addons-vauxoo
    $ git remote add your-name git@github.com:your-github-name/addons-vauxoo.git # << to push your changes
    ```

1. **Before declare this repository as part of your addons-path:** Install all
   external dependencies (read travis folder for more information). **note**:
   You will need some non normal packages (npm and lessc to be precise) when
   you have v8.0 normally installed, run this command in order to have them all
   in linux and avoid unexpected runtimes.

    ```bash
    $ cd addons-vauxoo
    $ sudo pip install -r ./travis/requirements.txt
    $ ./travis/travis_install_nightly
    ```

2. Create your own branch locally.

    ```bash
    $ git checkout -b 8.0-your_new_feature_theme
    ```

3. Push your first change branch to know you start to work on.

    ```bash
    $ git push -u origin 8.0-your_new_feature_theme
    ```

4. Prepare your environment to work with this repository and the mandatory ones
   to have all the environment ready.

    ```bash
    $ git clone https://github.com/odoo/odoo.git -b 8.0
    $ git clone https://github.com/vauxoo/addons-vauxoo.git -b 8.0
    $ git clone git@github.com:oca/server-tools.git -b 8.0
    ```
5. Create a postgres user (only for this work to avoid problems not related to this enviroment).

    ```bash
    $ sudo su postgres
    $ createuser testuser -P
    ##### put your password just the number one (1) for example.
    $ createdb test -U testuser -O testuser -T remplate0 -E UTF8
    ```
6. Run the development enviroment.

    ```bash
    $ cd path/to/odoo/odoo
    $ ./openerp-server \
    --addons-path=addons/,../addons-vauxoo,../server-tools -r \
    testuser -w 1 --db-filter=test \
    -i module_to_improve -d test
    ```
7. Do your code, code, code, code and update it passing -u module -d test (replacing this paramenter above).

8. Before you need to be sure all is ok, we can delete and create db again with -i
   paramenter to ensure all install correctly.

    ```bash
    $ sudo su postgres
    $ dropbd test
    $ createdb test -U testuser -O testuser -T remplate0 -E UTF8
    $ ./openerp-server \
    --addons-path=addons/,../addonstest-vauxoo,../server-tools -r \
    testuser -w 1 --db-filter=test \
    -i module_to_improve -d test
    ```
9. If all is ok installing, please test your environment running your code with ‘test-enabled’.

    ```bash
    $ ./openerp-server --addons-path=addons/,../addons-vauxoo,../test -r \
    testuser -w 1 --db-filter=test \
    -i module_to_improve-d test --test-enable
    ```
**Note:**

    This will take a time, just do it before commit your change and make push.

10. Add your changes to have them versioned.

    ```bash
    $ git add .
    ```

11. Commit your changes.

    ```bash
    $ git commit -m "[TAG] module: what you did"
    ```

12. Push your first change branch to know you start to work on.

    ```bash
    $ git push -u vauxoo-dev 8.0-your_new_feature_theme
    ```

13. Make a PR with your changes as you usually do it with github's web
    interface or using [hub](https://github.com/github/hub).

Modules Conventions
---

- **Descriptions**.
    - Descriptions of modules can be on a README.md, README.rst, avoid put the
      descriptions directly on the descriptor __openerp__.py file, the best way to
      do something new is using a README.md file in some moment all our modules
      will be on that way.
- **Dependencies**.
    - Try to avoid imports of external libraries without a try, except to manage a
      WARNING controlling the external error, if is mandatory such need.
- **Module Structure**.
    - The structure of all internal odoo stuff try to follow the rules under
      [OCA](http://odoo-community.org), and remember always do what we say and not
      what we do ;-) if you find things that do not comply such rules, it can be
      considered a bug, please share with us what you find and Pull Requests are
      welcome.
- **Naming convention.**
    - All modules must start with the name of meta functional area which they will
      work with, i.e: `account_*`, `website_*`, `sale_*`.
    - The module should not contain names not precises like `*_extra` or
      `*_extension` if your module do whatever call it whatever.
- **Reasons because a module can be here.**
    - The feature is generic.
    - The module can work standalone or combined with other modules here or in
      [OCA](https://github.com/OCA).
    - Feature is planned to be maintained in future versions, very specific
      features which are specific for a user case on a customer can not be
      here.
- **Coding**
    - *Python*: We try to follow pep8 and check with pylint all our Pull
      requests, to verify this locally just read the .travis file and replicate
      such verification locally.
    - *XML and HTML* We try to have 4 space for indentation, avoid the tabs,
      and try to have all initial tag declaration in one line except for reports
      declaration which can be in one line per attribute, this is not verified
      by any lint checker but it is good if you help us there.

Issues
---

- Where?: [here](https://github.com/Vauxoo/addons-vauxoo/issues/new)
- How? Follow [odoo’s](https://github.com/odoo/odoo/blob/8.0/CONTRIBUTING.md) standard to put your issues.

