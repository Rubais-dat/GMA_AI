import os
import re
import json
import ast
import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv
from groq import Groq
from embedding import embed_text
from rag_pipeline import RAGPipeline

# Load .env file
load_dotenv()

# Load API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment variables")

client = Groq(api_key=GROQ_API_KEY)
rag_pipeline = RAGPipeline()

GMA_COLLEGE_DATA = {
    # Government Colleges
    'KKM': {'gma_rank': 1, 'type': 'Government', 'name': 'Govt. Medical College, Kozhikkode.'},
    'TVM': {'gma_rank': 2, 'type': 'Government', 'name': 'Govt. Medical College, Thiruvananthapuram.'},
    'KTM': {'gma_rank': 3, 'type': 'Government', 'name': 'Govt. Medical College, Kottayam.'},
    'TCM': {'gma_rank': 4, 'type': 'Government', 'name': 'Govt. Medical College, Thrissur.'},
    'ALP': {'gma_rank': 5, 'type': 'Government', 'name': 'T D Govt. Medical College, Alappuzha'},
    'KLM': {'gma_rank': 6, 'type': 'Government', 'name': 'Govt. Medical College, Parippally, Kollam.'},
    'KNM': {'gma_rank': 7, 'type': 'Government', 'name': 'Government Medical College Kannur.'},
    'CMC': {'gma_rank': 8, 'type': 'Government', 'name': 'Govt. Medical College, Ernakulam.'},
    'MLP': {'gma_rank': 9, 'type': 'Government', 'name': 'Govt. Medical College, Manjeri.'},
    'IDM': {'gma_rank': 10, 'type': 'Government', 'name': 'Government Medical College Idukki'},
    'PKM': {'gma_rank': 11, 'type': 'Government', 'name': 'Government Medical College, Palakkad.'},
    'PTM': {'gma_rank': 12, 'type': 'Government', 'name': 'Government Medical College, Konni, Pathanamthitta.'},
    'KSM': {'gma_rank': 13, 'type': 'Government', 'name': 'Govt. Medical College, Kasaragod'},
    'WYM': {'gma_rank': 14, 'type': 'Government', 'name': 'Govt. Medical College, Wayanad'},

    # Private/Self-Financing Colleges
    'JMC': {'gma_rank': 1, 'type': 'Private', 'name': 'Jubilee Mission Medical College, Thrisur.'},
    'AMC': {'gma_rank': 2, 'type': 'Private', 'name': 'Amala Institute of Medical Sciences, Thrissur'},
    'MMC': {'gma_rank': 3, 'type': 'Private', 'name': 'Malankara Orthodox Syrian Church Medi.College, Kolenchery.'},
    'PMC': {'gma_rank': 4, 'type': 'Private', 'name': 'Pushpagiri Institute of Medical Science, Thiruvalla.'},
    'BCM': {'gma_rank': 5, 'type': 'Private', 'name': 'Believers Church Medical College Hospital, Thiruvalla'},
    'EMC': {'gma_rank': 6, 'type': 'Private', 'name': 'MES Medical College, Perinthalmanna, Malappuram.'},
    'GMC': {'gma_rank': 7, 'type': 'Private', 'name': 'Sree Gokulam Medical College, Venjaramoodu, TVPM.'},
    'TRM': {'gma_rank': 8, 'type': 'Private', 'name': 'Travancore Medical College, Umayanalloor, Kollam.'},
    'KCM': {'gma_rank': 9, 'type': 'Private', 'name': 'KMCT Medical College, Mukkom, Kozikkode.'},
    'MMH': {'gma_rank': 10, 'type': 'Private', 'name': 'Malabar Medical College Hospital, Kozhikkode'},
    'SMC': {'gma_rank': 11, 'type': 'Private', 'name': 'Dr. Somervell Memorial CSI Medical College, Karakonam.'},
    'SUC': {'gma_rank': 12, 'type': 'Private', 'name': 'SUT Accademy of Medical Sciences , Thiruvananthapuram.'},
    'SIM': {'gma_rank': 13, 'type': 'Private', 'name': 'Sree Narayana Institute of Medical Sciences, Ernakulam.'},
    'KDM': {'gma_rank': 14, 'type': 'Private', 'name': 'P K Das Institute of Medical Sciences, Ottapalam.'},
    'AZC': {'gma_rank': 15, 'type': 'Private', 'name': 'Azeezia Institute of Medi. Science, Meyyannoor, Kollam'},
    'DMM': {'gma_rank': 16, 'type': 'Private', 'name': 'Dr. Moopen\'s Medical College, Wayanad.'},
    'KMM': {'gma_rank': 17, 'type': 'Private', 'name': 'Karuna Medical College, Vilayodi, Palakkad.'},
    'AAM': {'gma_rank': 18, 'type': 'Private', 'name': 'Al Azhar Medical college, Thodupuzha.'},
    'MZM': {'gma_rank': 19, 'type': 'Private', 'name': 'Mount Zion Medical College, Pathanamthitta.'},
    'PIM': {'gma_rank': 20, 'type': 'Private', 'name': 'Palakkad Institute of Medical Sciences, Walayar'},
    'KEM': {'gma_rank': 21, 'type': 'Private', 'name': 'Kerala Medical College, Palakkad'}
}



def parse_query_for_lookup(question):
    """
    Parses natural language query to extract rank, category, course, and requested college type (Govt/Private).
    Example: "Which self-financing colleges can I get with rank 5000 in MU category?"
    """
    # Find numbers between 100 and 999999 (avoid years like 2024, 2025)
    numbers = re.findall(r'\b\d{3,6}\b', question)
    rank = None
    for num in numbers:
        n = int(num)
        if n != 2024 and n != 2025:
            rank = n
            break
            
    if rank is None:
        return None
        
    q_lower = question.lower()
    
    # Mapping table for categories to ensure correct code matching
    category_mappings = {
        'nri': 'NR',
        'state merit': 'SM',
        'general': 'SM',
        'merit': 'SM',
        'muslim': 'MU',
        'ezhava': 'EZ',
        'scheduled caste': 'SC',
        'scheduled tribe': 'ST',
        'backward hindu': 'BH',
        'latin catholic': 'LA',
        'latin': 'LA',
        'dheevara': 'DV',
        'ews': 'EW',
        'economically weaker': 'EW',
        'minority': 'AM',
        'christian': 'AM',
        'muslim minority': 'MM',
        'adventist': 'AC'
    }
    
    category = None
    
    # First check explicit mappings in the query
    for key, val in category_mappings.items():
        if re.search(r'\b' + re.escape(key) + r'\b', q_lower):
            category = val
            break
            
    # If not found, check direct codes in the query
    if not category:
        categories = ['SM', 'MU', 'EZ', 'SC', 'ST', 'BH', 'LA', 'DV', 'EW', 'AM', 'MM', 'AC', 'NR']
        for cat in categories:
            if re.search(r'\b' + cat + r'\b', question, re.IGNORECASE):
                category = cat.upper()
                break
                
    # Default category if none matched
    if not category:
        category = 'SM'
        
    course = 'MBBS'  # default course
    if re.search(r'\bbds\b', question, re.IGNORECASE):
        course = 'BDS'
        
    # Detect requested college type
    req_type = None
    if re.search(r'\b(govt|government|gov)\b', question, re.IGNORECASE):
        req_type = 'Government'
    elif re.search(r'\b(private|self-financing|self-finance|self finance|self financing|management|mgmt|sf)\b', question, re.IGNORECASE):
        req_type = 'Private'
        
    return {
        'rank': rank,
        'category': category,
        'course': course,
        'req_type': req_type
    }

def get_code(name):
    if ':' in str(name):
        return str(name).split(':')[0].strip()
    return str(name).strip()


def get_course_cutoff_summary(question):
    """
    When user asks about general BDS or MBBS cutoffs (no specific college, no rank),
    returns closing ranks for all colleges in that course.
    """
    cutoff_path = "data/smartchoice_data.csv"
    if not os.path.exists(cutoff_path):
        return ""

    q_lower = question.lower()

    cutoff_keywords = ["cutoff", "cut off", "last rank", "closing rank", "cut-off",
                       "last admitted", "qualifying rank", "cutoff rank"]
    if not any(kw in q_lower for kw in cutoff_keywords):
        return ""

    is_bds  = bool(re.search(r'\bbds\b', question, re.IGNORECASE))
    is_mbbs = bool(re.search(r'\bmbbs\b', question, re.IGNORECASE))
    if not is_bds and not is_mbbs:
        return ""

    course = 'BDS' if is_bds else 'MBBS'

    category_mappings = {
        'nri': 'NR', 'state merit': 'SM', 'general': 'SM', 'merit': 'SM',
        'muslim': 'MU', 'ezhava': 'EZ', 'scheduled caste': 'SC',
        'scheduled tribe': 'ST', 'backward hindu': 'BH', 'latin': 'LA',
        'dheevara': 'DV', 'ews': 'EW', 'christian': 'AM',
    }
    category = None
    for key, val in category_mappings.items():
        if re.search(r'\b' + re.escape(key) + r'\b', q_lower):
            category = val
            break
    if not category:
        for cat in ['SM', 'MU', 'EZ', 'SC', 'ST', 'BH', 'LA', 'DV', 'EW', 'AM', 'MM', 'NR']:
            if re.search(r'\b' + cat + r'\b', question, re.IGNORECASE):
                category = cat.upper()
                break
    if not category:
        category = 'SM'

    req_type = None
    if re.search(r'\b(govt|government)\b', question, re.IGNORECASE):
        req_type = 'Government'
    elif re.search(r'\b(private|self.financ|management)\b', question, re.IGNORECASE):
        req_type = 'Private'

    try:
        df = pd.read_csv(cutoff_path)
        df['code'] = df['College Name'].apply(get_code)
        df['college_clean'] = df['College Name'].apply(
            lambda x: x.split(':', 1)[1].strip() if ':' in str(x) else str(x)
        )

        df_f = pd.DataFrame()
        for year in [2025, 2024]:
            df_f = df[(df['Course'].str.upper() == course) &
                      (df['Alloted Category'].str.upper() == category) &
                      (df['Year'] == year)]
            if not df_f.empty:
                break

        if df_f.empty:
            return ""

        if req_type:
            df_f = df_f[df_f['College Category'].str.upper() == req_type.upper()]

        if df_f.empty:
            return ""

        summary = df_f.groupby(['code', 'college_clean'])['Rank'].max().reset_index()
        summary = summary.sort_values('Rank')

        result = [
            f"=== {course} Closing Ranks — {category} Category ({year}) ===",
            "(Last rank admitted across all allotment rounds)",
            "| College | Code | Closing Rank |",
            "| :--- | :---: | :---: |"
        ]
        for _, row in summary.iterrows():
            result.append(f"| {row['college_clean']} | {row['code']} | {int(row['Rank'])} |")

        return "\n".join(result)

    except Exception as e:
        print(f"Error in get_course_cutoff_summary: {e}")
        return ""


def get_college_cutoff_details(question):
    """
    When user asks about a specific college's cutoff/last rank for a category
    (without providing their own rank), fetch directly from smartchoice_data.csv.
    Returns a formatted markdown table of last admitted ranks per round.
    """
    cutoff_path = "data/smartchoice_data.csv"
    if not os.path.exists(cutoff_path):
        return ""

    # Only trigger if the question is about cutoffs/last ranks
    cutoff_keywords = ["cutoff", "cut off", "last rank", "closing rank",
                       "last admitted", "what rank", "which rank", "cutoff rank",
                       "cut-off", "qualifying rank"]
    q_lower = question.lower()
    if not any(kw in q_lower for kw in cutoff_keywords):
        return ""

    # Detect course (default MBBS)
    course = 'BDS' if re.search(r'\bbds\b', question, re.IGNORECASE) else 'MBBS'

    # Detect category
    category_mappings = {
        'nri': 'NR', 'state merit': 'SM', 'general': 'SM', 'merit': 'SM',
        'muslim minority': 'MM', 'muslim': 'MU', 'ezhava': 'EZ',
        'scheduled caste': 'SC', 'scheduled tribe': 'ST', 'backward hindu': 'BH',
        'latin': 'LA', 'dheevara': 'DV', 'ews': 'EW', 'economically weaker': 'EW',
        'christian minority': 'AM', 'christian': 'AM', 'all christian': 'AM',
    }
    category = None
    for key, val in category_mappings.items():
        if re.search(r'\b' + re.escape(key) + r'\b', q_lower):
            category = val
            break
    if not category:
        for cat in ['SM', 'MU', 'EZ', 'SC', 'ST', 'BH', 'LA', 'DV', 'EW', 'AM', 'MM', 'AC', 'NR']:
            if re.search(r'\b' + cat + r'\b', question, re.IGNORECASE):
                category = cat.upper()
                break

    try:
        df = pd.read_csv(cutoff_path)
        df['code'] = df['College Name'].apply(get_code)
        df['college_clean'] = df['College Name'].apply(
            lambda x: x.split(':', 1)[1].strip() if ':' in str(x) else str(x)
        )

        # Match college name from the question
        stop_words = {'medical', 'college', 'hospital', 'institute', 'sciences',
                      'science', 'and', 'the', 'of', 'in', 'at', 'govt', 'government'}
        matched_code = None
        matched_name = None

        for _, row in df.drop_duplicates(subset=['code']).iterrows():
            name_words = re.findall(r'[a-zA-Z]{3,}', row['college_clean'].lower())
            keywords = [w for w in name_words if w not in stop_words]
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    matched_code = row['code']
                    matched_name = row['college_clean']
                    break
            if matched_code:
                break
            # Also try matching by KEAM code directly
            if re.search(r'\b' + re.escape(row['code'].lower()) + r'\b', q_lower):
                matched_code = row['code']
                matched_name = row['college_clean']
                break

        if not matched_code:
            return ""

        # Filter by college + course + year (2025 first, fallback 2024)
        df_col = pd.DataFrame()
        for year in [2025, 2024]:
            df_col = df[(df['code'] == matched_code) &
                        (df['Course'].str.upper() == course.upper()) &
                        (df['Year'] == year)]
            if not df_col.empty:
                break

        if df_col.empty:
            return ""

        # Filter by category if detected
        df_cat = df_col[df_col['Alloted Category'].str.upper() == category.upper()] if category else df_col

        if df_cat.empty:
            return ""

        result = [
            f"=== {matched_name} ({matched_code}) — {course} Last Admitted (Closing) Rank ({year}) ==="
        ]

        if category:
            # Single category — just the overall closing rank (max across all rounds)
            closing_rank = int(df_cat['Rank'].max())
            result.append(f"Course       : {course}")
            result.append(f"Category     : {category}")
            result.append(f"Closing Rank : {closing_rank}")
            result.append(f"(This is the highest rank admitted across all allotment rounds in {year})")
        else:
            # All categories — one row per category showing max rank
            result.append("| Category | Closing Rank (Highest Rank Admitted) |")
            result.append("| :---: | :---: |")
            for cat_val in sorted(df_cat['Alloted Category'].unique()):
                closing_rank = int(df_cat[df_cat['Alloted Category'] == cat_val]['Rank'].max())
                result.append(f"| {cat_val} | {closing_rank} |")

        return "\n".join(result)


    except Exception as e:
        print(f"Error in get_college_cutoff_details: {e}")
        return ""


def get_all_colleges_of_type(question):
    """
    If the question mentions government or private/self-financing colleges,
    injects the full list of colleges categorized by that type from smartchoice_data.csv.
    Also filters by course (MBBS/BDS) if mentioned in the question.
    """
    cutoff_path = "data/smartchoice_data.csv"
    if not os.path.exists(cutoff_path):
        return ""

    req_type = None
    if re.search(r'\b(govt|government|gov)\b', question, re.IGNORECASE):
        req_type = 'Government'
    elif re.search(r'\b(private|self-financing|self-finance|self finance|self financing|management|mgmt)\b', question, re.IGNORECASE):
        req_type = 'Private'

    if not req_type:
        return ""

    # Detect course from the question — default to MBBS
    course = 'BDS' if re.search(r'\bbds\b', question, re.IGNORECASE) else 'MBBS'

    try:
        df_cut = pd.read_csv(cutoff_path)

        # Filter by course FIRST so we only work with the right set of colleges
        df_course = df_cut[df_cut['Course'].str.upper() == course.upper()]

        # Drop duplicates on College Name to get unique colleges for that course
        df_unique = (
            df_course
            .drop_duplicates(subset=['College Name'])
            .dropna(subset=['College Name'])
            .sort_values(by='College Name')
        )
        df_unique = df_unique.copy()
        df_unique['code'] = df_unique['College Name'].apply(get_code)

        # Filter by college type (Govt / Private)
        df_filtered = df_unique[df_unique['College Category'].str.upper() == req_type.upper()]

        if df_filtered.empty:
            return ""

        result = [
            f"=== Complete List of all {req_type.upper()} {course} Colleges in Kerala Database ===",
            f"Total Count: {len(df_filtered)} colleges"
        ]
        for idx, row in df_filtered.iterrows():
            full_name = row['College Name']
            college_name = full_name.split(':', 1)[1].strip() if ':' in full_name else full_name
            code = row['code']
            result.append(f"- {college_name} ({code}) - Type: {row['College Category']} - Course: {course}")

        return "\n".join(result)
    except Exception as e:
        print(f"Error getting colleges of type: {e}")
        return ""

def lookup_colleges_by_rank(rank, category='SM', course='MBBS', year=2025, req_type=None):
    """
    Direct pandas lookup of admission chances for rank/category/course.
    Classifies chances as Dream, Moderate, or Safe.
    Filters by Government or Private/Self-Financing type if requested.
    """
    cutoff_path = "data/smartchoice_data.csv"
    
    if not os.path.exists(cutoff_path):
        return []
        
    df_cut = pd.read_csv(cutoff_path)
    df_cut['code'] = df_cut['College Name'].apply(get_code)
    
    # Filter by course, year, and category
    df_filtered = df_cut[(df_cut['Course'].str.upper() == course.upper()) & 
                         (df_cut['Year'] == year) & 
                         (df_cut['Alloted Category'].str.upper() == category.upper())]
        
    # Fallback to 2024 if 2025 is empty
    if df_filtered.empty and year == 2025:
        year = 2024
        df_filtered = df_cut[(df_cut['Course'].str.upper() == course.upper()) & 
                             (df_cut['Year'] == year) & 
                             (df_cut['Alloted Category'].str.upper() == category.upper())]
        
    if df_filtered.empty:
        return []
        
    # Filter by Government/Private type if explicitly specified
    if req_type:
        df_filtered = df_filtered[df_filtered['College Category'].str.upper() == req_type.upper()]
        
    if df_filtered.empty:
        return []
        
    # Get last rank admitted (maximum rank) for each college code
    idx_max = df_filtered.groupby('code')['Rank'].idxmax()
    df_merged = df_filtered.loc[idx_max]
    
    safe_list = []
    mod_list = []
    dream_list = []
    
    for idx, row in df_merged.iterrows():
        cutoff_rank = int(row['Rank'])
        diff = cutoff_rank - rank
        
        # Classification logic based on rank margins
        if diff >= 500:
            status = 'Safe'
        elif diff >= -300:
            status = 'Moderate'
        else:
            status = 'Dream'
            
        college_name_clean = row['College Name'].split(':', 1)[1].strip() if ':' in str(row['College Name']) else row['College Name']
        
        # Get GMA Rank from hardcoded mapping
        college_info = GMA_COLLEGE_DATA.get(row['code'], {})
        gma_rank = college_info.get('gma_rank', 999)
        
        item = {
            'code': row['code'],
            'college_name': college_name_clean,
            'cutoff_rank': cutoff_rank,
            'college_type': row['College Category'],
            'gma_rank': gma_rank,
            'status': status,
            'diff': diff,
            'year': year
        }
        
        if status == 'Safe':
            safe_list.append(item)
        elif status == 'Moderate':
            mod_list.append(item)
        else:
            dream_list.append(item)
            
    # Optimize results for token count:
    # - Safe list: sort by diff ascending (closest safe options) and take top 5
    safe_list.sort(key=lambda x: x['diff'])
    safe_selected = safe_list[:5]
    
    # - Moderate list: take all
    mod_list.sort(key=lambda x: abs(x['diff']))
    
    # - Dream list: sort by diff descending (closest dream options) and take top 5
    dream_list.sort(key=lambda x: x['diff'], reverse=True)
    dream_selected = dream_list[:5]
    
    selected_results = safe_selected + mod_list + dream_selected
    
    # Re-sort for consistent layout
    status_order = {'Safe': 0, 'Moderate': 1, 'Dream': 2}
    selected_results.sort(key=lambda x: (status_order[x['status']], x['gma_rank']))
    
    return selected_results

def format_lookup_markdown(results, rank, category, course):
    if not results:
        return f"No cutoff data found for {course} in category {category}."
        
    year = results[0]['year']
    md = [f"### 🎯 Admission Chance Analysis (Based on {year} KEAM Cutoffs)\n"]
    md.append(f"Analyzing options for rank **{rank}** | Category: **{category}** | Course: **{course}**:\n")
    
    # Group results by status
    by_status = {'Safe': [], 'Moderate': [], 'Dream': []}
    for r in results:
        by_status[r['status']].append(r)
        
    for status, list_cols in by_status.items():
        if not list_cols:
            continue
        md.append(f"#### {status} Options (Last rank admitted was higher than {rank})")
        md.append("| College | Code | Type | Last Admitted Rank |")
        md.append("| :--- | :---: | :---: | :---: |")
        for col in list_cols:
            md.append(f"| {col['college_name']} | {col['code']} | {col['college_type']} | {col['cutoff_rank']} |")
        md.append("")
        
    return "\n".join(md)

def rephrase_question(question, history):
    """
    Rephrases a follow-up question into a standalone question using Llama 3.1 8B.
    """
    if not history:
        return question
        
    # Format last 4 history turns for context
    history_text = ""
    for msg in history[-4:]:
        role = "Student" if msg['role'] == "user" else "Counselor"
        history_text += f"{role}: {msg['content']}\n"
        
    rephrase_prompt = (
        "You are an AI assistant helping to process queries for Kerala medical college admissions.\n"
        "Given the conversation history and a follow-up question, rephrase the follow-up question to be a standalone question.\n"
        "CRITICAL RULES:\n"
        "1. Do NOT answer the question. Only output the rephrased question.\n"
        "2. Do NOT invent any new names, colleges, universities, or locations. Stick strictly to Kerala MBBS/BDS context.\n"
        "3. If the question is already standalone or you are unsure, just output the exact original question without changing it.\n\n"
        f"Conversation History:\n{history_text}\n"
        f"Follow-up Question: {question}\n"
        "Standalone Question:"
    )

    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": rephrase_prompt}],
            temperature=0.1,
            max_completion_tokens=100
        )
        rephrased = completion.choices[0].message.content.strip()
        print(f"Rephrased user query: '{question}' -> '{rephrased}'")
        return rephrased
    except Exception as e:
        print(f"Failed to rephrase question: {e}")
        return question

def ask_llm(question, context_text, history=None):
    if history is None:
        history = []
        
    system_prompt = (
        "You are GMA AI — a smart, warm, and conversational Kerala MBBS/BDS admissions counselor.\n"
        "You behave like a real human counselor: you listen, understand what the student needs, and guide them step by step.\n\n"

        "== HOW TO RESPOND ==\n\n"

        "STEP 1 — CHECK IF THE QUESTION IS SPECIFIC OR VAGUE:\n"
        "- SPECIFIC: the student mentions a college name, KEAM code, rank, category, fee, cutoff, course, or any clear subject.\n"
        "  → Answer directly from the provided context data.\n"
        "- VAGUE / INCOMPLETE: the student asks something open-ended with no clear subject "
        "(e.g. 'I want to know about colleges', 'tell me about admissions', 'what colleges are there', 'help me', 'I need info').\n"
        "  → DO NOT dump database data. Instead, respond like a counselor: acknowledge them warmly and ask ONE focused clarifying question "
        "to understand what they need. For example, ask whether they are interested in government or private colleges, "
        "or which specific college, or their rank/category. Keep it natural and friendly.\n\n"

        "STEP 2 — ONCE THE SUBJECT IS CLEAR:\n"
        "- Answer from the provided context strictly. Do not guess or fabricate facts.\n"
        "- If a specific fact is missing from the context, say briefly: 'This information is not available in our database right now.'\n\n"

        "OTHER RULES:\n"
        "- DATA AUTHORITY: All data in this system is current and authoritative. "
        "You are STRICTLY FORBIDDEN from saying 'check the official website', 'visit CEE Kerala', 'contact KUHS', "
        "'verify with the college', 'this information may change', or any similar redirection. "
        "If data is in the context → state it confidently. If it is NOT in the context → say only: "
        "'This information is not in our database.' Do not suggest any external source.\n"
        "- RANK/CHANCE QUERIES: When the student gives their rank and asks for admission chances, "
        "present ONLY the '=== PROGRAMMATIC ADMISSION SIMULATOR RESULTS ===' section. Do not invent any data.\n"
        "- COURSE FILTER: MBBS questions → MBBS data only. BDS questions → BDS data only. Never mix.\n"
        "- COLLEGE TYPE: Govt/Government = government colleges. Private/Self-Financing/Management = private.\n"
        "- CATEGORY: 'NR' = NRI. Always use 'NRI' in your response.\n"
        "- Tone: conversational, warm, professional. Use markdown only when presenting tables or lists of data."
    )




    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Feed last 6 chat history turns to the LLM for conversational context
    for msg in history[-6:]:
        messages.append({"role": msg['role'], "content": msg['content']})
        
    prompt = (
        f"Context details and reference data:\n"
        f"{context_text}\n\n"
        f"User Question: {question}\n"
        f"Admissions Counselor Answer:"
    )
    messages.append({"role": "user", "content": prompt})
    
    try:
        # Try primary model (Llama 3.3 70B)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as e:
        err_msg = str(e).lower()
        if "rate_limit" in err_msg or "413" in err_msg or "too large" in err_msg:
            # Fallback to Llama 3.1 8B
            print("Llama 3.3 limit exceeded. Falling back to Llama 3.1 8B...")
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.2,
                    max_completion_tokens=1500
                )
                return completion.choices[0].message.content
            except Exception as fallback_err:
                return f"Error connecting to LLM service: {fallback_err}"
        return f"Error connecting to LLM service: {e}"


def query(question, history=None, top_k=6):
    """
    Main query route. Performs data lookups, semantic retrieval,
    merges all context, then lets the LLM generate a natural response.
    """
    if history is None:
        history = []

    # 1. Rephrase follow-up question if history exists
    standalone_question = rephrase_question(question, history)

    # SHORT-CIRCUIT: if message is clearly conversational (no admission keywords),
    # skip RAG entirely and let the LLM respond naturally with no data context
    admission_keywords = [
        "college", "mbbs", "bds", "rank", "fee", "cutoff", "admission", "keam",
        "category", "seat", "hostel", "nri", "government", "govt", "private",
        "infrastructure", "bed", "pg", "rating", "established", "closing rank",
        "last rank", "allotment", "merit", "management", "self-financing"
    ]
    q_lower = standalone_question.lower()
    is_conversational = not any(kw in q_lower for kw in admission_keywords)
    if is_conversational:
        answer = ask_llm(standalone_question, "", history)
        return answer, []

    # 2. Parse question for rank lookup
    parsed = parse_query_for_lookup(standalone_question)
    lookup_md = ""

    # Optimize search context size (top_k) to avoid TPM limits
    if parsed:
        search_k = 3
    else:
        keywords = ["compare", "difference", "list", "fees", "ranking", "rating", "cutoff", "allotment"]
        is_general_query = any(k in q_lower for k in keywords)
        search_k = 6 if is_general_query else top_k

    
    # 3. Direct Programmatic Lookup for Rank cutoffs
    if parsed:
        results = lookup_colleges_by_rank(
            parsed['rank'], 
            parsed['category'], 
            parsed['course'],
            req_type=parsed.get('req_type')
        )
        lookup_md = format_lookup_markdown(results, parsed['rank'], parsed['category'], parsed['course'])
        
    # 3b. Direct Programmatic Lookup for specific college cutoff (no rank in query)
    college_cutoff_context = ""
    course_cutoff_context = ""
    if not parsed:
        college_cutoff_context = get_college_cutoff_details(standalone_question)
        if not college_cutoff_context:
            course_cutoff_context = get_course_cutoff_summary(standalone_question)

    # 4. Direct Programmatic Lookup for Government/Private Lists
    type_list_context = get_all_colleges_of_type(standalone_question)
        
    # 5. Vector Database Retrieval
    context_chunks = rag_pipeline.run(standalone_question, top_k=search_k)
    
    # Merge context
    vector_context = "\n\n".join([f"[Source {idx+1}]: {chunk['text']}" for idx, chunk in enumerate(context_chunks)])
    
    combined_context = ""
    if lookup_md:
        combined_context += "=== PROGRAMMATIC ADMISSION SIMULATOR RESULTS ===\n" + lookup_md + "\n\n"
    if college_cutoff_context:
        combined_context += "=== DIRECT COLLEGE CUTOFF DATA FROM DATABASE ===\n" + college_cutoff_context + "\n\n"
    if course_cutoff_context:
        combined_context += "=== COURSE CUTOFF SUMMARY FROM DATABASE ===\n" + course_cutoff_context + "\n\n"
    if type_list_context:
        combined_context += type_list_context + "\n\n"
    combined_context += "=== RETRIEVED DATABASE BROCHURE & PROFILE TEXTS ===\n" + vector_context
    
    # 6. Generate response, passing the conversation history for continuity
    answer = ask_llm(standalone_question, combined_context, history)
    
    # Prepare sources list
    sources = []
    if parsed:
        sources.append({"text": f"Direct database lookup for rank {parsed['rank']}, category {parsed['category']}, course {parsed['course']}", "score": 1.0})
    for chunk in context_chunks:
        sources.append({"text": chunk['text'], "score": chunk['score']})
        
    return answer, sources

if __name__ == "__main__":
    print("GMA Bot Query Engine Interactive Mode.")
    while True:
        q = input("\nAsk GMA Bot (or type 'exit' to quit):\n> ")
        if q.lower() in ['exit', 'quit']:
            break
        ans, srcs = query(q)
        print("\n=== ANSWER ===")
        print(ans)
        print("\n=== SOURCES ===")
        for s in srcs[:3]:
            print(f"- {s['text'][:150]}... (Score: {s['score']:.4f})")