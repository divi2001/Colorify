import mysql.connector
from mysql.connector import Error
import requests
import json
import pandas as pd
from datetime import datetime
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
import difflib
from Levenshtein import distance as levenshtein_distance
import nltk
from nltk.tokenize import word_tokenize
from langdetect import detect
from difflib import SequenceMatcher
import multiprocessing as mp
from multiprocessing import Pool, Manager
import os
from functools import partial

# Download the necessary resources
nltk.download('punkt')
from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

def preprocess_text(text):
    text = str(text) if pd.notna(text) else ""
    text = re.sub(r'_x[0-9A-Fa-f]{4}_', '', text)
    text = text.replace('-', '').replace('.', ' ').replace(',','').replace('$','').replace('#','').replace('"','').replace("'","").replace('|','').replace('।','').replace('\u200d','').replace('?','').replace('!','')
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    return text

def tokenize_text(text, language):
    if language in ['hi', 'mar']:
        return re.findall(r'\S+', text)
    elif language == 'en':
        text = text.lower()
        return word_tokenize(text)
    else:
        return text.split()

def word_similarity(word1, word2):
    return SequenceMatcher(None, word1, word2).ratio()

def is_compound_word_candidate(word1, word2, target):
    """
    Helper function to determine if two words should be combined to match a target word
    Returns True if this looks like a valid compound word case, False otherwise
    """
    # If target exactly matches either component word, don't combine
    if (word1.lower() == target.lower() or word2.lower() == target.lower()):
        return False
    
    # Check for compound form matching target
    combined = (word1 + word2).replace(" ", "").lower()
    target_clean = target.replace(" ", "").lower() 
    
    # If compound form exactly matches target, this is a candidate
    if combined == target_clean:
        return True
        
    # If not an exact match, check using similarity
    if len(combined) == len(target_clean):
        similarity = SequenceMatcher(None, combined, target_clean).ratio()
        if similarity > 0.8:
            return True
    
    return False

def check_combined_word_similarity(current_word, other_word, next_word):
    """
    Check if words should be combined or split
    Uses both exact matches and similarity thresholds
    """
    if not current_word or not other_word or not next_word:
        return False, None, False
    
    # Check if other_word is exactly the same as either current_word or next_word
    # This prevents combining when one of the words already matches
    if current_word.lower() == other_word.lower() or next_word.lower() == other_word.lower():
        return False, None, False
    
    # Check if other word contains either current_word or next_word as complete words
    # This handles the "critical (a critical)" case
    if " " in other_word:
        other_parts = other_word.lower().split()
        if current_word.lower() in other_parts or next_word.lower() in other_parts:
            return False, None, False
    
    # First check exact matches
    # Check if other word is already a compound of current and next
    current_next_combined_clean = (current_word + next_word).replace(" ", "")
    other_clean = other_word.replace(" ", "")
    
    if current_next_combined_clean.lower() == other_clean.lower():
        # Additional check for connector words
        if " " in other_word:
            other_parts = other_word.lower().split()
            if len(other_parts) > 1 and (current_word.lower() in other_parts or next_word.lower() in other_parts):
                return False, None, False
                
        # Return with space between words to maintain clarity
        return True, current_word + " " + next_word, False
    
    # Check if current word is a compound that should be split
    if current_word.replace(" ", "").lower() == (other_word + next_word).replace(" ", "").lower():
        # Additional check for connector words
        if " " in current_word:
            current_parts = current_word.lower().split()
            if len(current_parts) > 1 and (other_word.lower() in current_parts or next_word.lower() in current_parts):
                return False, None, False
                
        # Return with space between words to maintain clarity
        return True, other_word + " " + next_word, True
    
    # If exact matches fail, try similarity-based checks
    # Check if current matches other+next using similarity
    other_combined_clean = (other_word + next_word).replace(" ", "")
    current_clean = current_word.replace(" ", "")
    
    if len(other_combined_clean) == len(current_clean):
        similarity = SequenceMatcher(None, other_combined_clean, current_clean).ratio()
        if similarity > 0.8:
            # Return with space between words to maintain clarity
            return True, other_word + " " + next_word, True
    
    # Then check if current+next matches other using similarity
    combined_clean = (current_word + next_word).replace(" ", "")
    
    if len(combined_clean) == len(other_clean):
        similarity = SequenceMatcher(None, combined_clean, other_clean).ratio()
        if similarity > 0.8:
            # Return with space between words to maintain clarity
            return True, current_word + " " + next_word, False
            
    return False, None, False

def check_exact_compound_ignore_match(alignment, idx, ignore_list):
    """
    Check if current and next positions form an exact compound match that should be ignored
    Only returns True if both sequences match the ignored compound exactly
    """
    if idx + 1 >= len(alignment):
        return False
    
    op1, word1_1, word2_1 = alignment[idx]
    op2, word1_2, word2_2 = alignment[idx + 1]
    
    # Only check for compounds in match or similar operations
    if op1 not in ['match', 'similar'] or op2 not in ['match', 'similar']:
        return False
    
    # Check if word1 sequence forms a compound in ignore list
    if word1_1 and word1_2:
        compound1 = word1_1 + " " + word1_2
        if compound1.lower() in ignore_list:
            # Verify that word2 also represents the same compound
            # Either as a compound or as a single word without space
            if word2_1 and word2_2:
                compound2 = word2_1 + " " + word2_2
                if compound2.lower() == compound1.lower():
                    return True
            elif word2_1 and not word2_2:
                # Check if word2_1 is the compound without space
                if word2_1.replace(" ", "").lower() == compound1.replace(" ", "").lower():
                    return True
    
    return False

def compare_texts(text1, text2, ignore_list):
    if text1 is None or text2 is None:
        return {'is_empty': True}

    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    ignore_list = [preprocess_text(word).lower() for word in ignore_list]

    try:
        language = detect(text1) if len(text1) > len(text2) else detect(text2)
    except:
        language = 'en'

    tokens1 = tokenize_text(text1, language)
    tokens2 = tokenize_text(text2, language)

    added = []
    missed = []
    spelling = []
    grammar = []
    colored_words = []

    # Create alignment matrix
    m, n = len(tokens1), len(tokens2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if tokens1[i-1].lower() == tokens2[j-1].lower():
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                similarity = word_similarity(tokens1[i-1].lower(), tokens2[j-1].lower())
                dp[i][j] = max(dp[i-1][j], dp[i][j-1], dp[i-1][j-1] + similarity)

    # Backtrack to find the alignment
    i, j = m, n
    alignment = []
    while i > 0 and j > 0:
        if tokens1[i-1].lower() == tokens2[j-1].lower():
            alignment.append(('match', tokens1[i-1], tokens2[j-1]))
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i-1][j-1] + word_similarity(tokens1[i-1].lower(), tokens2[j-1].lower()):
            # Check for compound words
            combined_word1 = tokens1[i-1]
            combined_word2 = tokens2[j-1]
            
            # Look ahead for potential compound words in text1
            if i > 1:
                # Check if combining tokens1[i-2] + tokens1[i-1] matches tokens2[j-1]
                if is_compound_word_candidate(tokens1[i-2], tokens1[i-1], tokens2[j-1]):
                    # Preserve space between combined words
                    combined_word1 = tokens1[i-2] + " " + tokens1[i-1]
                    alignment.append(('similar', combined_word1, tokens2[j-1]))
                    i -= 2
                    j -= 1
                    continue
            
            # Look ahead for potential compound words in text2
            if j > 1:
                # Check if combining tokens2[j-2] + tokens2[j-1] matches tokens1[i-1]
                if is_compound_word_candidate(tokens2[j-2], tokens2[j-1], tokens1[i-1]):
                    # Preserve space between combined words
                    combined_word2 = tokens2[j-2] + " " + tokens2[j-1]
                    alignment.append(('similar', tokens1[i-1], combined_word2))
                    i -= 1
                    j -= 2
                    continue
            
            # If no compound words found, just align as similar
            alignment.append(('similar', tokens1[i-1], tokens2[j-1]))
            i -= 1
            j -= 1
            
        elif dp[i][j] == dp[i-1][j]:
            # Look ahead for compound words before deciding delete
            found_compound = False
            if i > 1 and j > 0:
                # Check if combining tokens1[i-2] + tokens1[i-1] matches tokens2[j-1]
                if is_compound_word_candidate(tokens1[i-2], tokens1[i-1], tokens2[j-1]):
                    alignment.append(('similar', tokens1[i-2] + " " + tokens1[i-1], tokens2[j-1]))
                    i -= 2
                    j -= 1
                    found_compound = True
            
            # Check if there's a match in the next few positions
            if not found_compound:
                found_match = False
                look_ahead = 1
                while j + look_ahead < n and look_ahead < 3:
                    if tokens1[i-1].lower() == tokens2[j+look_ahead].lower():
                        # Insert skipped words
                        for k in range(look_ahead):
                            alignment.append(('insert', None, tokens2[j+k]))
                        alignment.append(('match', tokens1[i-1], tokens2[j+look_ahead]))
                        i -= 1
                        j += look_ahead + 1
                        found_match = True
                        break
                    look_ahead += 1
            
                if not found_match:
                    alignment.append(('delete', tokens1[i-1], None))
                    i -= 1
        else:
            # Look ahead for compound words before deciding insert
            found_compound = False
            if j > 1 and i > 0:
                # Check if combining tokens2[j-2] + tokens2[j-1] matches tokens1[i-1]
                if is_compound_word_candidate(tokens2[j-2], tokens2[j-1], tokens1[i-1]):
                    alignment.append(('similar', tokens1[i-1], tokens2[j-2] + " " + tokens2[j-1]))
                    i -= 1
                    j -= 2
                    found_compound = True
            
            if not found_compound:
                alignment.append(('insert', None, tokens2[j-1]))
                j -= 1

    while i > 0:
        alignment.append(('delete', tokens1[i-1], None))
        i -= 1
    while j > 0:
        alignment.append(('insert', None, tokens2[j-1]))
        j -= 1

    alignment.reverse()
    
    # Process alignment to handle None cases - combine with next tokens
    processed_alignment = []
    i = 0
    while i < len(alignment):
        op, word1, word2 = alignment[i]
        
        # Handle the case where word1 is None (insert operation)
        if op == 'insert' and word1 is None and i+1 < len(alignment):
            next_op, next_word1, next_word2 = alignment[i+1]
            
            # If the next operation has a valid word1, try to find a match with combined word2
            if next_word1 is not None:
                # Check using compound word candidate function
                if word2 and next_word1 and is_compound_word_candidate(word2, next_word2 or "", next_word1):
                    combined_word2 = word2 + " " + next_word2 if next_word2 else word2
                    processed_alignment.append(('similar', next_word1, combined_word2))
                    i += 2  # Skip the next token since we used it
                    continue
                else:
                    processed_alignment.append((op, word1, word2))
            else:
                processed_alignment.append((op, word1, word2))
        
        # Handle the case where word2 is None (delete operation)
        elif op == 'delete' and word2 is None and i+1 < len(alignment):
            next_op, next_word1, next_word2 = alignment[i+1]
            
            # If the next operation has a valid word2, try to find a match with combined word1
            if next_word2 is not None:
                # Check using compound word candidate function
                if word1 and next_word2 and is_compound_word_candidate(word1, next_word1 or "", next_word2):
                    combined_word1 = word1 + " " + next_word1 if next_word1 else word1
                    processed_alignment.append(('similar', combined_word1, next_word2))
                    i += 2  # Skip the next token since we used it
                    continue
                else:
                    processed_alignment.append((op, word1, word2))
            else:
                processed_alignment.append((op, word1, word2))
        
        # If no special handling needed, add the operation as is
        else:
            processed_alignment.append((op, word1, word2))
        
        i += 1

    alignment = processed_alignment

    skip_next = False

    for idx, (op, word1, word2) in enumerate(alignment):
        if skip_next:
            skip_next = False
            continue

        if op == 'match':
            colored_words.append({'word': word1, 'color': 'black'})
        elif op == 'similar':
            # Check if this is part of an exact compound match that should be ignored
            if check_exact_compound_ignore_match(alignment, idx, ignore_list):
                colored_words.append({'word': word1, 'color': 'black'})
                skip_next = True
                continue
            
            if word1 and word2 and (word1.lower() in ignore_list or word2.lower() in ignore_list):
                # Handle single word ignores or compound words written as single word
                if " " in word1 and word1.replace(" ", "").lower() in ignore_list:
                    parts = word1.split()
                    for part in parts:
                        colored_words.append({'word': part, 'color': 'black'})
                else:
                    colored_words.append({'word': word1, 'color': 'black'})
            else:
                next_word1 = None
                next_word2 = None
                if idx + 1 < len(alignment):
                    next_op, next_w1, next_w2 = alignment[idx + 1]
                    # Look ahead for valid next words
                    look_ahead = 1
                    while (next_w1 is None or next_w2 is None) and idx + look_ahead + 1 < len(alignment):
                        _, temp_w1, temp_w2 = alignment[idx + look_ahead + 1]
                        if next_w1 is None and temp_w1 is not None:
                            next_w1 = temp_w1
                        if next_w2 is None and temp_w2 is not None:
                            next_w2 = temp_w2
                        look_ahead += 1

                    next_word1 = next_w1 if next_w1 != word1 else None
                    next_word2 = next_w2 if next_w2 != word2 else None

                # Process combination attempts
                if next_word1:
                    is_combined1, combined1, reverse1 = check_combined_word_similarity(word1, word2, next_word1)
                else:
                    is_combined1, combined1, reverse1 = False, None, False

                if next_word2:
                    is_combined2, combined2, reverse2 = check_combined_word_similarity(word2, word1, next_word2)
                else:
                    is_combined2, combined2, reverse2 = False, None, False

                # Check if combined words are in ignore list (only if they match exactly)
                if is_combined1 and combined1 and combined1.lower() in ignore_list:
                    parts = combined1.split()
                    for part in parts:
                        colored_words.append({'word': part, 'color': 'black'})
                    skip_next = True
                elif is_combined2 and combined2 and combined2.lower() in ignore_list:
                    parts = combined2.split()
                    for part in parts:
                        colored_words.append({'word': part, 'color': 'black'})
                    skip_next = True
                elif is_combined1 and not reverse1:
                    # Split combined word when showing
                    if " " in combined1:
                        parts = combined1.split()
                        for part in parts:
                            colored_words.append({'word': part, 'color': 'red'})
                    else:
                        colored_words.append({'word': combined1, 'color': 'red'})
                    colored_words.append({'word': word2, 'color': 'green'})
                    spelling.append((combined1, word2))
                    skip_next = True
                elif is_combined2 and not reverse2:
                    colored_words.append({'word': word1, 'color': 'red'})
                    # Split combined word when showing
                    if " " in combined2:
                        parts = combined2.split()
                        for part in parts:
                            colored_words.append({'word': part, 'color': 'green'})
                    else:
                        colored_words.append({'word': combined2, 'color': 'green'})
                    spelling.append((word1, combined2))
                    skip_next = True
                elif is_combined1 and reverse1:
                    colored_words.append({'word': word1, 'color': 'red'})
                    # Split combined word when showing
                    if " " in combined1:
                        parts = combined1.split()
                        for part in parts:
                            colored_words.append({'word': part, 'color': 'green'})
                    else:
                        colored_words.append({'word': combined1, 'color': 'green'})
                    spelling.append((word1, combined1))
                    skip_next = True
                elif is_combined2 and reverse2:
                    # Split combined word when showing
                    if " " in combined2:
                        parts = combined2.split()
                        for part in parts:
                            colored_words.append({'word': part, 'color': 'red'})
                    else:
                        colored_words.append({'word': combined2, 'color': 'red'})
                    colored_words.append({'word': word2, 'color': 'green'})
                    spelling.append((combined2, word2))
                    skip_next = True
                elif word1 and word2:  # Only process if both words exist
                    # Remove spaces for comparing compound words
                    word1_clean = word1.replace(" ", "")
                    word2_clean = word2.replace(" ", "")
                    
                    similarity = SequenceMatcher(None, word1_clean.lower(), word2_clean.lower()).ratio()
                    
                    if similarity > 0.8:
                        colored_words.append({'word': word1, 'color': 'red'})
                        colored_words.append({'word': word2, 'color': 'green'})
                        spelling.append((word1, word2))
                    else:
                        distance = levenshtein_distance(word1_clean, word2_clean)
                        max_length = max(len(word1_clean), len(word2_clean))
                        similarity_pct = (max_length - distance) / max_length * 100

                        if similarity_pct >= 40:
                            colored_words.append({'word': word1, 'color': 'red'})
                            colored_words.append({'word': word2, 'color': 'green'})
                            spelling.append((word1, word2))
                        else:
                            colored_words.append({'word': word1, 'color': 'red'})
                            colored_words.append({'word': word2, 'color': 'green'})
                            missed.append(word1)
                            added.append(word2)
        elif op == 'delete':
            if word1 and word1.lower() not in ignore_list:
                colored_words.append({'word': word1, 'color': 'red'})
                missed.append(word1)
            elif word1:
                colored_words.append({'word': word1, 'color': 'black'})
        elif op == 'insert':
            if word2 and word2.lower() not in ignore_list:
                colored_words.append({'word': word2, 'color': 'green'})
                added.append(word2)
            elif word2:
                colored_words.append({'word': word2, 'color': 'black'})

    return {
        'colored_words': colored_words,
        'missed': missed,
        'added': added,
        'spelling': spelling,
        'grammar': grammar
    }

# Database configuration
DB_CONFIG = {
    'host': "localhost",
    'port': 3306,
    'user': "root",
    'password': "1221",
    'database': "shexamjuly25checking_3rdst"
}

def create_connection():
    """Create database connection with proper configuration"""
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            autocommit=True,  # Enable autocommit
            use_pure=True,    # Use pure Python implementation
            consume_results=True,  # Consume all results
            buffered=True     # Use buffered cursor
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def load_all_data(department_id, limit=100):
    """Load all required data at once to avoid database connection issues in multiprocessing"""
    print(f"Loading data from database (first {limit} students)...")
    connection = create_connection()
    if not connection:
        return None, None, None, None
    
    try:
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        # Get first 100 students
        cursor.execute("SELECT student_id, subjectsId, qset FROM students WHERE departmentId = %s LIMIT %s", (department_id, limit))
        students = cursor.fetchall()
        cursor.fetchall()  # Consume any remaining results
        
        # Get all answer passages for the subjects/qsets used by students
        subject_qset_pairs = list(set((student['subjectsId'], student['qset']) for student in students))
        answer_passages = {}
        
        for subject_id, qset in subject_qset_pairs:
            cursor.execute("SELECT textPassageA, textPassageB FROM audiodb WHERE subjectId = %s AND qset = %s", 
                         (subject_id, qset))
            result = cursor.fetchone()
            cursor.fetchall()  # Consume any remaining results
            if result:
                answer_passages[(subject_id, qset)] = result
        
        # Get all student passages
        student_ids = [student['student_id'] for student in students]
        student_passages = {}
        
        # Process student IDs in batches to avoid query length issues
        batch_size = 1000
        for i in range(0, len(student_ids), batch_size):
            batch_ids = student_ids[i:i + batch_size]
            placeholders = ','.join(['%s'] * len(batch_ids))
            query = f"SELECT student_id, passageA, passageB FROM finalPassageSubmit WHERE student_id IN ({placeholders})"
            cursor.execute(query, batch_ids)
            results = cursor.fetchall()
            cursor.fetchall()  # Consume any remaining results
            
            for result in results:
                student_passages[result['student_id']] = result
        
        # Get all modreview data
        modreview_data = {}
        for i in range(0, len(student_ids), batch_size):
            batch_ids = student_ids[i:i + batch_size]
            placeholders = ','.join(['%s'] * len(batch_ids))
            query = f"SELECT student_id, QPA, QPB FROM modreviewlog WHERE student_id IN ({placeholders})"
            cursor.execute(query, batch_ids)
            results = cursor.fetchall()
            cursor.fetchall()  # Consume any remaining results
            
            for result in results:
                modreview_data[result['student_id']] = result
        
        cursor.close()
        connection.close()
        
        print(f"Loaded data for {len(students)} students (limited to first {limit})")
        print(f"Loaded {len(answer_passages)} answer passage sets")
        print(f"Loaded {len(student_passages)} student passage sets")
        print(f"Loaded {len(modreview_data)} modreview records")
        
        return students, answer_passages, student_passages, modreview_data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        if connection:
            connection.close()
        return None, None, None, None

def parse_ignore_list(ignore_text):
    """Convert ignore list text to array"""
    if not ignore_text or ignore_text.strip() == '':
        return []
    
    try:
        # Try JSON format first
        if ignore_text.strip().startswith('['):
            return json.loads(ignore_text)
        else:
            # Split by comma and clean
            items = [item.strip().strip('"\'') for item in ignore_text.split(',')]
            return [item for item in items if item]
    except:
        # Fallback to simple split
        items = [item.strip().strip('"\'') for item in ignore_text.split(',')]
        return [item for item in items if item]

def calculate_marks(api_result):
    """Calculate marks from API result"""
    if api_result is None:
        return 0, True, 0
    
    if api_result.get('is_empty', False):
        return 0, True, 0
    
    # Count total mistakes
    total_mistakes = (
        len(api_result.get('added', [])) +
        len(api_result.get('missed', [])) +
        len(api_result.get('spelling', [])) +
        len(api_result.get('grammar', []))
    )
    
    # Calculate marks (50 - mistakes/3, minimum 0)
    marks = max(0, 50 - (total_mistakes / 3))
    
    return marks, False, total_mistakes

def process_student_worker(args):
    """Worker function to process a single student - runs in parallel"""
    student_data, answer_passages, student_passages, modreview_data, process_id = args
    
    try:
        student_id = student_data['student_id']
        subject_id = student_data['subjectsId']
        qset = student_data['qset']
        
        # Get answer passages
        answer_key = (subject_id, qset)
        if answer_key not in answer_passages:
            return {
                'success': False,
                'student_id': student_id,
                'error': f'No answer passages found for subject {subject_id}, qset {qset}',
                'process_id': process_id
            }
        
        answer_data = answer_passages[answer_key]
        
        # Get student passages
        if student_id not in student_passages:
            return {
                'success': False,
                'student_id': student_id,
                'error': f'No student passages found for student {student_id}',
                'process_id': process_id
            }
        
        student_data_passages = student_passages[student_id]
        
        # Get modreview data (scores and ignore lists)
        modreview_record = modreview_data.get(student_id, {})
        modreview_qpa_score = modreview_record.get('QPA', None)
        modreview_qpb_score = modreview_record.get('QPB', None)
        
        # Parse ignore lists from modreview QPA and QPB columns
        ignore_a = parse_ignore_list(modreview_qpa_score) if modreview_qpa_score else []
        ignore_b = parse_ignore_list(modreview_qpb_score) if modreview_qpb_score else []
        
        # Compare Passage A
        result_a = compare_texts(
            student_data_passages['passageA'], 
            answer_data['textPassageA'], 
            ignore_a
        )
        
        if result_a is None:
            return {
                'success': False,
                'student_id': student_id,
                'error': 'Passage A comparison failed',
                'process_id': process_id
            }
        
        # Compare Passage B
        result_b = compare_texts(
            student_data_passages['passageB'], 
            answer_data['textPassageB'], 
            ignore_b
        )
        
        if result_b is None:
            return {
                'success': False,
                'student_id': student_id,
                'error': 'Passage B comparison failed',
                'process_id': process_id
            }
        
        # Calculate marks
        marks_a, empty_a, mistakes_a = calculate_marks(result_a)
        marks_b, empty_b, mistakes_b = calculate_marks(result_b)
        total_marks = marks_a + marks_b
        pass_status = 'Pass' if total_marks >= 32 else 'Fail'
        
        # Prepare result
        result = {
            'Student_ID': student_id,
            'Subject_ID': subject_id,
            'QSet': qset,
            'ModReview_QPA_Score': modreview_qpa_score,
            'ModReview_QPB_Score': modreview_qpb_score,
            
            'PassageA_IgnoreList': ', '.join(ignore_a) if ignore_a else 'None',
            'PassageA_Marks': round(marks_a, 2),
            'PassageA_Empty': empty_a,
            'PassageA_Added': ', '.join(str(x) for x in result_a.get('added', [])),
            'PassageA_Added_Count': len(result_a.get('added', [])),
            'PassageA_Missed': ', '.join(str(x) for x in result_a.get('missed', [])),
            'PassageA_Missed_Count': len(result_a.get('missed', [])),
            'PassageA_Spelling': ', '.join(str(x) for x in result_a.get('spelling', [])),
            'PassageA_Spelling_Count': len(result_a.get('spelling', [])),
            'PassageA_Grammar': ', '.join(str(x) for x in result_a.get('grammar', [])),
            'PassageA_Grammar_Count': len(result_a.get('grammar', [])),
            'PassageA_Total_Mistakes': mistakes_a,
            
            'PassageB_IgnoreList': ', '.join(ignore_b) if ignore_b else 'None',
            'PassageB_Marks': round(marks_b, 2),
            'PassageB_Empty': empty_b,
            'PassageB_Added': ', '.join(str(x) for x in result_b.get('added', [])),
            'PassageB_Added_Count': len(result_b.get('added', [])),
            'PassageB_Missed': ', '.join(str(x) for x in result_b.get('missed', [])),
            'PassageB_Missed_Count': len(result_b.get('missed', [])),
            'PassageB_Spelling': ', '.join(str(x) for x in result_b.get('spelling', [])),
            'PassageB_Spelling_Count': len(result_b.get('spelling', [])),
            'PassageB_Grammar': ', '.join(str(x) for x in result_b.get('grammar', [])),
            'PassageB_Grammar_Count': len(result_b.get('grammar', [])),
            'PassageB_Total_Mistakes': mistakes_b,
            
            'Total_Marks': round(total_marks, 2),
            'Pass_Status': pass_status,
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            'success': True,
            'result': result,
            'process_id': process_id,
            'marks': total_marks  # Add marks for logging
        }
        
    except Exception as e:
        return {
            'success': False,
            'student_id': student_data['student_id'],
            'error': f'Error: {str(e)}',
            'process_id': process_id
        }

def update_progress_with_marks(completed, total, start_time, recent_results, pass_count, fail_count):
    """Update and display progress with marks information"""
    elapsed_time = time.time() - start_time
    progress_pct = (completed / total) * 100
    
    if completed > 0:
        avg_time_per_student = elapsed_time / completed
        eta_seconds = avg_time_per_student * (total - completed)
        eta_minutes = eta_seconds / 60
        
        # Show recent student marks
        recent_marks_str = ""
        if recent_results:
            recent_marks = [f"{r['result']['Student_ID']}:{r['marks']:.1f}" for r in recent_results[-3:] if 'marks' in r]
            if recent_marks:
                recent_marks_str = f" | Recent: {', '.join(recent_marks)}"
        
        pass_rate = (pass_count / completed * 100) if completed > 0 else 0
        
        print(f"\rProgress: {completed}/{total} ({progress_pct:.1f}%) | "
              f"Pass: {pass_count} ({pass_rate:.1f}%) | Fail: {fail_count} | "
              f"Elapsed: {elapsed_time/60:.1f}m | ETA: {eta_minutes:.1f}m{recent_marks_str}", 
              end='', flush=True)

def save_to_excel(results, failed_students, department_id):
    """Save results to Excel"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_results_dept_{department_id}_first100_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main results
        if results:
            df = pd.DataFrame(results)
            df.to_excel(writer, sheet_name='Results', index=False)
        
        # Failed students
        if failed_students:
            failed_df = pd.DataFrame(failed_students)
            failed_df.to_excel(writer, sheet_name='Failed', index=False)
        
        # Summary
        total_students = len(results) + len(failed_students)
        success_rate = (len(results) / total_students * 100) if total_students > 0 else 0
        
        if results:
            pass_count = sum(1 for r in results if r['Pass_Status'] == 'Pass')
            fail_count = len(results) - pass_count
            avg_marks = sum(r['Total_Marks'] for r in results) / len(results)
            pass_rate = (pass_count / len(results) * 100) if len(results) > 0 else 0
            
            summary = pd.DataFrame({
                'Metric': ['Total Students (First 100)', 'Successful Processing', 'Failed Processing', 'Processing Success Rate (%)',
                          'Academic Pass', 'Academic Fail', 'Academic Pass Rate (%)', 'Average Marks'],
                'Value': [total_students, len(results), len(failed_students), round(success_rate, 1),
                         pass_count, fail_count, round(pass_rate, 1), round(avg_marks, 2)]
            })
        else:
            summary = pd.DataFrame({
                'Metric': ['Total Students (First 100)', 'Successful Processing', 'Failed Processing', 'Processing Success Rate (%)'],
                'Value': [total_students, len(results), len(failed_students), round(success_rate, 1)]
            })
        
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nResults saved to: {filename}")
    return filename

def parallel_process_students(students, answer_passages, student_passages, modreview_data, department_id, num_processes=20):
    """Process students in parallel using multiprocessing with preloaded data"""
    print(f"Starting parallel processing with {num_processes} processes...")
    
    # Prepare data for workers - each gets a copy of all preloaded data
    student_data_list = [
        (student, answer_passages, student_passages, modreview_data, i % num_processes) 
        for i, student in enumerate(students)
    ]
    
    results = []
    failed_students = []
    completed = 0
    total = len(students)
    pass_count = 0
    fail_count = 0
    recent_results = []
    
    start_time = time.time()
    
    # Use multiprocessing Pool
    with Pool(processes=num_processes) as pool:
        # Process students in parallel
        for result in pool.imap(process_student_worker, student_data_list):
            completed += 1
            
            if result['success']:
                results.append(result['result'])
                recent_results.append(result)
                
                # Keep only recent results for display
                if len(recent_results) > 10:
                    recent_results = recent_results[-10:]
                
                # Count pass/fail
                if result['result']['Pass_Status'] == 'Pass':
                    pass_count += 1
                else:
                    fail_count += 1
                    
            else:
                failed_students.append({
                    'Student_ID': result['student_id'],
                    'Subject_ID': 'N/A',
                    'QSet': 'N/A',
                    'Reason': result['error'],
                    'Process_ID': result['process_id']
                })
            
            # Update progress every 10 students or at the end
            if completed % 10 == 0 or completed == total:
                update_progress_with_marks(completed, total, start_time, recent_results, pass_count, fail_count)
    
    print()  # New line after progress
    return results, failed_students

def main():
    """Main function with parallel processing and preloaded data - FIRST 100 STUDENTS ONLY"""
    # Set department ID here
    DEPARTMENT_ID = 6
    NUM_PROCESSES = 20  # Use 20 out of 32 available cores
    STUDENT_LIMIT = 100  # Process only first 100 students
    
    print("=== PARALLEL PASSAGE EVALUATION SYSTEM (FIRST 100 STUDENTS) ===")
    print(f"Department ID: {DEPARTMENT_ID}")
    print(f"Student Limit: {STUDENT_LIMIT}")
    print(f"Number of CPU cores to use: {NUM_PROCESSES}")
    print(f"Available CPU cores: {mp.cpu_count()}")
    
    try:
        # Load data for first 100 students only
        students, answer_passages, student_passages, modreview_data = load_all_data(DEPARTMENT_ID, STUDENT_LIMIT)
        
        if not students:
            print("No students found or failed to load data")
            return
        
        print(f"Found {len(students)} students (limited to first {STUDENT_LIMIT})")
        print(f"Estimated processing time with {NUM_PROCESSES} cores: ~{len(students)/(NUM_PROCESSES*2):.1f} minutes")
        print("Starting processing...\n")
        
        # Process students in parallel
        start_time = time.time()
        results, failed_students = parallel_process_students(
            students, answer_passages, student_passages, modreview_data, DEPARTMENT_ID, NUM_PROCESSES
        )
        total_time = time.time() - start_time
        
        # Save results to Excel
        filename = save_to_excel(results, failed_students, DEPARTMENT_ID)
        
        # Calculate statistics
        if results:
            total_marks_list = [r['Total_Marks'] for r in results]
            pass_count = sum(1 for r in results if r['Pass_Status'] == 'Pass')
            fail_count = len(results) - pass_count
            avg_marks = sum(total_marks_list) / len(total_marks_list)
            max_marks = max(total_marks_list)
            min_marks = min(total_marks_list)
            
            print(f"\n=== DETAILED SUMMARY (FIRST 100 STUDENTS) ===")
            print(f"Total students processed: {len(students)} (limited to first {STUDENT_LIMIT})")
            print(f"Successful evaluations: {len(results)}")
            print(f"Failed evaluations: {len(failed_students)}")
            print(f"Processing success rate: {len(results)/len(students)*100:.1f}%")
            print(f"")
            print(f"Academic Results:")
            print(f"  Pass (≥32): {pass_count} ({pass_count/len(results)*100:.1f}%)")
            print(f"  Fail (<32): {fail_count} ({fail_count/len(results)*100:.1f}%)")
            print(f"  Average marks: {avg_marks:.2f}/100")
            print(f"  Highest marks: {max_marks:.2f}/100")
            print(f"  Lowest marks: {min_marks:.2f}/100")
            print(f"")
            print(f"Performance:")
            print(f"  Total processing time: {total_time/60:.1f} minutes")
            print(f"  Average time per student: {total_time/len(students):.2f} seconds")
            print(f"  Processing rate: {len(students)/(total_time/60):.1f} students/minute")
            print(f"  Speedup achieved: ~{NUM_PROCESSES}x faster than single-core")
            print(f"")
            print(f"Output file: {filename}")
            
            # Show top and bottom performers
            sorted_results = sorted(results, key=lambda x: x['Total_Marks'], reverse=True)
            print(f"\n=== TOP 5 PERFORMERS ===")
            for i, result in enumerate(sorted_results[:5], 1):
                print(f"{i}. Student {result['Student_ID']}: {result['Total_Marks']:.2f} marks ({result['Pass_Status']})")
            
            print(f"\n=== BOTTOM 5 PERFORMERS ===")
            for i, result in enumerate(sorted_results[-5:], 1):
                print(f"{i}. Student {result['Student_ID']}: {result['Total_Marks']:.2f} marks ({result['Pass_Status']})")
        
        # Show failed students if any
        if failed_students:
            print(f"\n=== FAILED STUDENTS (Processing Errors) ===")
            for failed in failed_students[:10]:  # Show first 10
                print(f"Student {failed['Student_ID']}: {failed['Reason']}")
            if len(failed_students) > 10:
                print(f"... and {len(failed_students) - 10} more (see Excel file)")
        
        print(f"\n=== NOTE ===")
        print(f"This run processed only the FIRST {STUDENT_LIMIT} students from department {DEPARTMENT_ID}")
        print(f"To process all students, modify STUDENT_LIMIT in the code or remove the limit parameter")
        
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure proper multiprocessing on Windows
    if mp.get_start_method(allow_none=True) != 'spawn':
        mp.set_start_method('spawn', force=True)
    main()