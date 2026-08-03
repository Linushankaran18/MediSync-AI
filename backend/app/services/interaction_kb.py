"""Allergen cross-reactivity lookup for the rule engine's allergy check.
Small, curated, demo-scale list (fuzzy/substring matching against medication
names) - not a substitute for a licensed clinical drug database. The drug
interaction pairs live in services/data/drug_interactions.json instead of
here, so they can be edited without a code change."""

ALLERGY_CROSS_REACTIVITY: dict[str, list[str]] = {
    "penicillin": ["penicillin", "amoxicillin", "ampicillin", "piperacillin", "oxacillin", "nafcillin"],
    "sulfa": ["sulfamethoxazole", "sulfasalazine", "sulfadiazine", "bactrim", "septra"],
    "nsaid": ["ibuprofen", "naproxen", "diclofenac", "ketorolac", "aspirin", "celecoxib"],
    "aspirin": ["aspirin", "acetylsalicylic"],
    "cephalosporin": ["cephalexin", "ceftriaxone", "cefazolin", "cefuroxime", "cefdinir"],
    "codeine": ["codeine", "hydrocodone", "oxycodone"],
    "iodine": ["contrast dye", "iodinated contrast"],
}
