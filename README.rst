|pypi| |actions| |codecov| |downloads|


intecomm-rando
--------------------
Randomization for INTECOMM_ trial

A dependency of the INTECOMM_ trial EDC.

The INTECOMM_ trial is a cluster randomized trial where the unit of randomization is the patient group.

At screening, data for individual potential participants are stored in the ``intecomm_screening.PatientLog`` model.
Eligible individual potential participants (model ``PatientLog``) are added to a patient group (model ``intecomm_group.PatientGroup``).

The data flow is PatientLog -> SubjectScreening -> if eligible -> SubjectConsent

Ideally, for a patient group to be considered for randomization, the group must contain
between 9-14 screened and consented members where a count of chronic conditions of those in the group meets an
approximate ratio of 2 : 1; that is, 2(DM/HTN) : 1(HIV). The site coordinators may override these values.

Once a PatientGroup is ready to randomize, the site staff open the ``PatientGroup`` form and click "randomize".

In the background, the ``Randomizer`` class calls its method ``randomize_group``.  ``randomize_group`` picks the next
available record from the randomization_list (''intecomm_rando.RandomizationList``) and inserts a unique ``group_identifier`` value.
A records is available if ``group_identifier`` has not been set. Ordering is ascending by ``sid``.

The PatientGroup is given its newly allocated ``group_identifier``. The subjects in this group may now be
followed longitudinally starting with visit 1000.

The ``group_identifier``, for subjects in a PatientGroup, is updated on the PatientLog record as well.

* The ``RegisteredGroup`` model holds the ``sid`` to ``group_identifier`` relationship
* The ``RandomizationList`` model holds the ``sid`` to ``assignment`` to ``group_identifier`` relationship
* ``PatientLog`` links group_identifier and subject_identifier

See also tables:
•	Intecomm_rando_registeredgroup
•	Intecomm_rando_randomizationlist
•	intecomm_screening_patientlog
•	intecomm_group_patientlog








.. |pypi| image:: https://img.shields.io/pypi/v/intecomm-rando.svg
    :target: https://pypi.python.org/pypi/intecomm-rando

.. |actions| image:: https://github.com/intecomm-trial/intecomm-rando/workflows/build/badge.svg?branch=develop
  :target: https://github.com/intecomm-trial/intecomm-rando/actions?query=workflow:build

.. |codecov| image:: https://codecov.io/gh/intecomm-trial/intecomm-rando/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/intecomm-trial/intecomm-rando

.. |downloads| image:: https://pepy.tech/badge/intecomm-rando
   :target: https://pepy.tech/project/intecomm-rando

.. _INTECOMM: https://github.com/intecomm-trial/intecomm-edc
