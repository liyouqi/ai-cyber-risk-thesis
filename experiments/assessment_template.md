# Risk Assessment Template

Use this template for all three experimental workflows:

- 01 Manual
- 02 LLM-only
- 03 Agentic RAG

The same Security Case must be assessed using the same output structure.

Do not invent missing facts. If business context, exposure, controls, ownership, or other information is not available, state that it is unknown.

---

## Case Information

**Case ID:**  
**Assessment Method:** Manual / LLM-only / Agentic RAG  
**Assessment Date:**  
**Assessor / Model:**  

---

## 1. Case Summary

Briefly describe the security issue based only on the information provided in the Security Case.

Include, where available:

- vulnerability or finding type;
- affected asset type;
- technical severity;
- relevant CVE or vulnerability information;
- observation period or remediation status.

**Assessment:**

---

## 2. Technical Risk Assessment

Assess the technical security risk of the case.

Consider, where supported by the available evidence:

- exploitability;
- severity;
- attack complexity;
- remote exploitation potential;
- affected service or technology;
- vulnerability age;
- known exploitation information;
- possible confidentiality, integrity, or availability impact.

Do not infer network exposure or compensating controls if they are not provided.

**Assessment:**

---

## 3. Business / Operational Impact

Assess the possible business or operational impact.

Use asset criticality and business context where available.

If the Security Case does not contain enough business information, explicitly state the limitation rather than inventing an impact.

**Assessment:**

---

## 4. Regulatory Relevance

Identify regulatory requirements that may be relevant to the case.

For each relevant regulatory point, provide:

- regulatory framework;
- article / provision / reference where available;
- short explanation of why it is relevant;
- supporting citation or evidence where the workflow provides one.

### Regulatory Finding 1

**Framework:**  
**Provision:**  
**Relevance:**  
**Evidence / Citation:**  

### Regulatory Finding 2

**Framework:**  
**Provision:**  
**Relevance:**  
**Evidence / Citation:**  

Add further findings only when necessary.

If no reliable regulatory evidence is available, state this clearly.

---

## 5. Overall Risk Level and Rationale

**Proposed Risk Level:** Critical / High / Medium / Low / Unable to Determine

Explain the proposed level using the evidence available in the Security Case and the analysis above.

Do not automatically copy the scanner severity. Scanner severity describes the
technical finding; the proposed risk level should also consider the asset,
available context, regulatory relevance and uncertainty.

The rationale should distinguish between:

- technical severity;
- asset or business importance;
- regulatory relevance;
- uncertainty caused by missing information.

**Rationale:**

---

## 6. Recommended Actions

Provide practical next actions based on the available evidence.

Where appropriate, distinguish between:

- immediate technical remediation;
- verification or validation;
- compensating controls;
- further information required;
- follow-up or monitoring;
- regulatory / governance follow-up.

Do not assume that remediation, risk acceptance, or management approval has already occurred.

**Recommended Actions:**

---

## 7. Limitations / Missing Information

Record any information that would materially affect the assessment but is not available.

Examples:

- internet exposure;
- business service dependency;
- compensating controls;
- remediation ownership;
- actual exploit activity;
- formal risk acceptance;
- production impact.

**Limitations:**

---

## 8. Final Assessment

Provide a short final conclusion of approximately 3–5 sentences.

The conclusion should summarise:

- the main risk;
- the proposed risk level;
- the most important regulatory relevance;
- the most important next action.

**Final Assessment:**
