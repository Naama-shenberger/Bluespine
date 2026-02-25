def generate_prompt(policy_text):
    return f"""Analyze the medical policy and return a JSON object.
    Structure: {{ "policy_name": str, "rules": [{{ "rule_name": str, "description": str, "sql": str, "classification": str, "logic_confidence": str, "quote": str }}] }}

### CLASSIFICATIONS (Rule Types):
1. 'Mutual Exclusion': Services that cannot appear together on the same claim or same Date of Service (DOS).
2. 'Overutilization': Limits on units, frequency, or quantity of service allowed over a time period.
3. 'Service Not Covered': Explicitly excluded services, or when clinical requirements (e.g., "requested by physician", "documented report") are NOT met.

### LOGIC CONFIDENCE GUIDELINES:
- Provide a confidence level (High, Medium, Low) for the SQL logic.
- **Industry Search:** Search for similar logic in external industry sources (e.g., CMS Medicare Claims Processing Manual, AMA CPT guidelines).
- **confidence_reasoning:** Briefly explain WHY this level was chosen and cite the external source if found (e.g., "Aligned with CMS Chapter 12 guidelines for pathology").

### STRICT QUOTING GUIDELINES:
- Quotes must be VERBATIM (word-for-word) from the policy text.
- Do not add words, fix grammar, or complete sentences if they are partial in the source.
- Start the quote exactly from the first word of the relevant line/bullet in the PDF.

### RULE ATOMICITY:
- If a policy section contains multiple distinct conditions or exclusions (e.g., a bulleted list), create a separate rule for each specific condition.

### CODE VALIDATION GUIDELINES:
- **Zero Tolerance for Hallucinations:** You are ONLY allowed to include CPT/HCPCS codes that appear explicitly in the provided "POLICY TEXT".
- If a code is not in the text, DO NOT include it in the rules, descriptions, or SQL, even if you think it's relevant.
- Before finalizing the JSON, cross-reference every code in your 'sql' and 'description' fields against the 'POLICY TEXT'. If it's not there, delete the rule.

### SQL GENERATION GUIDELINES:
- Use ONLY the provided schema.
- If a rule depends on non-claim data (e.g., "medical judgement"), write SQL to flag the ProcedureCode and add a comment: -- REQUIRES MANUAL REVIEW OF DOCUMENTATION.
- Include 'Specialty' checks from ProviderInfo where relevant.

### SQL SCHEMA:
- **PatientInfo**: PatientID, DOB, Gender
- **ProviderInfo**: NPI, TIN, Specialty
- **Claims**: ClaimNumber, PatientID, NPI, TIN, TotalAmountBilled
- **ClaimLines**: ClaimLineID, ClaimNumber, DOS, POS, ProcedureCode, DiagnosisCode, Units, LineAmountBilled, Modifiers.

### Rule Atomicity: If a policy section contains multiple distinct conditions or exclusions 
(e.g., a bulleted list), create a separate rule for each specific condition that can be independently audited or coded in SQL.

### POLICY TEXT:
{policy_text}"""