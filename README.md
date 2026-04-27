# FastAPI-Medical-Appointment-System.

A complete real-world FastAPI backend for managing doctors, appointments, and clinic workflows.

## 🚀 How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open: **http://127.0.0.1:8000/docs**

---

## 📋 All 20 Endpoints

| # | Method | Route | Day | Description |
|---|--------|-------|-----|-------------|
| 1 | GET | `/` | Day 1 | Welcome home route |
| 2 | GET | `/doctors` | Day 1 | List all doctors with available count |
| 3 | GET | `/doctors/{doctor_id}` | Day 1 | Get doctor by ID |
| 4 | GET | `/appointments` | Day 1 | List all appointments |
| 5 | GET | `/doctors/summary` | Day 1 | Summary stats — most experienced, cheapest fee, count per specialization |
| 6 | POST | `/appointments` | Day 2 | Book appointment with Pydantic validation |
| 7 | *(helpers)* | — | Day 3 | `find_doctor()`, `calculate_fee()` helper functions |
| 8 | POST | `/appointments` | Day 2+3 | Uses helpers to calculate fee, returns full appointment |
| 9 | POST | `/appointments` | Day 2+3 | Senior citizen 15% discount + appointment type multiplier |
| 10 | GET | `/doctors/filter` | Day 3 | Filter by specialization, max_fee, min_experience, is_available |
| 11 | POST | `/doctors` | Day 4 | Add new doctor (rejects duplicates, returns 201) |
| 12 | PUT | `/doctors/{doctor_id}` | Day 4 | Update fee and/or availability |
| 13 | DELETE | `/doctors/{doctor_id}` | Day 4 | Delete doctor (blocks if active appointments exist) |
| 14 | POST | `/appointments/{id}/confirm` | Day 5 | Confirm appointment |
| 14 | POST | `/appointments/{id}/cancel` | Day 5 | Cancel + mark doctor available |
| 15 | POST | `/appointments/{id}/complete` | Day 5 | Mark completed |
| 15 | GET | `/appointments/active` | Day 5 | All scheduled/confirmed appointments |
| 15 | GET | `/appointments/by-doctor/{id}` | Day 5 | All appointments for a doctor |
| 16 | GET | `/doctors/search` | Day 6 | Keyword search across name & specialization |
| 17 | GET | `/doctors/sort` | Day 6 | Sort by fee / name / experience_years |
| 18 | GET | `/doctors/page` | Day 6 | Pagination with total_pages |
| 19 | GET | `/appointments/search` | Day 6 | Search appointments by patient name |
| 19 | GET | `/appointments/sort` | Day 6 | Sort appointments by fee or date |
| 19 | GET | `/appointments/page` | Day 6 | Paginate appointments |
| 20 | GET | `/doctors/browse` | Day 6 | Combined search + sort + pagination |

---

## 🧠 Concepts Covered

- **Day 1** — GET routes, JSON responses, home route, summary endpoint
- **Day 2** — POST with Pydantic models, field constraints, validation errors
- **Day 3** — Helper functions (`find_doctor`, `calculate_fee`, `filter_doctors_logic`), Query params with `is not None`
- **Day 4** — Full CRUD: POST (201 Created), PUT, DELETE with 404 handling
- **Day 5** — Multi-step workflow: `scheduled → confirmed → completed / cancelled`, active appointments, by-doctor view
- **Day 6** — Keyword search, sorting with validation, pagination with `total_pages`, combined browse endpoint

---

## 🏥 Doctor Specializations
- Cardiologist
- Dermatologist
- Pediatrician
- General

## 💉 Appointment Types & Fee Rules
| Type | Fee Multiplier |
|------|---------------|
| in-person | 100% |
| video | 80% |
| emergency | 150% |

Senior citizens receive an additional **15% discount** on all types.
