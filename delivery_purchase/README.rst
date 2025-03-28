===========================
Delivery costs in purchases
===========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:db6d440113ff4fb7edc52ddbdffc7e177d3ff2925d96f349f39754bd0e00617f
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Production%2FStable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fdelivery--carrier-lightgray.png?logo=github
    :target: https://github.com/OCA/delivery-carrier/tree/17.0/delivery_purchase
    :alt: OCA/delivery-carrier
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/delivery-carrier-17-0/delivery-carrier-17-0-delivery_purchase
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/delivery-carrier&target_branch=17.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module allows to use delivery methods defined in *delivery* module
to calculate purchase delivery costs.

It reverses destinations in delivery pricelists to use them as sources
when applying the delivery method to purchases.

**Table of contents**

.. contents::
   :local:

Usage
=====

To use this module, you need to:

1. Go to *Purchase > Orders > Purchase Orders* and create a new Purchase
   Order.
2. Select a carrier in the field 'Delivery Method', fill out the rest of
   the form, be sure you added lines with storable products and save the
   form.
3. Confirm the purchase order.
4. Go to the linked 'Receipt' by clicking on 'Receipt' smart-button and
   you will see, under 'Additional info' tab, the same carrier selected
   in the purchase order.
5. If necessary, you can change the carrier in the 'Receipt'. When it is
   validated, the 'shipping cost' of the receipt will be calculated
   according to that new selected Carrier.
6. It is possible to change the shipping cost in picking.
7. The shipping cost will appear in an internal note created
   automatically when the 'Receipt' is validated.
8. A purchase order line will have been created for the cost of picking.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/delivery-carrier/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/delivery-carrier/issues/new?body=module:%20delivery_purchase%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Tecnativa

Contributors
------------

-  `Tecnativa <https://www.tecnativa.com>`__:

   -  Ernesto Tejeda
   -  Pedro M. Baeza
   -  Vicent Cubells
   -  Carolina Fernandez

-  `Sodexis <https://www.sodexis.com>`__:

   -  Sandeep J

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/delivery-carrier <https://github.com/OCA/delivery-carrier/tree/17.0/delivery_purchase>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
