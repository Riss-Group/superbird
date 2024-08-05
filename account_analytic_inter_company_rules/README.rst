=====================================================
Account Analytic Inter Company Rules
=====================================================

Module splits invoice lines by analytics if
interco automation is selected

Bug Tracker
===========

Problems with the module?
Write to: <support@archeti.com>


Credits
=======

Contributors
------------

* Justinas Orechovas <jorechovas@archeti.com>
* Marc Cassuto <mcassuto@archeti.com>

.. image:: https://www.archeti.com/logo.png
   :alt: ArcheTI
   :target: https://archeti.com


Changelog
=========================================================================
2023-05-09
-------------------------------------------------------------------------
What was done:
1. the analytic accounts must follow in the new invoices created
2. change the domain on the field interco_partner_id to
[is_company = True} => the customer expressed a new requirement where
they could reinvoice external partners
3. in the initial supplier bill, if some analytic accounts are linked
to the same interco_partner_id, please create only one invoice with
the different analytic account and distribution.

Example

Company C1 has 2 stores S11 and and S12
Company C2 has 3stores S21, S22 and S23
Company C3 creates a supplier bill:
    total amount is 1000$
    split is on all stores, 20%
On bill confirmation, 2 customer invoices are created :
one for C1 and one for C2
First invoice has
    total on line: 400$
    2 analytic accounts with 50% each
Second invoice has:
    total on line: 600$
    3 analytic accounts with 33.33% each

Update 2024-04-02
-----------------------------
The account must follow in the new invoices created
Example:

- Company C1 has 2 stores S11 and and S12
- Company C2 has 3stores S21, S22 and S23
- Company C3 creates a supplier bill with:
   - one invoice line with account 41xxx

On bill confirmation, 2 customer invoices are created:
one for C1 and one for C2
    First invoice has
        one invoice line with account 41xxx
    Second invoice has:
        one invoice line with account 41xxx
