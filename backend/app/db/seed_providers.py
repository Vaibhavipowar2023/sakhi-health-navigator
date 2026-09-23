"""Seed ~40 synthetic providers into MongoDB.

All providers are is_synthetic=True. Some have deliberately missing fields
(credentials, insurance, coordinates, availability) to test that the system
never invents data it doesn't have.

Each provider gets an embedding of their services for semantic search.
"""
from backend.app.db.engine import get_providers_collection, init_db
from backend.app.db.embeddings import embed_texts

PROVIDERS = [
    # --- Pune: general_gynecology ---
    {
        "id": "p-pune-gyn-001",
        "name": "Dr. Anita Kulkarni",
        "specialty": "general_gynecology",
        "subspecialty": "adolescent gynecology",
        "credentials": "MBBS, MD (OB-GYN), FICOG",
        "clinic_name": "Kulkarni Women's Clinic",
        "city": "Pune",
        "address": "301, Sai Plaza, Karve Rd, Deccan Gymkhana, Pune 411004",
        "latitude": 18.5089, "longitude": 73.8400,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam", "pap smear", "contraception counseling", "menstrual disorder management"],
        "insurance": ["Star Health", "ICICI Lombard", "New India Assurance"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "13:00"},
            {"day": "monday", "start": "17:00", "end": "20:00"},
            {"day": "wednesday", "start": "09:00", "end": "13:00"},
            {"day": "friday", "start": "09:00", "end": "13:00"},
            {"day": "saturday", "start": "10:00", "end": "14:00"},
        ],
    },
    {
        "id": "p-pune-gyn-002",
        "name": "Dr. Meera Patil",
        "specialty": "general_gynecology",
        "credentials": "MBBS, DNB (OB-GYN)",
        "clinic_name": "Sahyadri Hospital",
        "city": "Pune",
        "address": "Plot 30-C, Erandwane, Karve Rd, Pune 411004",
        "latitude": 18.5050, "longitude": 73.8310,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam", "cervical screening", "menstrual disorder management", "IUCD insertion"],
        "insurance": ["Star Health", "Bajaj Allianz", "HDFC ERGO", "Care Health"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "14:00"},
            {"day": "tuesday", "start": "10:00", "end": "14:00"},
            {"day": "thursday", "start": "10:00", "end": "14:00"},
            {"day": "saturday", "start": "09:00", "end": "12:00"},
        ],
    },
    {
        "id": "p-pune-gyn-003",
        "name": "Dr. Sunita Deshpande",
        "specialty": "general_gynecology",
        "credentials": "MBBS, MS (OB-GYN)",
        "clinic_name": "Ruby Hall Clinic",
        "city": "Pune",
        "address": "40, Sassoon Rd, Pune 411001",
        "latitude": 18.5255, "longitude": 73.8773,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam", "pap smear", "colposcopy"],
        "insurance": ["New India Assurance", "Niva Bupa", "ManipalCigna"],
        "availability": [
            {"day": "tuesday", "start": "09:00", "end": "16:00"},
            {"day": "thursday", "start": "09:00", "end": "16:00"},
        ],
    },
    # hallucination probe: no credentials, no insurance, no availability
    {
        "id": "p-pune-gyn-004",
        "name": "Dr. Kavita Joshi",
        "specialty": "general_gynecology",
        "credentials": None,
        "clinic_name": "City Care Hospital",
        "city": "Pune",
        "address": "Tilak Rd, Sadashiv Peth, Pune 411030",
        "latitude": 18.5120, "longitude": 73.8560,
        "phone": None,
        "services": ["routine gynecological exam", "pap smear"],
        "insurance": [],
        "availability": [],
    },

    # --- Pune: pelvic_pain_endometriosis ---
    {
        "id": "p-pune-endo-001",
        "name": "Dr. Priya Deshmukh",
        "specialty": "pelvic_pain_endometriosis",
        "subspecialty": "excision surgery",
        "credentials": "MBBS, MS (OB-GYN), Fellowship Endoscopy",
        "clinic_name": "Deshmukh Endo Centre",
        "city": "Pune",
        "address": "12, Baner Rd, Baner, Pune 411045",
        "latitude": 18.5590, "longitude": 73.7868,
        "phone": "+91-7249362032",
        "services": ["diagnostic laparoscopy", "endometriosis excision surgery", "pelvic pain management", "adhesiolysis"],
        "insurance": ["Star Health", "ICICI Lombard", "Bajaj Allianz"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "17:00"},
            {"day": "wednesday", "start": "10:00", "end": "17:00"},
            {"day": "friday", "start": "10:00", "end": "14:00"},
        ],
    },
    {
        "id": "p-pune-endo-002",
        "name": "Dr. Rashmi Bhosale",
        "specialty": "pelvic_pain_endometriosis",
        "credentials": "MBBS, MD (OB-GYN)",
        "clinic_name": "Jehangir Hospital",
        "city": "Pune",
        "address": "32, Sassoon Rd, Pune 411001",
        "latitude": 18.5280, "longitude": 73.8770,
        "phone": "+91-7249362032",
        "services": ["pelvic pain evaluation", "hormonal therapy for endometriosis", "laparoscopic surgery"],
        "insurance": ["HDFC ERGO", "Care Health", "Aditya Birla Health"],
        "availability": [
            {"day": "tuesday", "start": "11:00", "end": "18:00"},
            {"day": "thursday", "start": "11:00", "end": "18:00"},
            {"day": "saturday", "start": "09:00", "end": "13:00"},
        ],
    },

    # --- Pune: pcos_hormonal ---
    {
        "id": "p-pune-pcos-001",
        "name": "Dr. Neha Sharma",
        "specialty": "pcos_hormonal",
        "subspecialty": "reproductive endocrinology",
        "credentials": "MBBS, MD (OB-GYN), Fellowship Reproductive Endocrinology",
        "clinic_name": "Hormonal Wellness Clinic",
        "city": "Pune",
        "address": "15, Koregaon Park, Pune 411001",
        "latitude": 18.5362, "longitude": 73.8930,
        "phone": "+91-7249362032",
        "services": ["PCOS management", "hormonal profiling", "insulin resistance management", "hirsutism treatment"],
        "insurance": ["Star Health", "New India Assurance", "Niva Bupa"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "14:00"},
            {"day": "wednesday", "start": "09:00", "end": "14:00"},
            {"day": "friday", "start": "09:00", "end": "14:00"},
        ],
    },
    # hallucination probe: no coordinates
    {
        "id": "p-pune-pcos-002",
        "name": "Dr. Swati Marathe",
        "specialty": "pcos_hormonal",
        "credentials": "MBBS, DGO",
        "clinic_name": "Marathe Clinic",
        "city": "Pune",
        "address": "Kothrud, Pune",
        "latitude": None, "longitude": None,
        "phone": "+91-7249362032",
        "services": ["PCOS management", "thyroid-related menstrual issues"],
        "insurance": ["ICICI Lombard"],
        "availability": [
            {"day": "tuesday", "start": "10:00", "end": "13:00"},
            {"day": "saturday", "start": "10:00", "end": "13:00"},
        ],
    },

    # --- Pune: fertility ---
    {
        "id": "p-pune-fert-001",
        "name": "Dr. Aarti Khanna",
        "specialty": "fertility",
        "subspecialty": "IVF specialist",
        "credentials": "MBBS, MD (OB-GYN), Fellowship IVF (Singapore)",
        "clinic_name": "Nova IVF Fertility",
        "city": "Pune",
        "address": "Survey 215, Baner Rd, Baner, Pune 411045",
        "latitude": 18.5610, "longitude": 73.7890,
        "phone": "+91-7249362032",
        "services": ["IVF", "IUI", "egg freezing", "fertility assessment", "ovulation induction"],
        "insurance": ["Star Health", "Bajaj Allianz", "HDFC ERGO", "ManipalCigna"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "16:00"},
            {"day": "tuesday", "start": "08:00", "end": "16:00"},
            {"day": "wednesday", "start": "08:00", "end": "16:00"},
            {"day": "thursday", "start": "08:00", "end": "16:00"},
            {"day": "friday", "start": "08:00", "end": "16:00"},
        ],
    },
    {
        "id": "p-pune-fert-002",
        "name": "Dr. Pallavi Rao",
        "specialty": "fertility",
        "credentials": "MBBS, MS (OB-GYN), DNB",
        "clinic_name": "Pune Fertility Centre",
        "city": "Pune",
        "address": "Shivajinagar, Pune 411005",
        "latitude": 18.5308, "longitude": 73.8475,
        "phone": "+91-7249362032",
        "services": ["IVF", "IUI", "fertility counseling", "hysteroscopy"],
        "insurance": ["New India Assurance", "Care Health"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "17:00"},
            {"day": "wednesday", "start": "10:00", "end": "17:00"},
            {"day": "friday", "start": "10:00", "end": "14:00"},
        ],
    },

    # --- Pune: obstetrics ---
    {
        "id": "p-pune-obs-001",
        "name": "Dr. Shalini Iyer",
        "specialty": "obstetrics",
        "credentials": "MBBS, MD (OB-GYN), FRCOG",
        "clinic_name": "Iyer Maternity Home",
        "city": "Pune",
        "address": "45, Prabhat Rd, Lane 5, Pune 411004",
        "latitude": 18.5140, "longitude": 73.8330,
        "phone": "+91-7249362032",
        "services": ["antenatal care", "normal delivery", "caesarean section", "postnatal care"],
        "insurance": ["Star Health", "ICICI Lombard", "New India Assurance", "Niva Bupa"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "18:00"},
            {"day": "tuesday", "start": "09:00", "end": "18:00"},
            {"day": "wednesday", "start": "09:00", "end": "18:00"},
            {"day": "thursday", "start": "09:00", "end": "18:00"},
            {"day": "friday", "start": "09:00", "end": "18:00"},
            {"day": "saturday", "start": "09:00", "end": "14:00"},
        ],
    },
    # hallucination probe: no availability, no phone
    {
        "id": "p-pune-obs-002",
        "name": "Dr. Vijaya Mane",
        "specialty": "obstetrics",
        "credentials": "MBBS, DGO",
        "clinic_name": "Mane Hospital",
        "city": "Pune",
        "address": "Hadapsar, Pune 411028",
        "latitude": 18.5020, "longitude": 73.9260,
        "phone": None,
        "services": ["antenatal care", "normal delivery"],
        "insurance": ["Bajaj Allianz"],
        "availability": [],
    },
    {
        "id": "p-pune-obs-003",
        "name": "Dr. Madhuri Gadgil",
        "specialty": "obstetrics",
        "credentials": "MBBS, MS (OB-GYN)",
        "clinic_name": "Gadgil Maternity Hospital",
        "city": "Pune",
        "address": "Aundh, Pune 411007",
        "latitude": 18.5590, "longitude": 73.8070,
        "phone": "+91-7249362032",
        "services": ["antenatal care", "normal delivery", "postnatal care"],
        "insurance": ["Star Health", "Bajaj Allianz", "Aditya Birla Health"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "17:00"},
            {"day": "tuesday", "start": "09:00", "end": "17:00"},
            {"day": "wednesday", "start": "09:00", "end": "17:00"},
            {"day": "thursday", "start": "09:00", "end": "17:00"},
            {"day": "friday", "start": "09:00", "end": "17:00"},
        ],
    },

    # --- Pune: high_risk_obstetrics ---
    {
        "id": "p-pune-hro-001",
        "name": "Dr. Deepa Gokhale",
        "specialty": "high_risk_obstetrics",
        "subspecialty": "maternal fetal medicine",
        "credentials": "MBBS, MD (OB-GYN), DM (Maternal Fetal Medicine)",
        "clinic_name": "KEM Hospital",
        "city": "Pune",
        "address": "Sardar Moodliar Rd, Rasta Peth, Pune 411011",
        "latitude": 18.5220, "longitude": 73.8680,
        "phone": "+91-7249362032",
        "services": ["high-risk pregnancy management", "fetal monitoring", "gestational diabetes management", "preeclampsia monitoring"],
        "insurance": ["Star Health", "New India Assurance", "HDFC ERGO", "Care Health"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "15:00"},
            {"day": "tuesday", "start": "08:00", "end": "15:00"},
            {"day": "wednesday", "start": "08:00", "end": "15:00"},
            {"day": "thursday", "start": "08:00", "end": "15:00"},
            {"day": "friday", "start": "08:00", "end": "15:00"},
        ],
    },
    {
        "id": "p-pune-hro-002",
        "name": "Dr. Smita Chaudhari",
        "specialty": "high_risk_obstetrics",
        "credentials": "MBBS, MD (OB-GYN), DM (MFM)",
        "clinic_name": "Sahyadri Super Specialty Hospital",
        "city": "Pune",
        "address": "Plot 30-C, Erandwane, Pune 411004",
        "latitude": 18.5060, "longitude": 73.8310,
        "phone": "+91-7249362032",
        "services": ["high-risk pregnancy management", "multiple gestation care", "gestational diabetes management"],
        "insurance": ["Star Health", "ICICI Lombard", "HDFC ERGO", "New India Assurance"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "14:00"},
            {"day": "tuesday", "start": "08:00", "end": "14:00"},
            {"day": "thursday", "start": "08:00", "end": "14:00"},
            {"day": "saturday", "start": "09:00", "end": "12:00"},
        ],
    },

    # --- Pune: urogynecology ---
    {
        "id": "p-pune-uro-001",
        "name": "Dr. Aparna Kale",
        "specialty": "urogynecology",
        "subspecialty": "pelvic reconstructive surgery",
        "credentials": "MBBS, MS (OB-GYN), Fellowship Urogynecology",
        "clinic_name": "Jehangir Hospital",
        "city": "Pune",
        "address": "32, Sassoon Rd, Pune 411001",
        "latitude": 18.5280, "longitude": 73.8770,
        "phone": "+91-7249362032",
        "services": ["urinary incontinence treatment", "pelvic organ prolapse repair", "urodynamic testing", "mid-urethral sling surgery"],
        "insurance": ["Star Health", "ICICI Lombard", "Bajaj Allianz", "Aditya Birla Health"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "16:00"},
            {"day": "wednesday", "start": "10:00", "end": "16:00"},
            {"day": "friday", "start": "10:00", "end": "13:00"},
        ],
    },
    # hallucination probe: no credentials, no coordinates
    {
        "id": "p-pune-uro-002",
        "name": "Dr. Seema Bhagwat",
        "specialty": "urogynecology",
        "credentials": None,
        "clinic_name": "Aundh District Hospital",
        "city": "Pune",
        "address": "Aundh, Pune",
        "latitude": None, "longitude": None,
        "phone": "+91-7249362032",
        "services": ["urinary incontinence assessment", "pessary fitting"],
        "insurance": ["New India Assurance"],
        "availability": [
            {"day": "tuesday", "start": "09:00", "end": "14:00"},
            {"day": "thursday", "start": "09:00", "end": "14:00"},
        ],
    },

    # --- Pune: breast_health ---
    {
        "id": "p-pune-breast-001",
        "name": "Dr. Vaishali Phadke",
        "specialty": "breast_health",
        "subspecialty": "surgical oncology — breast",
        "credentials": "MBBS, MS (Surgery), MCh (Surgical Oncology)",
        "clinic_name": "Deenanath Mangeshkar Hospital",
        "city": "Pune",
        "address": "Erandwane, Pune 411004",
        "latitude": 18.5050, "longitude": 73.8290,
        "phone": "+91-7249362032",
        "services": ["breast examination", "mammography referral", "breast biopsy", "breast conservation surgery"],
        "insurance": ["Star Health", "HDFC ERGO", "Niva Bupa", "ManipalCigna"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "14:00"},
            {"day": "wednesday", "start": "09:00", "end": "14:00"},
            {"day": "friday", "start": "09:00", "end": "14:00"},
        ],
    },
    # hallucination probe: no insurance, no availability, no coordinates
    {
        "id": "p-pune-breast-002",
        "name": "Dr. Rohini Savant",
        "specialty": "breast_health",
        "credentials": "MBBS, MS (Surgery)",
        "clinic_name": "Savant Surgical Clinic",
        "city": "Pune",
        "address": "Warje, Pune",
        "latitude": None, "longitude": None,
        "phone": "+91-7249362032",
        "services": ["breast examination", "breast biopsy"],
        "insurance": [],
        "availability": [],
    },

    # --- Pune: menopause ---
    {
        "id": "p-pune-meno-001",
        "name": "Dr. Jyoti Waghmare",
        "specialty": "menopause",
        "credentials": "MBBS, MD (OB-GYN), Certified Menopause Practitioner (IMS)",
        "clinic_name": "Waghmare Women's Wellness",
        "city": "Pune",
        "address": "Lane 7, Koregaon Park, Pune 411001",
        "latitude": 18.5370, "longitude": 73.8950,
        "phone": "+91-7249362032",
        "services": ["menopause counseling", "HRT management", "bone density screening referral", "vaginal atrophy treatment"],
        "insurance": ["Star Health", "ICICI Lombard", "Care Health"],
        "availability": [
            {"day": "tuesday", "start": "10:00", "end": "16:00"},
            {"day": "thursday", "start": "10:00", "end": "16:00"},
            {"day": "saturday", "start": "10:00", "end": "13:00"},
        ],
    },
    # hallucination probe: no insurance, no availability
    {
        "id": "p-pune-meno-002",
        "name": "Dr. Nandini Puranik",
        "specialty": "menopause",
        "credentials": "MBBS, DGO",
        "clinic_name": "Puranik Health Centre",
        "city": "Pune",
        "address": "Kothrud, Pune 411038",
        "latitude": 18.5070, "longitude": 73.8100,
        "phone": "+91-7249362032",
        "services": ["menopause counseling", "HRT management"],
        "insurance": [],
        "availability": [],
    },

    # --- Pune: perinatal_mental_health ---
    {
        "id": "p-pune-pmh-001",
        "name": "Dr. Amruta Naik",
        "specialty": "perinatal_mental_health",
        "subspecialty": "perinatal psychiatry",
        "credentials": "MBBS, MD (Psychiatry), Fellowship Perinatal Mental Health",
        "clinic_name": "Naik Mind-Body Clinic",
        "city": "Pune",
        "address": "5, Boat Club Rd, Pune 411001",
        "latitude": 18.5340, "longitude": 73.8900,
        "phone": "+91-7249362032",
        "services": ["postpartum depression screening", "prenatal anxiety management", "perinatal psychiatric consultation", "mother-infant bonding support"],
        "insurance": ["Star Health", "Bajaj Allianz", "Aditya Birla Health"],
        "availability": [
            {"day": "monday", "start": "11:00", "end": "17:00"},
            {"day": "wednesday", "start": "11:00", "end": "17:00"},
            {"day": "friday", "start": "11:00", "end": "15:00"},
        ],
    },
    {
        "id": "p-pune-pmh-002",
        "name": "Dr. Aishwarya Deo",
        "specialty": "perinatal_mental_health",
        "credentials": "MBBS, MD (Psychiatry)",
        "clinic_name": "Deo Psychiatry & Wellness",
        "city": "Pune",
        "address": "Model Colony, Shivajinagar, Pune 411016",
        "latitude": 18.5320, "longitude": 73.8420,
        "phone": "+91-7249362032",
        "services": ["postpartum depression treatment", "perinatal OCD management", "grief counseling — pregnancy loss"],
        "insurance": ["Care Health", "Niva Bupa"],
        "availability": [
            {"day": "tuesday", "start": "11:00", "end": "18:00"},
            {"day": "friday", "start": "11:00", "end": "18:00"},
        ],
    },

    # --- Pune: pelvic_floor_physio ---
    {
        "id": "p-pune-pf-001",
        "name": "Sneha Tambe",
        "specialty": "pelvic_floor_physio",
        "credentials": "BPTh, MPTh (Women's Health), CAPP-Pelvic",
        "clinic_name": "Tambe Pelvic Floor Rehab",
        "city": "Pune",
        "address": "Lane 3, Kalyani Nagar, Pune 411006",
        "latitude": 18.5480, "longitude": 73.9020,
        "phone": "+91-7249362032",
        "services": ["pelvic floor assessment", "biofeedback therapy", "postpartum rehabilitation", "diastasis recti management"],
        "insurance": ["Star Health", "ICICI Lombard"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "14:00"},
            {"day": "tuesday", "start": "08:00", "end": "14:00"},
            {"day": "wednesday", "start": "08:00", "end": "14:00"},
            {"day": "thursday", "start": "08:00", "end": "14:00"},
            {"day": "friday", "start": "08:00", "end": "14:00"},
        ],
    },
    {
        "id": "p-pune-pf-002",
        "name": "Priyanka Kadam",
        "specialty": "pelvic_floor_physio",
        "credentials": "BPTh, Certified Pelvic Floor Therapist",
        "clinic_name": "PhysioFirst Women's Rehab",
        "city": "Pune",
        "address": "Viman Nagar, Pune 411014",
        "latitude": 18.5680, "longitude": 73.9140,
        "phone": "+91-7249362032",
        "services": ["pelvic floor assessment", "postpartum rehabilitation", "core stability training"],
        "insurance": [],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "12:00"},
            {"day": "wednesday", "start": "08:00", "end": "12:00"},
            {"day": "friday", "start": "08:00", "end": "12:00"},
        ],
    },

    # --- Pune: adolescent_gynecology ---
    {
        "id": "p-pune-adol-001",
        "name": "Dr. Revati Karve",
        "specialty": "adolescent_gynecology",
        "credentials": "MBBS, MD (OB-GYN), Diploma Adolescent Health",
        "clinic_name": "Karve Adolescent Health Centre",
        "city": "Pune",
        "address": "FC Rd, Shivajinagar, Pune 411005",
        "latitude": 18.5290, "longitude": 73.8420,
        "phone": "+91-7249362032",
        "services": ["adolescent menstrual counseling", "puberty-related concerns", "vaccination counseling (HPV)", "PCOS screening in teens"],
        "insurance": ["Star Health", "New India Assurance", "Niva Bupa"],
        "availability": [
            {"day": "monday", "start": "16:00", "end": "20:00"},
            {"day": "wednesday", "start": "16:00", "end": "20:00"},
            {"day": "saturday", "start": "10:00", "end": "14:00"},
        ],
    },
    {
        "id": "p-pune-adol-002",
        "name": "Dr. Tanuja Shinde",
        "specialty": "adolescent_gynecology",
        "credentials": "MBBS, DGO",
        "clinic_name": "Shinde Women's Care",
        "city": "Pune",
        "address": "Bibwewadi, Pune 411037",
        "latitude": 18.4790, "longitude": 73.8660,
        "phone": "+91-7249362032",
        "services": ["adolescent menstrual counseling", "PCOS screening in teens"],
        "insurance": ["Bajaj Allianz", "Star Health"],
        "availability": [
            {"day": "monday", "start": "17:00", "end": "20:00"},
            {"day": "thursday", "start": "17:00", "end": "20:00"},
            {"day": "saturday", "start": "10:00", "end": "14:00"},
        ],
    },

    # --- Mumbai: general_gynecology ---
    {
        "id": "p-mum-gyn-001",
        "name": "Dr. Ranjana Nair",
        "specialty": "general_gynecology",
        "credentials": "MBBS, MD (OB-GYN), FICS",
        "clinic_name": "Lilavati Hospital",
        "city": "Mumbai",
        "address": "A-791, Bandra Reclamation, Bandra (W), Mumbai 400050",
        "latitude": 19.0510, "longitude": 72.8290,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam", "pap smear", "colposcopy", "contraception counseling"],
        "insurance": ["Star Health", "ICICI Lombard", "Bajaj Allianz", "HDFC ERGO"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "14:00"},
            {"day": "tuesday", "start": "09:00", "end": "14:00"},
            {"day": "thursday", "start": "09:00", "end": "14:00"},
            {"day": "saturday", "start": "09:00", "end": "12:00"},
        ],
    },
    {
        "id": "p-mum-gyn-002",
        "name": "Dr. Fatima Shaikh",
        "specialty": "general_gynecology",
        "credentials": "MBBS, MS (OB-GYN)",
        "clinic_name": "Hiranandani Hospital",
        "city": "Mumbai",
        "address": "Hillside Ave, Hiranandani Gardens, Powai, Mumbai 400076",
        "latitude": 19.1190, "longitude": 72.9070,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam", "menstrual disorder management"],
        "insurance": ["New India Assurance", "Care Health", "ManipalCigna"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "18:00"},
            {"day": "wednesday", "start": "10:00", "end": "18:00"},
            {"day": "friday", "start": "10:00", "end": "15:00"},
        ],
    },
    # hallucination probe: no credentials
    {
        "id": "p-mum-gyn-003",
        "name": "Dr. Pooja Gupta",
        "specialty": "general_gynecology",
        "credentials": None,
        "clinic_name": "Gupta Medical Centre",
        "city": "Mumbai",
        "address": "Andheri (W), Mumbai",
        "latitude": 19.1360, "longitude": 72.8370,
        "phone": "+91-7249362032",
        "services": ["routine gynecological exam"],
        "insurance": ["Star Health"],
        "availability": [
            {"day": "tuesday", "start": "10:00", "end": "13:00"},
            {"day": "friday", "start": "10:00", "end": "13:00"},
        ],
    },

    # --- Mumbai: pelvic_pain_endometriosis ---
    {
        "id": "p-mum-endo-001",
        "name": "Dr. Shruti Menon",
        "specialty": "pelvic_pain_endometriosis",
        "subspecialty": "advanced laparoscopy",
        "credentials": "MBBS, MD (OB-GYN), FMAS, DMAS",
        "clinic_name": "Kokilaben Dhirubhai Ambani Hospital",
        "city": "Mumbai",
        "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bungalows, Andheri (W), Mumbai 400053",
        "latitude": 19.1310, "longitude": 72.8260,
        "phone": "+91-7249362032",
        "services": ["advanced laparoscopic endometriosis surgery", "pelvic pain evaluation", "deep infiltrating endometriosis treatment"],
        "insurance": ["Star Health", "HDFC ERGO", "Niva Bupa", "Aditya Birla Health"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "16:00"},
            {"day": "tuesday", "start": "09:00", "end": "16:00"},
            {"day": "thursday", "start": "09:00", "end": "16:00"},
        ],
    },

    # --- Mumbai: pcos_hormonal ---
    {
        "id": "p-mum-pcos-001",
        "name": "Dr. Leela Krishnan",
        "specialty": "pcos_hormonal",
        "credentials": "MBBS, MD (OB-GYN), Fellowship Reproductive Endocrinology",
        "clinic_name": "Breach Candy Hospital",
        "city": "Mumbai",
        "address": "60-A, Bhulabhai Desai Rd, Mumbai 400026",
        "latitude": 18.9710, "longitude": 72.8050,
        "phone": "+91-7249362032",
        "services": ["PCOS management", "hormonal profiling", "metabolic syndrome screening"],
        "insurance": ["Star Health", "ICICI Lombard", "Bajaj Allianz"],
        "availability": [
            {"day": "tuesday", "start": "10:00", "end": "16:00"},
            {"day": "thursday", "start": "10:00", "end": "16:00"},
        ],
    },

    # --- Mumbai: fertility ---
    {
        "id": "p-mum-fert-001",
        "name": "Dr. Anagha Karkhanis",
        "specialty": "fertility",
        "subspecialty": "ART specialist",
        "credentials": "MBBS, MD (OB-GYN), Fellowship Reproductive Medicine (UK)",
        "clinic_name": "Jaslok Hospital",
        "city": "Mumbai",
        "address": "15, Dr. G. Deshmukh Marg, Peddar Rd, Mumbai 400026",
        "latitude": 18.9710, "longitude": 72.8100,
        "phone": "+91-7249362032",
        "services": ["IVF", "IUI", "egg freezing", "donor program", "surrogacy counseling"],
        "insurance": ["HDFC ERGO", "ManipalCigna", "New India Assurance"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "15:00"},
            {"day": "tuesday", "start": "08:00", "end": "15:00"},
            {"day": "wednesday", "start": "08:00", "end": "15:00"},
            {"day": "thursday", "start": "08:00", "end": "15:00"},
            {"day": "friday", "start": "08:00", "end": "15:00"},
        ],
    },
    # hallucination probe: no insurance, no phone
    {
        "id": "p-mum-fert-002",
        "name": "Dr. Tanvi Hegde",
        "specialty": "fertility",
        "credentials": "MBBS, DNB (OB-GYN)",
        "clinic_name": "Hegde Fertility",
        "city": "Mumbai",
        "address": "Thane (W), Mumbai",
        "latitude": 19.1970, "longitude": 72.9630,
        "phone": None,
        "services": ["IVF", "IUI"],
        "insurance": [],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "14:00"},
            {"day": "friday", "start": "10:00", "end": "14:00"},
        ],
    },

    # --- Mumbai: obstetrics ---
    {
        "id": "p-mum-obs-001",
        "name": "Dr. Gauri Tendulkar",
        "specialty": "obstetrics",
        "credentials": "MBBS, MD (OB-GYN), FRCOG",
        "clinic_name": "Hinduja Hospital",
        "city": "Mumbai",
        "address": "Veer Savarkar Marg, Mahim, Mumbai 400016",
        "latitude": 19.0390, "longitude": 72.8400,
        "phone": "+91-7249362032",
        "services": ["antenatal care", "normal delivery", "caesarean section", "high-risk pregnancy"],
        "insurance": ["Star Health", "ICICI Lombard", "Bajaj Allianz", "HDFC ERGO", "Care Health"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "17:00"},
            {"day": "tuesday", "start": "09:00", "end": "17:00"},
            {"day": "wednesday", "start": "09:00", "end": "17:00"},
            {"day": "thursday", "start": "09:00", "end": "17:00"},
            {"day": "friday", "start": "09:00", "end": "17:00"},
        ],
    },

    # --- Mumbai: high_risk_obstetrics ---
    {
        "id": "p-mum-hro-001",
        "name": "Dr. Nisha D'Souza",
        "specialty": "high_risk_obstetrics",
        "subspecialty": "maternal fetal medicine",
        "credentials": "MBBS, MD (OB-GYN), Fellowship MFM (Australia)",
        "clinic_name": "Wockhardt Hospital",
        "city": "Mumbai",
        "address": "1877, Dr. Anandrao Nair Marg, Mumbai Central, Mumbai 400011",
        "latitude": 18.9720, "longitude": 72.8190,
        "phone": "+91-7249362032",
        "services": ["high-risk pregnancy management", "fetal echocardiography", "amniocentesis", "cervical cerclage"],
        "insurance": ["Star Health", "New India Assurance", "Aditya Birla Health"],
        "availability": [
            {"day": "monday", "start": "08:00", "end": "14:00"},
            {"day": "wednesday", "start": "08:00", "end": "14:00"},
            {"day": "friday", "start": "08:00", "end": "14:00"},
        ],
    },

    # --- Mumbai: urogynecology ---
    # hallucination probe: no coordinates, no availability
    {
        "id": "p-mum-uro-001",
        "name": "Dr. Manasi Patel",
        "specialty": "urogynecology",
        "credentials": "MBBS, MS (OB-GYN), Fellowship Urogynecology",
        "clinic_name": "Patel Urogynaecology Clinic",
        "city": "Mumbai",
        "address": "Dadar (W), Mumbai",
        "latitude": None, "longitude": None,
        "phone": "+91-7249362032",
        "services": ["urinary incontinence treatment", "pelvic organ prolapse repair"],
        "insurance": ["ICICI Lombard", "Bajaj Allianz"],
        "availability": [],
    },

    # --- Mumbai: breast_health ---
    {
        "id": "p-mum-breast-001",
        "name": "Dr. Chitra Sundaram",
        "specialty": "breast_health",
        "subspecialty": "onco-surgery — breast",
        "credentials": "MBBS, MS (Surgery), Fellowship Breast Surgery (Tata Memorial)",
        "clinic_name": "Tata Memorial Hospital",
        "city": "Mumbai",
        "address": "Dr. Ernest Borges Rd, Parel, Mumbai 400012",
        "latitude": 19.0040, "longitude": 72.8430,
        "phone": "+91-7249362032",
        "services": ["breast examination", "breast biopsy", "breast conservation surgery", "sentinel lymph node biopsy"],
        "insurance": ["Star Health", "New India Assurance", "HDFC ERGO", "Care Health"],
        "availability": [
            {"day": "monday", "start": "09:00", "end": "15:00"},
            {"day": "wednesday", "start": "09:00", "end": "15:00"},
            {"day": "friday", "start": "09:00", "end": "13:00"},
        ],
    },

    # --- Mumbai: menopause ---
    {
        "id": "p-mum-meno-001",
        "name": "Dr. Sarita Bhat",
        "specialty": "menopause",
        "credentials": "MBBS, MD (OB-GYN), Certified Menopause Practitioner (IMS)",
        "clinic_name": "Bombay Hospital",
        "city": "Mumbai",
        "address": "12, New Marine Lines, Mumbai 400020",
        "latitude": 18.9430, "longitude": 72.8270,
        "phone": "+91-7249362032",
        "services": ["menopause counseling", "HRT management", "osteoporosis screening"],
        "insurance": ["Star Health", "ICICI Lombard", "Niva Bupa"],
        "availability": [
            {"day": "tuesday", "start": "11:00", "end": "17:00"},
            {"day": "thursday", "start": "11:00", "end": "17:00"},
        ],
    },

    # --- Mumbai: perinatal_mental_health ---
    # hallucination probe: no credentials
    {
        "id": "p-mum-pmh-001",
        "name": "Dr. Aditi Ranade",
        "specialty": "perinatal_mental_health",
        "credentials": None,
        "clinic_name": "Mind Matters Clinic",
        "city": "Mumbai",
        "address": "Bandra (W), Mumbai 400050",
        "latitude": 19.0600, "longitude": 72.8360,
        "phone": "+91-7249362032",
        "services": ["postpartum depression screening", "prenatal anxiety counseling"],
        "insurance": ["Bajaj Allianz", "Care Health"],
        "availability": [
            {"day": "monday", "start": "10:00", "end": "16:00"},
            {"day": "thursday", "start": "10:00", "end": "16:00"},
        ],
    },

    # --- Mumbai: pelvic_floor_physio ---
    {
        "id": "p-mum-pf-001",
        "name": "Nikita Chavan",
        "specialty": "pelvic_floor_physio",
        "credentials": "BPTh, MPTh (Musculoskeletal), CAPP-Pelvic",
        "clinic_name": "Restore Pelvic Health",
        "city": "Mumbai",
        "address": "Linking Rd, Khar (W), Mumbai 400052",
        "latitude": 19.0720, "longitude": 72.8340,
        "phone": "+91-7249362032",
        "services": ["pelvic floor assessment", "pre/postnatal exercise therapy", "incontinence rehab"],
        "insurance": ["Star Health"],
        "availability": [
            {"day": "monday", "start": "07:00", "end": "13:00"},
            {"day": "tuesday", "start": "07:00", "end": "13:00"},
            {"day": "wednesday", "start": "07:00", "end": "13:00"},
            {"day": "thursday", "start": "07:00", "end": "13:00"},
            {"day": "friday", "start": "07:00", "end": "13:00"},
        ],
    },

    # --- Mumbai: adolescent_gynecology ---
    {
        "id": "p-mum-adol-001",
        "name": "Dr. Yamini Thakur",
        "specialty": "adolescent_gynecology",
        "credentials": "MBBS, MD (OB-GYN), Diploma Adolescent Medicine",
        "clinic_name": "Nanavati Max Hospital",
        "city": "Mumbai",
        "address": "SV Rd, Vile Parle (W), Mumbai 400056",
        "latitude": 19.0980, "longitude": 72.8430,
        "phone": "+91-7249362032",
        "services": ["adolescent menstrual counseling", "puberty education", "HPV vaccination counseling"],
        "insurance": ["New India Assurance", "HDFC ERGO", "ManipalCigna"],
        "availability": [
            {"day": "wednesday", "start": "15:00", "end": "19:00"},
            {"day": "saturday", "start": "10:00", "end": "14:00"},
        ],
    },
]


def _build_embed_text(data: dict) -> str:
    """Combine specialty + services into a single string for embedding.

    This is what the semantic search compares against patient symptoms.
    """
    parts = [data["specialty"].replace("_", " ")]
    parts.extend(data.get("services", []))
    return ", ".join(parts)


def seed():
    """Wipe synthetic providers and re-insert from PROVIDERS list.

    Each provider gets a 384-dim embedding vector built from their
    specialty + services text, so semantic search can match patient
    symptoms to provider capabilities via cosine similarity.
    """
    init_db()
    collection = get_providers_collection()

    # remove old synthetic data
    deleted = collection.delete_many({"is_synthetic": True})
    print(f"Removed {deleted.deleted_count} old synthetic providers")

    # build embedding texts for the whole batch at once (faster)
    embed_strings = [_build_embed_text(d) for d in PROVIDERS]
    embeddings = embed_texts(embed_strings)

    docs = []
    for data, embedding in zip(PROVIDERS, embeddings):
        doc = {
            "_id": data["id"],
            "name": data["name"],
            "specialty": data["specialty"],
            "subspecialty": data.get("subspecialty"),
            "credentials": data.get("credentials"),
            "clinic_name": data.get("clinic_name"),
            "city": data["city"],
            "address": data.get("address"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "phone": data.get("phone"),
            "services": data.get("services", []),
            "insurance": data.get("insurance", []),
            "availability": data.get("availability", []),
            "is_synthetic": True,
            "is_active": True,
            "embedding": embedding,
        }
        docs.append(doc)

    collection.insert_many(docs)
    print(f"Seeded {len(docs)} synthetic providers into MongoDB (sakhi.providers)")


if __name__ == "__main__":
    seed()
