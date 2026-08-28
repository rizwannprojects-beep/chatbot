"""
Seed script to populate the CampusAI database with common Kerala college
rules, regulations, hostel policies, exam schedules, library info, fee
structures, and admission guidelines.

Run: python seed_kerala_data.py
"""

import os
import sys
import uuid
import json
import sqlite3
from datetime import datetime, timezone

# Add parent to path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.database.db_service import LOCAL_DB_PATH, init_db
from app.ai.embedding_service import generate_embedding

# Initialize DB tables if they don't exist
init_db()

NOW = datetime.now(timezone.utc).isoformat()

# ─── Kerala College Document Data ────────────────────────────────────────────

DOCUMENTS = [
    {
        "id": str(uuid.uuid4()),
        "title": "General College Rules and Code of Conduct",
        "description": "Comprehensive rules and regulations for students enrolled in the college, including disciplinary policies and dress code.",
        "category": "Rules & Regulations",
        "file_name": "college_rules_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """General College Rules and Code of Conduct

1. College Timings: The college functions from 9:00 AM to 4:00 PM on all working days (Monday to Friday). Saturday classes may be scheduled for arrear examinations and special sessions. Students must be present in the campus by 8:55 AM.

2. Attendance Policy: A minimum of 75% attendance is mandatory for all students to be eligible to appear for the end semester examinations, as per Kerala University regulations. Students falling below 75% attendance will be detained and will not be permitted to write the university examinations. Medical certificates for absence must be submitted within 7 days of rejoining.

3. Identity Card: Every student must carry their college identity card at all times within the campus. The ID card must be produced on demand by any faculty member, administrative staff, or security personnel. Loss of ID card must be reported immediately to the office and a duplicate card can be obtained by paying Rs. 200."""
            },
            {
                "page": 2,
                "content": """4. Dress Code: Students are expected to maintain a decent and formal dress code. On designated days, students must wear the prescribed college uniform. Wearing of shorts, sleeveless tops, and slippers is strictly prohibited inside the campus. First-year students must wear the college uniform on all working days.

5. Use of Mobile Phones: Mobile phones must be switched off or kept in silent mode during lecture hours and inside the library. Using mobile phones for recording lectures, taking photographs, or making videos without prior permission from the faculty is strictly prohibited. Violation will result in confiscation of the phone for a period of one week.

6. Ragging: Ragging in any form is a criminal offence as per the Supreme Court of India and the Kerala Prohibition of Ragging Act, 1998. Any student found involved in ragging shall be expelled from the college and criminal proceedings will be initiated. The Anti-Ragging Committee and Squad are active on campus. Complaints can be filed at the anti-ragging helpline: 1800-180-5522."""
            },
            {
                "page": 3,
                "content": """7. Discipline and Conduct: Students shall not indulge in any activity that brings disrepute to the institution. The following are strictly prohibited on campus:
- Consumption of alcohol, tobacco, or any narcotic substance
- Gambling in any form
- Possession of weapons or dangerous materials
- Defacing or damaging college property
- Political activities and demonstrations without prior permission from the Principal

8. Grievance Redressal: The college has a Student Grievance Redressal Cell headed by a senior faculty member. Students can submit their grievances in writing to the cell. The cell meets every first Monday of the month. An online grievance submission portal is also available through the college website.

9. Leave and Absence: Students must apply for leave in advance through the prescribed leave application form. Emergency leave must be intimated to the class tutor within 24 hours. Continuous absence of more than 10 working days without sanctioned leave shall lead to the student's name being struck off the rolls. Parents/guardians will be informed of irregular attendance through SMS and email."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Hostel Rules and Regulations",
        "description": "Rules governing hostel accommodation, mess facilities, curfew timings, and visitor policies for residential students.",
        "category": "Hostel",
        "file_name": "hostel_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Hostel Rules and Regulations

1. Hostel Admission: Hostel admission is granted on a merit-cum-means basis. Priority is given to students from distant places (beyond 30 km from the college). Application for hostel admission must be submitted along with the college admission form. The hostel deposit is Rs. 5,000 (refundable) and the annual hostel fee is Rs. 15,000 for boys and Rs. 12,000 for girls.

2. Check-in and Check-out: Students must check in at the hostel reception upon arrival. A proper check-in register must be signed with the date and time. Room keys are issued at the reception and must be returned at the end of the academic year. Room allotment is done by the Hostel Warden and changing rooms without permission is not allowed.

3. Curfew Timings: The hostel gates close at 8:00 PM for girls and 9:30 PM for boys. Students must be inside the hostel premises before curfew time. Late entry requires written permission from the Hostel Warden with a valid reason. Night-outs are permitted only with prior written approval from parents and countersigned by the Hostel Warden. A maximum of 4 night-out permissions are allowed per month."""
            },
            {
                "page": 2,
                "content": """4. Mess Facilities: The hostel provides three meals a day (breakfast, lunch, and dinner) and evening tea/snacks. Mess timings are:
- Breakfast: 7:30 AM to 9:00 AM
- Lunch: 12:30 PM to 2:00 PM
- Tea/Snacks: 4:30 PM to 5:30 PM
- Dinner: 7:00 PM to 8:30 PM
The monthly mess charge is Rs. 3,500 which is payable before the 5th of every month. A mess committee comprising student representatives reviews the menu weekly. Both vegetarian and non-vegetarian options are available daily. Students with medical dietary requirements must inform the Warden with a medical certificate.

5. Visitors: Visitors (parents/guardians only) are allowed between 4:00 PM and 6:00 PM on weekdays and 10:00 AM to 5:00 PM on weekends. All visitors must register at the hostel reception with a valid ID proof. Visitors of the opposite gender are not allowed inside the hostel rooms under any circumstances. Visitors may meet students in the designated common area or visitor's room only."""
            },
            {
                "page": 3,
                "content": """6. Hostel Discipline: The following activities are strictly prohibited in the hostel:
- Ragging in any form
- Consumption of alcohol, smoking, or use of drugs
- Cooking inside rooms (only permitted in designated pantry areas)
- Using high-power electrical appliances (heaters, irons, immersion rods) in rooms
- Playing loud music or creating noise after 10:00 PM (quiet hours from 10 PM to 6 AM)
- Keeping pets

7. Room Maintenance: Students are responsible for maintaining cleanliness of their rooms. The hostel staff will carry out weekly inspections. Furniture provided by the college should not be moved or modified. Any damage to hostel property will be charged to the occupant. Each room is provided with a bed, mattress, study table, chair, cupboard, and a ceiling fan.

8. Hostel Leave: Students wishing to leave the hostel for weekends or holidays must enter their details in the outing register at least one day in advance, specifying the destination, purpose, and expected date of return. The Hostel Warden may contact parents to verify the details."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Examination Rules and Schedule",
        "description": "University and internal examination policies, grading system, supplementary exam procedures, and academic calendar.",
        "category": "Examinations",
        "file_name": "exam_regulations.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Examination Rules and Schedule

1. Examination Pattern: The college follows the Choice Based Credit and Semester System (CBCSS) as prescribed by the University of Kerala / Mahatma Gandhi University / University of Calicut (as applicable). Each academic year consists of two semesters. Internal (Continuous) Assessment carries 20% weightage and the End Semester Examination carries 80% weightage.

2. Internal Assessment: Internal assessment is based on the following components:
- Two internal examinations per semester (10 marks each, best of two considered)
- Assignments and seminars: 5 marks
- Attendance: 5 marks
The total internal assessment is scaled to 20 marks. Internal marks are submitted to the university before the commencement of end semester exams.

3. End Semester Examinations: End semester examinations are conducted by the university, typically in November/December for odd semesters and April/May for even semesters. The exam schedule is published on the university website at least 3 weeks before the examination. Students must have a minimum of 75% attendance and satisfactory performance in internal assessments to be eligible."""
            },
            {
                "page": 2,
                "content": """4. Grading System: The following grading system is used (10-point CGPA scale):
- A+ : 90-100 (Grade Point 10) - Outstanding
- A  : 80-89  (Grade Point 9)  - Excellent
- B+ : 70-79  (Grade Point 8)  - Very Good
- B  : 60-69  (Grade Point 7)  - Good
- C+ : 50-59  (Grade Point 6)  - Above Average
- C  : 40-49  (Grade Point 5)  - Average
- D  : 30-39  (Grade Point 4)  - Below Average (Pass)
- F  : Below 30 (Grade Point 0) - Fail

The minimum grade required for passing each course is D (30 marks out of 100). The Cumulative Grade Point Average (CGPA) is calculated at the end of each semester.

5. Supplementary Examinations: Students who fail in any subject may appear for the supplementary examination, which is usually conducted along with the next regular semester examination. Supplementary exam registration must be done through the university portal within the prescribed deadline. A supplementary examination fee of Rs. 500 per paper is applicable."""
            },
            {
                "page": 3,
                "content": """6. Examination Hall Rules:
- Students must bring their hall ticket and college ID card to every examination.
- Students must be seated at least 15 minutes before the scheduled start time.
- No student will be allowed to enter the examination hall after 30 minutes from the start of the exam.
- Use of calculators is allowed only for specified subjects; programmable calculators are prohibited.
- Mobile phones, smartwatches, and electronic gadgets are strictly prohibited in the examination hall.
- Copying, cheating, or any form of malpractice will result in cancellation of the examination and debarment for one to two years.

7. Revaluation and Scrutiny: Students can apply for revaluation or scrutiny of their answer papers within 15 days of the publication of results. Revaluation fee is Rs. 750 per paper, and scrutiny fee is Rs. 300 per paper. Applications must be submitted through the university portal.

8. Project and Viva Voce: Final semester students must submit a project report (dissertation) and face a viva voce examination. The project carries 4 credits and is evaluated by an internal guide and an external examiner appointed by the university. The project report must be submitted in the prescribed format, both in print (3 copies) and digital (CD/USB) format."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Library Rules and Policies",
        "description": "Library operating hours, book borrowing limits, fine policies, digital resources access, and reading room rules.",
        "category": "Library",
        "file_name": "library_policy.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Library Rules and Policies

1. Library Timings: The college library operates from 8:30 AM to 5:30 PM on all working days (Monday to Saturday). During examination periods, the library hours are extended until 8:00 PM. The digital library section is open from 9:00 AM to 4:30 PM.

2. Membership: All bonafide students, faculty members, and staff are eligible for library membership. A library card will be issued upon admission after completing the library registration form. Students must produce their library card for all transactions.

3. Book Borrowing Policy:
- UG Students: May borrow up to 3 books at a time for a period of 14 days.
- PG Students: May borrow up to 5 books at a time for a period of 21 days.
- Faculty: May borrow up to 10 books at a time for the entire semester.
- Reference books, rare books, periodicals, and journals cannot be borrowed and are for in-library use only.

4. Renewal and Reservation: Books may be renewed once for an additional period of 7 days, provided no other reader has reserved the book. Reservation of books can be done online through the library OPAC (Online Public Access Catalogue) or at the library counter."""
            },
            {
                "page": 2,
                "content": """5. Fine Policy for Overdue Books:
- A fine of Rs. 2 per day per book will be charged for overdue books.
- If a book is not returned within 30 days of the due date, the fine increases to Rs. 5 per day.
- Lost books must be reported immediately. The borrower must either replace the book with a new copy of the same edition or pay the current market price plus a processing fee of Rs. 100.
- Library clearance is mandatory before receiving hall tickets for examinations and at the time of Transfer Certificate (TC) issuance.

6. Textbook Return Policy: All borrowed textbooks must be returned by the last working day of each semester. Failure to return textbooks before the semester ends will attract a penalty of Rs. 10 per day per book. Students with outstanding library dues will not be issued their semester mark sheets.

7. Digital Resources: The library provides access to the following digital resources:
- INFLIBNET N-LIST (National Library and Information Services Infrastructure for Scholarly Content)
- DELNET (Developing Library Network)
- E-journals and e-books subscribed through university consortium
- Access credentials for online resources are provided by the librarian upon request. Remote access is available for registered users using the institutional VPN."""
            },
            {
                "page": 3,
                "content": """8. Reading Room Rules:
- Maintain absolute silence inside the library and reading room.
- Switch off mobile phones or keep them on silent mode.
- Bags, personal books, and food items are not allowed inside the library (use the locker facility provided).
- Do not deface, mark, underline, or mutilate library books and resources.
- Newspapers and magazines must be returned to the display rack after reading.
- Computers in the digital section are for academic purposes only; social media browsing is not permitted.

9. Library Collections: The college library houses over 45,000 books, 120 periodicals and journals, 15 national and regional newspapers, and a dedicated section for competitive exam preparation materials. The library also maintains a collection of previous year university question papers, project reports of former students, and a Kerala Studies section with books on Kerala history, culture, and literature.

10. Book Bank Scheme: The college operates a Book Bank Scheme for economically weaker students. Under this scheme, a set of textbooks for each semester is lent to eligible students for the entire semester at a nominal fee of Rs. 50. Application for the Book Bank Scheme must be submitted with income certificate and BPL/APL card copy within the first two weeks of each semester."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Fee Structure and Scholarships",
        "description": "Detailed fee structure for various programmes, scholarship information, fee concession policies, and payment deadlines.",
        "category": "Fees & Finance",
        "file_name": "fee_structure.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Fee Structure and Scholarships (Academic Year 2025-2026)

1. Tuition Fee Structure (Annual):
- B.A. / B.Sc. / B.Com (Government Aided): Rs. 3,060 to Rs. 5,590 per year (as per Kerala Government fee regulations)
- B.Tech / BCA / BBA (Self-Financing): Rs. 35,000 to Rs. 50,000 per year
- M.A. / M.Sc. / M.Com (Government Aided): Rs. 4,200 to Rs. 7,500 per year
- MBA / MCA (Self-Financing): Rs. 40,000 to Rs. 55,000 per year

2. Other Compulsory Fees (Annual):
- Caution Deposit (one-time, refundable): Rs. 5,000
- Library Fee: Rs. 500
- Laboratory Fee (Science students): Rs. 750
- Sports & Games Fee: Rs. 300
- Magazine & Cultural Fee: Rs. 200
- Student Welfare Fund: Rs. 150
- IT Infrastructure Fee: Rs. 1,000
- Examination Fee (per semester): Rs. 750 to Rs. 1,500 (as per university norms)

3. Fee Payment Deadlines:
- First installment: Within 15 days of admission
- Second installment: Before December 31st (Odd Semester) / Before June 30th (Even Semester)
- Late fee payment will attract a fine of Rs. 50 per day, up to a maximum of Rs. 1,000.
- Fee can be paid online through the college portal, via NEFT/RTGS, or by demand draft drawn in favour of the Principal."""
            },
            {
                "page": 2,
                "content": """4. Scholarships Available:
- Kerala State Government Merit Scholarship: For students who secured above 80% in qualifying examination. Amount: Rs. 5,000 to Rs. 10,000 per year.
- E-Grantz Scholarship (Kerala Government): Available for students belonging to SC/ST/OBC/Minority communities. Covers tuition fee and provides a monthly stipend.
- Central Sector Scholarship (Government of India): For students scoring above 80th percentile in Class 12. Amount: Rs. 10,000 per year for UG, Rs. 20,000 per year for PG.
- Post-Matric Scholarship for SC/ST Students: Covers tuition fees, maintenance allowance, and book grant.
- National Means-cum-Merit Scholarship (NMMS): For economically weaker students with academic merit.
- College Endowment Scholarships: Various scholarships instituted by donors for toppers, financially weak students, and students excelling in sports or cultural activities.

5. Fee Concession: Students belonging to BPL (Below Poverty Line) families are eligible for full fee concession. Application for fee concession must be submitted with BPL certificate, income certificate, and ration card copy. The Fee Concession Committee reviews applications within 30 days of submission."""
            },
            {
                "page": 3,
                "content": """6. Refund Policy:
- If a student withdraws within 15 days of admission: Full tuition fee refund (minus Rs. 1,000 processing fee).
- Withdrawal between 15 to 30 days: 80% refund of tuition fee.
- Withdrawal between 30 to 60 days: 50% refund of tuition fee.
- After 60 days: No refund of tuition fee.
- Caution deposit is refundable in full at the time of leaving the college, provided there are no outstanding dues.
- Hostel fees are refunded on a pro-rata basis for the remaining months.

7. Education Loan Support: The college provides education loan recommendation letters for students applying to nationalized banks. The college has tie-ups with State Bank of India, Federal Bank, and Kerala Gramin Bank for hassle-free education loans. Students can avail loans up to Rs. 10 lakh for UG and Rs. 20 lakh for PG programmes. The college Placement Cell also provides documentation support for loan applications.

8. Payment of Stipend: Students eligible for government scholarships and stipends will receive the amount directly to their bank account linked with Aadhaar through Direct Benefit Transfer (DBT). Students must update their bank account details and Aadhaar number in the E-Grantz portal. The stipend disbursal typically happens in two installments per semester."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Admission Guidelines and Procedures",
        "description": "Admission eligibility, required documents, reservation policies, and admission calendar for UG and PG programmes.",
        "category": "Admissions",
        "file_name": "admission_guidelines.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Admission Guidelines and Procedures

1. Eligibility Criteria:
- UG Programmes (B.A., B.Sc., B.Com, BCA, BBA): Candidates must have passed the Higher Secondary Examination (Plus Two) from Kerala Board or equivalent examination recognized by the University, with a minimum of 45% aggregate marks (40% for SC/ST candidates).
- PG Programmes (M.A., M.Sc., M.Com, MBA, MCA): Candidates must hold a Bachelor's degree from a recognized university with a minimum of 50% aggregate marks (45% for SC/ST candidates).
- B.Tech: Admission through KEAM (Kerala Engineering Architecture Medical) entrance examination conducted by the Commissioner of Entrance Examinations (CEE), Kerala.

2. Admission Process:
- Government/Aided Colleges: Admission is through Single Window Admission (SWA) conducted by the respective university, based on merit in the qualifying examination and reservation norms.
- Self-Financing Programmes: Admission is through management quota and merit-based selection. A certain percentage of seats are filled through centralized allotment.
- Lateral Entry: Available for diploma holders into the second year of B.Tech programmes."""
            },
            {
                "page": 2,
                "content": """3. Required Documents for Admission:
- Completed application form (available online on the college website and offline at the admission office)
- SSLC (10th standard) mark sheet and certificate (original + 2 photocopies)
- Plus Two (12th standard) mark sheet and certificate (original + 2 photocopies)
- Transfer Certificate (TC) from the previous institution
- Migration Certificate (for students from other universities/states)
- Community Certificate (for SC/ST/OBC candidates, issued by the Village Officer/Tahsildar)
- Income Certificate (for scholarship and fee concession applicants)
- Aadhaar Card (original + 2 photocopies)
- 6 recent passport-size colour photographs (white background)
- Nativity Certificate (for Kerala domicile reservation)
- Physical Fitness Certificate from a registered medical practitioner
- BPL Certificate / Ration Card (if applicable, for fee concession)
- Conduct Certificate from the previous institution

4. Reservation Policy (as per Kerala Government norms):
- SC (Scheduled Caste): 8% reservation
- ST (Scheduled Tribe): 2% reservation
- OBC (Other Backward Classes): 20% reservation (within community-wise sub-reservation)
- Persons with Disabilities (PwD): 5% horizontal reservation
- Economically Weaker Sections (EWS): 10% reservation
- Sports Quota: 2% of seats reserved for meritorious sportspersons
- Management Quota (Self-Financing Colleges): Up to 20% of total seats"""
            },
            {
                "page": 3,
                "content": """5. Admission Calendar (Tentative):
- Online application portal opens: First week of June
- Last date for submission of applications: Last week of June
- Publication of merit list (first allotment): First week of July
- Reporting for admission (first allotment): Within 7 days of allotment
- Second allotment (if seats available): Third week of July
- Final allotment and spot admission: First week of August
- Commencement of classes: Second week of August

6. Age Limit: There is no upper age limit for admission to UG programmes. For PG programmes, the maximum age limit is 40 years (relaxation for SC/ST/OBC as per government rules).

7. Transfer and Migration: Students seeking transfer from other colleges must apply through the university. Inter-university migration requires a Migration Certificate and No Objection Certificate (NOC) from both institutions. Transfer is subject to availability of seats and is permitted only during the first two weeks of a semester.

8. Cancellation of Admission: Students wishing to cancel their admission must submit a written application to the Principal. The TC and original documents will be returned after deducting applicable charges. Cancellation must be done in person or by an authorized representative (parent/guardian) with a valid authorization letter."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Department and Programme Details",
        "description": "Details of academic departments, programmes offered, faculty information, and departmental facilities.",
        "category": "Academics",
        "file_name": "department_details.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Department and Programme Details

1. Departments and Programmes Offered:

Department of English:
- B.A. English Language and Literature (3 years, 6 semesters) - 60 seats
- M.A. English Literature (2 years, 4 semesters) - 20 seats

Department of Malayalam:
- B.A. Malayalam Language and Literature (3 years, 6 semesters) - 50 seats

Department of Commerce:
- B.Com (Finance & Taxation) (3 years, 6 semesters) - 60 seats
- B.Com (Computer Application) (3 years, 6 semesters) - 50 seats
- M.Com (2 years, 4 semesters) - 25 seats

Department of Computer Science:
- B.Sc. Computer Science (3 years, 6 semesters) - 40 seats
- BCA - Bachelor of Computer Applications (3 years, 6 semesters) - 60 seats
- M.Sc. Computer Science (2 years, 4 semesters) - 20 seats
- MCA - Master of Computer Applications (2 years, 4 semesters) - 30 seats"""
            },
            {
                "page": 2,
                "content": """Department of Physics:
- B.Sc. Physics (3 years, 6 semesters) - 40 seats
- M.Sc. Physics (2 years, 4 semesters) - 15 seats

Department of Chemistry:
- B.Sc. Chemistry (3 years, 6 semesters) - 40 seats

Department of Mathematics:
- B.Sc. Mathematics (3 years, 6 semesters) - 50 seats
- M.Sc. Mathematics (2 years, 4 semesters) - 20 seats

Department of Economics:
- B.A. Economics (3 years, 6 semesters) - 60 seats

Department of Management Studies:
- BBA - Bachelor of Business Administration (3 years, 6 semesters) - 60 seats
- MBA - Master of Business Administration (2 years, 4 semesters) - 60 seats

2. Medium of Instruction: The medium of instruction for all programmes is English, except for language courses which are taught in the respective languages. Additional tutorials in Malayalam are available for students who need language support."""
            },
            {
                "page": 3,
                "content": """3. Academic Calendar Overview:
- Odd Semester (Semester 1, 3, 5): August to December
  - Classes begin: Second week of August
  - First internal exam: October
  - Second internal exam: November
  - End semester exams: November-December
  - Christmas and New Year holidays: December 20 to January 1

- Even Semester (Semester 2, 4, 6): January to May
  - Classes resume: First week of January
  - First internal exam: February
  - Second internal exam: March-April
  - End semester exams: April-May
  - Summer vacation: May-June

4. Add-on Courses and Certificate Programmes:
- Certificate in Tally ERP 9 and GST (Department of Commerce)
- Certificate in Web Development and Python Programming (Department of Computer Science)
- Certificate in Communicative English (Department of English)
- Certificate in Yoga and Wellness (Physical Education Department)
- Certificate in Digital Marketing (Department of Management Studies)
These add-on courses are conducted in collaboration with industry partners and carry additional credits recognized by the university.

5. Placement Cell: The college has an active Placement and Career Guidance Cell that organizes campus recruitment drives, career counseling sessions, mock interviews, and personality development workshops. Major recruiters include TCS, Infosys, Wipro, UST Global, IBS Software, Federal Bank, and South Indian Bank."""
            }
        ]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Sports and Extracurricular Activities",
        "description": "Details about sports facilities, cultural festivals, clubs, NSS, NCC, and extracurricular programmes.",
        "category": "Campus Life",
        "file_name": "campus_life_handbook.pdf",
        "chunks": [
            {
                "page": 1,
                "content": """Sports and Extracurricular Activities

1. Sports Facilities: The college has the following sports facilities available for all students:
- Football ground (full-size with floodlights)
- Cricket pitch and practice nets
- Basketball court (2 courts)
- Volleyball court
- Badminton courts (indoor, 4 courts)
- Table tennis room (3 tables)
- Athletics track (200m)
- Gymnasium with modern equipment (open 6 AM to 8 PM)

2. Sports Activities: Annual inter-departmental sports meet (Spardha) is held in January. The college participates in the University-level, Inter-University, and State-level sports competitions. Students representing the college in university or state level sports are eligible for sports quota attendance relaxation (up to 10% additional). Best sportsperson awards (male and female) are given during the Annual Day celebrations.

3. Cultural Activities: The college organizes an annual cultural festival called 'Kalolsavam' in February-March. Events include classical dance, folk arts, music, drama, literary competitions, fine arts, quiz, debate, and fashion show. Students are encouraged to participate in the University Youth Festival (Kerala University Youth Festival / MG University Youth Festival) and intercollegiate competitions."""
            },
            {
                "page": 2,
                "content": """4. Clubs and Associations:
- Literary Club: Organizes debates, essay writing, poetry recitation, and book review sessions.
- Science Club: Conducts science exhibitions, guest lectures, and field trips to research institutions.
- Nature Club: Undertakes environmental awareness campaigns, tree planting drives, and trekking expeditions.
- Film Club: Organizes film screenings, short film making workshops, and documentary production.
- IT Club: Conducts hackathons, coding competitions, tech talks, and app development workshops.
- Entrepreneurship Development Club (EDC): Organizes business plan competitions, startup mentoring sessions, and entrepreneurship awareness programmes.
- Fine Arts Club: Painting exhibitions, photography contests, and craft workshops.
- Music Club (Sargam): Western and Indian classical music practice sessions and performances.

5. NSS (National Service Scheme): The college has two NSS units with 200 volunteers each. NSS activities include:
- Weekly community service programmes
- Annual special camp (7-day residential camp in a rural area)
- Blood donation drives, health awareness campaigns
- Swachh Bharat activities, road safety awareness
- Flood relief and disaster management programmes (Kerala Floods relief participation)
Students who complete NSS requirements earn 2 additional grace marks in university examinations."""
            },
            {
                "page": 3,
                "content": """6. NCC (National Cadet Corps): The college has NCC Army wing for both boys and girls. NCC cadets undergo regular training, drills, and participate in camps including:
- Annual Training Camp (ATC)
- Combined Annual Training Camp (CATC)
- Republic Day Camp (RDC) at New Delhi
- Thal Sainik Camp and other national-level camps
NCC B and C Certificate holders receive additional preference in government job recruitments and university admissions. NCC cadets are eligible for 2 grace marks in university examinations.

7. Annual Day and Awards: The college Annual Day is celebrated in March with prize distribution ceremony. Awards given include:
- Best Student Award (Overall) - Male and Female
- Best Student in Academics - Department-wise
- Best Sportsperson - Male and Female
- Best NSS Volunteer
- Best NCC Cadet
- Proficiency Prize for each programme

8. Student Union: The college has an elected Student Union as per the Kerala University Students Union Act. Elections are conducted through parliamentary system. The Student Union organizes Arts Day, Sports Day, Freshers' Day, and various cultural and social programmes throughout the academic year. The Student Union office is located adjacent to the main auditorium."""
            }
        ]
    }
]

def seed_database():
    """Insert all documents and chunks with embeddings into the local SQLite database."""
    conn = sqlite3.connect(LOCAL_DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    total_chunks = 0
    total_docs = 0

    for doc in DOCUMENTS:
        doc_id = doc["id"]

        # Check if a document with the same title already exists
        cursor.execute("SELECT id FROM documents WHERE title = ?", (doc["title"],))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⏭️  Skipping (already exists): {doc['title']}")
            continue

        # Insert document
        cursor.execute("""
            INSERT INTO documents (id, title, description, category, file_name, file_url, file_size, mime_type, status, uploaded_by, created_at, updated_at, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            doc["title"],
            doc["description"],
            doc["category"],
            doc["file_name"],
            f"/uploads/{doc['file_name']}",
            len(json.dumps(doc["chunks"])),
            "application/pdf",
            "COMPLETED",
            None,
            NOW,
            NOW,
            NOW
        ))
        total_docs += 1
        print(f"  📄 Inserted document: {doc['title']}")

        # Insert chunks with embeddings
        for idx, chunk in enumerate(doc["chunks"]):
            chunk_id = str(uuid.uuid4())
            content = chunk["content"]

            # Generate embedding vector
            print(f"     🔢 Generating embedding for chunk {idx + 1} (page {chunk['page']})...")
            embedding = generate_embedding(content)
            embedding_json = json.dumps(embedding)

            cursor.execute("""
                INSERT INTO document_chunks (id, document_id, chunk_index, content, page_number, embedding, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id,
                doc_id,
                idx,
                content,
                chunk["page"],
                embedding_json,
                json.dumps({"source": doc["file_name"], "category": doc["category"]}),
                NOW
            ))
            total_chunks += 1

    conn.commit()
    conn.close()

    print(f"\n✅ Seeding complete! Inserted {total_docs} documents with {total_chunks} chunks.")


if __name__ == "__main__":
    print("🌱 Seeding Kerala College Data into CampusAI Database...\n")
    seed_database()
    print("\n🎉 Done! The chatbot now has Kerala college knowledge to answer questions.")
