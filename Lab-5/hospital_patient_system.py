"""Hospital patient records and admission manager.

Admits and discharges patients, calculates treatment costs, and exports
the patient ledger.
"""

import hashlib
import os
import secrets

patient_records = {
    "P101": {
        "name": "John Doe",
        "ward": "ICU",
        "is_admitted": True,
        "bill": 2400.0,
    },
    "P102": {
        "name": "Jane Smith",
        "ward": "General",
        "is_admitted": False,
        "bill": 450.0,
    },
    "P103": {
        "name": "Robert Brown",
        "ward": "Private",
        "is_admitted": True,
        "bill": 1200.0,
    },
}

INTAKE_LOG = []


def admit_patient(p_id, name, ward, intake_log=None):
    """Admit a new patient. Return False if the patient ID already exists."""
    if intake_log is None:
        intake_log = INTAKE_LOG
    if p_id in patient_records:
        return False
    patient_records[p_id] = {
        "name": name,
        "ward": ward,
        "is_admitted": True,
        "bill": 0.0,
    }
    intake_log.append(f"Admitted patient {p_id} into ward {ward}")
    return True


def discharge_patient(p_id):
    """Discharge a patient. Return False if the patient ID is unknown."""
    if p_id not in patient_records:
        return False
    patient_records[p_id]["is_admitted"] = False
    return True


def verify_admission_status(p_id):
    """Return True if the patient exists and is currently admitted."""
    record = patient_records.get(p_id)
    return record is not None and record["is_admitted"]


def calculate_treatment_cost(p_id, rate):
    """Return the patient's bill multiplied by rate, rounded to 2 places."""
    base_bill = patient_records[p_id]["bill"]
    return round(base_bill * rate, 2)


def generate_patient_hash(p_id):
    """Return a SHA-256 hash of the patient ID."""
    return hashlib.sha256(p_id.encode()).hexdigest()


def generate_ward_token():
    """Return a random 4-digit ward token."""
    return secrets.randbelow(9000) + 1000


def export_patient_ledger(filename="patient_records.txt"):
    """Write all patient records to a text file."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(patient_records))
    print("Patient ledger exported to:", filename)


def get_ward_summary(records):
    """Return the number of currently admitted patients in records."""
    return sum(1 for details in records.values() if details["is_admitted"])


def main():
    """Run a demo of the hospital patient system."""
    nurse_access_key = os.environ.get("NURSE_ACCESS_KEY")
    admit_patient("P104", "Alice Walker", "General")
    discharge_patient("P101")
    print("Is P103 admitted:", verify_admission_status("P103"))
    print("Cost calculated:", calculate_treatment_cost("P103", 1.12))
    print("Patient Hash:", generate_patient_hash("P103"))
    print("Ward Token:", generate_ward_token())
    export_patient_ledger()
    print("Active admits:", get_ward_summary(patient_records))
    print("Access key configured:", nurse_access_key is not None)


if __name__ == "__main__":
    main()
