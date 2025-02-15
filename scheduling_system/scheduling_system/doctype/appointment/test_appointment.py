# Copyright (c) 2025, Gabriel Henrique Brioto and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class UnitTestAppointment(FrappeTestCase):
    """
    Unit tests for Appointment.
    Use this class for testing individual functions and methods.
    """

    def test_validate_conflict(self):
        """
        Testa se a função de validação de conflitos detecta corretamente sobreposições de horários.
        """
        seller = frappe.get_doc({
            "doctype": "User",
            "email": "test_seller@example.com",
            "first_name": "Test Seller"
        }).insert(ignore_if_duplicate=True)

        existing_appointment = frappe.get_doc({
            "doctype": "Appointment",
            "seller": seller.name,
            "start_date": "2025-02-20 10:00:00",
            "end_date": "2025-02-20 11:00:00",
            "client_name": "Client A"
        }).insert()

        new_appointment = frappe.get_doc({
            "doctype": "Appointment",
            "seller": seller.name,
            "start_date": "2025-02-20 10:30:00",
            "end_date": "2025-02-20 11:30:00",
            "client_name": "Client B"
        })

        self.assertRaises(frappe.ValidationError, new_appointment.insert)

    def test_create_appointment_without_seller(self):
        """
        Testa a tentativa de criar um compromisso sem um vendedor válido.
        """
        appointment = frappe.get_doc({
            "doctype": "Appointment",
            "start_date": "2025-02-20 12:00:00",
            "end_date": "2025-02-20 13:00:00",
            "client_name": "Client C"
        })
        self.assertRaises(frappe.ValidationError, appointment.insert)

    def test_delete_appointment(self):
        """
        Testa a exclusão de um compromisso.
        """
        seller = frappe.get_doc({
            "doctype": "User",
            "email": "test_seller_delete@example.com",
            "first_name": "Test Seller"
        }).insert(ignore_if_duplicate=True)

        appointment = frappe.get_doc({
            "doctype": "Appointment",
            "seller": seller.name,
            "start_date": "2025-02-20 14:00:00",
            "end_date": "2025-02-20 15:00:00",
            "client_name": "Client D"
        }).insert()

        appointment_name = appointment.name
        appointment.delete()

        self.assertFalse(frappe.db.exists("Appointment", appointment_name))


class IntegrationTestAppointment(FrappeTestCase):
    """
    Integration tests for Appointment.
    """

    def setUp(self):
        # Remove qualquer Appointment existente para evitar interferência nos testes
        frappe.db.delete("Appointment")
        frappe.db.commit()
    
        # Verifica se o usuário já existe antes de criá-lo
        if not frappe.db.exists("User", "test_seller@example.com"):
            self.seller = frappe.get_doc({
                "doctype": "User",
                "email": "test_seller@example.com",
                "first_name": "Test Seller"
            }).insert()
        else:
            self.seller = frappe.get_doc("User", "test_seller@example.com")

    def test_create_appointment(self):
        """
        Testa a criação de um compromisso válido.
        """
        appointment = frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 10:00:00",
            "end_date": "2025-02-20 11:00:00",
            "client_name": "Client A"
        })
        appointment.insert()
        self.assertTrue(appointment.name)

    def test_conflict_detection_on_insertion(self):
        """
        Testa se o sistema impede a criação de compromissos conflitantes.
        """
        frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 10:00:00",
            "end_date": "2025-02-20 11:00:00",
            "client_name": "Client A"
        }).insert()

        conflicting_appointment = frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 10:30:00",
            "end_date": "2025-02-20 11:30:00",
            "client_name": "Client B"
        })
        self.assertRaises(frappe.ValidationError, conflicting_appointment.insert)

    def test_multiple_non_conflicting_appointments(self):
        """
        Testa a criação de múltiplos compromissos sem conflitos.
        """
        frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 08:00:00",
            "end_date": "2025-02-20 09:00:00",
            "client_name": "Client X"
        }).insert()

        frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 11:00:00",
            "end_date": "2025-02-20 12:00:00",
            "client_name": "Client Y"
        }).insert()

        appointments = frappe.get_all("Appointment", filters={"seller": self.seller.name})
        self.assertEqual(len(appointments), 2)

    def test_create_appointment_with_different_sellers(self):
        """
        Testa a criação de compromissos para diferentes vendedores, sem conflito.
        """
        another_seller = frappe.get_doc({
            "doctype": "User",
            "email": "test_seller_2@example.com",
            "first_name": "Test Seller 2"
        }).insert(ignore_if_duplicate=True)

        frappe.get_doc({
            "doctype": "Appointment",
            "seller": self.seller.name,
            "start_date": "2025-02-20 09:00:00",
            "end_date": "2025-02-20 10:00:00",
            "client_name": "Client P"
        }).insert()

        frappe.get_doc({
            "doctype": "Appointment",
            "seller": another_seller.name,
            "start_date": "2025-02-20 09:00:00",
            "end_date": "2025-02-20 10:00:00",
            "client_name": "Client Q"
        }).insert()

        appointments = frappe.get_all("Appointment")
        self.assertEqual(len(appointments), 2)
