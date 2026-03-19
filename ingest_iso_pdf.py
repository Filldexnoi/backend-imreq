# ingest_iso_pdf.py
import pdfplumber
import uuid
from sqlalchemy import text
from database import SessionLocal
from embedding import embed

PDF_PATH = "29148-2018-ISOIECIEEE.pdf"
SOURCE_NAME = "ISO/IEC/IEEE 29148:2018"
CHUNK_SIZE = 400  # words


def chunk_text(text: str, chunk_size: int):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])


def ingest_pdf():
    db = SessionLocal()

    with pdfplumber.open(PDF_PATH) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if not page_text:
                continue

            chunks = chunk_text(page_text, CHUNK_SIZE)

            for chunk in chunks:
                embedding = embed(chunk)

                db.execute(
                    text("""
                        INSERT INTO documents
                        (id, source, page, chunk_text, embedding)
                        VALUES
                        (:id, :source, :page, :chunk_text, :embedding)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "source": SOURCE_NAME,
                        "page": page_number,
                        "chunk_text": chunk,
                        "embedding": embedding
                    }
                )

                print(f"Inserted page {page_number}")

    db.commit()
    db.close()


if __name__ == "__main__":
    iso_rules = [
    # --- Clause 5.2.4: Requirements Construct ---
    {"clause": "5.2.4", "topic": "Formal Syntax", "rule_text": "A well-formed requirement should follow the structure: [Condition] [Subject] [Action] [Object] [Constraint]."},
    {"clause": "5.2.4", "topic": "Active Voice", "rule_text": "Use active voice to clearly identify the subject (e.g., 'The system shall...' instead of 'It is required that...')."},
    {"clause": "5.2.4", "topic": "Positive Phrasing", "rule_text": "Requirements should be stated as positive statements (what the system shall do) rather than negative (shall not)."},
    {"clause": "5.2.4", "topic": "Modal Verb 'Shall'", "rule_text": "Use 'shall' to denote a binding, mandatory requirement that is contractually required."},
    {"clause": "5.2.4", "topic": "Modal Verb 'Should'", "rule_text": "Use 'should' to denote a non-mandatory goal, preference, or recommended practice."},
    {"clause": "5.2.4", "topic": "Avoid 'Must'", "rule_text": "Avoid using the term 'must' to prevent potential misinterpretation; use 'shall' for binding requirements."},
    {"clause": "5.2.4", "topic": "Avoid 'Shall be able to'", "rule_text": "Avoid using 'shall be able to' or 'shall be capable of'; state the action directly (e.g., 'The system shall [Action]')."},
    {"clause": "5.2.4", "topic": "System Performance", "rule_text": "Requirements should define the performance of the system, not a capability of the user or operator."},
    {"clause": "5.2.4", "topic": "Measurable Conditions", "rule_text": "A well-formed requirement is qualified by measurable conditions that define its boundaries."},

    # --- Clause 5.2.5: Individual Characteristics ---
    {"clause": "5.2.5", "topic": "Necessary", "rule_text": "The requirement defines an essential capability. If removed, a deficiency will exist which cannot be fulfilled by other requirements."},
    {"clause": "5.2.5", "topic": "Appropriate", "rule_text": "The requirement is appropriate to the level of the entity and avoids unnecessary constraints on design."},
    {"clause": "5.2.5", "topic": "Unambiguous", "rule_text": "The requirement can be interpreted in only one way. It uses simple and concise language."},
    {"clause": "5.2.5", "topic": "Complete", "rule_text": "The requirement sufficiently describes the capability and conditions without needing further explanation."},
    {"clause": "5.2.5", "topic": "Singular", "rule_text": "The requirement states a single capability. Avoid using 'and', 'or', 'with', 'also'."},
    {"clause": "5.2.5", "topic": "Feasible", "rule_text": "The requirement is technically achievable and can be realized within cost and schedule constraints."},
    {"clause": "5.2.5", "topic": "Verifiable", "rule_text": "The requirement's fulfillment can be proven through inspection, analysis, test, or demonstration."},
    {"clause": "5.2.5", "topic": "Correct", "rule_text": "The requirement is an accurate representation of the entity need from which it was transformed."},
    {"clause": "5.2.5", "topic": "Conforming", "rule_text": "The requirement is consistent with the standard format and syntax rules defined for the project."},

    # --- Clause 5.2.7: Language Criteria ---
    {"clause": "5.2.7", "topic": "Design Independence", "rule_text": "Requirements should state 'what' is needed, not 'how'. Do not include design decisions or commercial products."},
    {"clause": "5.2.7", "topic": "Subjective Language", "rule_text": "Avoid terms like 'user-friendly', 'easy to use', 'robust', or 'reliable' without quantitative criteria."},
    {"clause": "5.2.7", "topic": "Ambiguous Adjectives", "rule_text": "Avoid vague adjectives like 'adequate', 'significant', 'sufficient', 'flexible', or 'minimal'."},
    {"clause": "5.2.7", "topic": "Loopholes", "rule_text": "Avoid phrases like 'if possible', 'as appropriate', 'as applicable', or 'including but not limited to'."},
    {"clause": "5.2.7", "topic": "Open-ended Terms", "rule_text": "Avoid using 'etc.', 'and so on', or 'and/or' which lead to uncertainty in scope."},
    {"clause": "5.2.7", "topic": "Superlatives", "rule_text": "Avoid superlatives like 'best', 'fastest', or 'most efficient' unless they are verifiable constraints."},
    {"clause": "5.2.7", "topic": "Vague Pronouns", "rule_text": "Avoid using 'it', 'this', 'that', or 'they' to refer to subjects; always restate the subject for clarity."},
    {"clause": "5.2.7", "topic": "Comparative Phrases", "rule_text": "Avoid phrases like 'better than' or 'superior' because they cannot be verified without a defined baseline."}
]
    db = SessionLocal()
    try:
        for item in iso_rules:
            # ใช้ Logic ตามตัวอย่างที่คุณส่งมา
            embedding = embed(item['rule_text'])
            
            db.execute(
                text("""
                    INSERT INTO rules 
                    (id, clause, topic, rule_text, embedding) 
                    VALUES 
                    (:id, :clause, :topic, :rule_text, :embedding)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "clause": item['clause'],
                    "topic": item['topic'],
                    "rule_text": item['rule_text'],
                    "embedding": embedding
                }
            )
            print(f"Inserted Rule: {item['clause']} - {item['topic']}")
        
        db.commit()
        print("All rules have been successfully inserted.")
    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()
