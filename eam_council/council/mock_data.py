"""Mock SAP EAM data for dry-run mode and testing."""

from __future__ import annotations

MOCK_WORK_ORDERS = [
    {
        "order_id": "WO-001234",
        "order_type": "PM02",
        "priority": 1,
        "status": "REL",
        "equipment_id": "EQ-5001",
        "func_loc_id": "PLT1-AREA2-LINE3",
        "planned_start": "2026-03-15T08:00:00Z",
        "planned_end": "2026-03-15T16:00:00Z",
        "work_center_id": "WC-MECH-01",
    },
    {
        "order_id": "WO-001235",
        "order_type": "PM01",
        "priority": 2,
        "status": "CRTD",
        "equipment_id": "EQ-5002",
        "func_loc_id": "PLT1-AREA2-LINE3",
        "planned_start": "2026-03-16T06:00:00Z",
        "planned_end": "2026-03-16T14:00:00Z",
        "work_center_id": "WC-ELEC-01",
    },
    {
        "order_id": "WO-001236",
        "order_type": "PM03",
        "priority": 3,
        "status": "REL",
        "equipment_id": "EQ-5003",
        "func_loc_id": "PLT1-AREA1-LINE1",
        "planned_start": "2026-03-17T08:00:00Z",
        "planned_end": "2026-03-17T12:00:00Z",
        "work_center_id": "WC-MECH-01",
    },
]

MOCK_EQUIPMENT = [
    {
        "equipment_id": "EQ-5001",
        "description": "Conveyor Belt Drive Motor",
        "func_loc_id": "PLT1-AREA2-LINE3",
        "criticality": "A",
        "manufacturer": "Siemens",
    },
    {
        "equipment_id": "EQ-5002",
        "description": "Hydraulic Press Unit",
        "func_loc_id": "PLT1-AREA2-LINE3",
        "criticality": "B",
        "manufacturer": "Bosch Rexroth",
    },
    {
        "equipment_id": "EQ-5003",
        "description": "Cooling Tower Fan",
        "func_loc_id": "PLT1-AREA1-LINE1",
        "criticality": "C",
        "manufacturer": "ABB",
    },
]

MOCK_WORK_CENTERS = [
    {
        "work_center_id": "WC-MECH-01",
        "description": "Mechanical Maintenance Team A",
        "plant": "PLT1",
        "capacity_hours_per_day": 8.0,
    },
    {
        "work_center_id": "WC-ELEC-01",
        "description": "Electrical Maintenance Team A",
        "plant": "PLT1",
        "capacity_hours_per_day": 8.0,
    },
]


def get_mock_context() -> str:
    """Return mock SAP data as a formatted context string."""
    lines = ["## Mock SAP EAM Data (for reference)\n"]
    lines.append("### Work Orders")
    for wo in MOCK_WORK_ORDERS:
        lines.append(f"- {wo['order_id']} | Type: {wo['order_type']} | "
                      f"Priority: {wo['priority']} | Equipment: {wo['equipment_id']}")
    lines.append("\n### Equipment")
    for eq in MOCK_EQUIPMENT:
        lines.append(f"- {eq['equipment_id']} | {eq['description']} | "
                      f"Criticality: {eq['criticality']}")
    lines.append("\n### Work Centers")
    for wc in MOCK_WORK_CENTERS:
        lines.append(f"- {wc['work_center_id']} | {wc['description']} | "
                      f"Capacity: {wc['capacity_hours_per_day']}h/day")
    return "\n".join(lines)
