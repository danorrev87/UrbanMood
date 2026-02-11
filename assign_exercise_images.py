"""
Scan static/images/exercises/ subdirectories and auto-match images to exercises.
Maps directory names to BodySection values, fuzzy-matches filenames to exercise names,
and creates new Ejercicio entries for unmatched images.

Run with: python assign_exercise_images.py
"""
import os
import re
import unicodedata
from difflib import SequenceMatcher
from db import SessionLocal
from models import Ejercicio, BodySection, ExerciseType

# Map directory names to BodySection enum values
DIR_TO_SECTION = {
    'abdomen': BodySection.abdomen,
    'antebrazos': BodySection.biceps,
    'biceps': BodySection.biceps,
    'cardio': BodySection.cardio,
    'cuello': BodySection.estiramiento,
    'cuerpo_completo': BodySection.funcional,
    'espalda': BodySection.espalda,
    'espalda_baja': BodySection.espalda,
    'flexibilidad': BodySection.estiramiento,
    'gluteos': BodySection.gluteos,
    'hombros': BodySection.hombros,
    'pantorrillas': BodySection.piernas,
    'pecho': BodySection.pecho,
    'piernas': BodySection.piernas,
    'triceps': BodySection.triceps,
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def normalize(text):
    """Normalize text for comparison: lowercase, strip accents, remove special chars."""
    text = text.lower().strip()
    # Remove file extension
    text = os.path.splitext(text)[0]
    # Strip accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Replace hyphens/underscores/dots with spaces
    text = re.sub(r'[-_.\(\)]+', ' ', text)
    # Remove "descarga" and trailing numbers (common generic names)
    text = re.sub(r'\bdescarga\b', '', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def filename_to_name(filename):
    """Convert a filename to a human-readable exercise name."""
    name = os.path.splitext(filename)[0]
    # Replace hyphens/underscores with spaces
    name = re.sub(r'[-_]+', ' ', name)
    # Remove parenthetical numbers like (1), (2)
    name = re.sub(r'\s*\(\d+\)\s*', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    # Title case
    return name.title()

def run():
    base_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'exercises')
    if not os.path.isdir(base_dir):
        print("ERROR: static/images/exercises/ not found. Copy images first.")
        return

    db = SessionLocal()
    try:
        exercises = db.query(Ejercicio).all()
        # Build lookup: normalized name -> Ejercicio
        ex_lookup = {}
        for ex in exercises:
            ex_lookup[normalize(ex.name)] = ex

        matched = 0
        created = 0
        skipped = 0
        unmatched_files = []

        for dirname in sorted(os.listdir(base_dir)):
            dirpath = os.path.join(base_dir, dirname)
            if not os.path.isdir(dirpath):
                continue

            section = DIR_TO_SECTION.get(dirname)
            if not section:
                print(f"  WARN: Unknown directory '{dirname}', skipping")
                continue

            # Get exercises for this section
            section_exercises = [e for e in exercises if e.body_section == section]
            section_names = {normalize(e.name): e for e in section_exercises}

            files = sorted(f for f in os.listdir(dirpath)
                          if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS)

            for filename in files:
                image_url = f'/static/images/exercises/{dirname}/{filename}'
                norm_file = normalize(filename)

                # Skip if empty normalized name (generic files like "descarga (1).jpg")
                if not norm_file:
                    # Assign to an exercise in this section that has no image
                    unassigned = [e for e in section_exercises if not e.image_url]
                    if unassigned:
                        ex = unassigned[0]
                        ex.image_url = image_url
                        section_exercises = [e for e in section_exercises if e.id != ex.id or e.image_url]
                        matched += 1
                        print(f"  ASSIGNED (section fill): {filename} -> {ex.name}")
                    else:
                        # Create new exercise from filename
                        display_name = f"{dirname.replace('_', ' ').title()} - {filename_to_name(filename)}"
                        if not display_name or len(display_name) < 3:
                            display_name = f"{dirname.replace('_', ' ').title()} - Ejercicio {created + 1}"
                        # Check if name already exists
                        existing = db.query(Ejercicio).filter(Ejercicio.name == display_name).first()
                        if existing:
                            if not existing.image_url:
                                existing.image_url = image_url
                                matched += 1
                            else:
                                skipped += 1
                            continue
                        new_ej = Ejercicio(
                            name=display_name,
                            description=f'Ejercicio de {dirname.replace("_", " ")}',
                            image_url=image_url,
                            body_section=section,
                            exercise_type=ExerciseType.fuerza
                        )
                        db.add(new_ej)
                        created += 1
                        print(f"  CREATED: {display_name} <- {filename}")
                    continue

                # Try fuzzy match against all exercises (section first, then global)
                best_score = 0
                best_match = None

                # Check section exercises first
                for norm_name, ex in section_names.items():
                    score = SequenceMatcher(None, norm_file, norm_name).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = ex

                # Check global if section match is poor
                if best_score < 0.5:
                    for norm_name, ex in ex_lookup.items():
                        score = SequenceMatcher(None, norm_file, norm_name).ratio()
                        if score > best_score:
                            best_score = score
                            best_match = ex

                if best_match and best_score >= 0.45 and not best_match.image_url:
                    best_match.image_url = image_url
                    matched += 1
                    print(f"  MATCHED ({best_score:.0%}): {filename} -> {best_match.name}")
                elif best_match and best_score >= 0.45 and best_match.image_url:
                    # Exercise already has an image, create a new one
                    display_name = filename_to_name(filename)
                    existing = db.query(Ejercicio).filter(Ejercicio.name == display_name).first()
                    if existing:
                        if not existing.image_url:
                            existing.image_url = image_url
                            matched += 1
                        else:
                            skipped += 1
                        continue
                    new_ej = Ejercicio(
                        name=display_name,
                        description=f'Ejercicio de {dirname.replace("_", " ")}',
                        image_url=image_url,
                        body_section=section,
                        exercise_type=ExerciseType.fuerza
                    )
                    db.add(new_ej)
                    created += 1
                    print(f"  CREATED: {display_name} <- {filename}")
                else:
                    # No good match - create new exercise
                    display_name = filename_to_name(filename)
                    if not display_name or len(display_name) < 3:
                        display_name = f"{dirname.replace('_', ' ').title()} - Ejercicio"
                    # Ensure unique name
                    existing = db.query(Ejercicio).filter(Ejercicio.name == display_name).first()
                    if existing:
                        if not existing.image_url:
                            existing.image_url = image_url
                            matched += 1
                        else:
                            # Add section prefix to make unique
                            display_name = f"{dirname.replace('_', ' ').title()} - {display_name}"
                            existing2 = db.query(Ejercicio).filter(Ejercicio.name == display_name).first()
                            if existing2:
                                skipped += 1
                                continue
                            new_ej = Ejercicio(
                                name=display_name,
                                description=f'Ejercicio de {dirname.replace("_", " ")}',
                                image_url=image_url,
                                body_section=section,
                                exercise_type=ExerciseType.fuerza
                            )
                            db.add(new_ej)
                            created += 1
                            print(f"  CREATED: {display_name} <- {filename}")
                        continue
                    new_ej = Ejercicio(
                        name=display_name,
                        description=f'Ejercicio de {dirname.replace("_", " ")}',
                        image_url=image_url,
                        body_section=section,
                        exercise_type=ExerciseType.fuerza
                    )
                    db.add(new_ej)
                    created += 1
                    print(f"  CREATED: {display_name} <- {filename}")

        db.commit()

        print(f"\n{'='*50}")
        print(f"REPORT:")
        print(f"  Matched to existing exercises: {matched}")
        print(f"  New exercises created: {created}")
        print(f"  Skipped (duplicate): {skipped}")
        print(f"  Total images processed: {matched + created + skipped}")

        # Show exercises still without images
        no_image = db.query(Ejercicio).filter(Ejercicio.image_url == None).count()
        print(f"  Exercises still without image: {no_image}")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    run()
