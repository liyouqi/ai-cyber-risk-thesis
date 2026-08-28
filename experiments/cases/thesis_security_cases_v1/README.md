# Thesis Security Cases v1

This package contains ten standardized, anonymized Security Case JSON files derived from the supplied Tenable vulnerability export.

## Why JSON?

JSON is **not a university or thesis requirement**. It is used here because the experiment needs the same structured input for Manual, LLM-only, and Agentic RAG workflows, and because the future Risk Assessment Agent can consume the same files directly.

In the thesis, the important methodological point is the **standardized Security Case schema**, not the JSON file format itself.

## Data integrity

The cases are derived from real rows in the supplied vulnerability export.

The package deliberately does **not** invent:
- business context;
- internet exposure;
- compensating controls;
- risk acceptance;
- remediation ownership.

Where those fields are absent from the source, they remain `null`.

The following information has been anonymized or excluded:
- IP addresses;
- original node names;
- branch/location;
- raw plugin output.

Plugin IDs, plugin names, severity, CVEs, VPR, EPSS, protocol/port, source dates, synopsis, description, and remediation are retained from the supplied source where present.

## Initial experiment size

The experiment uses ten cases across three workflows: 10 cases × 3 workflows = 30 assessments.

The cases were selected to cover different technical severities and issue types while keeping the experiment manageable for a master's thesis.

## Cases

1. CASE-01 — Critical VMware ESXi multiple vulnerabilities
2. CASE-02 — Unsupported Microsoft SQL Server
3. CASE-03 — OpenSSH remote code execution
4. CASE-04 — VMware vCenter arbitrary file upload
5. CASE-05 — IKE aggressive mode with pre-shared key
6. CASE-06 — SNMP default community string on a critical storage device
7. CASE-07 — SWEET32 medium-strength cipher support
8. CASE-08 — RDP man-in-the-middle weakness
9. CASE-09 — RPC portmapper service detection
10. CASE-10 — SSH Terrapin prefix truncation weakness

## Source data

The original Tenable CSV is retained in the project as the source dataset. The
experiment inputs and thesis examples use the anonymized Security Case files.
