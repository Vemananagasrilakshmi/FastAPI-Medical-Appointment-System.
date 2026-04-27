from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(
    title="🏥 MediCare Clinic — Medical Appointment System",
    description="""
A complete FastAPI backend for managing doctors, scheduling appointments,
and tracking consultations.


### Concepts Covered
-  Day 1 — GET APIs & JSON responses
-  Day 2 — POST APIs with Pydantic validation
-  Day 3 — Helper functions & filter logic
-  Day 4 — Full CRUD (POST / PUT / DELETE)
-  Day 5 — Multi-step appointment workflow
-  Day 6 — Search, Sort & Pagination
""",
    version="1.0.0",
)


# ---------------------------------------------------- **** IN-MEMORY DATA STORE ****----------------------------------------------

doctors = [
    {"id": 1, "name": "Dr. Sneha Reddy",  "specialization": "Cardiologist",  "fee": 800,  "experience_years": 12, "is_available": True},
    {"id": 2, "name": "Dr. Prasanth varma",   "specialization": "Dermatologist", "fee": 600,  "experience_years": 8,  "is_available": True},
    {"id": 3, "name": "Dr. Priya Sharma",  "specialization": "Pediatrician",  "fee": 500,  "experience_years": 10, "is_available": True},
    {"id": 4, "name": "Dr. Suresh Kumar",  "specialization": "General",       "fee": 300,  "experience_years": 15, "is_available": True},
    {"id": 5, "name": "Dr. Padma Priya",    "specialization": "Dermatologist", "fee": 700,  "experience_years": 6,  "is_available": False},
    {"id": 6, "name": "Dr. Mounika",   "specialization": "Cardiologist",  "fee": 900,  "experience_years": 20, "is_available": True},
    {"id": 7, "name": "Dr. Kavya Sri",    "specialization": "Pediatrician",  "fee": 450,  "experience_years": 9,  "is_available": True},
]

appointments = []
appt_counter = 1
doctor_counter = 8      # next ID for newly added doctors



# -------------------------------------------------------- **** HELPER FUNCTIONS ****---------------------------------------------

def find_doctor(doctor_id: int):
    """Return the doctor dict that matches doctor_id, or None."""
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None


def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool = False) -> dict:
    """
    Calculate consultation fee.
      video     -> 80 % of base fee
      in-person -> 100 % of base fee  (default)
      emergency -> 150 % of base fee
    Senior citizens get an additional 15 % discount on the calculated fee.
    Returns {"original_fee": ..., "final_fee": ...}
    """
    t = appointment_type.lower()
    if t == "video":
        calculated = base_fee * 0.80
    elif t == "emergency":
        calculated = base_fee * 1.50
    else:
        calculated = float(base_fee)

    original_fee = round(calculated, 2)
    final_fee = round(calculated * 0.85, 2) if senior_citizen else original_fee
    return {"original_fee": original_fee, "final_fee": final_fee}


def filter_doctors_logic(
    specialization: Optional[str],
    max_fee: Optional[int],
    min_experience: Optional[int],
    is_available: Optional[bool],
):
    """Apply optional filters to the global doctors list."""
    result = doctors[:]
    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result


# --------------------------------------------- **** PYDANTIC MODELS **** --------------------------------------------------------

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2, description="Full name of the patient")
    doctor_id: int = Field(..., gt=0, description="ID of the doctor to consult")
    date: str = Field(..., min_length=8, description="Appointment date  e.g. 2026-04-25")
    reason: str = Field(..., min_length=5, description="Reason for the visit (min 5 chars)")
    appointment_type: str = Field(default="in-person", description="in-person | video | emergency")
    senior_citizen: bool = Field(default=False, description="Apply senior-citizen 15 % discount")


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2, description="Doctor's full name")
    specialization: str = Field(..., min_length=2, description="Medical specialization")
    fee: int = Field(..., gt=0, description="Consultation fee in INR")
    experience_years: int = Field(..., gt=0, description="Years of experience")
    is_available: bool = Field(default=True, description="Availability status")



# -------------------------------------------- **** A P I   R O U T E S **** --------------------------------------------------------


# ------------------------------------------------ *** Q1 — HOME ROUTE *** ----------------------------------------------------------

@app.get("/", tags=["General"])
def home():
    """ 1 — Welcome endpoint for MediCare Clinic API."""
    return {
        "message": "Welcome to MediCare Clinic",
        "description": "Your complete medical appointment management system",
        "version": "1.0.0",
        "swagger_docs": "http://127.0.0.1:8000/docs",
    }



# ---------------------------------------- FIXED DOCTOR ROUTES  — must appear BEFORE /doctors/{id} ---------------------------------------------

@app.get("/doctors/summary", tags=["Doctors"])
def get_doctors_summary():
    """ 5 — Summary statistics for all doctors."""
    available = [d for d in doctors if d["is_available"]]
    most_experienced = max(doctors, key=lambda d: d["experience_years"]) if doctors else None
    cheapest_fee = min(d["fee"] for d in doctors) if doctors else None

    spec_count: dict = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1

    return {
        "total_doctors": len(doctors),
        "available_count": len(available),
        "most_experienced_doctor": most_experienced["name"] if most_experienced else None,
        "cheapest_consultation_fee": cheapest_fee,
        "doctors_per_specialization": spec_count,
    }


@app.get("/doctors/filter", tags=["Doctors"])
def filter_doctors(
    specialization: Optional[str] = Query(default=None, description="e.g. Cardiologist"),
    max_fee: Optional[int] = Query(default=None, description="Maximum consultation fee"),
    min_experience: Optional[int] = Query(default=None, description="Minimum years of experience"),
    is_available: Optional[bool] = Query(default=None, description="true / false"),
):
    """ 10 — Filter doctors by optional query parameters."""
    result = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    return {
        "filters_applied": {
            "specialization": specialization,
            "max_fee": max_fee,
            "min_experience": min_experience,
            "is_available": is_available,
        },
        "total_found": len(result),
        "doctors": result,
    }


@app.get("/doctors/search", tags=["Doctors"])
def search_doctors(
    keyword: str = Query(..., description="Search in doctor name AND specialization")
):
    """ 16 — Keyword search across name AND specialization (case-insensitive)."""
    
    kw = keyword.lower()
    matches = [
        d for d in doctors
        if kw in d["name"].lower() or kw in d["specialization"].lower()
    ]
    if not matches:
        return {
            "message": f"No doctors found matching '{keyword}'. Try a different keyword.",
            "total_found": 0,
            "doctors": [],
        }
    return {"keyword": keyword, "total_found": len(matches), "doctors": matches}


@app.get("/doctors/sort", tags=["Doctors"])
def sort_doctors(
    sort_by: str = Query(default="fee", description="fee | name | experience_years"),
    order: str = Query(default="asc", description="asc | desc"),
):
    """ 17 — Sort doctors by fee, name, or experience_years."""
    valid_fields = ["fee", "name", "experience_years"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    sorted_list = sorted(doctors, key=lambda d: d[sort_by], reverse=(order == "desc"))
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "doctors": sorted_list,
    }


@app.get("/doctors/page", tags=["Doctors"])
def paginate_doctors(
    page: int = Query(default=1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(default=3, ge=1, description="Records per page"),
):
    """ 18 — Paginate doctors list with total_pages calculation."""
    total = len(doctors)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    page_data = doctors[start: start + limit]

    return {
        "page": page,
        "limit": limit,
        "total_doctors": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "doctors": page_data,
    }


@app.get("/doctors/browse", tags=["Doctors"])
def browse_doctors(
    keyword: Optional[str] = Query(default=None, description="Search keyword"),
    sort_by: str = Query(default="fee", description="fee | name | experience_years"),
    order: str = Query(default="asc", description="asc | desc"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=4, ge=1, description="Records per page"),
):
    """ 20 — Combined browse: filter -> sort -> paginate in one endpoint."""
    # 1. Filter
    result = (
        [d for d in doctors if keyword.lower() in d["name"].lower()
         or keyword.lower() in d["specialization"].lower()]
        if keyword else doctors[:]
    )

    # 2. Sort
    valid_fields = ["fee", "name", "experience_years"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    result = sorted(result, key=lambda d: d[sort_by], reverse=(order == "desc"))

    # 3. Paginate
    total = len(result)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    page_data = result[start: start + limit]

    return {
        "query": {"keyword": keyword, "sort_by": sort_by, "order": order, "page": page, "limit": limit},
        "total_found": total,
        "total_pages": total_pages,
        "current_page": page,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "doctors": page_data,
    }



# -------------------------------------------------------------- DOCTOR VARIABLE ROUTES --------------------------------------------------------

@app.get("/doctors", tags=["Doctors"])
def get_all_doctors():
    """ 2 — List all doctors with total count and available count."""
    available_count = sum(1 for d in doctors if d["is_available"])
    return {
        "total": len(doctors),
        "available_count": available_count,
        "doctors": doctors,
    }


@app.post("/doctors", status_code=201, tags=["Doctors"])
def add_doctor(new_doc: NewDoctor):
    """ 11 — Add a new doctor. Rejects duplicate names. Returns HTTP 201."""
    global doctor_counter
    for d in doctors:
        if d["name"].lower() == new_doc.name.lower():
            raise HTTPException(status_code=400, detail=f"Doctor '{new_doc.name}' already exists.")

    doctor = {
        "id": doctor_counter,
        "name": new_doc.name,
        "specialization": new_doc.specialization,
        "fee": new_doc.fee,
        "experience_years": new_doc.experience_years,
        "is_available": new_doc.is_available,
    }
    doctors.append(doctor)
    doctor_counter += 1
    return {"message": "Doctor added successfully", "doctor": doctor}


@app.get("/doctors/{doctor_id}", tags=["Doctors"])
def get_doctor_by_id(doctor_id: int):
    """ 3 — Fetch a single doctor by ID."""
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}
    return doc


@app.put("/doctors/{doctor_id}", tags=["Doctors"])
def update_doctor(
    doctor_id: int,
    fee: Optional[int] = Query(default=None, gt=0, description="New consultation fee"),
    is_available: Optional[bool] = Query(default=None, description="Update availability"),
):
    """ 12 — Update a doctor's fee and/or availability. Returns 404 if not found."""
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available
    return {"message": "Doctor updated successfully", "doctor": doc}


@app.delete("/doctors/{doctor_id}", tags=["Doctors"])
def delete_doctor(doctor_id: int):
    """ 13 — Delete a doctor. Blocked if doctor has active scheduled appointments."""
    global doctors
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    active = [a for a in appointments if a["doctor_id"] == doctor_id and a["status"] == "scheduled"]
    if active:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete — Dr. {doc['name']} has {len(active)} active scheduled appointment(s).",
        )

    doctors = [d for d in doctors if d["id"] != doctor_id]
    return {"message": f"Doctor '{doc['name']}' deleted successfully."}



# ------------------------------------------------- FIXED APPOINTMENT ROUTES — must appear BEFORE /{appointment_id} -----------------------------------------

@app.get("/appointments/active", tags=["Appointments"])
def get_active_appointments():
    """ 15 — Return only scheduled or confirmed appointments."""
    active = [a for a in appointments if a["status"] in ("scheduled", "confirmed")]
    return {"total_active": len(active), "appointments": active}


@app.get("/appointments/search", tags=["Appointments"])
def search_appointments(
    patient_name: str = Query(..., description="Patient name to search (case-insensitive)")
):
    """ 19a — Search appointments by patient name."""
    kw = patient_name.lower()
    matches = [a for a in appointments if kw in a["patient_name"].lower()]
    return {"patient_name_query": patient_name, "total_found": len(matches), "appointments": matches}


@app.get("/appointments/sort", tags=["Appointments"])
def sort_appointments(
    sort_by: str = Query(default="fee", description="fee | date"),
    order: str = Query(default="asc", description="asc | desc"),
):
    """ 19b — Sort appointments by fee or date."""
    valid_fields = ["fee", "date"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    sorted_list = sorted(appointments, key=lambda a: a[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "total": len(sorted_list), "appointments": sorted_list}


@app.get("/appointments/page", tags=["Appointments"])
def paginate_appointments(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=3, ge=1, description="Records per page"),
):
    """ 19c — Paginate the appointments list."""
    total = len(appointments)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    page_data = appointments[start: start + limit]

    return {
        "page": page,
        "limit": limit,
        "total_appointments": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "appointments": page_data,
    }



# ----------------------------------------------------- APPOINTMENT CRUD + WORKFLOW ROUTES ------------------------------------------------------

@app.get("/appointments", tags=["Appointments"])
def get_all_appointments():
    """ 4 — Return all appointments with total count."""
    return {"total": len(appointments), "appointments": appointments}


@app.post("/appointments", status_code=201, tags=["Appointments"])
def book_appointment(req: AppointmentRequest):
    """
    8 / 9 — Book a new appointment.
    Validates doctor, checks availability, calculates fee
    (type multiplier + optional senior-citizen 15 % discount).
    """
    global appt_counter

    doc = find_doctor(req.doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doc["is_available"]:
        raise HTTPException(status_code=400, detail=f"{doc['name']} is currently not available.")

    fee_info = calculate_fee(doc["fee"], req.appointment_type, req.senior_citizen)

    appt = {
        "appointment_id": appt_counter,
        "patient_name": req.patient_name,
        "doctor_id": doc["id"],
        "doctor_name": doc["name"],
        "specialization": doc["specialization"],
        "date": req.date,
        "reason": req.reason,
        "appointment_type": req.appointment_type,
        "senior_citizen": req.senior_citizen,
        "original_fee": fee_info["original_fee"],
        "fee": fee_info["final_fee"],
        "status": "scheduled",
    }
    appointments.append(appt)
    appt_counter += 1
    return {"message": "Appointment booked successfully", "appointment": appt}


@app.get("/appointments/by-doctor/{doctor_id}", tags=["Appointments"])
def get_appointments_by_doctor(doctor_id: int):
    """ 15 — Return all appointments for a specific doctor."""
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doc_appts = [a for a in appointments if a["doctor_id"] == doctor_id]
    return {
        "doctor": doc["name"],
        "total_appointments": len(doc_appts),
        "appointments": doc_appts,
    }


@app.get("/appointments/{appointment_id}", tags=["Appointments"])
def get_appointment_by_id(appointment_id: int):
    """Get a single appointment by its ID."""
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            return a
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/confirm", tags=["Appointments"])
def confirm_appointment(appointment_id: int):
    """ 14 — Confirm a scheduled appointment -> status becomes 'confirmed'."""
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            if a["status"] != "scheduled":
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot confirm — appointment is already '{a['status']}'.",
                )
            a["status"] = "confirmed"
            return {"message": "Appointment confirmed successfully", "appointment": a}
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/cancel", tags=["Appointments"])
def cancel_appointment(appointment_id: int):
    """ 14 — Cancel an appointment -> status 'cancelled', doctor marked available again."""
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            if a["status"] == "cancelled":
                raise HTTPException(status_code=400, detail="Appointment is already cancelled.")
            if a["status"] == "completed":
                raise HTTPException(status_code=400, detail="Cannot cancel a completed appointment.")
            a["status"] = "cancelled"
            doc = find_doctor(a["doctor_id"])
            if doc:
                doc["is_available"] = True
            return {
                "message": "Appointment cancelled. Doctor is now marked as available.",
                "appointment": a,
            }
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.post("/appointments/{appointment_id}/complete", tags=["Appointments"])
def complete_appointment(appointment_id: int):
    """ 15 — Mark a confirmed (or scheduled) appointment as completed."""
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            if a["status"] == "completed":
                raise HTTPException(status_code=400, detail="Appointment is already completed.")
            if a["status"] == "cancelled":
                raise HTTPException(status_code=400, detail="Cannot complete a cancelled appointment.")
            a["status"] = "completed"
            return {"message": "Appointment marked as completed", "appointment": a}
    raise HTTPException(status_code=404, detail="Appointment not found")