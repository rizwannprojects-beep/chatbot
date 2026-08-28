"""
Comprehensive Seed Script for CampusAI Database
Populates local SQLite database with realistic, highly detailed college regulations,
rules, hostel policies, examination rules, fee structures, placement policies,
library rules, IT guidelines, and extracurricular frameworks based on top Indian institutes.

Run: .\.venv\Scripts\python seed_comprehensive_college_data.py
"""

import os
import sys
import uuid
import json
import sqlite3
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from app.database.db_service import LOCAL_DB_PATH, init_db
from app.ai.embedding_service import generate_embedding
from app.rag.vector_search import invalidate_vector_cache

init_db()

NOW = datetime.now(timezone.utc).isoformat()

DOCUMENTS = [
    {
        "id": str(uuid.uuid4()),
        "title": "Academic Regulations and Credit Grading System",
        "description": "Official regulations governing degree completion, CGPA/SGPA calculation, 10-point letter grading scale, credit requirements, and course registration.",
        "category": "Academic Regulations",
        "file_name": "academic_regulations_grading.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Academic Credit System and Degree Duration:
1. Degree Duration: The standard duration for B.Tech is 4 academic years (8 semesters), B.Sc/B.Com/BCA is 3 years (6 semesters), and M.Tech/MCA/MBA is 2 years (4 semesters). The maximum permissible period to complete a 4-year degree is 6 years (12 semesters).
2. Credit Requirements: B.Tech students must earn a minimum of 160 credits to graduate. Honors degree requires an additional 20 credits in specialized electives with a minimum cumulative GPA of 8.5. Minor degree requires 18 credits in a secondary discipline.
3. Credit Allocation: 1 hour of Lecture (L) per week = 1 credit; 1 hour of Tutorial (T) per week = 1 credit; 2 hours of Practical/Lab (P) per week = 1 credit."""
            },
            {
                "page": 2,
                "content": """10-Point Letter Grading Scale:
Performance is evaluated on a 10-point scale:
- Grade S (Outstanding): 10 Grade Points (90% to 100% marks)
- Grade A+ (Excellent): 9 Grade Points (85% to 89% marks)
- Grade A (Very Good): 8.5 Grade Points (80% to 84% marks)
- Grade B+ (Good): 8 Grade Points (75% to 79% marks)
- Grade B (Above Average): 7 Grade Points (65% to 74% marks)
- Grade C (Average): 6 Grade Points (55% to 64% marks)
- Grade P (Pass): 5 Grade Points (45% to 54% marks)
- Grade F (Fail): 0 Grade Points (Below 45% or End-Sem mark < 40%)
- Grade FE (Failed due to Attendance Shortage): 0 Grade Points (Attendance < 75%)
- Grade I (Incomplete): Temporary grade due to medical leave during exams."""
            },
            {
                "page": 3,
                "content": """SGPA and CGPA Calculation Formula:
1. Semester Grade Point Average (SGPA): SGPA = Sum of (Course Credits x Grade Points) / Sum of Course Credits for the semester.
2. Cumulative Grade Point Average (CGPA): CGPA = Sum of (Course Credits x Grade Points) for all passed courses across all semesters / Total Credits of all passed courses.
3. Classification of Degree:
- First Class with Distinction: CGPA >= 8.0 without any backlogs in any semester.
- First Class: CGPA >= 6.5.
- Second Class: CGPA >= 5.5 and < 6.5.
- Pass Class: CGPA >= 5.0 and < 5.5."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Attendance Policy and Duty Leave Regulations",
        "description": "Mandatory 75% attendance criteria, condonation of shortage, medical leave guidelines, and duty leave rules for sports, NSS, NCC, and tech fests.",
        "category": "Attendance & Leave",
        "file_name": "attendance_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Mandatory Attendance Rule:
1. Minimum 75% Attendance: A student must secure a minimum of 75% attendance in each registered course to be eligible to appear for the End Semester University Examination.
2. Attendance Shortage & Condonation:
- Attendance between 65% and 74%: Can be condoned by the Principal on genuine medical grounds or sanctioned extra-curricular representation.
- Condonation Fee: Rs. 500 per course. Condonation can be availed maximum twice during the entire degree program.
- Attendance below 65%: Strictly NOT eligible for condonation. The student is awarded 'FE' grade, detained from the examination, and must repeat the course when offered in subsequent semesters."""
            },
            {
                "page": 2,
                "content": """Duty Leave and Medical Leave Rules:
1. Medical Leave: Medical certificates signed by a registered medical practitioner must be submitted to the Head of Department (HOD) within 3 working days of returning to college along with a leave application counter-signed by the parent/guardian.
2. Duty Leave (DL): Duty leave up to a maximum of 10 working days per semester is granted for:
- Representing the college in Inter-College / University / State level Sports tournaments.
- Participating in NSS / NCC camps and parades.
- Paper presentation in National / International conferences or winning technical competitions in top institutions.
3. Duty Leave Procedure: Duty leave applications must be pre-approved by the Faculty Advisor and HOD before attending the event."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Examination, Internal Evaluation and Revaluation System",
        "description": "Rules for internal continuous evaluation, series examinations, end-semester university exams, revaluation, scrutiny, and supplementary exams.",
        "category": "Examinations",
        "file_name": "exam_evaluation_rules.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Internal Assessment and Evaluation Breakdown:
Total Course Evaluation = 100 Marks (Internal Assessment: 40 Marks, End Semester Exam: 60 Marks).
Internal Assessment (40 Marks) Breakdown:
- Series Test 1 (Mid-Semester Exam 1): 12.5 Marks (held in 5th week of semester)
- Series Test 2 (Mid-Semester Exam 2): 12.5 Marks (held in 11th week of semester)
- Assignments / Seminars / Mini-Projects: 10 Marks (minimum 2 assignments per course)
- Class Attendance & Participation: 5 Marks (90%+ = 5 marks, 85-89% = 4, 80-84% = 3, 75-79% = 2 marks).
Minimum Internal Requirement: A student must secure a minimum of 45% (18 out of 40) in internal assessment to be eligible for the end semester examination."""
            },
            {
                "page": 2,
                "content": """End Semester Examination and Revaluation Rules:
1. End Semester Exam: Duration is 3 hours for 60 marks. Minimum passing mark in End-Sem exam is 40% (24 out of 60 marks). Overall course pass mark is 45% (internal + end-sem combined).
2. Revaluation Policy: Students dissatisfied with their end-semester marks can apply for online revaluation within 10 days of result publication.
- Revaluation Fee: Rs. 600 per answer script.
- Scrutiny Fee: Rs. 200 per answer script (for checking addition errors and unvaluated answers).
- Copy of Answer Script: Rs. 500 per paper.
3. Supplementary Examinations: Conducted twice a year — during July (summer vacation) and January (winter break). Students with 'F' or 'FE' grades must register for supplementary exams by paying Rs. 250 per paper."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Hostel Residence Rules, Curfew Timings and Guest Policies",
        "description": "Comprehensive hostel rules for boys and girls, night curfew times, gate pass procedures, mess charges, quiet hours, and anti-ragging in hostels.",
        "category": "Hostel & Housing",
        "file_name": "hostel_rules_regulations.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Hostel Curfew and Entry/Exit Timings:
1. Curfew Timings:
- Girls' Hostel Gate Close Time: 8:30 PM strictly. Late entry after 8:30 PM requires prior written approval from Warden and SMS notification to parents.
- Boys' Hostel Gate Close Time: 9:30 PM strictly. Campus main gate closes for hostelers at 9:30 PM.
2. Morning Gate Opening: Hostel gates open at 6:00 AM daily.
3. Out-Pass & Night Leave Procedure: Students leaving hostel overnight or for weekend home visits must submit an online Gate Pass request on the student portal at least 24 hours prior. Parent confirmation via registered mobile number is compulsory before Warden approval."""
            },
            {
                "page": 2,
                "content": """Hostel Mess Timings, Charges and Quiet Hours:
1. Mess Timings:
- Breakfast: 7:30 AM to 8:45 AM
- Lunch: 12:30 PM to 1:45 PM
- Evening Tea & Snacks: 4:30 PM to 5:30 PM
- Dinner: 7:30 PM to 9:00 PM
2. Mess Charges: Operates on a dividing system. Average monthly mess bill is approximately Rs. 3,800 to Rs. 4,200 depending on actual monthly consumption.
3. Quiet Study Hours: 10:00 PM to 6:00 AM. Playing loud music, shouting, or causing disturbance during quiet hours is strictly prohibited.
4. Visitors Policy: Parents and local guardians can visit students in the designated Hostel Visitor Lobby between 4:00 PM and 6:30 PM. No visitor or guest is permitted inside student rooms under any circumstances."""
            },
            {
                "page": 3,
                "content": """Prohibited Items and Safety Regulations in Hostels:
1. Electric Appliances: Possession or use of high-wattage electrical items such as electric kettles, induction stoves, room heaters, iron boxes, and immersion rods is strictly forbidden inside rooms. Violators face a fine of Rs. 1,000 and confiscation of the appliance.
2. Alcohol, Tobacco & Substance Abuse: Possession, sale, or consumption of liquor, cigarettes, e-cigarettes, or drugs inside hostel premises is a zero-tolerance offence resulting in immediate expulsion from the hostel, 1-year academic suspension, and reporting to law enforcement.
3. Room Maintenance: Students are responsible for furniture provided (cot, study table, chair, cupboard). Damage to property will be deducted from the hostel caution deposit."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Fee Structure, Payment Deadlines and Scholarship Schemes",
        "description": "Tuition fees for Govt/Management/NRI quotas, hostel fee structure, caution deposit refund procedure, E-Grantz, NSP, and Tuition Fee Waiver (TFW) schemes.",
        "category": "Fees & Scholarships",
        "file_name": "fee_structure_scholarships.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Annual Tuition and Special Fee Structure:
1. B.Tech Tuition Fee (Annual):
- Merit Quota (Govt Allotment): Rs. 35,000 per year.
- Management Quota: Rs. 65,000 per year.
- NRI Quota: Rs. 1,00,000 per year.
2. University & Special Fees (Annual):
- University Registration & Exam Fee: Rs. 3,200 / year
- Special Fees (Lab, Library, Sports, Cultural): Rs. 4,500 / year
- One-time Caution Deposit (Refundable at degree completion): Rs. 5,000
3. Payment Schedule: Semester fees must be paid within 15 working days of semester commencement. Late fee penalty: Rs. 50 per day for first 10 days, Rs. 100 per day thereafter."""
            },
            {
                "page": 2,
                "content": """Scholarships and Financial Assistance Schemes:
1. Tuition Fee Waiver (TFW) Scheme: 5% supernumerary seats in every branch are reserved under TFW. Full tuition fee waiver is provided to merit students whose annual family income is below Rs. 8.0 Lakhs.
2. E-Grantz Scholarship: Full fee exemption and monthly stipend for SC, ST, OEC, and eligible OBC students awarded by the State Government.
3. National Scholarship Portal (NSP): Central Sector Scheme for university students securing above 80th percentile in Higher Secondary exams. Financial aid of Rs. 12,000 per year for UG degree.
4. Merit Cum Means (MCM) Scholarship: Awarded to minority community students with family income < Rs. 2.5 Lakhs/year and minimum 50% marks."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Training & Placement Cell (TPC) Guidelines and Code of Conduct",
        "description": "Campus recruitment policy, eligibility criteria, One Student One Job rule, dream offer options, interview etiquette, and pre-placement training rules.",
        "category": "Placements",
        "file_name": "placement_policy_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Placement Eligibility Criteria:
1. Minimum CGPA Requirement: Students must maintain a minimum CGPA of 6.0 (or 60% aggregate) with no active backlogs to be eligible for Tier-1 campus placement drives (IT & Core engineering companies).
2. Training Attendance: 100% attendance in pre-placement soft skills, aptitude training, and mock technical interviews organized by the TPC is mandatory to participate in campus recruitment.
3. Registration: Eligible students must register with the TPC portal in the 6th semester by submitting verified marksheets and resumes."""
            },
            {
                "page": 2,
                "content": """Placement Rules - One Student One Job Policy:
1. One Job Rule: Once a student receives an official job offer from any campus recruiting company, they are considered 'Placed' and will be de-registered from attending further recruitment drives.
2. Exception - Dream Company Option: A placed student is allowed ONE additional opportunity to apply for a 'Dream Company' if the offered CTC is at least 1.5 times higher than their current offer (e.g. initial offer Rs. 4 LPA -> eligible for Dream drives offering >= Rs. 6 LPA).
3. Non-Attendance Penalty: Absenteeism from an interview after registering without valid medical emergency results in immediate debarment from the next 3 campus recruitment drives."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Central Library Rules, Book Circulation and Digital Resources",
        "description": "Library working hours, borrowing limits for UG/PG/Faculty, late fine fees, book renewal rules, digital library access, and quiet environment rules.",
        "category": "Library Services",
        "file_name": "library_rules_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Library Timings and Book Circulation Limits:
1. Working Hours:
- Monday to Friday: 8:00 AM to 8:00 PM
- Saturday: 9:00 AM to 4:00 PM (Closed on Sundays and Public Holidays)
2. Borrowing Entitlement:
- Undergraduate Students (B.Tech / B.Sc / BCA / B.Com): 4 books for 14 days.
- Postgraduate Students (M.Tech / MCA / MBA): 6 books for 21 days.
- Faculty Members: 10 books for 30 days.
3. Overdue Fine: Late return of books attracts a fine of Rs. 2.00 per book per day. Loss of library book requires replacement with latest edition or payment of 2x original book cost."""
            },
            {
                "page": 2,
                "content": """Digital Library, E-Journals and Reference Section:
1. Digital Library Section: Equipped with 40 high-speed multimedia terminals. Students can access e-journals (IEEE Xplore, ScienceDirect, SpringerLink, Elsevier) and NPTEL video lectures free of cost on campus.
2. Reference Section: Rare encyclopedias, handbooks, project reports, and bound volumes of journals are strictly for reference within the library reading hall and cannot be checked out.
3. Code of Conduct: Absolute silence must be maintained. Group discussions, eating, drinking, and mobile phone calls are strictly prohibited inside the library."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Campus IT Facilities, WiFi Usage and Cyber Security Policy",
        "description": "Student WiFi credentials, data quota limits, network security regulations, forbidden websites, lab equipment usage, and software copyright policies.",
        "category": "IT & Campus Facilities",
        "file_name": "campus_it_wifi_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus High-Speed WiFi and Data Quota Rules:
1. WiFi Credentials: Every student is provided with unique LDAP credentials (username and password) for connecting to the campus-wide secure WiFi network.
2. Monthly Data Quota: 15 GB high-speed data per student per month. Bandwidth speed is throttled to 2 Mbps after quota exhaustion.
3. Class Hours Restrictions: Entertainment streaming platforms (Netflix, YouTube 4K, Gaming servers) are restricted on campus WiFi during lecture hours (9:00 AM to 4:00 PM).
4. Cyber Security Violations: Using VPN bypasses, torrent downloads, unauthorized network scanning, or accessing illegal websites will lead to immediate MAC address blocking and disciplinary action by the IT Security Cell."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Anti-Ragging Regulations, Discipline and Redressal Cell",
        "description": "Zero tolerance anti-ragging policy, UGC mandates, Anti-Ragging Committee contacts, Student Grievance Cell, and disciplinary penalties for misconduct.",
        "category": "Discipline & Anti-Ragging",
        "file_name": "anti_ragging_discipline_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """UGC Anti-Ragging Mandate and Zero Tolerance Policy:
1. Zero Tolerance: Ragging in any form (physical, verbal, psychological, electronic) inside or outside the campus is strictly prohibited by law (Kerala Prohibition of Ragging Act, 1998 & UGC Regulations).
2. Mandatory Affidavit: Every student and parent must submit an online anti-ragging undertaking at www.antiragging.in during annual registration.
3. Penalties for Ragging: Suspension from classes, expulsion from hostel, cancellation of admission, and lodging of FIR with police. National Anti-Ragging Toll-Free Helpline: 1800-180-5522. Campus Anti-Ragging Squad Officer Contact: 9447012345."""
            },
            {
                "page": 2,
                "content": """Student Grievance Redressal and Disciplinary Action:
1. Disciplinary Committee: Misconduct such as destruction of college property, physical brawls, forgery, or examination malpractice is referred to the Staff Disciplinary Committee.
2. Examination Malpractice: Copying or carrying mobile phones/chits during exams results in cancellation of all papers in the semester and 1-year suspension.
3. Grievance Redressal Cell: Students can submit academic or administrative complaints online via the campus portal or drop written letters in the Grievance Box near the Administrative Block."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Clubs, Sports, NSS, NCC and Extracurricular Activity Credits",
        "description": "Student clubs (IEEE, GDSC, Robotics, Literary, Arts), Sports facilities, Gymnasium timings, NSS/NCC units, and 100 Activity Points requirement.",
        "category": "Clubs & Extracurriculars",
        "file_name": "extracurricular_clubs_sports.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """100 Activity Points Requirement for Degree:
1. Activity Points Mandate: To qualify for B.Tech degree, every student must earn a minimum of 100 Activity Points during their 4-year program through non-academic activities.
2. Activity Point Distribution:
- NSS / NCC Cadet (2 years active service): 60 Points
- Sports Tournament (University Winner / Runner-up): 40 Points
- Office Bearer of Student Clubs (IEEE / GDSC / Robotics / Arts): 15-25 Points
- Organizing Tech Fests / Cultural Events: 10-20 Points
- Social Service / Community Service (minimum 40 hours): 20 Points."""
            },
            {
                "page": 2,
                "content": """Sports Facilities and Gymnasium Timings:
1. Facilities Available: Synthetic Basketball Court, Football Ground, Cricket Nets, Volleyball Court, Indoor Badminton Courts, and Table Tennis Tables.
2. Campus Gymnasium Timings:
- Morning Session: 6:00 AM to 8:00 AM
- Evening Session: 4:30 PM to 7:30 PM
3. Equipment Issue: Sports equipment can be issued from the Physical Education Department against college ID card for up to 2 hours per day."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Campus Infirmary, Medical Center and Health Emergency Services",
        "description": "24/7 campus medical center, resident nurse, visiting doctor hours, emergency ambulance service, medical certificate validation, and student health insurance.",
        "category": "Health & Medical",
        "file_name": "medical_health_services.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Health Center and Emergency Medical Support:
1. Infirmary Services: 24/7 campus medical room equipped with first-aid, emergency beds, oxygen cylinders, and basic diagnostics located adjacent to the Main Hostel Block.
2. Doctor Consultation Hours: Visiting Medical Officer available Monday to Saturday from 4:00 PM to 6:00 PM. First-aid and basic medicines provided free of charge to all students.
3. Emergency Ambulance Service: Dedicated 24/7 campus ambulance available for immediate transfer to City Multispecialty Hospital. Emergency Contact Number: 0471-2555999 / 9447111222.
4. Student Health Insurance: Every registered student is covered under Group Medical Insurance up to Rs. 1,00,000 for accidental hospitalization."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Canteen, Dining Hall and Transportation Services",
        "description": "Campus cafeteria timings, food safety guidelines, subsidized pricing, college bus routes, vehicle parking permits, and traffic rules on campus.",
        "category": "Campus Services",
        "file_name": "canteen_transport_guidelines.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Canteen Timings and Food Hygiene:
1. Canteen Working Hours: 7:30 AM to 6:00 PM on all working days. Serves hygienic vegetarian and non-vegetarian meals, snacks, fresh juices, and beverages at subsidized student rates.
2. Food Safety: Monitored monthly by Food Safety Inspection Cell. Single-use plastic is strictly banned across all food stalls on campus.
3. College Bus Routes & Passes: Fleet of 15 college buses operates across major city routes. Semester bus pass must be renewed within 5 days of semester re-opening.
4. Vehicle Parking Rules: Student two-wheelers and cars must have valid campus parking sticker. Speed limit inside campus is 20 km/h. Helmets are mandatory for riders and pillion riders."""
            }
        ]
    }
]

def seed_database():
    print("=" * 65)
    print("  CAMPUSAI — SEEDING COMPREHENSIVE COLLEGE KNOWLEDGE BASE")
    print("=" * 65)

    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()

    # Clear existing documents and chunks to ensure clean state
    cursor.execute("DELETE FROM document_chunks")
    cursor.execute("DELETE FROM documents")
    conn.commit()
    print("Cleaned existing documents & chunks from database.")

    total_chunks = 0
    for doc_idx, doc in enumerate(DOCUMENTS, 1):
        print(f"\n[{doc_idx}/{len(DOCUMENTS)}] Processing: '{doc['title']}' ({doc['category']})")

        cursor.execute("""
            INSERT INTO documents (id, title, description, category, file_name, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'COMPLETED', ?, ?)
        """, (doc["id"], doc["title"], doc["description"], doc["category"], doc["file_name"], NOW, NOW))

        for chunk_idx, chunk_data in enumerate(doc["chunks"]):
            content = chunk_data["content"].strip()
            page_num = chunk_data.get("page", 1)

            print(f"   -> Generating embedding for chunk {chunk_idx + 1}/{len(doc['chunks'])} (Page {page_num})...")
            embedding = generate_embedding(content)

            chunk_id = str(uuid.uuid4())
            metadata = json.dumps({
                "document_title": doc["title"],
                "category": doc["category"],
                "page_number": page_num
            })

            cursor.execute("""
                INSERT INTO document_chunks (id, document_id, chunk_index, content, page_number, embedding, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (chunk_id, doc["id"], chunk_idx, content, page_num, json.dumps(embedding), metadata, NOW))

            total_chunks += 1

    conn.commit()
    conn.close()

    # Invalidate in-RAM vector cache so new embeddings are reloaded immediately
    invalidate_vector_cache()

    print("\n" + "=" * 65)
    print(f" SUCCESS: Ingested {len(DOCUMENTS)} Documents & {total_chunks} Chunks into CampusAI DB!")
    print(" RAM Vector Cache invalidated and ready for immediate instant lookup.")
    print("=" * 65)

if __name__ == "__main__":
    seed_database()
