import os
import json

from dotenv import load_dotenv
from models import SessionLocal, Matchup, Bracket, Player, Tournament, TournamentPlayer, BracketPlayer

load_dotenv()

def export_table_to_file(table_name, rows):
    """Save rows of a table to a JSON file."""
    output_dir = "exported_data"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{table_name}.json")

    with open(file_path, "w") as f:
        json.dump(rows, f, indent=4)

    print(f"Exported {len(rows)} rows from {table_name} to {file_path}")

def export_all_tables():
    """Export all rows from the database tables to separate JSON files."""
    session = SessionLocal()

    try:
        # Export Bracket table
        brackets = session.query(Bracket).all()
        bracket_rows = [
            {
                "id": bracket.id,
                "tournament_id": bracket.tournament_id,
                "name": bracket.name
            }
            for bracket in brackets
        ]
        export_table_to_file("brackets", bracket_rows)

        # Export Player table
        players = session.query(Player).all()
        player_rows = [
            {
                "id": player.id,
                "name": player.name,
                "gender": player.gender,
                "phone_number": player.phone_number
            }
            for player in players
        ]
        export_table_to_file("players", player_rows)

        # Export Tournament table
        tournaments = session.query(Tournament).all()
        tournament_rows = [
            {
                "id": tournament.id,
                "name": tournament.name,
                "start_date": tournament.start_date,
                "end_date": tournament.end_date,
                "format": tournament.format,
                "status": tournament.status
            }
            for tournament in tournaments
        ]
        export_table_to_file("tournaments", tournament_rows)
        
        # Export Matchup table
        matchups = session.query(Matchup).all()
        matchup_rows = [
            {
                "id": matchup.id,
                "bracket_id": matchup.bracket_id,
                "player1_id": matchup.player1_id,
                "player2_id": matchup.player2_id,
                "player1_partner_id": matchup.player1_partner_id,
                "player2_partner_id": matchup.player2_partner_id,
                "winner_id": matchup.winner_id,
                "score": matchup.score,
                "status": matchup.status,
                "round": matchup.round
            }
            for matchup in matchups
        ]
        export_table_to_file("matchups", matchup_rows)

        # Export TournamentPlayer table
        tournament_players = session.query(TournamentPlayer).all()
        tournament_player_rows = [
            {
                "id": tp.id,
                "tournament_id": tp.tournament_id,
                "player_id": tp.player_id
            }
            for tp in tournament_players
        ]
        export_table_to_file("tournament_players", tournament_player_rows)

        # Export BracketPlayer table
        bracket_players = session.query(BracketPlayer).all()
        bracket_player_rows = [
            {
                "id": bp.id,
                "bracket_id": bp.bracket_id,
                "player_id": bp.player_id
            }
            for bp in bracket_players
        ]
        export_table_to_file("bracket_players", bracket_player_rows)

        print("All tables exported successfully.")
    except Exception as e:
        print(f"Error exporting tables: {e}")
    finally:
        session.close()

def import_data_from_files():
    """Import data from JSON files and insert them into the database."""
    session = SessionLocal()
    input_dir = "exported_data"

    try:
        # Import Bracket data
        bracket_file = os.path.join(input_dir, "brackets.json")
        if os.path.exists(bracket_file):
            with open(bracket_file, "r") as f:
                brackets = json.load(f)
                for bracket_data in brackets:
                    bracket = Bracket(**bracket_data)
                    session.add(bracket)

        # Import Player data
        player_file = os.path.join(input_dir, "players.json")
        if os.path.exists(player_file):
            with open(player_file, "r") as f:
                players = json.load(f)
                for player_data in players:
                    player = Player(**player_data)
                    session.add(player)

        # Import Tournament data
        tournament_file = os.path.join(input_dir, "tournaments.json")
        if os.path.exists(tournament_file):
            with open(tournament_file, "r") as f:
                tournaments = json.load(f)
                for tournament_data in tournaments:
                    tournament = Tournament(**tournament_data)
                    session.add(tournament)

        # Import Matchup data
        matchup_file = os.path.join(input_dir, "matchups.json")
        if os.path.exists(matchup_file):
            with open(matchup_file, "r") as f:
                matchups = json.load(f)
                for matchup_data in matchups:
                    matchup = Matchup(**matchup_data)
                    session.add(matchup)

        # Import TournamentPlayer data
        tournament_player_file = os.path.join(input_dir, "tournament_players.json")
        if os.path.exists(tournament_player_file):
            with open(tournament_player_file, "r") as f:
                tournament_players = json.load(f)
                for tp_data in tournament_players:
                    tournament_player = TournamentPlayer(**tp_data)
                    session.add(tournament_player)

        # Import BracketPlayer data
        bracket_player_file = os.path.join(input_dir, "bracket_players.json")
        if os.path.exists(bracket_player_file):
            with open(bracket_player_file, "r") as f:
                bracket_players = json.load(f)
                for bp_data in bracket_players:
                    bracket_player = BracketPlayer(**bp_data)
                    session.add(bracket_player)

        session.commit()
        print("All data imported successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error importing data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if os.getenv("DATA_PHASE") == "EXPORT":
        export_all_tables()
    elif os.getenv("DATA_PHASE") == "IMPORT":
        import_data_from_files()