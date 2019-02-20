Account Analytic Required
=========================

This module adds an option "analytic policy" on Account Types.

You have the choice between 3 policies : always, never and optional. For
example, if you want to have an analytic account on all your expenses, set
the policy to "always" for the account type "expense" ; then, if you try to
save an account move line with an account of type "expense" without
analytic account, you will get an error message.

In a preemptively it avoid that an Invoice be validated if using accounts
that has to fulfil the policy by adding field analytic_required, making
mandatory filling an Analytic Account when depending on the policy
selected in the Account Type

This module uses original code from a module with same name developed by
Alexis de Lattre <alexis.delattre@akretion.com> during the
Akretion-Camptocamp code sprint of June 2011. Modification of code has been
made to comply with Odoo available API.