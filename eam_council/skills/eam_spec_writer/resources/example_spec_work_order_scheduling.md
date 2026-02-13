# Example Spec: Work Order Scheduling Module

## Spec: Work Order Scheduling Engine
**Version:** 0.1
**Status:** Example / Reference
**Author:** EAM Architecture Council

### 1. Scope
Covers the scheduling and dispatching of maintenance work orders across plant assets. Does NOT cover work order creation, approval workflows, or financial settlement.

### 2. Business Context
Maintenance planners need to schedule preventive and corrective work orders against available resources (technicians, tools, parts) while respecting asset criticality, safety windows, and production schedules.

### 3. Key Entities
| Entity | Source System / API | Description | Key Fields |
|--------|---------------------|-------------|------------|
| Work Order | SAP PM -- API_MAINTORDER_SRV (OData v4) | Maintenance task to be executed | order_id, order_type, priority, status, planned_start, planned_end |
| Functional Location | SAP PM -- API_FUNCLOCATION_SRV (OData v4) | Physical location in plant hierarchy | func_loc_id, description, plant, area |
| Equipment | SAP PM -- API_EQUIPMENT_SRV (OData v4) | Individual asset/machine | equipment_id, description, func_loc_id, criticality |
| Work Center | SAP PM -- API_WORKCENTER_SRV (OData v4) | Group of technicians/resources | work_center_id, capacity, plant |
| Operation | SAP PM -- API_MAINTORDER_SRV (OData v4) | Individual task within a work order | operation_id, work_order_id, duration, work_center_id |
| Maintenance Plan | SAP PM -- API_MAINTENANCEPLAN_SRV (OData v4) | Recurring schedule definition | plan_id, cycle, strategy, call_horizon |

### 4. Functional Requirements
- FR-1: Schedule work orders based on priority, asset criticality, and resource availability.
- FR-2: Detect scheduling conflicts (double-booked resources, overlapping maintenance windows).
- FR-3: Suggest optimal scheduling windows given production calendar constraints.
- FR-4: Support drag-and-drop rescheduling with conflict re-evaluation.

### 5. Non-Functional Requirements
- NFR-1: Scheduling engine must return results within 2 seconds for up to 500 work orders.
- NFR-2: Must support concurrent access by up to 20 planners.

### 6. Interface Design
#### 6.1 Inputs
- SAP PM: Work orders, operations, work centers (via OData v4 APIs; RFC/BAPI as fallback)
- Production calendar: Plant-specific shift and downtime windows

#### 6.2 Outputs
- Scheduled work order timeline (Gantt-compatible data structure)
- Conflict report

#### 6.3 Integration Points
- SAP PM <-> Scheduling Engine: OData v4, real-time pull on demand
- Scheduling Engine <-> UI: REST API, JSON

### 7. Data Model (Simplified)
```
WorkOrder(order_id PK, equipment_id FK, priority, status, planned_start, planned_end)
  +-- Operation(operation_id PK, work_order_id FK, work_center_id FK, duration, sequence)
Equipment(equipment_id PK, func_loc_id FK, criticality)
WorkCenter(work_center_id PK, capacity_hours_per_day)
```

### 8. Acceptance Criteria
- [ ] AC-1: Given 100 work orders and 10 work centers, the engine produces a conflict-free schedule.
- [ ] AC-2: A priority-1 work order is always scheduled before a priority-3 work order for the same resource.
- [ ] AC-3: Scheduling conflicts are reported with affected order IDs and suggested resolution.

### 9. Mock Data Examples
```json
{
  "work_order": {
    "order_id": "WO-001234",
    "order_type": "PM02",
    "priority": 1,
    "equipment_id": "EQ-5001",
    "planned_start": "2026-03-15T08:00:00Z",
    "planned_end": "2026-03-15T16:00:00Z",
    "operations": [
      {"operation_id": "OP-010", "work_center_id": "WC-MECH-01", "duration_hours": 4},
      {"operation_id": "OP-020", "work_center_id": "WC-ELEC-01", "duration_hours": 2}
    ]
  }
}
```

### 10. Open Items
- [ ] Confirm OData v4 write-back support vs BAPI fallback for work order status updates
- [ ] Define priority escalation rules for overdue PMs
- [ ] Clarify whether scheduling considers spare parts availability
