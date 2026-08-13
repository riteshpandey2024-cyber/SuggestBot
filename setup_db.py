"""
setup_db.py — Create and seed the SuggestBot SQLite database with 60 diseases & treatment data.

Run this script:
    python3 setup_db.py
"""

import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "suggestbot.db")

SEED_DATA = [
    ("Diabetes", "Manage blood sugar through a balanced diet (low glycemic index foods), regular exercise (150 min/week), and medication such as Metformin or Insulin. Monitor HbA1c levels every 3 months. Maintain healthy weight and reduce stress."),
    ("Hypertension", "Adopt lifestyle modifications: reduce sodium intake (<2300 mg/day), follow the DASH diet, exercise regularly, limit alcohol. Medications include ACE inhibitors (Enalapril), ARBs (Losartan), or calcium channel blockers. Monitor BP daily."),
    ("Asthma", "Use rescue inhalers (Salbutamol/Albuterol) for acute attacks. Long-term control with inhaled corticosteroids (Fluticasone) and long-acting beta-agonists. Avoid known triggers (dust, pollen, smoke). Keep an action plan ready."),
    ("Malaria", "Antimalarial drugs: Chloroquine (for P. vivax) or Artemisinin-based Combination Therapy (ACT) for P. falciparum. Supportive care includes hydration and fever management. Prevent with mosquito nets and repellents."),
    ("Typhoid", "Antibiotics: Ciprofloxacin, Azithromycin, or Ceftriaxone depending on resistance. Supportive care: oral rehydration, rest, and a soft diet. Vaccination (Vi polysaccharide or Ty21a) for prevention."),
    ("Dengue", "No specific antiviral treatment. Supportive care: adequate fluid intake (ORS), rest, and Paracetamol for fever. AVOID Aspirin and NSAIDs (bleeding risk). Monitor platelet count. Hospitalize if severe (DHF/DSS)."),
    ("Common Cold", "Rest and hydration. Symptomatic relief: decongestants (Pseudoephedrine), antihistamines, throat lozenges, and warm saline gargles. Vitamin C and Zinc may shorten duration. Usually resolves in 7-10 days."),
    ("COVID-19", "Vaccination is primary prevention. Antivirals (Paxlovid/Nirmatrelvir-Ritonavir) for high-risk patients within 5 days of symptom onset. Supportive care: rest, fluids, Paracetamol. Seek emergency care for breathing difficulty."),
    ("Tuberculosis", "DOTS therapy: 2-month intensive phase (Isoniazid + Rifampicin + Pyrazinamide + Ethambutol) followed by 4-month continuation phase (Isoniazid + Rifampicin). Never skip doses. Regular sputum tests for monitoring."),
    ("Migraine", "Acute: Triptans (Sumatriptan), NSAIDs (Ibuprofen), or antiemetics. Preventive: Beta-blockers (Propranolol), antidepressants (Amitriptyline), or CGRP inhibitors. Avoid triggers: stress, poor sleep, certain foods, bright lights."),
    ("Pneumonia", "Bacterial: Antibiotics (Amoxicillin, Azithromycin, or Levofloxacin). Viral: Supportive care, antivirals if influenza-related. Rest, fluids, oxygen therapy if needed. Pneumococcal vaccine for prevention."),
    ("Anemia", "Iron-deficiency: Ferrous sulfate supplements, iron-rich diet (spinach, red meat, legumes), Vitamin C to boost absorption. B12 deficiency: Cyanocobalamin injections or oral supplements. Treat underlying cause."),
    ("Arthritis", "Osteoarthritis: NSAIDs, physical therapy, weight management, joint replacement if severe. Rheumatoid: DMARDs (Methotrexate), biologics (Adalimumab), corticosteroids. Regular exercise and anti-inflammatory diet."),
    ("Depression", "Psychotherapy (CBT, interpersonal therapy). Antidepressants: SSRIs (Fluoxetine, Sertraline) or SNRIs (Venlafaxine). Regular exercise, adequate sleep, social support. Severe cases may need combination therapy."),
    ("Allergies", "Avoid known allergens. Antihistamines (Cetirizine, Loratadine) for mild symptoms. Nasal corticosteroids (Fluticasone) for allergic rhinitis. Epinephrine auto-injector (EpiPen) for anaphylaxis. Immunotherapy for long-term control."),
    ("Gastritis", "Antacids (Aluminum/Magnesium hydroxide), PPIs (Omeprazole, Pantoprazole), or H2 blockers (Ranitidine). If H. pylori positive: triple therapy (PPI + Clarithromycin + Amoxicillin). Avoid spicy food, alcohol, and NSAIDs."),
    ("Thyroid Disorders", "Hypothyroidism: Levothyroxine replacement therapy, regular TSH monitoring. Hyperthyroidism: Antithyroid drugs (Methimazole), radioactive iodine, or surgery. Balanced iodine intake and regular follow-ups."),
    ("Kidney Stones", "Small stones: Hydration (2-3L/day), pain management (NSAIDs), alpha-blockers (Tamsulosin) to aid passage. Large stones: ESWL (shock wave lithotripsy), ureteroscopy, or PCNL. Dietary changes to prevent recurrence."),
    ("Conjunctivitis", "Bacterial: Antibiotic eye drops (Ciprofloxacin, Moxifloxacin). Viral: Supportive care, cold compresses, artificial tears. Allergic: Antihistamine drops (Olopatadine). Avoid touching eyes, practice hand hygiene."),
    ("Jaundice", "Treat underlying cause. Hepatitis: antivirals or supportive care. Obstructive: surgical intervention (ERCP, stenting). Neonatal: phototherapy. Adequate hydration, rest, and avoid hepatotoxic substances (alcohol, certain drugs)."),
    ("Alzheimer's Disease", "Memory care, cognitive training, Cholinesterase inhibitors (Donepezil, Rivastigmine), Memantine. Manage cardiovascular risk factors, maintain structured daily routines, and provide caregiver support."),
    ("Parkinson's Disease", "Dopamine replacement (Levodopa/Carbidopa), Dopamine agonists (Pramipexole), MAO-B inhibitors. Physical therapy, occupational therapy, speech therapy, and regular aerobic exercise."),
    ("Influenza", "Antivirals (Oseltamivir/Tamiflu) within 48 hours of onset. Supportive care: bed rest, hydration, acetaminophen or ibuprofen for fever and muscle aches. Annual flu vaccine for prevention."),
    ("GERD", "Lifestyle changes: avoid trigger foods (fatty, spicy, caffeine), elevate head during sleep, lose weight. Medications: H2 blockers (Famotidine) and PPIs (Omeprazole, Esomeprazole)."),
    ("Psoriasis", "Topical corticosteroids, Vitamin D analogues, Coal tar. Systemic treatments for severe cases: Methotrexate, Biologics (Adalimumab, Ustekinumab). Phototherapy (UVB radiation)."),
    ("Eczema", "Emollients and moisturizers after bathing, topical corticosteroids (Hydrocortisone), topical calcineurin inhibitors (Tacrolimus). Avoid harsh soaps, synthetic fabrics, and known skin allergens."),
    ("Insomnia", "Cognitive Behavioral Therapy for Insomnia (CBT-I). Sleep hygiene: fixed sleep schedule, avoid screens before bed, limit caffeine. Short-term sedative-hypnotics under strict medical supervision."),
    ("Anxiety Disorders", "Psychotherapy (CBT), SSRIs (Escitalopram, Sertraline), SNRIs (Venlafaxine), short-term Benzodiazepines for acute crises. Mindfulness, deep breathing exercises, and regular physical activity."),
    ("Bipolar Disorder", "Mood stabilizers (Lithium, Valproate), atypical antipsychotics (Quetiapine, Olanzapine), psychotherapy. Maintain strict sleep-wake cycles, avoid alcohol and recreational drugs."),
    ("Osteoporosis", "Bisphosphonates (Alendronate, Risedronate), Calcium (1000-1200 mg/day) and Vitamin D (800-1000 IU/day) supplementation. Weight-bearing exercises and home fall prevention strategies."),
    ("Gout", "Acute attacks: NSAIDs (Indomethacin), Colchicine, or systemic corticosteroids. Urate-lowering therapy for chronic prevention: Allopurinol or Febuxostat. Avoid high-purine foods and red meat."),
    ("Celiac Disease", "Strict, lifelong gluten-free diet (avoid wheat, barley, rye). Nutritional supplementation for deficiencies (Iron, Calcium, Vitamin D). Monitor anti-tTG antibody levels periodically."),
    ("Irritable Bowel Syndrome", "Dietary modifications (Low-FODMAP diet), fiber supplementation (Psyllium). Antispasmodics (Dicyclomine), antidiarrheals (Loperamide), or laxatives based on IBS subtype."),
    ("Crohn's Disease", "Corticosteroids for acute flares, Immunomodulators (Azathioprine, Methotrexate), Biologics (Infliximab, Adalimumab). Nutritional therapy, smoking cessation, and surgery for complications."),
    ("Ulcerative Colitis", "5-ASA compounds (Mesalamine, Sulfasalazine), Corticosteroids, Immunosuppressants, Biologics (Vedolizumab). Colectomy surgery for severe refractory cases or high dysplasia."),
    ("Chronic Kidney Disease", "Strict blood pressure and blood sugar control (ACE inhibitors/ARBs, SGLT2 inhibitors). Low-sodium and protein-controlled diet. Manage anemia and phosphate. Dialysis or kidney transplant in ESRD."),
    ("Hepatitis B", "Antiviral therapy (Entecavir, Tenofovir) for chronic active infection. Regular monitoring of liver function, AFP, and viral load. Hepatitis B vaccine for prevention."),
    ("Hepatitis C", "Direct-acting antivirals (DAAs like Sofosbuvir/Velpatasvir) for 8-12 weeks achieving high cure rates (>95%). Avoid alcohol and hepatotoxic medications."),
    ("PCOS", "Lifestyle changes (weight loss, low-GI diet). Combined oral contraceptives for cycle regulation. Metformin for insulin resistance, Clomiphene or Letrozole for fertility treatment."),
    ("Endometriosis", "NSAIDs for pain management. Hormonal therapies: combined oral contraceptives, progestins, GnRH agonists (Leuprolide). Laparoscopic conservative surgery or hysterectomy for severe cases."),
    ("Gallstones", "Asymptomatic: clinical observation. Symptomatic (biliary colic/cholecystitis): Laparoscopic cholecystectomy (surgical gallbladder removal). Ursodeoxycholic acid for non-surgical candidates."),
    ("Appendicitis", "Emergency surgical appendectomy (laparoscopic or open). IV antibiotics prior to surgery. Fluid resuscitation and pain management."),
    ("Sinusitis", "Viral/Mild: Nasal saline irrigation, decongestants, warm compresses, topical nasal corticosteroids (Fluticasone). Bacterial (>10 days/severe): Antibiotics like Amoxicillin-Clavulanate."),
    ("Bronchitis", "Acute (viral): Rest, fluids, cough suppressants, bronchodilator inhalers if wheezing. Chronic (COPD-related): Smoking cessation, long-acting bronchodilators, inhaled steroids, pulmonary rehab."),
    ("Otitis Media", "Analgesics (Paracetamol, Ibuprofen), warm compresses. Watchful waiting for 48-72 hrs in mild cases. Antibiotics (Amoxicillin) for severe pain, high fever, or infants <6 months."),
    ("Urticaria", "Second-generation H1 antihistamines (Cetirizine, Loratadine, Fexofenadine). High-dose antihistamines or short courses of systemic steroids (Prednisone) for severe acute outbreaks."),
    ("Shingles", "Antivirals (Valacyclovir, Acyclovir) started within 72 hours of rash onset. Analgesics, topical capsaicin, or Gabapentin for neuropathic pain. Recombinant Zoster Vaccine (Shingrix) for prevention."),
    ("Glaucoma", "Prostaglandin analog eye drops (Latanoprost), Beta-blockers (Timolol) to reduce intraocular pressure. Laser trabeculoplasty or trabeculectomy surgery for non-controlled cases."),
    ("Cataracts", "Early stages: updated prescription glasses, anti-glare sunglasses, brighter lighting. Definitive treatment: phacoemulsification surgery with intraocular lens (IOL) implantation."),
    ("Macular Degeneration", "Dry AMD: AREDS2 formula supplements (Vitamin C, E, Zinc, Lutein/Zeaxanthin). Wet AMD: Anti-VEGF intravitreal injections (Ranibizumab, Aflibercept) to prevent vision loss."),
    ("Hemochromatosis", "Therapeutic phlebotomy (regular blood removal) to maintain target ferritin levels (<50 ng/mL). Iron-chelating agents (Deferasirox) if phlebotomy is contraindicated. Avoid iron supplements."),
    ("Multiple Sclerosis", "Acute flares: high-dose IV corticosteroids (Methylprednisolone). Disease-modifying therapies (DMTs like Ocrelizumab, Interferon-beta, Fingolimod) to prevent relapses. Physical therapy."),
    ("Fibromyalgia", "Low-impact exercise, aerobic conditioning, CBT. Medications: SNRIs (Duloxetine), Anticonvulsants (Pregabalin, Gabapentin), Tricyclics (Amitriptyline). Avoid opioid analgesics."),
    ("Systemic Lupus", "Hydroxychloroquine for all patients. NSAIDs for joint pain, Systemic corticosteroids for flares. Immunosuppressants (Mycophenolate, Azathioprine, Belimumab) for organ involvement."),
    ("Gastroenteritis", "Rehydration is primary: Oral Rehydration Salts (ORS), clear fluids. Soft bland diet (BRAT). Antiemetics (Ondansetron) if severe vomiting. Avoid anti-diarrheal meds in invasive infection."),
    ("Vertigo", "BPPV: Epley maneuver / canalith repositioning procedures. Vestibular suppressants (Meclizine, Betahistine) for acute symptoms. Vestibular rehabilitation therapy."),
    ("Epilepsy", "Anti-seizure medications (Levetiracetam, Lamotrigine, Carbamazepine, Valproate). Ketogenic diet or vagus nerve stimulation for refractory cases. Avoid sleep deprivation and alcohol."),
    ("Psoriatic Arthritis", "NSAIDs for mild peripheral joint symptoms. DMARDs (Methotrexate, Sulfasalazine). Biologic therapies (TNF inhibitors like Etanercept, IL-17 inhibitors like Secukinumab) for severe disease."),
    ("Sleep Apnea", "Continuous Positive Airway Pressure (CPAP) therapy. Weight reduction, positional therapy, oral appliances. Surgical options (UPPP) for anatomical obstruction."),
    ("Hyperthyroidism", "Antithyroid drugs (Methimazole, Propylthiouracil), Beta-blockers (Propranolol) for symptom control. Radioactive Iodine (RAI) therapy or thyroidectomy for definitive management.")
]


def create_database():
    """Create the database and seed it with treatment data."""
    print(f"📦 Creating database at: {os.path.abspath(DB_PATH)}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create Treatment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Treatment (
            Disease TEXT PRIMARY KEY,
            treat TEXT NOT NULL
        );
    """)

    # Create ChatHistory table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ChatHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed treatment data (insert or replace to be idempotent)
    cur.executemany(
        "INSERT OR REPLACE INTO Treatment (Disease, treat) VALUES (?, ?)",
        SEED_DATA
    )

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM Treatment")
    count = cur.fetchone()[0]
    print(f"✅ Database updated with {count} total diseases!")

    conn.close()


if __name__ == "__main__":
    create_database()
