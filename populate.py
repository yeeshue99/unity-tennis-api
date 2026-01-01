from models import Player, SessionLocal

def populate_players():
    session = SessionLocal()
    names = [
        "Danielle Neal",
        "Kane Vincent",
        "Allyson Watkins",
        "Nash Franco",
        "Charleigh Ferguson",
        "Miguel Franco",
        "Charleigh Reid",
        "Josue Chung",
        "Rivka Wiley",
        "Mathew Cisneros",
        "Janelle Hardin",
        "Hassan Russell",
        "Raelynn Hodges",
        "Alonzo Hester",
        "Zendaya Shaffer",
        "Dexter Correa",
        "Valery Holloway",
        "Sutton Dejesus",
        "Julissa Waller",
        "Marley Armstrong",
        "Presley Clark",
        "John Dunn",
        "Olive Hancock",
        "Rex Tanner",
        "Harmoni Mahoney",
        "Kamryn Mejia",
        "Saylor Gill",
        "Matthias Cain"
    ]
    try:
        players = [
            Player(name=name, gender="Male" if i % 2 == 0 else "Female", phone_number=f"555-00{i+1:02}")
            for i, name in enumerate(names)
        ]
        session.bulk_save_objects(players)
        session.commit()
        print("28 players added successfully.")
    except Exception as e:
        session.rollback()
        print(f"Failed to add players: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_players()
