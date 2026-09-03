"""
Comprehensive Seed Script for CampusAI Database
Populates local SQLite database and Supabase Cloud Database with realistic, highly detailed
college regulations, rules, hostel policies, examination rules, fee structures, placement policies,
library rules, IT guidelines, admissions processes, scholarships, and campus frameworks.

Run: python seed_comprehensive_college_data.py
"""

import os
import sys
import uuid
import json
import sqlite3
from datetime import datetime, timezone

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
2. Mess Bill & Fee Structure: Monthly mess bill is calculated on a dividing system basis (approx. Rs. 3,800 to Rs. 4,500 per month). Mess bill must be paid by the 10th of every month. Late fee of Rs. 50 per day applies after due date.
3. Quiet Hours: 10:00 PM to 6:00 AM is designated quiet hours. Playing loud music, shouting, or causing disturbance in corridors is strictly forbidden."""
            },
            {
                "page": 3,
                "content": """Hostel Visitors, Maintenance and Disciplinary Rules:
1. Guest Policy: Parents and authorized local guardians may visit hostellers in the Hostel Visitor Room between 4:30 PM and 6:30 PM on working days, and 10:00 AM to 6:00 PM on holidays. No male visitors are permitted inside Girls' Hostel rooms.
2. Prohibited Items: Electric heaters, hot plates, immersion rods, air conditioners, alcohol, tobacco, contraband, and dangerous weapons are strictly banned. Violation leads to immediate eviction and Rs. 5,000 fine.
3. Room Allocation: Rooms are allocated annually on merit-cum-distance basis during semester registration."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Fee Structure, Payment Deadlines and Scholarship Schemes",
        "description": "Tuition fees for B.Tech, M.Tech, MCA, MBA, hostel fees, payment schedules, penalty for late payment, refund rules, and merit/means scholarships.",
        "category": "Fees & Scholarships",
        "file_name": "fee_structure_scholarships.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Tuition Fee Structure (Per Semester):
1. B.Tech (Merit Seat): Rs. 37,500 per semester.
2. B.Tech (Management Seat): Rs. 65,000 per semester.
3. B.Tech (NRI Quota): Rs. 1,00,000 per semester.
4. M.Tech / MCA: Rs. 42,000 per semester.
5. MBA: Rs. 55,000 per semester.
6. Other Annual One-Time Fees: Admission Fee: Rs. 1,500; Caution Deposit (Refundable): Rs. 10,000; University Exam Registration: Rs. 1,800 per semester; Library & Internet Fee: Rs. 2,500/year; Student Insurance: Rs. 500/year."""
            },
            {
                "page": 2,
                "content": """Payment Deadlines, Penalties and Scholarship Schemes:
1. Fee Payment Schedule: Semester fees must be paid online via the SBI Collect / Student Portal within 15 days from the date of semester commencement.
2. Late Payment Penalty:
- First 10 days post due date: Fine of Rs. 100 per day.
- Next 15 days: Fine of Rs. 250 per day.
- Beyond 25 days: Student name is removed from roll calls and portal login is suspended until cleared with HOD approval.
3. Institutional Scholarships:
- Merit Scholarship: 100% tuition fee waiver for top 3 rank holders in university entrance exams.
- Merit-Cum-Means Scholarship: 50% tuition fee waiver for students with SGPA > 8.0 and annual family income below Rs. 2.5 Lakhs.
- Sports Excellence Scholarship: Rs. 15,000 per year for state/national players."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Training & Placement Cell (TPC) Guidelines and Code of Conduct",
        "description": "Eligibility criteria for campus recruitment, dream company policy, code of conduct during placement drives, resume verification, and internship guidelines.",
        "category": "Placements",
        "file_name": "placement_cell_guidelines.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Placement Eligibility and Registration:
1. Eligibility Criteria: Students must have a minimum cumulative CGPA of 6.0 (60%) with no active standing backlogs at the time of recruitment registration.
2. TPC Registration: Final year students must register with the Placement Cell during 6th semester by paying a one-time registration fee of Rs. 1,000.
3. Placement Rule - One Student One Job Policy: Once a student receives a job offer (Offer Letter / Email Intent), they are considered 'PLACED' and are de-registered from subsequent campus placement drives, with the exception of the 'Dream Company Option'."""
            },
            {
                "page": 2,
                "content": """Dream Company Policy and Placement Conduct:
1. Dream Company Option: A placed student holding a job offer with Package X is permitted to participate in a 'Dream Company' drive ONLY if the offered package is at least 1.5 times higher (150%+) than their current offer.
2. Absenteeism Fine: Registering for a campus placement drive and failing to appear for the test/interview without 24-hour prior written medical excuse results in automatic suspension from the next 3 placement drives.
3. Dress Code & Discipline: Candidates must be dressed strictly in formal business attire (dark blazer, tie, formal trousers, polished shoes). Professional decorum must be maintained during pre-placement talks (PPT)."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Central Library Rules, Book Circulation and Digital Resources",
        "description": "Library working hours, borrowing limits, late return fine, digital library access (IEEE, Springer), quiet study rules, and lost book replacement policy.",
        "category": "Library Services",
        "file_name": "library_rules_services.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Library Timings and Book Circulation Rules:
1. Working Hours:
- General Library: 8:00 AM to 8:00 PM on all working days.
- Central Reading Hall: Open 24/7 during end-semester examination months.
- Sunday & Public Holidays: 9:00 AM to 4:00 PM.
2. Book Borrowing Limits & Duration:
- Undergraduate (UG) Students: 4 books for 14 days.
- Postgraduate (PG) Students: 6 books for 21 days.
- Faculty Members: 10 books for 90 days.
3. Book Renewal: Books can be renewed once for an additional 14 days provided there are no pending reservations by other users."""
            },
            {
                "page": 2,
                "content": """Overdue Fines, Lost Books and Digital Library:
1. Overdue Fine: Rs. 2 per day per book for the first 7 overdue days; Rs. 5 per day per book thereafter.
2. Lost Book Policy: If a borrowed book is lost, the borrower must replace the book with the latest edition OR pay double the current market price of the book plus 15% handling charges.
3. Digital Resources & E-Journals: Central Library subscribes to IEEE Xplore Digital Library, SpringerLink, ScienceDirect, Elsevier, and NPTEL video lectures. Off-campus remote access is provided via Knimbus portal using student institutional email ID."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Campus IT Facilities, WiFi Usage and Cyber Security Policy",
        "description": "Student WiFi login setup, MAC address binding, bandwidth quota, lab security policy, software licensing, and acceptable IT usage policy.",
        "category": "IT & Campus Facilities",
        "file_name": "it_wifi_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus WiFi Registration and Internet Usage:
1. WiFi Access: High-speed campus-wide 1 Gbps fiber internet connection is available for all registered students across academic blocks, labs, and hostels.
2. Device Registration & MAC Binding: Students must register their laptop/mobile MAC address on the Campus IT Portal (http://wifi.campus.internal) using institutional credentials (@college.edu). Maximum 2 devices allowed per student.
3. Bandwidth Limit: 20 GB high-speed quota per student per month. Speeds throttled to 2 Mbps after exhaustion of monthly quota.
4. Banned Activities: BitTorrent / P2P file sharing, accessing copyrighted pirated material, pornographic content, darknet, or executing network scanning tools is strictly prohibited. Campus firewall logs all active traffic with user IP mapping."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Anti-Ragging Regulations, Discipline and Redressal Cell",
        "description": "UGC mandated anti-ragging policies, anti-ragging squad contacts, disciplinary committee procedures, penalties, and helpline numbers.",
        "category": "Discipline & Anti-Ragging",
        "file_name": "anti_ragging_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Anti-Ragging Policy and Zero Tolerance Framework:
1. Zero Tolerance Policy: Ragging in any form (physical, verbal, mental harassment, teasing, or demanding unnatural tasks) inside or outside the campus is a cognizable criminal offense under UGC Regulations 2009.
2. Mandatory Affidavit: Every student and parent must submit an online Anti-Ragging Undertaking at www.antiragging.in during annual registration.
3. Anti-Ragging Helpline & Contacts:
- National Toll-Free Anti-Ragging Helpline: 1800-180-5522 (24x7)
- Campus Anti-Ragging Squad Hotline: +91 94470 12345 / anti-ragging@college.edu
- Nodal Officer Contact: Prof. K. R. Nair (Mob: +91 98460 98765)."""
            },
            {
                "page": 2,
                "content": """Penalties for Ragging and Disciplinary Actions:
Any student found guilty of ragging by the Anti-Ragging Committee will face one or more of the following punishments:
1. Immediate suspension from attending classes and academic privileges.
2. Expulsion from the hostel and forfeiture of hostel security deposit.
3. Debarring from appearing in mid-term or end-semester examinations.
4. Cancellation of admission and rustication from the institution for periods ranging from 1 to 4 semesters.
5. Filing of First Information Report (FIR) with the local police station leading to legal prosecution."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Clubs, Sports, NSS, NCC and Extracurricular Activity Credits",
        "description": "Overview of student clubs, IEEE/ACM chapters, NSS, NCC units, annual tech fest, cultural fest, and activity credits required for graduation.",
        "category": "Clubs & Extracurriculars",
        "file_name": "clubs_extracurricular_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Student Activity Points and Extracurricular Credits:
1. Mandatory Activity Points: As per university regulations, every B.Tech student must earn a minimum of 100 Activity Points during their 4-year program to be eligible for degree award.
2. Activity Point Allocation Examples:
- NSS / NCC participation (2 years completed): 60 Activity Points
- Executive Committee Member of Student Club / Society: 15 Points per year
- Winner in National Level Tech Fest / Hackathon: 30 Points
- Organizer of College Tech Fest / Cultural Fest: 20 Points
- Paper publication in Scopus indexed journal: 40 Points
- Sports Representation (University Level): 30 Points."""
            },
            {
                "page": 2,
                "content": """Campus Student Organizations and Major Events:
1. Technical Chapters: IEEE Student Branch, ACM Chapter, SAE India Club, Robotics & AI Club, Coding Club.
2. Cultural & Creative Clubs: Music Club (Acoustics), Dance Club, Drama & Literary Society, Photography Club.
3. Major Annual Events:
- 'INNOVISION' — Annual National Level Inter-College Technical Symposium & Hackathon (conducted in October).
- 'SANGAM' — Annual Cultural Festival & Music Night (conducted in February).
- 'OLYMPIA' — Annual Inter-Departmental Sports Tournament (conducted in January)."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Campus Infirmary, Medical Center and Health Emergency Services",
        "description": "24/7 medical center facilities, resident doctor availability, ambulance services, medical insurance coverage, and emergency contacts.",
        "category": "Health & Medical",
        "file_name": "medical_infirmary_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Health Center and Emergency Medical Services:
1. Medical Center Location & Hours: Located next to Boys Hostel Block 2. Operates 24x7 with resident medical officer and trained nursing staff.
2. Doctor Consultation Timings: Out-Patient (OP) consultations: 9:00 AM to 1:00 PM and 4:00 PM to 7:00 PM on working days. Emergency services available round-the-clock.
3. Emergency Contacts:
- Medical Center Reception: Ext. 4444 / Mobile: +91 94460 11111
- 24/7 Campus Ambulance Service: +91 94460 22222
4. Student Health Insurance: All enrolled students are automatically covered under the Group Mediclaim Insurance Policy up to Rs. 1,00,000 for emergency hospitalization due to accident or sudden illness."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Canteen, Dining Hall and Transportation Services",
        "description": "Food court timings, hygiene standards, daily bus routes, bus pass fee structure, and campus vehicle rules.",
        "category": "Campus Services",
        "file_name": "canteen_transport_services.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Canteen and Transport Facilities:
1. Central Food Court: Functions from 7:30 AM to 8:30 PM. Serves South Indian, North Indian, snacks, fresh juice counter, and bakery items. Food hygiene is regularly audited by the FSSAI-certified Food Quality Committee.
2. Campus Bus Transport: Fleet of 18 college buses operate across major city routes picking up day-scholar students and staff.
3. Transport Fee & Bus Pass: Annual transport fee ranges from Rs. 12,000 to Rs. 18,000 depending on distance zone. Bus passes are issued per semester upon payment receipt. RFID bus pass scanning is mandatory while boarding."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Admission Process, Eligibility Criteria and Application Procedures",
        "description": "Detailed guidelines for admission into UG & PG courses, eligibility criteria, entrance exams (JEE, KEAM, GATE, CAT, CUET), seat allocation, required documents, and admission calendar 2024-2026.",
        "category": "Admissions",
        "file_name": "admission_guidelines_2026.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Comprehensive Admission Guidelines and Eligibility Criteria:
1. B.Tech Admissions:
- Entrance Exams: Admission is offered through JEE Main / State Level Engineering Entrance (KEAM / CET) centralized counselling.
- Eligibility: Passed 10+2 (Higher Secondary) with Minimum 50% aggregate marks in Physics, Chemistry, and Mathematics (PCM) combined (45% for SC/ST/OBC).
- Direct / Management Quota: 30% of total seats are reserved for Management Quota based on 10+2 PCM merit and rank in entrance test.
2. B.Sc / BCA / B.Com Admissions: Passed 10+2 with minimum 45% aggregate marks from a recognized board. Selection based on Merit in qualifying 12th board exam.
3. Lateral Entry to 2nd Year B.Tech: Passed 3-year Diploma in Engineering with minimum 60% marks or B.Sc (Mathematics) with minimum 60% marks."""
            },
            {
                "page": 2,
                "content": """Postgraduate (PG) Admission Criteria:
1. M.Tech Program:
- Eligibility: Bachelor's Degree in Engineering/Technology (B.E./B.Tech) with CGPA >= 6.0 or 60% aggregate marks.
- Selection: Valid GATE score candidates get preference and monthly AICTE stipend (Rs. 12,400/month). Non-GATE candidates are selected based on Institutional Entrance Test & Interview.
2. MBA Program:
- Eligibility: Bachelor's degree in any discipline with minimum 50% aggregate marks.
- Entrance Exams: Valid score in CAT / MAT / CMAT / KMAT followed by Group Discussion (GD) and Personal Interview (PI).
3. MCA Program: Passed BCA / B.Sc (Computer Science / IT) or Graduation with Mathematics at 10+2 level with minimum 50% marks. Admission via MCA Entrance Test."""
            },
            {
                "page": 3,
                "content": """Required Admission Documents & Admission Calendar 2026:
1. Required Documents Checklist during Physical Reporting:
- Allotment Memo & Fee Receipt
- 10th / SSLC Marksheet & Passing Certificate (Original + 3 copies)
- 12th / Higher Secondary Marksheet & Pass Certificate (Original + 3 copies)
- Graduation Degree Certificate & Consolidated Marksheets (for PG applicants)
- Entrance Exam Score Card & Admit Card (JEE / KEAM / GATE / CAT)
- Transfer Certificate (TC) & Conduct Certificate from last attended institution
- Migration Certificate (for boards other than State Board)
- Category / Caste / EWS Certificate (if seeking reservation benefit)
- Passport-sized Photographs (6 copies)
2. Tentative Admission Calendar 2026:
- Online Application Opens: June 1st week
- Last Date for Online Application: July 15th
- Merit List & First Seat Allotment: July 25th
- Document Verification & Fee Payment: August 1st to August 10th
- Commencement of Classes: August 16th."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "International Students, NRI Quota & Foreign Student Admissions",
        "description": "Guidelines for foreign nationals, Persons of Indian Origin (PIO), Overseas Citizens of India (OCI), and Non-Resident Indian (NRI) quota admissions.",
        "category": "Admissions",
        "file_name": "nri_international_admissions.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """NRI and Foreign National Admission Guidelines:
1. NRI Quota Seats: 15% of total approved seat intake in each B.Tech branch is allocated for NRI sponsorship candidates as per AICTE guidelines.
2. Eligibility for NRI Seats:
- Passed 10+2 or equivalent examination abroad / India with Physics, Chemistry, and Mathematics. Minimum 50% aggregate in PCM.
- Candidate must be a child / dependent of a Non-Resident Indian (NRI) with valid NRI status certificate from Embassy / Indian Consulate.
3. Required Documents for NRI Admission:
- NRI Sponsor Declaration Affidavit (Notarized)
- Copy of Sponsor's valid Passport and Visa / Work Permit
- Embassy Certificate proving NRI status of sponsor
- Relationship Certificate issued by Revenue Authority
4. Fee Structure for NRI Students: Tuition fee is $2,500 USD per year (or equivalent in INR) plus one-time registration fee of $500 USD."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Scholarship Portal, Government Grants & Financial Assistance",
        "description": "Comprehensive info on National Scholarship Portal (NSP), State Post-Matric Scholarships, Central Sector Schemes, Pragati & Saksham AICTE scholarships.",
        "category": "Fees & Scholarships",
        "file_name": "government_scholarships_guide.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Government & Central Scholarship Schemes:
1. National Scholarship Portal (NSP): Students can apply for Central Sector Scheme of Top Class Education, Post-Matric Scholarship for SC/ST/OBC, and Minority Scholarships at www.scholarships.gov.in.
2. AICTE Pragati Scholarship for Girl Students: Rs. 50,000 per annum for eligible female students admitted into 1st year B.Tech/Diploma (family income < Rs. 8 Lakhs).
3. AICTE Saksham Scholarship for Specially-Abled Students: Rs. 50,000 per annum for differently-abled students with disability >= 40%.
4. College Nodal Officer Assistance: The Scholarship Helpdesk located at Administrative Block Room 104 assists with online verification, document uploading, and income certificate renewal."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Student Rights, Grievance Redressal and Equal Opportunity Cell",
        "description": "Structure of Student Grievance Redressal Committee (SGRC), Internal Complaints Committee (ICC), SC/ST Cell, and equal opportunity guidelines.",
        "category": "Discipline & Grievance",
        "file_name": "grievance_redressal_cell.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Student Grievance Redressal Mechanism:
1. Student Grievance Redressal Committee (SGRC): Provides a fair, transparent platform for resolving academic, fee, evaluation, or harassment complaints.
2. Online Grievance Portal: Complaints can be lodged anonymously or directly at http://grievance.college.edu.
3. Internal Complaints Committee (ICC): Banned harassment of women at workplace/campus as per PoSH Act 2013. Convener Contact: Dr. S. Lakshmi (+91 94470 33333).
4. Equal Opportunity Cell (EOC): Ensures non-discrimination and special guidance for SC/ST/OBC, PwD, and economically weaker section students."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Campus Security, Parking Regulations and Visitor Guidelines",
        "description": "Campus entry gate security rules, vehicle parking passes, helmet rules, visitor entry logging, and CCTV monitoring.",
        "category": "Campus Security",
        "file_name": "security_parking_rules.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Security & Vehicle Regulations:
1. Vehicle Registration & Parking Pass: Two-wheelers and four-wheelers owned by students must be registered at the Security Office (Main Gate) to obtain a vehicle pass sticker.
2. Mandatory Helmet Rule: Riding two-wheelers inside campus without a helmet is strictly banned. Triple riding is punishable with an instant Rs. 500 fine and parking sticker cancellation.
3. Speed Limit: Maximum speed limit inside campus roads is 20 km/h. Honking near academic blocks and central library is prohibited.
4. CCTV Surveillance: Campus is under 24/7 CCTV camera coverage with centralized recording at the Security Control Room."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Research & Innovation Cell, Patent Support and Incubation Center",
        "description": "Funding for student innovative projects, startup incubation center, patent filing support, and undergraduate research fellowships.",
        "category": "Research & Innovation",
        "file_name": "research_incubation_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Campus Innovation & Startup Incubation Center:
1. Student Project Innovation Fund: Financial grant up to Rs. 50,000 awarded per semester to promising final-year B.Tech / M.Tech prototype projects selected by the Research Board.
2. Technology Business Incubator (TBI): Offers free co-working office space, high-speed internet, mentorship, and seed funding up to Rs. 5 Lakhs for student startups registered under the Incubation Cell.
3. Intellectual Property (IPR) & Patent Cell: Provides 100% financial reimbursement for patent application filing fees for inventions created by students and faculty."""
            }
        ]
    }
]

def seed_database():
    print("=" * 65)
    print("  CAMPUSAI — SEEDING UNIVERSAL COMPREHENSIVE COLLEGE DATA")
    print("=" * 65)

    # 1. Seed Local SQLite Database
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM document_chunks")
    cursor.execute("DELETE FROM documents")
    conn.commit()
    print("Cleaned existing documents & chunks from local SQLite database.")

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

            print(f"   -> Generating embedding for chunk {chunk_idx + 1}/{len(doc['chunks'])} (Page {page_num})...", flush=True)
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

    # 2. Seed Supabase Cloud Database if configured
    try:
        from app.database.supabase import get_supabase_admin_client
        sp = get_supabase_admin_client()
        print("\nCleaned old documents & chunks from Supabase Cloud Database...")
        sp.table("document_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        sp.table("documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        sp_docs = []
        sp_chunks = []

        # Read back from SQLite to ensure exact consistency
        cursor = sqlite3.connect(LOCAL_DB_PATH).cursor()
        cursor.execute("SELECT id, title, description, category, file_name, status, created_at, updated_at FROM documents")
        for row in cursor.fetchall():
            sp_docs.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "category": row[3],
                "file_name": row[4],
                "status": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            })

        cursor.execute("SELECT id, document_id, chunk_index, content, page_number, embedding, metadata, created_at FROM document_chunks")
        for row in cursor.fetchall():
            sp_chunks.append({
                "id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "content": row[3],
                "page_number": row[4],
                "embedding": json.loads(row[5]),
                "metadata": json.loads(row[6]),
                "created_at": row[7]
            })

        if sp_docs:
            sp.table("documents").insert(sp_docs).execute()
            print(f"Ingested {len(sp_docs)} Documents into Supabase Cloud Database.")
        if sp_chunks:
            # Insert chunks in batches of 10
            for i in range(0, len(sp_chunks), 10):
                sp.table("document_chunks").insert(sp_chunks[i:i+10]).execute()
            print(f"Ingested {len(sp_chunks)} Chunks into Supabase Cloud Database.")

    except Exception as e:
        print(f"\n[WARNING] Could not seed Supabase Cloud Database: {e}")

    invalidate_vector_cache()

    print("\n" + "=" * 65)
    print(f" SUCCESS: Ingested {len(DOCUMENTS)} Documents & {total_chunks} Chunks into SQLite & Supabase!")
    print("=" * 65)

if __name__ == "__main__":
    seed_database()
