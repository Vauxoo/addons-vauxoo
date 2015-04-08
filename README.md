[![Build Status](http://runbot.odoo.com/logo.png)](http://runbot.vauxoo.com/runbot/)
[![Build Status](https://travis-ci.org/Vauxoo/addons-vauxoo.svg)](https://travis-ci.org/Vauxoo/addons-vauxoo)

Vauxoo modules for Odoo
===

On this project we try to mantain all our generic modules that can be used as
little extensions of odoo.

If a module is here frequently is because such need comply a very specific need
of a customer and we considered such feature is generic enought to share on
this repository.

The combination of several of this modules compliment other projects like
odoo-mexico, odoo-venezuela, odoo-ifrs, odoo-afr look on [our github
page](https://github.com/Vauxoo) for such repositories and the utilities where
this modules are used.

Reasons because a module can be here.
---

1. The feature is generic.
2. The module can work standalone or combined with other modules here or in [OCA](https://github.com/OCA).
3. Feature is planned to be mantained in future versions, very specific
   features which are specific for a user case on a customer can not be here.

Naming convention.
---

All modules must start with the name of meta functional area which they will work with, i.e: account_*, website_*, sale_*, etc.

Repositories which we depend from.
---

Read the repo_dependencies.txt file for more information.

Python Libraries which we depend from.
---

Read the requirements.txt file for more information.

Hacking this set of modules.
---

The main idea is create a little how-to commit by commit to know how to improve this modules in a clean way and help us to help you.

How add a new features:
---

0. Clone this repository:

    ```bash
    $ git clone git@github.com:vauxoo/addons-vauxoo.git -b 8.0
    $ cd addons-vauxoo
    $ git remote add your-name git@github.com:your-github-name/addons-vauxoo.git # << to push your changes
    ```

1. **Before declare this repository as part of your addons-path:** Install all external dependencies (read travis folder for more information).
**note**: You will need some non normal packages (npm and lessc to be precise) when you have v8.0 normally installed,
run this command in order to have them all in linux and avoid unexpected runtimes.

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

4. Prepare your enviroment to work with this repository and the mandatory ones to have all the enviroment ready.

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

9. If all is ok installing, please test your enviroment running your code with ‘test-enabled’.

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

13. Make a PR with your changes as you usually do it with github's web interface or using [hub](https://github.com/github/hub).

Understanding our little structure of files per module.
---

Descriptions of modules can be on a README.md, README.rst, or directly on the descriptor __openerp__.py file,
the best way to do something new is using a README.md file in some moment all our modules will be on that way.

Try to avoid imports of external libraries without a try, except to manage a WARNING controlling the external error,
if is mandatory such need.

The structure of all internal odoo stuff try to follow the rules under [OCA](http://odoo-community.org),
and remember always do what we say and not what we do ;-) if you find things that do not comply such rules,
it can be considered a bug, please share with us what you find and Pull Requests are welcome.

Paid support and warranties.
---

Are you planning to use this modules in a production enviromnent that can hire some work from the team behind this work?

#Better go with [Vauxoo](http://vauxoo.com)
