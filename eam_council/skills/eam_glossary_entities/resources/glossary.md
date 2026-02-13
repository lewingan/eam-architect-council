# EAM Glossary

| Term | Definition |
|------|-----------|
| **Work Order (WO)** | A formal instruction to perform a maintenance task on an asset. SAP API: API_MAINTORDER_SRV (legacy table: AUFK). |
| **Functional Location (FLoc)** | A point in the plant hierarchy where maintenance is performed. SAP API: API_FUNCLOCATION_SRV (legacy table: IFLO). |
| **Equipment** | An individual physical asset that can be maintained independently. SAP API: API_EQUIPMENT_SRV (legacy table: EQUI). |
| **Work Center** | A resource group (people, machines) that performs maintenance operations. SAP API: API_WORKCENTER_SRV (legacy table: CRHD). |
| **Operation** | A single step/task within a work order. Accessed via API_MAINTORDER_SRV entity set MaintenanceOrderOperation (legacy table: AFVC). |
| **Maintenance Plan** | A time- or performance-based rule that generates work orders on a recurring schedule. SAP API: API_MAINTENANCEPLAN_SRV (legacy table: MPOS). |
| **Maintenance Strategy** | A set of scheduling rules (cycle lengths, call horizons) that drive maintenance plans. |
| **Notification** | A report of a malfunction or condition that may trigger a work order. SAP API: API_MAINTNOTIFICATION_SRV (legacy table: QMEL). |
| **Bill of Materials (BOM)** | List of spare parts/materials associated with an equipment or functional location. |
| **Task List** | A reusable template of operations that can be assigned to work orders. |
| **Preventive Maintenance (PM)** | Scheduled maintenance to prevent failures before they occur. |
| **Corrective Maintenance (CM)** | Unplanned maintenance to fix a failure that has already occurred. |
| **Predictive Maintenance (PdM)** | Condition-based maintenance using sensor data or analytics to predict failures. |
| **Asset Criticality** | A rating (e.g., A/B/C) indicating the business impact of an asset's failure. |
| **Scheduling Period** | The time window in which work orders are planned and assigned to resources. |
| **Backlog** | The set of open, unscheduled work orders awaiting planning. |
| **Planner Group** | The organizational unit responsible for planning maintenance work. |
| **MRP (Material Requirements Planning)** | Process to ensure spare parts are available for scheduled maintenance. |
| **CMMS** | Computerized Maintenance Management System -- the software category EAM belongs to. |
| **EAM** | Enterprise Asset Management -- the discipline of managing the lifecycle of physical assets. |
| **SAP Business Accelerator Hub** | SAP's API catalog (api.sap.com) where published OData services are documented with entity sets, parameters, and usage examples. |
| **OData v4** | The standard REST-based protocol used by S/4HANA for exposing APIs. Preferred over legacy BAPI/RFC for new integrations. |
