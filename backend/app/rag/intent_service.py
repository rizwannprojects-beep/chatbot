import re
from typing import Dict, Any, Set, List, Optional

# ══════════════════════════════════════════════════════════════
#  DOMAIN CATEGORIES & KEYWORD MAPS
# ══════════════════════════════════════════════════════════════

DOMAIN_CATEGORIES = {
    "attendance": {
        "category": "Attendance & Leave",
        "keywords": {"attendance", "condonation", "shortage", "absent", "leave", "duty leave", "75%", "65%", "fe grade", "medical leave", "shortage of attendance"},
        "title_keywords": ["attendance", "leave"]
    },
    "exams": {
        "category": "Examinations",
        "keywords": {"exam", "exams", "examination", "examinations", "end-sem", "series test", "internal marks", "revaluation", "scrutiny", "supplementary", "pass mark", "passing marks", "cgpa", "sgpa", "grading", "credits"},
        "title_keywords": ["examination", "evaluation", "grading", "academic regulations"]
    },
    "hostel": {
        "category": "Hostel & Housing",
        "keywords": {"hostel", "curfew", "gate pass", "warden", "mess", "gate close", "night leave", "out-pass", "quiet hours", "room", "housing"},
        "title_keywords": ["hostel", "housing", "residence"]
    },
    "scholarships": {
        "category": "Fees & Scholarships",
        "keywords": {"scholarship", "scholarships", "fee", "fees", "tuition", "installment", "stipend", "e-grantz", "merit", "financial aid", "concession", "waiver"},
        "title_keywords": ["fees", "scholarships", "fee structure"]
    },
    "facilities": {
        "category": "Campus Facilities",
        "keywords": {"facility", "facilities", "canteen", "sports", "gym", "auditorium", "health center", "bus", "transport", "bank", "atm", "amenities"},
        "title_keywords": ["facilities", "infrastructure", "campus"]
    },
    "library": {
        "category": "Library & IT",
        "keywords": {"library", "book", "books", "borrowing", "fine", "wifi", "internet", "lab", "computer", "it guidelines"},
        "title_keywords": ["library", "it", "wifi"]
    },
    "admissions": {
        "category": "Admissions & Eligibility",
        "keywords": {"admission", "admissions", "eligibility", "apply", "keam", "nri", "seat", "cutoff", "b.tech", "certificate", "certificates"},
        "title_keywords": ["admissions", "eligibility"]
    },
    "placements": {
        "category": "Placements & Internships",
        "keywords": {"placement", "placements", "tpc", "company", "companies", "package", "salary", "internship", "recruitment", "interview"},
        "title_keywords": ["placement", "recruitment"]
    }
}

AMBIGUOUS_PATTERNS = [
    r"^(what\s+are\s+the\s+)?rules\??$",
    r"^tell\s+me\s+(the\s+)?rules\??$",
    r"^rules\??$",
    r"^guidelines\??$",
    r"^what\s+are\s+the\s+guidelines\??$",
    r"^info\??$",
    r"^information\??$",
    r"^policies\??$",
]

def analyze_query_intent(query: str) -> Dict[str, Any]:
    """
    Analyzes student query text to determine domain, category matching, and ambiguity status.
    """
    clean_q = query.strip().lower()
    
    # 1. Check ambiguity
    for pattern in AMBIGUOUS_PATTERNS:
        if re.match(pattern, clean_q):
            return {
                "is_ambiguous": True,
                "domain": "ambiguous",
                "target_category": None,
                "keywords": set(),
                "title_keywords": [],
                "clarification_message": (
                    "Which rules would you like to know about? We have official policies for:\n"
                    "• **Attendance & Leave** (75% minimum criteria, condonation, duty leave)\n"
                    "• **Hostel Rules & Curfew** (8:30 PM / 9:30 PM curfew, gate pass procedure)\n"
                    "• **Examinations & Grading** (Series tests, 10-point scale, revaluation)\n"
                    "• **Library & IT Guidelines** (Book borrowing limits, Wi-Fi usage)\n"
                    "• **Fees & Scholarships** (Tuition installments, government scholarship portals)\n\n"
                    "Please ask your specific question!"
                )
            }
            
    # 2. Match intent keywords
    words = set(re.findall(r"\w+", clean_q))
    matched_domains = []
    
    for domain_key, info in DOMAIN_CATEGORIES.items():
        overlap = words.intersection(info["keywords"])
        phrase_matches = sum(1 for kw in info["keywords"] if kw in clean_q)
        total_score = len(overlap) * 2 + phrase_matches
        
        if total_score > 0:
            matched_domains.append((total_score, domain_key, info))
            
    if matched_domains:
        matched_domains.sort(key=lambda x: x[0], reverse=True)
        top_match = matched_domains[0][2]
        return {
            "is_ambiguous": False,
            "domain": matched_domains[0][1],
            "target_category": top_match["category"],
            "keywords": top_match["keywords"],
            "title_keywords": top_match["title_keywords"]
        }
        
    return {
        "is_ambiguous": False,
        "domain": "general",
        "target_category": None,
        "keywords": set(),
        "title_keywords": []
    }
