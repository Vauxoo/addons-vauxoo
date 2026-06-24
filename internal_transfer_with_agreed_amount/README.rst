=======================================================
Internal Transfers with an Agreed Amount
=======================================================

Create internal transfers between bank accounts in different currencies,
specifying the exact local amount to record on both sides regardless of
the current exchange rate.

When moving funds between two bank accounts that operate in different
currencies, Odoo calculates the local (company currency) amount using
the exchange rate on the transfer date. This module lets you override
that amount: you decide what local amount both journal entries will carry.

- Creates both the outbound and inbound payments in a single operation
  directly from the bank journal dashboard.
- Accepts a foreign-currency amount on each side and a single agreed
  local amount that applies to both entries.
- Automatically reconciles the transit account after both payments are
  posted, keeping the Liquidity Transfer account balanced.
- Adds an **Internal Transfers** link to each bank journal's Kanban card
  to view existing transfers filtered by that journal.
- Protects paired transfers on reset: resetting one payment to draft
  triggers a confirmation dialog and resets both payments together,
  removing the reconciliation between them.

Installation
============

- Requires the **Accounting** app.
- No additional localization modules are required.

Configuration
=============

1. Go to **Accounting > Configuration > Settings**.
2. Verify that an **Internal Transfer Account** is set for your company.
   This account is used as the transit account between the two payments.

.. image:: /internal_transfer_with_agreed_amount/static/img/internal_transfer_account.png
   :align: center
   :width: 400pt
   :alt: Internal Transfer Account in Accounting Settings

3. Go to **Settings > Users & Companies > Users**.
4. Open the user who will create internal transfers with agreed amounts.
5. Under the **Accounting** section, enable the
   **Allow to confirm an internal transfer with an agreed amount** permission.

.. image:: /internal_transfer_with_agreed_amount/static/img/agreed_amount_in_accounting_access_rights_on_users.png
   :align: center
   :width: 400pt
   :alt: User form showing the Allow to confirm an internal transfer with an agreed amount permission under Accounting

6. Go to **Accounting > Configuration > Journals** and open each bank
   journal you plan to use as source or destination.
7. On the source journal, go to the **Outgoing Payments** tab and verify
   that the payment method you will use has an **Outstanding Account**
   set.
8. On the destination journal, go to the **Incoming Payments** tab and
   verify that the payment method you will use has an **Outstanding
   Account** set.
9. The outstanding account on the source journal and the outstanding
   account on the destination journal must be different.

.. image:: /internal_transfer_with_agreed_amount/static/img/journal_outgoing_payment_method_outstanding_account.png
   :align: center
   :width: 400pt
   :alt: Journal form showing the Outgoing Payments tab with the Outstanding Account column on a payment method line

Usage
=====

Step 1: Open the Internal Transfer wizard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to **Accounting > Dashboard**. Locate the bank journal you want to
send funds from. Click the vertical-dots menu (⋮) on the journal card
and select **Internal Transfer** under the **New** section.

.. image:: /internal_transfer_with_agreed_amount/static/img/internal_transfer_button_in_journal.png
   :align: center
   :width: 400pt
   :alt: Internal Transfer button in bank journal card

Step 2: Fill in the transfer details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The wizard shows two sides: **Sending Transaction** and
**Receiving Transaction**.

Header fields:

- **Date**: the date to record on both journal entries.
- **Memo**: optional note that appears on both payments.
- **Company Currency**: Read-only field showing the company's currency.

Sending side:

- **Journal**: pre-filled with the journal you opened the wizard from.
- **Amount**: the amount in the journal's currency (e.g. USD if the
  source journal is in dollars).
- **Local Amount**: the agreed company-currency amount to record. If the
  journal uses the company currency, this field matches **Amount**
  automatically and cannot differ.
- **Payment Method**: the outbound payment method to use.

Receiving side:

- **Journal**: the destination bank journal.
- **Amount**: the amount in the destination journal's currency.
- **Local Amount**: read-only; always equal to the sending side's
  **Local Amount**.
- **Payment Method**: the inbound payment method to use.

.. image:: /internal_transfer_with_agreed_amount/static/img/internal_transfer_wizard_with_both_sides_filled_in_using_different_currencies.png
   :align: center
   :width: 400pt
   :alt: Internal Transfer wizard with both sides filled in using different currencies

Step 3: Create the transfer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click **Create Internal Transfer**. The button is only active when all
required fields on both sides are filled.

Odoo creates one outbound payment and one inbound payment, posts both,
and reconciles the transit account automatically. After creation, the
view shows the two newly created payments.

.. image:: /internal_transfer_with_agreed_amount/static/img/payment_list_showing_two_payments.png
   :align: center
   :width: 400pt
   :alt: Payment list showing the two payments created by the Internal Transfer wizard

Step 4: Verify the transit account reconciliation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To confirm that the Liquidity Transfer account was cleared:

1. Go to **Accounting > Accounting > Journal Items**.
2. Filter by the **Liquidity Transfer** account.
3. Both lines for the transfer (debit and credit) will display the same
   **Matching #** badge, confirming the transit account is balanced.


.. image:: /internal_transfer_with_agreed_amount/static/img/matching_journal_items.png
   :align: center
   :width: 400pt
   :alt: Journal Items filtered by the Liquidity Transfer account, showing both lines of the transfer with the same Matching # badge

Viewing existing internal transfers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the **Accounting > Dashboard**, click **Internal Transfers** on any
bank journal's Kanban card. This opens the payment list pre-filtered by
that journal and showing only internal transfers.

.. image:: /internal_transfer_with_agreed_amount/static/img/journal_kanban_internal_transfer_link.png
   :align: center
   :width: 400pt
   :alt: Journal Kanban card with the Internal Transfers link highlighted, showing the payment list filtered by that journal and only internal transfers

Resetting a transfer to draft
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to modify a posted internal transfer:

1. Go to **Accounting > Accounting > Payments** and open either payment
   of the pair.
2. Click **Reset to Draft**.
3. A confirmation dialog informs you that the paired payment will also be
   reset and the reconciliation between them removed.
4. Click **Confirm** to reset both payments simultaneously.

.. image:: /internal_transfer_with_agreed_amount/static/img/reset_both_payment_to_draft_button.png
   :align: center
   :width: 400pt
   :alt: Reset to Draft button on a posted payment, showing the confirmation dialog that informs the paired payment will also be reset and the reconciliation removed

Payments already matched to a bank statement line cannot be reset to
draft.


Bug Tracker
===========

Bugs are tracked on our support channel. In case you found an issue,
please contact us at support@vauxoo.com.

Credits
=======

Authors
~~~~~~~

* Vauxoo

Contributors
~~~~~~~~~~~~

* Humberto Arocha <hbto@vauxoo.com> (Designer)
* Irving Reyes <irving@vauxoo.com> (Developer)

Maintainers
~~~~~~~~~~~

This module is maintained by Vauxoo.

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :width: 600px
