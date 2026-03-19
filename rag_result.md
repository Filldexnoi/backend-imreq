# RAG Analyze Prototype — Results

## REQ-1 — -
> ระบบต้องรองรับการสมัครสมาชิก (Sign Up) โดยใช้อีเมลและรหัสผ่านที่กำหนดตามมาตรฐานความปลอดภัย

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3007 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Modal Verb 'Shall' | 0.2933 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 3 | Measurable Conditions | 0.291 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 4 | Conforming | 0.2777 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 5 | Complete | 0.2759 | The requirement sufficiently describes the capability and conditions without needing further... |
| 6 | Positive Phrasing | 0.2326 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 7 | Unambiguous | 0.2271 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 8 | System Performance | 0.2262 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 9 | Verifiable | 0.2221 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 10 | Necessary | 0.2149 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 11 | Appropriate | 0.2095 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 12 | Subjective Language | 0.2046 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 13 | Formal Syntax | 0.1954 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 14 | Singular | 0.1887 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 15 | Design Independence | 0.1834 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 16 | Active Voice | 0.1695 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 17 | Avoid 'Must' | 0.1575 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 18 | Correct | 0.15 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 19 | Comparative Phrases | 0.1405 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 20 | Avoid 'Shall be able to' | 0.1067 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 21 | Ambiguous Adjectives | 0.1002 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 22 | Modal Verb 'Should' | 0.0913 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 23 | Loopholes | 0.0577 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Superlatives | 0.0504 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 25 | Open-ended Terms | 0.0035 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Vague Pronouns | -0.0128 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเกี่ยวกับมาตรฐานความปลอดภัยที่ต้องการ เช่น ความยาวขั้นต่ำของรหัสผ่าน, การใช้ตัวอักษรพิเศษ, การเข้ารหัสข้อมูล
- **RAG:** ไม่ระบุรายละเอียดของมาตรฐานความปลอดภัยที่ต้องการ เช่น มาตรฐานการเข้ารหัสรหัสผ่าน, ความยาวขั้นต่ำของรหัสผ่าน, หรือการป้องกันการโจมตีแบบ brute-force

**Conforming**
- **Normal:** ไม่ได้ใช้รูปแบบที่กำหนด (เช่น EARS) หรือรูปแบบที่ชัดเจนสำหรับการเขียนข้อกำหนด
- **RAG:** ไม่ใช้คำว่า 'shall' เพื่อระบุข้อกำหนดที่จำเป็น (ตาม Rule 2)

**Unambiguous**
- **Normal:** คำว่า 'ตามมาตรฐานความปลอดภัย' ยังคลุมเครือ ต้องระบุมาตรฐานที่เฉพาะเจาะจง
- **RAG:** คำว่า 'ตามมาตรฐานความปลอดภัย' เป็นคำที่คลุมเครือ ต้องระบุมาตรฐานความปลอดภัยที่เฉพาะเจาะจง

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากไม่ได้ระบุเกณฑ์การวัดผลที่ชัดเจน เช่น ความยาวขั้นต่ำของรหัสผ่าน หรือวิธีการเข้ารหัส
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากไม่ได้ระบุเกณฑ์ที่วัดได้สำหรับ 'มาตรฐานความปลอดภัย'

---

## REQ-10 — -
> ระบบต้องส่งการแจ้งเตือน (Notification) เมื่อผู้ใช้ใช้เงินเกิน 80% ของงบประมาณ

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Verifiable | 0.3103 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 2 | Active Voice | 0.3069 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 3 | System Performance | 0.3036 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 4 | Feasible | 0.2978 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 5 | Positive Phrasing | 0.2917 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 6 | Modal Verb 'Shall' | 0.2866 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 7 | Conforming | 0.2689 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 8 | Correct | 0.245 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 9 | Appropriate | 0.2396 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 10 | Modal Verb 'Should' | 0.2295 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 11 | Complete | 0.2089 | The requirement sufficiently describes the capability and conditions without needing further... |
| 12 | Measurable Conditions | 0.2047 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 13 | Design Independence | 0.1994 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 14 | Avoid 'Must' | 0.1924 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 15 | Comparative Phrases | 0.1901 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 16 | Formal Syntax | 0.1876 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 17 | Superlatives | 0.1854 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 18 | Avoid 'Shall be able to' | 0.1784 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 19 | Singular | 0.1728 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 20 | Necessary | 0.1652 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 21 | Open-ended Terms | 0.1619 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 22 | Ambiguous Adjectives | 0.1528 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 23 | Unambiguous | 0.136 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 24 | Subjective Language | 0.1353 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 25 | Loopholes | 0.1186 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 26 | Vague Pronouns | 0.1152 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดของการแจ้งเตือน (เช่น ช่องทาง, เนื้อหา, ความถี่) และเงื่อนไขเพิ่มเติม (เช่น การแจ้งเตือนซ้ำ)
- **RAG:** ไม่ระบุรายละเอียดของการแจ้งเตือน (เช่น ช่องทาง, เนื้อหา) ซึ่งอาจทำให้ไม่สามารถนำไปใช้งานได้จริง

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน (เช่น EARS หรือ ISO 29148) เนื่องจากขาดรายละเอียดที่จำเป็น
- **RAG:** ไม่ได้ใช้รูปแบบที่ชัดเจน เช่น 'ระบบจะต้อง...' (ใช้ 'shall' ในภาษาอังกฤษ)

**Unambiguous**
- **Normal:** คำว่า 'การแจ้งเตือน' ยังคลุมเครือ ต้องระบุรายละเอียดเพิ่มเติม เช่น ช่องทางและรูปแบบการแจ้งเตือน
- **RAG:** คำว่า 'ระบบ' และ 'ผู้ใช้' อาจมีความคลุมเครือได้หากไม่มีบริบทที่ชัดเจน

**Verifiable**
- **Normal:** ขาดเกณฑ์ที่วัดผลได้ เช่น 'เมื่อผู้ใช้ใช้เงินเกิน 80% ของงบประมาณ' สามารถตรวจสอบได้ แต่ยังขาดรายละเอียดว่าการแจ้งเตือนจะเกิดขึ้นอย่างไร (เช่น เวลา, ช่องทาง)

---

## REQ-11 — -
> ระบบต้องส่งการแจ้งเตือนอีกครั้งเมื่อผู้ใช้ใช้เงินเกิน 100% ของงบประมาณ

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Verifiable | 0.3155 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 2 | Feasible | 0.2923 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Positive Phrasing | 0.2883 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 4 | Active Voice | 0.2873 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 5 | System Performance | 0.2766 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 6 | Modal Verb 'Shall' | 0.2381 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 7 | Correct | 0.2289 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 8 | Comparative Phrases | 0.2135 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 9 | Modal Verb 'Should' | 0.209 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 10 | Superlatives | 0.2058 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 11 | Measurable Conditions | 0.2021 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 12 | Conforming | 0.1995 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 13 | Avoid 'Shall be able to' | 0.196 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 14 | Necessary | 0.1878 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 15 | Appropriate | 0.1796 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 16 | Avoid 'Must' | 0.1716 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 17 | Complete | 0.1676 | The requirement sufficiently describes the capability and conditions without needing further... |
| 18 | Design Independence | 0.1627 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 19 | Open-ended Terms | 0.1608 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 20 | Formal Syntax | 0.1513 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 21 | Singular | 0.149 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 22 | Loopholes | 0.1427 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 23 | Ambiguous Adjectives | 0.1315 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 24 | Subjective Language | 0.1248 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 25 | Vague Pronouns | 0.1144 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Unambiguous | 0.0999 | The requirement can be interpreted in only one way. It uses simple and concise language. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Verifiable | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ช่องทางการแจ้งเตือน (อีเมล, การแจ้งเตือนในแอปพลิเคชัน, SMS) และความถี่ในการแจ้งเตือน

**Conforming**
- **Normal:** ไม่ระบุว่าใช้เทมเพลตหรือสไตล์ใดในการเขียน
- **RAG:** The requirement does not use a standard template or style (e.g., EARS). It also lacks the use of 'shall' to denote a binding requirement.

**Unambiguous**
- **Normal:** คำว่า 'เกิน' อาจตีความได้หลายแบบ เช่น เกิน 100.01% หรือเกิน 100.000001%

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์ที่วัดได้ เช่น วิธีการคำนวณการใช้จ่ายเทียบกับงบประมาณ และวิธีการตรวจสอบการแจ้งเตือน

---

## REQ-12 — -
> ระบบต้องรีเซ็ตงบประมาณให้เป็นค่าเริ่มต้นทุกวันที่ 1 ของเดือนใหม่อัตโนมัติ

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3567 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Correct | 0.2751 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 3 | Conforming | 0.2473 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 4 | Positive Phrasing | 0.2444 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 5 | Unambiguous | 0.2386 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 6 | Modal Verb 'Shall' | 0.2192 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 7 | Formal Syntax | 0.2189 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 8 | Measurable Conditions | 0.2155 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 9 | Appropriate | 0.2115 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 10 | Active Voice | 0.1929 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 11 | Complete | 0.1806 | The requirement sufficiently describes the capability and conditions without needing further... |
| 12 | Verifiable | 0.179 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 13 | System Performance | 0.175 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 14 | Avoid 'Shall be able to' | 0.1466 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 15 | Necessary | 0.1429 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 16 | Modal Verb 'Should' | 0.1279 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 17 | Design Independence | 0.1271 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 18 | Avoid 'Must' | 0.1215 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 19 | Singular | 0.0935 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 20 | Comparative Phrases | 0.0904 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 21 | Subjective Language | 0.0844 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 22 | Superlatives | 0.0728 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 23 | Ambiguous Adjectives | 0.0682 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 24 | Loopholes | 0.0591 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 25 | Open-ended Terms | 0.0459 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Vague Pronouns | 0.016 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุค่าเริ่มต้นของงบประมาณที่ต้องรีเซ็ต
- **RAG:** The requirement is missing details about the initial value of the budget after reset. It also doesn't specify what happens if the reset fails.

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 (ไม่มีส่วนประกอบที่จำเป็น เช่น เงื่อนไข, เกณฑ์การยอมรับ)
- **RAG:** The requirement does not use the standard 'shall' format. It is written in Thai and does not follow a defined template.

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผล เช่น 'งบประมาณจะถูกรีเซ็ตเป็นค่า X'
- **RAG:** The requirement is verifiable, but lacks specific criteria. For example, it doesn't specify how the reset is confirmed (e.g., by checking the budget value).

---

## REQ-13 — -
> ผู้ใช้สามารถโอนเงินจากกระเป๋าหลักเข้าสู่กระเป๋าเป้าหมายการออมได้

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3328 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Modal Verb 'Should' | 0.1897 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 3 | Positive Phrasing | 0.1772 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 4 | Appropriate | 0.1627 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 5 | Verifiable | 0.1556 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 6 | Design Independence | 0.1439 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 7 | Complete | 0.1327 | The requirement sufficiently describes the capability and conditions without needing further... |
| 8 | Subjective Language | 0.1127 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 9 | Correct | 0.1056 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 10 | Ambiguous Adjectives | 0.102 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 11 | Measurable Conditions | 0.098 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 12 | Avoid 'Shall be able to' | 0.0955 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 13 | Modal Verb 'Shall' | 0.0952 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 14 | Conforming | 0.0914 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 15 | Unambiguous | 0.0854 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 16 | Active Voice | 0.0829 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 17 | Necessary | 0.0825 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 18 | Singular | 0.0798 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 19 | Avoid 'Must' | 0.0774 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 20 | Formal Syntax | 0.0656 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 21 | System Performance | 0.0655 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 22 | Superlatives | 0.0478 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 23 | Loopholes | 0.0427 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Comparative Phrases | 0.0223 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 25 | Open-ended Terms | -0.0086 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Vague Pronouns | -0.0351 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น จำนวนเงินขั้นต่ำ/สูงสุด, ค่าธรรมเนียม, ข้อจำกัดอื่นๆ
- **RAG:** ไม่ระบุข้อมูลเพิ่มเติม เช่น จำนวนเงินขั้นต่ำ/สูงสุด, ค่าธรรมเนียม, หรือข้อจำกัดอื่นๆ ที่เกี่ยวข้องกับการโอนเงิน

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบที่กำหนด (เช่น EARS หรือ ISO 29148) เนื่องจากขาดข้อมูลเพิ่มเติมและรูปแบบที่ชัดเจน
- **RAG:** ไม่เป็นไปตามรูปแบบมาตรฐานที่กำหนด (เช่น EARS) และไม่ได้ใช้คำว่า 'shall' เพื่อแสดงถึงข้อกำหนดที่จำเป็น

**Unambiguous**
- **Normal:** อาจมีหลายวิธีในการตีความ เช่น 'กระเป๋าหลัก' และ 'กระเป๋าเป้าหมายการออม' หมายถึงอะไรกันแน่
- **RAG:** อาจมีการตีความได้หลายแบบ เช่น 'กระเป๋าหลัก' และ 'กระเป๋าเป้าหมายการออม' หมายถึงอะไรบ้าง, มีข้อจำกัดอะไรในการโอนเงินหรือไม่

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรงโดยไม่มีเกณฑ์ที่วัดได้ เช่น 'ผู้ใช้สามารถ' นั้นกว้างเกินไป ไม่มีการระบุเงื่อนไขความสำเร็จ
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรงโดยไม่มีเกณฑ์ที่วัดได้ เช่น จำนวนเงินขั้นต่ำ/สูงสุด, ระยะเวลาในการโอน, หรือข้อผิดพลาดที่ยอมรับได้

---

## REQ-14 — -
> ระบบต้องแสดงกราฟวงกลม (Pie Chart) เพื่อสรุปสัดส่วนค่าใช้จ่ายแบ่งตามหมวดหมู่

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Appropriate | 0.3459 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 2 | Feasible | 0.3172 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Formal Syntax | 0.2888 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 4 | Measurable Conditions | 0.2849 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 5 | System Performance | 0.2718 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 6 | Correct | 0.2714 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 7 | Conforming | 0.2708 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 8 | Design Independence | 0.2658 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 9 | Positive Phrasing | 0.2213 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 10 | Verifiable | 0.2132 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 11 | Complete | 0.179 | The requirement sufficiently describes the capability and conditions without needing further... |
| 12 | Unambiguous | 0.1776 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 13 | Modal Verb 'Shall' | 0.1316 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 14 | Open-ended Terms | 0.1138 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 15 | Active Voice | 0.1112 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 16 | Necessary | 0.1109 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 17 | Superlatives | 0.0872 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 18 | Avoid 'Shall be able to' | 0.0638 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 19 | Comparative Phrases | 0.0636 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 20 | Modal Verb 'Should' | 0.0635 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 21 | Singular | 0.0443 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 22 | Subjective Language | 0.0373 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 23 | Avoid 'Must' | 0.0199 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 24 | Vague Pronouns | 0.0161 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 25 | Ambiguous Adjectives | 0.0139 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 26 | Loopholes | -0.0169 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ข้อมูลอะไรที่จะนำมาแสดงในกราฟ, รูปแบบการแสดงผล (สี, ขนาด), การโต้ตอบกับกราฟ
- **RAG:** The requirement is not fully complete. It does not specify details such as: the data source for the pie chart, the update frequency, the level of detail for the categories, or any interactive features. More information is needed to fully understand the requirement.

**Conforming**
- **Normal:** ไม่ระบุว่าใช้ template หรือ style แบบใด
- **RAG:** The requirement is not written in a standard format. It lacks a 'shall' or similar modal verb to indicate a binding requirement. It also lacks a clear subject, action, object, and constraint structure.

**Unambiguous**
- **Normal:** คำว่า 'ระบบต้องแสดง' อาจตีความได้หลายแบบ เช่น ต้องแสดงตลอดเวลา หรือแสดงเมื่อผู้ใช้ต้องการ
- **RAG:** While the core concept is clear, the requirement is somewhat ambiguous. Terms like 'หมวดหมู่' (categories) could be interpreted differently depending on the context. The requirement could be more specific about the data to be displayed.

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผล เช่น ขนาดของกราฟ, ความถูกต้องของข้อมูลที่แสดง, เวลาในการแสดงผล
- **RAG:** The requirement is not easily verifiable. There are no measurable criteria. For example, it doesn't specify the required accuracy of the chart, the update frequency, or the acceptable rendering time. Without these, it's difficult to prove the requirement is met.

---

## REQ-15 — -
> ระบบต้องแสดงกราฟแท่งเปรียบเทียบรายรับและรายจ่ายในแต่ละเดือน

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Positive Phrasing | 0.3634 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 2 | Feasible | 0.3618 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Verifiable | 0.3356 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 4 | Measurable Conditions | 0.329 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 5 | Conforming | 0.3132 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 6 | Correct | 0.3064 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 7 | Appropriate | 0.281 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 8 | Formal Syntax | 0.2732 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 9 | System Performance | 0.2728 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 10 | Complete | 0.261 | The requirement sufficiently describes the capability and conditions without needing further... |
| 11 | Modal Verb 'Shall' | 0.2478 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 12 | Design Independence | 0.2395 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 13 | Unambiguous | 0.2213 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 14 | Modal Verb 'Should' | 0.1935 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 15 | Active Voice | 0.1889 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 16 | Open-ended Terms | 0.1726 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 17 | Singular | 0.1566 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 18 | Comparative Phrases | 0.145 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 19 | Avoid 'Shall be able to' | 0.1382 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 20 | Subjective Language | 0.1316 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 21 | Necessary | 0.1225 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 22 | Superlatives | 0.1211 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 23 | Avoid 'Must' | 0.1165 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 24 | Ambiguous Adjectives | 0.0953 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 25 | Loopholes | 0.0793 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 26 | Vague Pronouns | 0.0252 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น รูปแบบกราฟแท่ง, ข้อมูลที่ใช้ในการคำนวณ, ช่วงเวลาที่แสดง
- **RAG:** ไม่ระบุรายละเอียดของกราฟแท่ง เช่น จำนวนข้อมูลที่แสดง, รูปแบบกราฟ, สี, ขนาด, หรือการโต้ตอบกับกราฟ

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐานที่กำหนด (เช่น EARS หรือ ISO 29148) เนื่องจากขาดรายละเอียดที่จำเป็น
- **RAG:** ไม่ได้ใช้คำว่า 'shall' และไม่ได้อยู่ในรูปแบบที่กำหนด (เช่น EARS)

**Unambiguous**
- **Normal:** อาจมีการตีความได้หลายแบบ เช่น รูปแบบกราฟแท่ง, รายละเอียดข้อมูล
- **RAG:** คำว่า 'ระบบ' อาจไม่ชัดเจน และ 'รายรับและรายจ่าย' อาจต้องการคำจำกัดความเพิ่มเติม

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากขาดเกณฑ์การวัดผล เช่น ขนาดกราฟ, สี, รายละเอียดข้อมูลที่แสดง
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากไม่มีเกณฑ์วัดผล เช่น ความละเอียดของกราฟ, ช่วงเวลาที่แสดง, หรือรูปแบบการแสดงผล

---

## REQ-16 — -
> ผู้ใช้สามารถเปิด/ปิด การแจ้งเตือน (Push Notification) ของแอปพลิเคชันได้

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.2185 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Subjective Language | 0.1897 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 3 | Active Voice | 0.1764 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 4 | Appropriate | 0.1546 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 5 | Modal Verb 'Should' | 0.1514 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 6 | Unambiguous | 0.1415 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 7 | Verifiable | 0.1378 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 8 | System Performance | 0.1195 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 9 | Complete | 0.1138 | The requirement sufficiently describes the capability and conditions without needing further... |
| 10 | Design Independence | 0.1092 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 11 | Positive Phrasing | 0.1086 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 12 | Singular | 0.1037 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 13 | Avoid 'Shall be able to' | 0.0979 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 14 | Open-ended Terms | 0.0954 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 15 | Superlatives | 0.0943 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 16 | Loopholes | 0.0934 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 17 | Conforming | 0.068 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 18 | Vague Pronouns | 0.0655 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 19 | Measurable Conditions | 0.0576 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 20 | Ambiguous Adjectives | 0.0569 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 21 | Formal Syntax | 0.0446 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 22 | Necessary | 0.0372 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 23 | Avoid 'Must' | 0.0346 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 24 | Comparative Phrases | 0.0251 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 25 | Modal Verb 'Shall' | 0.0234 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 26 | Correct | 0.0164 | The requirement is an accurate representation of the entity need from which it was transformed. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น สถานะเริ่มต้นของการแจ้งเตือน (เปิดหรือปิด) และวิธีการที่ผู้ใช้จะเปิด/ปิดการแจ้งเตือน
- **RAG:** ไม่ระบุว่าผู้ใช้สามารถเปิด/ปิดการแจ้งเตือนได้ในรูปแบบใด (เช่น ผ่านการตั้งค่าในแอปพลิเคชัน) และไม่มีเงื่อนไขเพิ่มเติม เช่น การแจ้งเตือนประเภทใดบ้างที่สามารถเปิด/ปิดได้

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน (เช่น EARS หรือ ISO 29148) เนื่องจากขาดรายละเอียดที่จำเป็น
- **RAG:** ไม่เป็นไปตามรูปแบบมาตรฐาน (เช่น EARS) และไม่มีการใช้คำว่า 'shall' หรือ 'should' อย่างถูกต้อง

**Unambiguous**
- **RAG:** อาจตีความได้หลายแบบ เช่น 'การแจ้งเตือน' หมายถึงการแจ้งเตือนทั้งหมดหรือเฉพาะบางประเภท

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผลที่ชัดเจน เช่น จะตรวจสอบได้อย่างไรว่าการเปิด/ปิดการแจ้งเตือนทำงานได้ถูกต้อง
- **RAG:** ไม่ระบุเกณฑ์ที่วัดผลได้ เช่น 'ผู้ใช้สามารถเปิด/ปิดการแจ้งเตือนได้ภายใน X วินาที' หรือ 'การแจ้งเตือนจะถูกส่งเมื่อเปิดใช้งาน' 

---

## REQ-17 — -
> ระบบต้องรองรับการเปลี่ยนธีม (Dark Mode / Light Mode)

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Positive Phrasing | 0.2771 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 2 | Appropriate | 0.2686 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 3 | System Performance | 0.2624 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 4 | Feasible | 0.2502 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 5 | Complete | 0.2442 | The requirement sufficiently describes the capability and conditions without needing further... |
| 6 | Unambiguous | 0.2437 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 7 | Singular | 0.2323 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 8 | Active Voice | 0.2285 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 9 | Conforming | 0.2262 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 10 | Design Independence | 0.2106 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 11 | Necessary | 0.1826 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 12 | Subjective Language | 0.1736 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 13 | Avoid 'Shall be able to' | 0.1713 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 14 | Ambiguous Adjectives | 0.1685 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 15 | Correct | 0.163 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 16 | Modal Verb 'Shall' | 0.1587 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 17 | Avoid 'Must' | 0.1499 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 18 | Loopholes | 0.1456 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 19 | Measurable Conditions | 0.1425 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 20 | Open-ended Terms | 0.1423 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 21 | Formal Syntax | 0.1402 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 22 | Modal Verb 'Should' | 0.1315 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 23 | Comparative Phrases | 0.1281 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 24 | Superlatives | 0.1017 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 25 | Verifiable | 0.0817 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 26 | Vague Pronouns | 0.0817 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น วิธีการเปลี่ยนธีม (ปุ่ม, การตั้งค่า), ขอบเขตของธีม (ทั้งระบบ, บางส่วน), และการคงอยู่ของธีม (จำค่าไว้หรือไม่)
- **RAG:** Requirement ไม่ได้ระบุรายละเอียดเพิ่มเติม เช่น วิธีการเปลี่ยนธีม (เช่น ผ่านการตั้งค่า, ปุ่ม, ฯลฯ) หรือขอบเขตของธีม (เช่น เปลี่ยนเฉพาะ UI หรือรวมถึงเนื้อหาด้วย)

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 (ไม่มีส่วนประกอบที่จำเป็น เช่น ที่มา, เหตุผล)
- **RAG:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 เนื่องจากไม่ได้ใช้คำว่า 'shall' หรือรูปแบบที่ชัดเจนในการระบุข้อกำหนด

**Unambiguous**
- **Normal:** คำว่า 'รองรับ' ไม่ชัดเจนว่าหมายถึงอะไร (เช่น ต้องมีปุ่มให้เลือก, เปลี่ยนอัตโนมัติ)
- **RAG:** คำว่า 'ระบบต้องรองรับ' อาจตีความได้หลายแบบ ควรระบุให้ชัดเจนว่าระบบจะต้องทำอะไร

**Verifiable**
- **Normal:** ไม่มีเกณฑ์การวัดผล เช่น 'ระบบต้องเปลี่ยนธีมได้ภายใน X วินาที' หรือ 'ธีมต้องเปลี่ยนสีขององค์ประกอบ Y'
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรง ต้องมีการระบุเกณฑ์การวัดผล เช่น วิธีการเปลี่ยนธีม, UI ที่เปลี่ยนไป, หรือการทดสอบ

---

## REQ-18 — -
> ผู้ใช้งานต้องสามารถลบข้อมูลธุรกรรมทั้งหมด (Clear Data) ได้โดยต้องมีการยืนยันรหัสผ่านก่อน

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Necessary | 0.2425 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 2 | Unambiguous | 0.2269 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 3 | Complete | 0.1999 | The requirement sufficiently describes the capability and conditions without needing further... |
| 4 | Feasible | 0.19 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 5 | Modal Verb 'Shall' | 0.1542 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 6 | Singular | 0.152 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 7 | Subjective Language | 0.1497 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 8 | Correct | 0.1478 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 9 | Verifiable | 0.1419 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 10 | Avoid 'Must' | 0.1341 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 11 | System Performance | 0.1279 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 12 | Measurable Conditions | 0.1231 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 13 | Design Independence | 0.1006 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 14 | Conforming | 0.0901 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 15 | Appropriate | 0.0872 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 16 | Comparative Phrases | 0.0848 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 17 | Positive Phrasing | 0.077 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 18 | Active Voice | 0.0759 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 19 | Avoid 'Shall be able to' | 0.0672 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 20 | Superlatives | 0.0632 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 21 | Modal Verb 'Should' | 0.0437 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 22 | Loopholes | 0.0416 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 23 | Formal Syntax | 0.033 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 24 | Vague Pronouns | 0.0169 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 25 | Ambiguous Adjectives | 0.0024 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 26 | Open-ended Terms | -0.0621 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเกี่ยวกับการยืนยันรหัสผ่าน เช่น จำนวนครั้งที่ผิดพลาดสูงสุด, ระยะเวลาที่ต้องรอหลังใส่รหัสผ่านผิด, หรือวิธีการแสดงผลเมื่อลบข้อมูลสำเร็จ/ล้มเหลว

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 อย่างชัดเจน (เช่น ไม่มีส่วนหัว, ข้อมูลจำเพาะเพิ่มเติม)
- **RAG:** The requirement does not use a standard template or syntax. It lacks a subject and uses informal language. Consider using 'The user shall be able to...' to conform to a standard.

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์ที่วัดผลได้ เช่น ไม่ได้ระบุว่าการลบข้อมูลทั้งหมดหมายถึงอะไร (เช่น ลบข้อมูลในระยะเวลาเท่าไหร่) หรือวิธีการตรวจสอบการลบข้อมูลสำเร็จ

---

## REQ-19 — -
> รหัสผ่านของผู้ใช้งานต้องถูกเข้ารหัส (Encryption) ด้วยมาตรฐาน SHA-256 หรือดีกว่า ก่อนบันทึกลงฐานข้อมูล

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Modal Verb 'Shall' | 0.2227 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 2 | Complete | 0.1819 | The requirement sufficiently describes the capability and conditions without needing further... |
| 3 | Necessary | 0.1817 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 4 | Measurable Conditions | 0.1812 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 5 | Conforming | 0.1801 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 6 | Comparative Phrases | 0.1689 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 7 | System Performance | 0.1514 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 8 | Subjective Language | 0.1486 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 9 | Unambiguous | 0.1457 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 10 | Avoid 'Must' | 0.1341 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 11 | Formal Syntax | 0.1175 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 12 | Design Independence | 0.099 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 13 | Singular | 0.097 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 14 | Verifiable | 0.0965 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 15 | Appropriate | 0.0908 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 16 | Positive Phrasing | 0.0893 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 17 | Feasible | 0.0872 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 18 | Correct | 0.0867 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 19 | Superlatives | 0.0795 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 20 | Avoid 'Shall be able to' | 0.0548 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 21 | Ambiguous Adjectives | 0.0487 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 22 | Active Voice | 0.0411 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 23 | Loopholes | 0.0007 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Vague Pronouns | -0.027 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 25 | Open-ended Terms | -0.0315 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Modal Verb 'Should' | -0.0422 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **4/9** | Appropriate, Correct, Feasible, Necessary |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Unambiguous | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Verifiable | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |

### Failed Reasons
**Complete**
- **RAG:** ไม่ระบุวิธีการเข้ารหัส (เช่น salt, iteration) ซึ่งอาจส่งผลต่อความปลอดภัยและความสมบูรณ์ของการเข้ารหัส

**Conforming**
- **Normal:** ไม่ได้ระบุรูปแบบการเขียนที่ชัดเจน (เช่น EARS) แต่โดยรวมแล้วเข้าใจได้
- **RAG:** ไม่ใช้คำว่า 'shall' เพื่อแสดงถึงข้อกำหนดที่จำเป็น (Rule 1)

**Singular**
- **RAG:** ใช้คำว่า 'หรือดีกว่า' ซึ่งเป็นการระบุทางเลือก (Rule 13)

**Unambiguous**
- **RAG:** คำว่า 'หรือดีกว่า' อาจตีความได้หลายแบบ (Rule 9, Rule 6)

**Verifiable**
- **RAG:** ไม่ระบุเกณฑ์ที่วัดได้สำหรับ 'ดีกว่า' (Rule 14, Rule 6)

---

## REQ-2 — -
> ระบบต้องมีฟังก์ชัน "ลืมรหัสผ่าน" โดยส่งลิงก์รีเซ็ตไปที่อีเมลของผู้ใช้งาน

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Necessary | 0.1831 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 2 | Subjective Language | 0.1584 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 3 | Feasible | 0.1269 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 4 | Unambiguous | 0.1252 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 5 | Active Voice | 0.1047 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 6 | Complete | 0.1019 | The requirement sufficiently describes the capability and conditions without needing further... |
| 7 | System Performance | 0.0969 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 8 | Modal Verb 'Shall' | 0.0903 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 9 | Avoid 'Shall be able to' | 0.0859 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 10 | Avoid 'Must' | 0.0783 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 11 | Positive Phrasing | 0.0754 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 12 | Singular | 0.0731 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 13 | Modal Verb 'Should' | 0.0671 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 14 | Comparative Phrases | 0.0565 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 15 | Correct | 0.0369 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 16 | Appropriate | 0.0357 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 17 | Design Independence | 0.0333 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 18 | Conforming | 0.0272 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 19 | Loopholes | 0.0244 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 20 | Ambiguous Adjectives | 0.021 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 21 | Verifiable | 0.0209 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 22 | Measurable Conditions | 0.0054 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 23 | Formal Syntax | 0.0048 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 24 | Superlatives | -0.0045 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 25 | Vague Pronouns | -0.0166 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Open-ended Terms | -0.0811 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น: รูปแบบของลิงก์รีเซ็ต, ระยะเวลาที่ลิงก์ใช้งานได้, การจัดการกรณีที่อีเมลไม่ถูกต้อง, การแจ้งเตือนเมื่อมีการรีเซ็ตรหัสผ่าน
- **RAG:** ไม่ระบุรายละเอียด เช่น: ระบบต้องมีฟังก์ชัน 'ลืมรหัสผ่าน' โดยส่งลิงก์รีเซ็ตไปที่อีเมลของผู้ใช้งาน พร้อมระบุระยะเวลาที่ลิงก์ใช้งานได้, รูปแบบของลิงก์, และการแจ้งเตือนเมื่อมีการรีเซ็ต

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 อย่างชัดเจน (เช่น ไม่มีส่วนหัว, ข้อมูลจำเพาะเพิ่มเติม)
- **RAG:** ไม่เป็นไปตามรูปแบบมาตรฐานของ ISO 29148 (เช่น การใช้คำว่า 'ต้องมี' แทน 'shall')

**Unambiguous**
- **Normal:** อาจมีการตีความได้หลายแบบ เช่น รูปแบบของลิงก์, วิธีการส่งอีเมล
- **RAG:** คำว่า 'ระบบ' และ 'ผู้ใช้งาน' อาจมีความคลุมเครือได้ ควรระบุให้ชัดเจนยิ่งขึ้น

**Verifiable**
- **Normal:** ไม่มีเกณฑ์ที่วัดผลได้ เช่น ไม่ได้ระบุว่าการส่งอีเมลต้องใช้เวลาเท่าไหร่ หรือต้องมีอัตราความสำเร็จเท่าไหร่
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรง ต้องมีการระบุเกณฑ์การวัดผล เช่น: ระบบต้องส่งอีเมลภายใน X วินาที, ลิงก์รีเซ็ตต้องใช้งานได้ภายใน Y นาที

---

## REQ-20 — -
> การรับส่งข้อมูลระหว่างแอปพลิเคชันและเซิร์ฟเวอร์ต้องทำผ่านโปรโตคอล HTTPS ทั้งหมด

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Conforming | 0.3116 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 2 | System Performance | 0.2836 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 3 | Unambiguous | 0.2028 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 4 | Complete | 0.18 | The requirement sufficiently describes the capability and conditions without needing further... |
| 5 | Design Independence | 0.1755 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 6 | Appropriate | 0.1626 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 7 | Feasible | 0.1618 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 8 | Modal Verb 'Shall' | 0.1477 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 9 | Correct | 0.1335 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 10 | Singular | 0.1307 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 11 | Formal Syntax | 0.1217 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 12 | Vague Pronouns | 0.1044 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 13 | Necessary | 0.0891 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 14 | Verifiable | 0.0769 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 15 | Avoid 'Must' | 0.0664 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 16 | Avoid 'Shall be able to' | 0.0555 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 17 | Active Voice | 0.05 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 18 | Measurable Conditions | 0.0477 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 19 | Superlatives | 0.0253 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 20 | Positive Phrasing | 0.0242 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 21 | Subjective Language | 0.0062 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 22 | Open-ended Terms | 0.0053 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 23 | Comparative Phrases | -0.0212 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 24 | Modal Verb 'Should' | -0.0227 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 25 | Loopholes | -0.0682 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 26 | Ambiguous Adjectives | -0.0849 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ✅ PASS |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Conforming**
- **Normal:** ไม่เป็นไปตามเทมเพลตหรือสไตล์ที่ระบุ (ISO 29148) เนื่องจากไม่ได้ระบุรูปแบบที่ชัดเจน
- **RAG:** The requirement does not use a standard template or style. It also does not use the modal verb 'shall' as recommended by ISO 29148.

---

## REQ-21 — -
> ระบบต้องทำการ Logout อัตโนมัติ (Session Timeout) หากผู้ใช้ไม่มีการใช้งานเกิน 15 นาที

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3967 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | System Performance | 0.2711 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 3 | Complete | 0.2609 | The requirement sufficiently describes the capability and conditions without needing further... |
| 4 | Necessary | 0.2477 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 5 | Modal Verb 'Shall' | 0.2137 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 6 | Appropriate | 0.2041 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 7 | Measurable Conditions | 0.1961 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 8 | Design Independence | 0.1929 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 9 | Verifiable | 0.191 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 10 | Conforming | 0.178 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 11 | Avoid 'Shall be able to' | 0.1738 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 12 | Active Voice | 0.1696 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 13 | Correct | 0.1643 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 14 | Modal Verb 'Should' | 0.1634 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 15 | Superlatives | 0.1616 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 16 | Positive Phrasing | 0.1601 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 17 | Avoid 'Must' | 0.1531 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 18 | Unambiguous | 0.1475 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 19 | Subjective Language | 0.1347 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 20 | Singular | 0.132 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 21 | Formal Syntax | 0.1154 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 22 | Ambiguous Adjectives | 0.1032 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 23 | Loopholes | 0.0953 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Comparative Phrases | 0.056 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 25 | Vague Pronouns | 0.0282 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Open-ended Terms | -0.0003 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **7/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Complete**
- **Normal:** ขาดรายละเอียดว่าระบบจะทำอย่างไรเมื่อทำการ Logout (เช่น แสดงข้อความอะไร, ไปหน้าไหน)

**Conforming**
- **Normal:** ไม่ได้ระบุรูปแบบการเขียน requirement ที่ชัดเจน (เช่น EARS)
- **RAG:** The requirement does not use a standard template or style. It also does not use the modal verb 'shall' as recommended by ISO 29148.

---

## REQ-22 — -
> แอปพลิเคชันต้องใช้เวลาในการโหลดหน้า Dashboard ไม่เกิน 2 วินาที (ภายใต้สัญญาณอินเทอร์เน็ต 4G ปกติ)

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3226 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Complete | 0.2198 | The requirement sufficiently describes the capability and conditions without needing further... |
| 3 | Conforming | 0.1616 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 4 | System Performance | 0.1581 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 5 | Superlatives | 0.1424 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 6 | Unambiguous | 0.1314 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 7 | Appropriate | 0.0995 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 8 | Subjective Language | 0.0987 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 9 | Verifiable | 0.0971 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 10 | Design Independence | 0.0893 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 11 | Ambiguous Adjectives | 0.0818 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 12 | Singular | 0.076 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 13 | Modal Verb 'Should' | 0.0635 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 14 | Avoid 'Shall be able to' | 0.0591 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 15 | Measurable Conditions | 0.0401 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 16 | Necessary | 0.03 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 17 | Active Voice | 0.0249 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 18 | Formal Syntax | 0.0109 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 19 | Correct | 0.001 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 20 | Positive Phrasing | -0.0065 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 21 | Comparative Phrases | -0.0101 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 22 | Loopholes | -0.0103 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 23 | Modal Verb 'Shall' | -0.0159 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 24 | Open-ended Terms | -0.0262 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 25 | Vague Pronouns | -0.0411 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Avoid 'Must' | -0.0581 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **9/9** | Appropriate, Complete, Conforming, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ✅ PASS |  |
| Conforming | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Conforming**
- **Normal:** ไม่ได้ระบุรูปแบบการเขียนที่ชัดเจน (เช่น EARS)

---

## REQ-23 — -
> แอปพลิเคชันต้องสามารถติดตั้งและใช้งานได้บน iOS เวอร์ชัน 15 ขึ้นไป

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Design Independence | 0.2325 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 2 | Feasible | 0.172 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Appropriate | 0.1338 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 4 | Necessary | 0.123 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 5 | Complete | 0.1225 | The requirement sufficiently describes the capability and conditions without needing further... |
| 6 | Verifiable | 0.1187 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 7 | Conforming | 0.1159 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 8 | System Performance | 0.1151 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 9 | Modal Verb 'Shall' | 0.0996 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 10 | Unambiguous | 0.0915 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 11 | Singular | 0.0863 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 12 | Correct | 0.0758 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 13 | Avoid 'Must' | 0.073 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 14 | Avoid 'Shall be able to' | 0.0693 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 15 | Active Voice | 0.0636 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 16 | Positive Phrasing | 0.0547 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 17 | Formal Syntax | 0.0453 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 18 | Measurable Conditions | 0.043 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 19 | Loopholes | 0.0322 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 20 | Subjective Language | 0.0183 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 21 | Ambiguous Adjectives | 0.0129 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 22 | Vague Pronouns | 0.0097 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 23 | Open-ended Terms | 0.007 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 24 | Superlatives | 0.0006 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 25 | Modal Verb 'Should' | -0.004 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 26 | Comparative Phrases | -0.0428 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ✅ PASS |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Conforming**
- **Normal:** ไม่เป็นไปตามเทมเพลตหรือสไตล์ที่ระบุ (ISO 29148) เนื่องจากไม่ได้ระบุรูปแบบการเขียนที่ชัดเจน
- **RAG:** The requirement does not use a standard format or syntax. It should use 'shall' to denote a binding requirement. (Rule 7, 9)

---

## REQ-24 — -
> แอปพลิเคชันต้องสามารถติดตั้งและใช้งานได้บน Android เวอร์ชัน 10 ขึ้นไป

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.1916 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Design Independence | 0.1805 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 3 | Verifiable | 0.1337 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 4 | Conforming | 0.1296 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 5 | Appropriate | 0.1186 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 6 | Complete | 0.0959 | The requirement sufficiently describes the capability and conditions without needing further... |
| 7 | Unambiguous | 0.094 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 8 | Modal Verb 'Shall' | 0.0856 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 9 | Correct | 0.0706 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 10 | Necessary | 0.0585 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 11 | System Performance | 0.0576 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 12 | Measurable Conditions | 0.0522 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 13 | Singular | 0.0505 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 14 | Active Voice | 0.0365 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 15 | Avoid 'Must' | 0.0327 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 16 | Formal Syntax | 0.0272 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 17 | Modal Verb 'Should' | 0.0209 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 18 | Loopholes | 0.0107 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 19 | Avoid 'Shall be able to' | 0.0038 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 20 | Positive Phrasing | 0.0015 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 21 | Subjective Language | 0.0006 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 22 | Superlatives | 0.0001 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 23 | Vague Pronouns | -0.0177 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 24 | Open-ended Terms | -0.0307 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 25 | Ambiguous Adjectives | -0.0375 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 26 | Comparative Phrases | -0.0387 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **9/9** | Appropriate, Complete, Conforming, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ✅ PASS |  |
| Conforming | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Conforming**
- **Normal:** ไม่เป็นไปตามเทมเพลตหรือสไตล์ที่ระบุ (ISO 29148) เนื่องจากไม่ได้ระบุรูปแบบการเขียนที่ชัดเจน

---

## REQ-25 — -
> ระบบต้องทำการสำรองข้อมูล (Backup) ของผู้ใช้งานทุกวันเวลา 03:00 น.

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3686 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | System Performance | 0.2984 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 3 | Conforming | 0.2795 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 4 | Correct | 0.2401 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 5 | Positive Phrasing | 0.2245 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 6 | Verifiable | 0.22 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 7 | Modal Verb 'Shall' | 0.2168 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 8 | Complete | 0.2147 | The requirement sufficiently describes the capability and conditions without needing further... |
| 9 | Measurable Conditions | 0.1794 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 10 | Necessary | 0.1622 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 11 | Formal Syntax | 0.1609 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 12 | Unambiguous | 0.1447 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 13 | Avoid 'Shall be able to' | 0.137 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 14 | Appropriate | 0.137 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 15 | Active Voice | 0.1348 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 16 | Design Independence | 0.1014 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 17 | Modal Verb 'Should' | 0.094 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 18 | Singular | 0.088 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 19 | Avoid 'Must' | 0.073 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 20 | Subjective Language | 0.0682 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 21 | Superlatives | 0.0253 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 22 | Ambiguous Adjectives | 0.0093 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 23 | Loopholes | -0.0019 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Comparative Phrases | -0.0048 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 25 | Vague Pronouns | -0.0099 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Open-ended Terms | -0.0594 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **7/9** | Appropriate, Conforming, Correct, Feasible, Necessary, Singular, Unambiguous |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น สถานที่เก็บข้อมูลสำรอง, ประเภทการสำรองข้อมูล (Full, Incremental), การแจ้งเตือนเมื่อสำรองข้อมูลสำเร็จ/ล้มเหลว
- **RAG:** Requirement ไม่ได้ระบุรายละเอียดเกี่ยวกับวิธีการสำรองข้อมูล (เช่น ประเภทของการสำรองข้อมูล, ที่เก็บข้อมูล) ซึ่งอาจทำให้เกิดความไม่ชัดเจน

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 (ไม่มีการระบุที่มา, ผู้เขียน, วันที่, สถานะ)

**Unambiguous**
- **Normal:** คำว่า 'ระบบ' และ 'ข้อมูลผู้ใช้งาน' ยังคลุมเครือ ต้องระบุให้ชัดเจนกว่านี้

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรง ต้องมีเกณฑ์การวัดผล เช่น จำนวนข้อมูลที่สำรอง, ระยะเวลาในการสำรอง, ความสำเร็จในการสำรองข้อมูล
- **RAG:** ไม่สามารถตรวจสอบได้โดยตรงว่าการสำรองข้อมูลสำเร็จหรือไม่โดยไม่มีเกณฑ์การวัดที่ชัดเจน เช่น จำนวนข้อมูลที่สำรอง, ระยะเวลาในการสำรอง, หรือการตรวจสอบความถูกต้องของข้อมูลที่สำรอง

---

## REQ-26 — -
> ระบบต้องไม่อนุญาตให้ผู้ใช้บันทึกวันที่ในอนาคต (Future Date) เกินกว่า 1 ปี

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Modal Verb 'Shall' | 0.3443 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 2 | Positive Phrasing | 0.3371 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 3 | System Performance | 0.3297 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 4 | Avoid 'Must' | 0.3253 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 5 | Feasible | 0.3089 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 6 | Avoid 'Shall be able to' | 0.2932 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 7 | Singular | 0.2701 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 8 | Active Voice | 0.263 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 9 | Measurable Conditions | 0.2582 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 10 | Appropriate | 0.2563 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 11 | Open-ended Terms | 0.2562 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 12 | Unambiguous | 0.2469 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 13 | Comparative Phrases | 0.2452 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 14 | Design Independence | 0.2401 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 15 | Complete | 0.2303 | The requirement sufficiently describes the capability and conditions without needing further... |
| 16 | Verifiable | 0.2201 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 17 | Conforming | 0.206 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 18 | Loopholes | 0.2059 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 19 | Necessary | 0.1933 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 20 | Vague Pronouns | 0.1922 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 21 | Correct | 0.1808 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 22 | Modal Verb 'Should' | 0.1764 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 23 | Formal Syntax | 0.1726 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 24 | Subjective Language | 0.1639 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 25 | Superlatives | 0.1593 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 26 | Ambiguous Adjectives | 0.0894 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ✅ PASS | ✅ PASS |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Conforming**
- **Normal:** ไม่ได้ระบุรูปแบบการเขียน (template) ที่ใช้
- **RAG:** The requirement uses negative phrasing ('ไม่อนุญาต') which is discouraged (Rule 2). It should be rephrased to a positive statement.

---

## REQ-27 — -
> ในกรณีที่ Login ผิดเกิน 5 ครั้ง ระบบต้องระงับบัญชีชั่วคราวเป็นเวลา 30 นาที

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Necessary | 0.2458 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 2 | Feasible | 0.1967 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Modal Verb 'Shall' | 0.1615 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 4 | Verifiable | 0.1373 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 5 | Complete | 0.1357 | The requirement sufficiently describes the capability and conditions without needing further... |
| 6 | Measurable Conditions | 0.1337 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 7 | System Performance | 0.1213 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 8 | Avoid 'Must' | 0.1181 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 9 | Positive Phrasing | 0.118 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 10 | Modal Verb 'Should' | 0.1075 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 11 | Subjective Language | 0.1055 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 12 | Correct | 0.1015 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 13 | Active Voice | 0.1012 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 14 | Avoid 'Shall be able to' | 0.09 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 15 | Ambiguous Adjectives | 0.0805 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 16 | Unambiguous | 0.0679 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 17 | Appropriate | 0.0676 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 18 | Superlatives | 0.0641 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 19 | Comparative Phrases | 0.0634 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 20 | Singular | 0.056 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 21 | Loopholes | 0.0544 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 22 | Design Independence | 0.0398 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 23 | Formal Syntax | 0.0349 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 24 | Conforming | 0.0293 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 25 | Vague Pronouns | -0.0493 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 26 | Open-ended Terms | -0.0557 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **7/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |
| RAG    | **8/9** | Appropriate, Complete, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ✅ PASS | ⬆ RAG more lenient |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ✅ PASS | ✅ PASS |  |

### Failed Reasons
**Complete**
- **Normal:** ขาดข้อมูลเกี่ยวกับวิธีการระงับบัญชี (เช่น การส่งอีเมลแจ้งเตือน, การแสดงข้อความบนหน้าจอ) และสิ่งที่เกิดขึ้นเมื่อผู้ใช้พยายาม Login ในช่วงเวลาระงับ

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน (เช่น EARS หรือ ISO 29148) ที่ระบุไว้
- **RAG:** The requirement does not use a standard template or style (e.g., EARS). It lacks a subject and uses informal language. It does not use 'shall'.

---

## REQ-28 — -
> กราฟเส้นแสดงแนวโน้มการเงินต้องอัปเดตแบบ Real-time ทันทีที่มีการบันทึกข้อมูล

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Correct | 0.3075 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 2 | Feasible | 0.3058 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Measurable Conditions | 0.2456 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 4 | Verifiable | 0.2284 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 5 | Conforming | 0.2114 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 6 | Positive Phrasing | 0.177 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 7 | Complete | 0.1672 | The requirement sufficiently describes the capability and conditions without needing further... |
| 8 | Modal Verb 'Shall' | 0.1573 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 9 | Formal Syntax | 0.1528 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 10 | Active Voice | 0.1224 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 11 | System Performance | 0.1084 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 12 | Appropriate | 0.1054 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 13 | Unambiguous | 0.103 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 14 | Avoid 'Shall be able to' | 0.0953 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 15 | Open-ended Terms | 0.0926 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 16 | Superlatives | 0.092 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 17 | Design Independence | 0.0809 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 18 | Modal Verb 'Should' | 0.0764 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 19 | Subjective Language | 0.0704 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 20 | Necessary | 0.0578 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 21 | Comparative Phrases | 0.0548 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 22 | Avoid 'Must' | 0.0383 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 23 | Singular | 0.0206 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 24 | Vague Pronouns | 0.0135 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 25 | Loopholes | -0.0038 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 26 | Ambiguous Adjectives | -0.0278 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ขาดรายละเอียดเกี่ยวกับความถี่ในการอัปเดต, ความเร็วในการแสดงผล, และข้อมูลที่แสดงบนกราฟ
- **RAG:** ไม่ระบุรายละเอียดที่เพียงพอ เช่น ความถี่ในการอัปเดต (เช่น ทุกๆ กี่วินาที) หรือเกณฑ์การวัด 'ทันที' (เช่น ภายในกี่วินาที)

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 (ไม่มีการระบุที่มา, ผู้เขียน, วันที่, หรือรายละเอียดอื่นๆ ที่จำเป็น)
- **RAG:** ไม่เป็นไปตามรูปแบบหรือสไตล์ที่อนุมัติ (เช่น EARS, ISO29148) เนื่องจากไม่ได้ใช้คำว่า 'จะต้อง' (shall) หรือรูปแบบที่ชัดเจน

**Unambiguous**
- **Normal:** คำว่า 'ทันที' ไม่ชัดเจน ต้องระบุเวลาที่แน่นอน
- **RAG:** คำว่า 'ทันที' อาจตีความได้หลายแบบ จำเป็นต้องระบุเกณฑ์ที่ชัดเจนกว่านี้

**Verifiable**
- **Normal:** ไม่มีเกณฑ์ที่วัดผลได้ เช่น ความล่าช้าสูงสุดในการอัปเดต, ความถี่ในการอัปเดต, หรือความถูกต้องของข้อมูลที่แสดง
- **RAG:** ไม่สามารถพิสูจน์หรือตรวจสอบได้โดยตรง เนื่องจากไม่มีเกณฑ์การวัดที่ชัดเจนสำหรับ 'Real-time' และ 'ทันที'

---

## REQ-3 — -
> ระบบต้องรองรับการเข้าสู่ระบบด้วย Biometric (สแกนนิ้วหรือใบหน้า) บนอุปกรณ์มือถือ

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Verifiable | 0.3301 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 2 | Feasible | 0.2777 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Complete | 0.2409 | The requirement sufficiently describes the capability and conditions without needing further... |
| 4 | Measurable Conditions | 0.2398 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 5 | Active Voice | 0.2328 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 6 | Design Independence | 0.2299 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 7 | System Performance | 0.2292 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 8 | Positive Phrasing | 0.2231 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 9 | Conforming | 0.2154 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 10 | Correct | 0.214 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 11 | Necessary | 0.2114 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 12 | Modal Verb 'Shall' | 0.2106 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 13 | Appropriate | 0.186 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 14 | Unambiguous | 0.1694 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 15 | Formal Syntax | 0.1669 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 16 | Avoid 'Shall be able to' | 0.1493 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 17 | Singular | 0.1345 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 18 | Subjective Language | 0.1284 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 19 | Modal Verb 'Should' | 0.1246 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 20 | Avoid 'Must' | 0.1025 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 21 | Comparative Phrases | 0.0835 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 22 | Loopholes | 0.0543 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 23 | Vague Pronouns | 0.0467 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 24 | Ambiguous Adjectives | 0.0312 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 25 | Open-ended Terms | 0.0113 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Superlatives | -0.0097 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **4/9** | Appropriate, Correct, Feasible, Necessary |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ประเภทของ Biometric ที่รองรับ (สแกนนิ้ว, ใบหน้า, หรือทั้งสองอย่าง), ความแม่นยำที่ต้องการ, หรือการจัดการข้อผิดพลาด
- **RAG:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ประเภทของอุปกรณ์มือถือที่รองรับ, ความแม่นยำในการสแกน, หรือการตอบสนองต่อความผิดพลาด

**Conforming**
- **Normal:** ไม่ระบุรูปแบบการเขียนที่ชัดเจน (เช่น EARS) หรือใช้เทมเพลตที่กำหนดไว้
- **RAG:** ไม่ใช้คำว่า 'shall' หรือคำที่คล้ายกันเพื่อระบุข้อกำหนดที่จำเป็น

**Singular**
- **RAG:** ระบุการรองรับทั้งการสแกนนิ้วและใบหน้า ซึ่งอาจพิจารณาเป็นสองข้อกำหนดแยกกันได้

**Unambiguous**
- **Normal:** อาจมีการตีความได้หลายแบบ เช่น 'อุปกรณ์มือถือ' หมายถึงอุปกรณ์ใดบ้าง, 'รองรับ' หมายถึงอย่างไร (เช่น รองรับทุกรุ่น, รองรับบางรุ่น)
- **RAG:** คำว่า 'ระบบ' อาจไม่ชัดเจนว่าหมายถึงส่วนใดของระบบ

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผล เช่น ความเร็วในการเข้าสู่ระบบ, อัตราความสำเร็จในการยืนยันตัวตน, หรือจำนวนครั้งที่ผู้ใช้สามารถลองเข้าสู่ระบบได้
- **RAG:** ไม่ระบุเกณฑ์ที่วัดผลได้ เช่น เวลาในการตรวจสอบสิทธิ์, อัตราการยอมรับ, หรือความปลอดภัย

---

## REQ-4 — -
> ผู้ใช้ต้องสามารถออกจากระบบ (Logout) ได้จากทุกหน้าจอ

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.2585 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Complete | 0.1697 | The requirement sufficiently describes the capability and conditions without needing further... |
| 3 | Active Voice | 0.1669 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 4 | System Performance | 0.1656 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 5 | Necessary | 0.1576 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 6 | Unambiguous | 0.1567 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 7 | Verifiable | 0.1388 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 8 | Singular | 0.1379 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 9 | Correct | 0.1378 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 10 | Design Independence | 0.1284 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 11 | Appropriate | 0.1234 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 12 | Avoid 'Shall be able to' | 0.1158 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 13 | Positive Phrasing | 0.1091 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 14 | Measurable Conditions | 0.1072 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 15 | Modal Verb 'Should' | 0.1055 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 16 | Conforming | 0.1026 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 17 | Subjective Language | 0.1019 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 18 | Modal Verb 'Shall' | 0.1003 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 19 | Avoid 'Must' | 0.0834 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 20 | Loopholes | 0.0482 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 21 | Vague Pronouns | 0.0475 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 22 | Formal Syntax | 0.0283 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 23 | Comparative Phrases | 0.0232 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 24 | Superlatives | 0.0231 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 25 | Open-ended Terms | 0.0199 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 26 | Ambiguous Adjectives | -0.0268 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุวิธีการออกจากระบบ (เช่น ปุ่ม, เมนู) หรือผลลัพธ์ที่คาดหวังหลังออกจากระบบ (เช่น กลับไปหน้า login)
- **RAG:** Requirement tidak menyebutkan bagaimana cara logout (misalnya, tombol, menu). Mungkin perlu informasi tambahan.

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 (เช่น ไม่มี ID, คำอธิบายเพิ่มเติม)
- **RAG:** Tidak ada template atau gaya yang disetujui yang disebutkan. Perlu diperiksa terhadap template yang digunakan.

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การตรวจสอบ (เช่น จะตรวจสอบอย่างไรว่าสามารถออกจากระบบได้จากทุกหน้าจอ)
- **RAG:** Tidak ada kriteria terukur. Bagaimana kita memverifikasi bahwa logout dapat dilakukan dari 'setiap' halaman? Perlu definisi lebih lanjut.

---

## REQ-5 — -
> ผู้ใช้สามารถบันทึกรายรับ (Income) โดยระบุจำนวนเงิน วันที่ และหมวดหมู่ได้

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.3657 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Measurable Conditions | 0.2556 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 3 | Complete | 0.2121 | The requirement sufficiently describes the capability and conditions without needing further... |
| 4 | Conforming | 0.2088 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 5 | Correct | 0.2021 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 6 | Appropriate | 0.1986 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 7 | Formal Syntax | 0.1863 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 8 | Unambiguous | 0.1862 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 9 | Modal Verb 'Shall' | 0.1835 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 10 | Verifiable | 0.1738 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 11 | Positive Phrasing | 0.1702 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 12 | Modal Verb 'Should' | 0.1416 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 13 | Active Voice | 0.1329 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 14 | System Performance | 0.1297 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 15 | Design Independence | 0.1283 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 16 | Subjective Language | 0.101 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 17 | Singular | 0.0795 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 18 | Avoid 'Shall be able to' | 0.0676 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 19 | Open-ended Terms | 0.0591 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 20 | Superlatives | 0.0556 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 21 | Avoid 'Must' | 0.0489 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 22 | Ambiguous Adjectives | 0.0247 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 23 | Loopholes | 0.0201 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 24 | Vague Pronouns | 0.0162 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |
| 25 | Comparative Phrases | 0.0108 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 26 | Necessary | 0.0017 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ขาดข้อมูลเพิ่มเติม เช่น ข้อมูลหมวดหมู่มีอะไรบ้าง, รูปแบบการระบุวันที่, การจัดการข้อผิดพลาด (เช่น กรณีใส่จำนวนเงินผิดพลาด)
- **RAG:** The requirement is not completely describing the need. It does not specify how the user will interact with the system to record the income (e.g., through a form, a specific button). It also doesn't specify any constraints on the data (e.g., data types, allowed values, maximum length).

**Conforming**
- **Normal:** ไม่ระบุรูปแบบการเขียนที่ชัดเจน (เช่น EARS หรือ ISO29148 template)
- **RAG:** The requirement does not use a standard template or syntax. It lacks a subject, action, and object structure. It also doesn't use 'shall' to denote a binding requirement.

**Unambiguous**
- **Normal:** คำว่า 'หมวดหมู่' ยังคลุมเครือ ต้องระบุให้ชัดเจนว่าหมายถึงอะไร
- **RAG:** While the core meaning is clear, the requirement could be interpreted in multiple ways. For example, it doesn't specify the format of the date or the allowed values for the amount and category.

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผล เช่น จะตรวจสอบได้อย่างไรว่าการบันทึกถูกต้อง, มีการแสดงผลอย่างไร
- **RAG:** The requirement is not verifiable because it lacks measurable criteria. There are no specific details about how the system should behave. For example, there is no mention of error handling or data validation.

---

## REQ-6 — -
> ผู้ใช้สามารถสร้างหมวดหมู่การใช้จ่ายเพิ่มเติมเองได้ (Custom Category)

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Appropriate | 0.4349 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 2 | Feasible | 0.4003 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Design Independence | 0.3044 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 4 | Formal Syntax | 0.3019 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 5 | Measurable Conditions | 0.2919 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 6 | Subjective Language | 0.2776 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 7 | Complete | 0.2733 | The requirement sufficiently describes the capability and conditions without needing further... |
| 8 | Modal Verb 'Should' | 0.252 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 9 | Singular | 0.239 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 10 | Superlatives | 0.2347 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 11 | Conforming | 0.2336 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 12 | Ambiguous Adjectives | 0.2288 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 13 | Positive Phrasing | 0.227 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 14 | Open-ended Terms | 0.2177 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 15 | System Performance | 0.2098 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 16 | Unambiguous | 0.2097 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 17 | Modal Verb 'Shall' | 0.1965 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 18 | Loopholes | 0.1806 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 19 | Correct | 0.1763 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 20 | Comparative Phrases | 0.1752 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 21 | Verifiable | 0.1694 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 22 | Avoid 'Must' | 0.1564 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 23 | Active Voice | 0.1519 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 24 | Necessary | 0.1405 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 25 | Avoid 'Shall be able to' | 0.1118 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 26 | Vague Pronouns | 0.0146 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ขอบเขตของหมวดหมู่ที่สร้างได้ (จำนวน, ชื่อ, รายละเอียด) หรือข้อจำกัดอื่นๆ
- **RAG:** The requirement is complete, but could benefit from specifying what constitutes a 'custom category'. For example, does it include a name, description, and icon? This is not strictly necessary, but would improve completeness.

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบที่กำหนด (เช่น EARS หรือ ISO 29148) เนื่องจากขาดรายละเอียดที่จำเป็น
- **RAG:** The requirement does not explicitly follow a standard template (e.g., Subject-Action-Object). It is written in Thai, which is acceptable, but the structure could be improved for clarity and consistency.

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากขาดเกณฑ์การวัดผล เช่น 'ผู้ใช้สามารถสร้างหมวดหมู่ได้ไม่เกิน X หมวดหมู่' หรือ 'ชื่อหมวดหมู่ต้องมีความยาวไม่เกิน Y ตัวอักษร'
- **RAG:** The requirement is verifiable, but lacks specific measurable criteria. For example, it doesn't specify the maximum number of custom categories, the allowed characters for the category name, or any validation rules. Without these, it's difficult to definitively prove the requirement is met.

---

## REQ-7 — -
> ระบบต้องรองรับการบันทึกรายการแบบทำซ้ำ (Recurring) เช่น ค่าเช่าหอพัก ที่จ่ายเท่าเดิมทุกเดือน

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Conforming | 0.466 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 2 | Feasible | 0.4264 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 3 | Complete | 0.3033 | The requirement sufficiently describes the capability and conditions without needing further... |
| 4 | Appropriate | 0.3027 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 5 | Measurable Conditions | 0.2943 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 6 | Unambiguous | 0.2796 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 7 | Verifiable | 0.2742 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 8 | Formal Syntax | 0.255 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 9 | Correct | 0.2398 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 10 | Positive Phrasing | 0.2209 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 11 | Modal Verb 'Shall' | 0.2203 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 12 | Subjective Language | 0.1945 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 13 | System Performance | 0.1852 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 14 | Singular | 0.1557 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 15 | Design Independence | 0.148 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 16 | Active Voice | 0.1355 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 17 | Ambiguous Adjectives | 0.1244 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 18 | Modal Verb 'Should' | 0.1136 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 19 | Comparative Phrases | 0.1087 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 20 | Avoid 'Must' | 0.1062 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 21 | Loopholes | 0.0996 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 22 | Necessary | 0.0896 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 23 | Superlatives | 0.0884 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 24 | Open-ended Terms | 0.0779 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 25 | Avoid 'Shall be able to' | 0.0693 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 26 | Vague Pronouns | 0.0415 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ❌ FAIL | ⬇ RAG stricter |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น รูปแบบการบันทึกซ้ำ (รายวัน, รายสัปดาห์, รายเดือน, ฯลฯ), ขอบเขตของข้อมูลที่ต้องบันทึกซ้ำ, และวิธีการจัดการเมื่อมีการเปลี่ยนแปลง
- **RAG:** ไม่ระบุรายละเอียดที่เพียงพอ เช่น ข้อมูลที่ต้องบันทึกซ้ำ, ความถี่ในการบันทึก, ระยะเวลาในการบันทึกซ้ำ, และวิธีการจัดการกับรายการที่ซ้ำ

**Conforming**
- **Normal:** ไม่เป็นไปตามรูปแบบมาตรฐาน ISO 29148 หรือรูปแบบการเขียนข้อกำหนดที่กำหนดไว้
- **RAG:** ไม่เป็นไปตามรูปแบบหรือสไตล์ที่กำหนด (เช่น EARS, ISO29148) เนื่องจากไม่มีการใช้คำว่า 'shall' หรือรูปแบบที่ชัดเจน

**Unambiguous**
- **RAG:** อาจตีความได้หลายแบบ เนื่องจากไม่ได้ระบุรายละเอียดที่ชัดเจนเกี่ยวกับวิธีการบันทึกรายการซ้ำ

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผลที่ชัดเจน เช่น จำนวนรายการที่รองรับ, ความถี่ในการบันทึก, หรือประสิทธิภาพในการทำงาน
- **RAG:** ไม่สามารถพิสูจน์ได้โดยตรงเนื่องจากขาดเกณฑ์ที่วัดได้ เช่น ไม่มีการระบุว่ารายการซ้ำจะถูกบันทึกอย่างไร หรือมีวิธีการตรวจสอบอย่างไร

---

## REQ-8 — -
> ผู้ใช้งานสามารถกำหนดงบประมาณ (Budget) รายเดือนสำหรับแต่ละหมวดหมู่ได้

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.4958 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Appropriate | 0.4598 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 3 | Measurable Conditions | 0.3602 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 4 | Conforming | 0.3395 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 5 | Formal Syntax | 0.3184 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 6 | Complete | 0.3068 | The requirement sufficiently describes the capability and conditions without needing further... |
| 7 | Design Independence | 0.3066 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 8 | Unambiguous | 0.2749 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 9 | Subjective Language | 0.2594 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 10 | Positive Phrasing | 0.2576 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 11 | Correct | 0.2521 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 12 | Modal Verb 'Should' | 0.2445 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 13 | System Performance | 0.2407 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 14 | Modal Verb 'Shall' | 0.2384 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 15 | Singular | 0.2136 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 16 | Ambiguous Adjectives | 0.204 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 17 | Open-ended Terms | 0.1949 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 18 | Verifiable | 0.1949 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 19 | Superlatives | 0.1917 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 20 | Loopholes | 0.1835 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 21 | Avoid 'Must' | 0.1394 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 22 | Active Voice | 0.1327 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 23 | Avoid 'Shall be able to' | 0.1172 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 24 | Comparative Phrases | 0.1031 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 25 | Necessary | 0.1023 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 26 | Vague Pronouns | 0.0131 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |
| RAG    | **6/9** | Appropriate, Correct, Feasible, Necessary, Singular, Unambiguous |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ✅ PASS | ✅ PASS |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ขอบเขตของหมวดหมู่, รูปแบบการป้อนค่า, การจัดเก็บข้อมูล, หรือการแสดงผล
- **RAG:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น ขอบเขตของหมวดหมู่ (categories) ที่ผู้ใช้สามารถกำหนดงบประมาณได้, รูปแบบการแสดงผล, หรือข้อจำกัดอื่นๆ

**Conforming**
- **Normal:** ไม่ระบุว่าใช้ template หรือ style แบบใด
- **RAG:** ไม่เป็นไปตามรูปแบบมาตรฐาน (เช่น EARS) หรือรูปแบบที่กำหนดไว้สำหรับโครงการ

**Verifiable**
- **Normal:** ไม่ระบุเกณฑ์การวัดผล เช่น จะตรวจสอบได้อย่างไรว่าผู้ใช้สามารถกำหนดงบประมาณได้จริง, หรือจะตรวจสอบได้อย่างไรว่าระบบสามารถรองรับการกำหนดงบประมาณได้ถูกต้อง
- **RAG:** ไม่ระบุเกณฑ์ที่วัดผลได้ เช่น จะตรวจสอบได้อย่างไรว่าผู้ใช้สามารถกำหนดงบประมาณได้จริง? จำเป็นต้องมีเกณฑ์ที่วัดผลได้ เช่น จำนวนหมวดหมู่ขั้นต่ำ/สูงสุด, รูปแบบการป้อนข้อมูล, หรือการแสดงผล

---

## REQ-9 — -
> ระบบต้องแสดงแถบความคืบหน้า (Progress Bar) เปรียบเทียบยอดใช้จ่ายจริงกับงบประมาณที่ตั้งไว้

### 📚 Retrieved Rules (RAG context)
| # | Topic | Similarity | Rule (excerpt) |
|---|-------|-----------|----------------|
| 1 | Feasible | 0.4205 | The requirement is technically achievable and can be realized within cost and schedule constraints. |
| 2 | Verifiable | 0.3879 | The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration. |
| 3 | Positive Phrasing | 0.3754 | Requirements should be stated as positive statements (what the system shall do) rather than... |
| 4 | Measurable Conditions | 0.3726 | A well-formed requirement is qualified by measurable conditions that define its boundaries. |
| 5 | Conforming | 0.3637 | The requirement is consistent with the standard format and syntax rules defined for the project. |
| 6 | Correct | 0.3618 | The requirement is an accurate representation of the entity need from which it was transformed. |
| 7 | Appropriate | 0.338 | The requirement is appropriate to the level of the entity and avoids unnecessary constraints on... |
| 8 | System Performance | 0.3305 | Requirements should define the performance of the system, not a capability of the user or operator. |
| 9 | Formal Syntax | 0.2962 | A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object]... |
| 10 | Complete | 0.2812 | The requirement sufficiently describes the capability and conditions without needing further... |
| 11 | Modal Verb 'Shall' | 0.2558 | Use 'shall' to denote a binding, mandatory requirement that is contractually required. |
| 12 | Design Independence | 0.2403 | Requirements should state 'what' is needed, not 'how'. Do not include design decisions or... |
| 13 | Modal Verb 'Should' | 0.2308 | Use 'should' to denote a non-mandatory goal, preference, or recommended practice. |
| 14 | Active Voice | 0.2302 | Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is... |
| 15 | Avoid 'Shall be able to' | 0.2112 | Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The... |
| 16 | Comparative Phrases | 0.1989 | Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined... |
| 17 | Superlatives | 0.1898 | Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable... |
| 18 | Unambiguous | 0.1881 | The requirement can be interpreted in only one way. It uses simple and concise language. |
| 19 | Open-ended Terms | 0.1442 | Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope. |
| 20 | Ambiguous Adjectives | 0.1349 | Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'. |
| 21 | Subjective Language | 0.1342 | Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative... |
| 22 | Necessary | 0.1334 | The requirement defines an essential capability. If removed, a deficiency will exist which cannot... |
| 23 | Singular | 0.1266 | The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'. |
| 24 | Avoid 'Must' | 0.126 | Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding... |
| 25 | Loopholes | 0.0735 | Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not... |
| 26 | Vague Pronouns | 0.0407 | Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for... |

### Score Comparison
| Method | Score | Passed Criteria |
|--------|-------|-----------------|
| Normal | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |
| RAG    | **5/9** | Appropriate, Correct, Feasible, Necessary, Singular |

### Per-Criteria Breakdown
| Criterion | Normal | RAG | Note |
|-----------|--------|-----|------|
| Appropriate | ✅ PASS | ✅ PASS |  |
| Complete | ❌ FAIL | ❌ FAIL |  |
| Conforming | ❌ FAIL | ❌ FAIL |  |
| Correct | ✅ PASS | ✅ PASS |  |
| Feasible | ✅ PASS | ✅ PASS |  |
| Necessary | ✅ PASS | ✅ PASS |  |
| Singular | ✅ PASS | ✅ PASS |  |
| Unambiguous | ❌ FAIL | ❌ FAIL |  |
| Verifiable | ❌ FAIL | ❌ FAIL |  |

### Failed Reasons
**Complete**
- **Normal:** ไม่ระบุรายละเอียดเพิ่มเติม เช่น รูปแบบของแถบความคืบหน้า (เช่น สี, ขนาด), ข้อมูลที่แสดงเพิ่มเติม (เช่น ตัวเลข, เปอร์เซ็นต์), หรือตำแหน่งที่แสดงผล
- **RAG:** The requirement is missing details about the progress bar's visual representation (e.g., color, size, update frequency). It also doesn't specify the level of detail for the comparison (e.g., daily, monthly, or total). It could be improved by adding more details about the expected behavior and appearance.

**Conforming**
- **Normal:** ไม่เป็นไปตามเทมเพลตหรือสไตล์ที่กำหนด (เช่น EARS, ISO29148) เนื่องจากขาดรายละเอียดที่จำเป็น
- **RAG:** The requirement does not use the standard 'shall' format. It is a statement of intent, but it doesn't explicitly use the modal verb 'ต้อง' (must/shall) which is the equivalent of 'shall' in Thai. It also lacks a clear subject, action, object, and constraint structure.

**Unambiguous**
- **Normal:** อาจมีการตีความได้หลายแบบ เช่น รูปแบบของแถบความคืบหน้า, ข้อมูลที่แสดง
- **RAG:** While the core intent is clear, the phrase 'เปรียบเทียบยอดใช้จ่ายจริงกับงบประมาณที่ตั้งไว้' could be interpreted in different ways. For example, it doesn't specify how the comparison should be displayed (e.g., percentage, numerical values). It could be improved by adding more details about the expected behavior and appearance.

**Verifiable**
- **Normal:** ไม่สามารถตรวจสอบได้โดยตรงเนื่องจากขาดเกณฑ์การวัดผล เช่น ความแม่นยำของข้อมูล, การตอบสนองของแถบความคืบหน้า
- **RAG:** The requirement lacks measurable criteria. It doesn't specify how the progress bar's accuracy will be verified, the update frequency, or the visual representation. For example, it doesn't specify the acceptable error margin for the comparison.

---

## Summary
- **Project ID:** `57fb6546-ab28-47d5-95d0-db4d6bdf4145`
- **Generated:** 2026-02-18 10:08:53
- **Total requirements:** 28

| req_id | Normal | RAG | Diff |
|--------|--------|-----|------|
| REQ-1 | 5/9 | 5/9 | 0 |
| REQ-10 | 5/9 | 6/9 | +1 |
| REQ-11 | 5/9 | 8/9 | +3 |
| REQ-12 | 6/9 | 6/9 | 0 |
| REQ-13 | 5/9 | 5/9 | 0 |
| REQ-14 | 5/9 | 5/9 | 0 |
| REQ-15 | 5/9 | 5/9 | 0 |
| REQ-16 | 6/9 | 5/9 | -1 |
| REQ-17 | 5/9 | 5/9 | 0 |
| REQ-18 | 6/9 | 8/9 | +2 |
| REQ-19 | 8/9 | 4/9 | -4 |
| REQ-2 | 5/9 | 5/9 | 0 |
| REQ-20 | 8/9 | 8/9 | 0 |
| REQ-21 | 7/9 | 8/9 | +1 |
| REQ-22 | 8/9 | 9/9 | +1 |
| REQ-23 | 8/9 | 8/9 | 0 |
| REQ-24 | 8/9 | 9/9 | +1 |
| REQ-25 | 5/9 | 7/9 | +2 |
| REQ-26 | 8/9 | 8/9 | 0 |
| REQ-27 | 7/9 | 8/9 | +1 |
| REQ-28 | 5/9 | 5/9 | 0 |
| REQ-3 | 5/9 | 4/9 | -1 |
| REQ-4 | 6/9 | 6/9 | 0 |
| REQ-5 | 5/9 | 5/9 | 0 |
| REQ-6 | 6/9 | 6/9 | 0 |
| REQ-7 | 6/9 | 5/9 | -1 |
| REQ-8 | 6/9 | 6/9 | 0 |
| REQ-9 | 5/9 | 5/9 | 0 |
| **Average** | **6.0/9** | **6.2/9** | |
