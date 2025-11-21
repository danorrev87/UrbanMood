"""
Seed script to populate exercise catalog with common gym exercises.
Run with: python seed_ejercicios.py
"""
from db import SessionLocal
from models import Ejercicio, BodySection, ExerciseType

def seed_ejercicios():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Ejercicio).count() > 0:
            print("⚠️  Exercises already seeded. Skipping.")
            return
        
        ejercicios = [
            # PECHO
            {
                'name': 'Press de Banca',
                'description': 'Acostado en banco plano, baja la barra hasta el pecho y empuja hacia arriba.',
                'body_section': BodySection.pecho,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Press Inclinado con Mancuernas',
                'description': 'En banco inclinado 30-45°, empuja las mancuernas hacia arriba.',
                'body_section': BodySection.pecho,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Aperturas con Mancuernas',
                'description': 'En banco plano, abre los brazos en arco con mancuernas.',
                'body_section': BodySection.pecho,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Flexiones / Push-ups',
                'description': 'Con peso corporal, baja el pecho al suelo y empuja hacia arriba.',
                'body_section': BodySection.pecho,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # ESPALDA
            {
                'name': 'Dominadas / Pull-ups',
                'description': 'Colgado de barra, tracciona hasta que el pecho toque la barra.',
                'body_section': BodySection.espalda,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Remo con Barra',
                'description': 'Inclinado hacia adelante, tracciona la barra hacia el abdomen.',
                'body_section': BodySection.espalda,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Remo con Mancuerna',
                'description': 'Apoyado en banco, tracciona la mancuerna hacia la cadera.',
                'body_section': BodySection.espalda,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Peso Muerto',
                'description': 'Con barra en el suelo, levanta manteniendo la espalda recta.',
                'body_section': BodySection.espalda,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # HOMBROS
            {
                'name': 'Press Militar',
                'description': 'De pie o sentado, empuja la barra desde los hombros hacia arriba.',
                'body_section': BodySection.hombros,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Elevaciones Laterales',
                'description': 'Con mancuernas, eleva los brazos hacia los lados hasta la altura del hombro.',
                'body_section': BodySection.hombros,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Elevaciones Frontales',
                'description': 'Con mancuernas, eleva los brazos al frente hasta la altura del hombro.',
                'body_section': BodySection.hombros,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Face Pulls',
                'description': 'Con polea alta, tracciona hacia la cara separando las manos.',
                'body_section': BodySection.hombros,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # BRAZOS
            {
                'name': 'Curl de Bíceps con Barra',
                'description': 'De pie, flexiona los codos llevando la barra hacia los hombros.',
                'body_section': BodySection.brazos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Curl con Mancuernas',
                'description': 'Sentado o de pie, flexiona los codos alternando brazos.',
                'body_section': BodySection.brazos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Press Francés',
                'description': 'Acostado, baja la barra hacia la frente flexionando solo los codos.',
                'body_section': BodySection.brazos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Fondos en Paralelas',
                'description': 'En paralelas, baja el cuerpo flexionando los codos y empuja hacia arriba.',
                'body_section': BodySection.brazos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # PIERNAS
            {
                'name': 'Sentadilla con Barra',
                'description': 'Con barra en la espalda, baja hasta que muslos queden paralelos al suelo.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Zancadas / Lunges',
                'description': 'Da un paso largo hacia adelante y baja la rodilla trasera.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Prensa de Piernas',
                'description': 'En máquina, empuja la plataforma con los pies.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Curl Femoral',
                'description': 'En máquina, flexiona las rodillas llevando talones hacia glúteos.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Extensión de Cuádriceps',
                'description': 'En máquina, extiende las piernas completamente.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Elevaciones de Pantorrilla',
                'description': 'De pie, eleva los talones lo más alto posible.',
                'body_section': BodySection.piernas,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # ABDOMEN
            {
                'name': 'Plank / Plancha',
                'description': 'En posición de flexión sobre antebrazos, mantén el cuerpo recto.',
                'body_section': BodySection.abdomen,
                'exercise_type': ExerciseType.core,
                'image_url': None
            },
            {
                'name': 'Crunches',
                'description': 'Acostado, flexiona el tronco llevando los hombros hacia las rodillas.',
                'body_section': BodySection.abdomen,
                'exercise_type': ExerciseType.core,
                'image_url': None
            },
            {
                'name': 'Elevación de Piernas',
                'description': 'Acostado, eleva las piernas rectas hacia arriba.',
                'body_section': BodySection.abdomen,
                'exercise_type': ExerciseType.core,
                'image_url': None
            },
            {
                'name': 'Russian Twists',
                'description': 'Sentado con piernas elevadas, rota el torso de lado a lado.',
                'body_section': BodySection.abdomen,
                'exercise_type': ExerciseType.core,
                'image_url': None
            },
            
            # GLÚTEOS
            {
                'name': 'Hip Thrust',
                'description': 'Espalda apoyada en banco, empuja la cadera hacia arriba con peso en pelvis.',
                'body_section': BodySection.gluteos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            {
                'name': 'Patada de Glúteo en Polea',
                'description': 'Con correa en tobillo, empuja la pierna hacia atrás.',
                'body_section': BodySection.gluteos,
                'exercise_type': ExerciseType.fuerza,
                'image_url': None
            },
            
            # CARDIO
            {
                'name': 'Burpees',
                'description': 'Flexión, salto hacia atrás, flexión, salto hacia adelante y salto vertical.',
                'body_section': BodySection.cardio,
                'exercise_type': ExerciseType.hiit,
                'image_url': None
            },
            {
                'name': 'Mountain Climbers',
                'description': 'En posición de flexión, lleva rodillas alternadas hacia el pecho rápidamente.',
                'body_section': BodySection.cardio,
                'exercise_type': ExerciseType.hiit,
                'image_url': None
            },
            {
                'name': 'Jumping Jacks',
                'description': 'Salta abriendo piernas y brazos simultáneamente.',
                'body_section': BodySection.cardio,
                'exercise_type': ExerciseType.cardio,
                'image_url': None
            },
            {
                'name': 'Cinta de Correr',
                'description': 'Corre o camina en cinta a velocidad controlada.',
                'body_section': BodySection.cardio,
                'exercise_type': ExerciseType.cardio,
                'image_url': None
            },
            {
                'name': 'Bicicleta Estática',
                'description': 'Pedalea manteniendo ritmo constante o por intervalos.',
                'body_section': BodySection.cardio,
                'exercise_type': ExerciseType.cardio,
                'image_url': None
            },
            
            # FUNCIONAL
            {
                'name': 'Kettlebell Swing',
                'description': 'Con kettlebell, balancea entre las piernas y empuja con cadera hasta altura del pecho.',
                'body_section': BodySection.funcional,
                'exercise_type': ExerciseType.funcional,
                'image_url': None
            },
            {
                'name': 'Box Jumps',
                'description': 'Salta sobre caja o plataforma elevada.',
                'body_section': BodySection.funcional,
                'exercise_type': ExerciseType.funcional,
                'image_url': None
            },
            {
                'name': 'Battle Ropes',
                'description': 'Con cuerdas gruesas, genera ondas moviendo los brazos alternadamente.',
                'body_section': BodySection.funcional,
                'exercise_type': ExerciseType.funcional,
                'image_url': None
            },
        ]
        
        for ej_data in ejercicios:
            ejercicio = Ejercicio(**ej_data)
            db.add(ejercicio)
        
        db.commit()
        print(f"✅ Successfully seeded {len(ejercicios)} exercises!")
        
        # Print summary by body section
        for section in BodySection:
            count = db.query(Ejercicio).filter(Ejercicio.body_section == section).count()
            if count > 0:
                print(f"   • {section.value.title()}: {count} exercises")
        
    except Exception as e:
        print(f"❌ Error seeding exercises: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    seed_ejercicios()
