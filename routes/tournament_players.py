from flask import jsonify, request, g
from apiflask import APIBlueprint
from models import TournamentPlayer, SessionLocal

tournament_players_bp = APIBlueprint("tournament_players", __name__)

@tournament_players_bp.before_request
def create_session():
    g.db = SessionLocal()

@tournament_players_bp.teardown_request
def close_session(exception=None):
    g.db.close()

@tournament_players_bp.route("/tournament-players", methods=["GET"])
def get_tournament_players():
    tournament_players = g.db.query(TournamentPlayer).all()
    return jsonify([{
        "id": tp.id,
        "tournament_id": tp.tournament_id,
        "player_id": tp.player_id
    } for tp in tournament_players])

@tournament_players_bp.route("/tournament_players", methods=["POST"])
def add_players_to_tournament():
    data = request.get_json()
    tournament_id = data.get("tournament_id")
    player_ids = data.get("player_ids")

    if not tournament_id or not player_ids:
        return jsonify({"error": "tournament_id and player_ids are required"}), 400

    tournament_players = [
        TournamentPlayer(tournament_id=tournament_id, player_id=player_id)
        for player_id in player_ids
    ]

    try:
        g.db.bulk_save_objects(tournament_players)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify([
        {
            "id": tp.id,
            "tournament_id": tp.tournament_id,
            "player_id": tp.player_id
        }
        for tp in tournament_players
    ]), 201

@tournament_players_bp.route("/tournaments/<int:tournament_id>/players", methods=["GET"])
def get_players_by_tournament(tournament_id):
    tournament_players = g.db.query(TournamentPlayer).filter(TournamentPlayer.tournament_id == tournament_id).all()

    if not tournament_players:
        return jsonify({"error": "No players found for the given tournament"}), 404

    players = [
        {
            "id": tp.player.id,
            "name": tp.player.name,
            "gender": tp.player.gender,
            "phone_number": tp.player.phone_number
        }
        for tp in tournament_players
    ]

    return jsonify(players)

@tournament_players_bp.route("/tournaments/<int:tournament_id>/players/<int:player_id>", methods=["DELETE"])
def remove_player_from_tournament(tournament_id, player_id):
    tournament_player = g.db.query(TournamentPlayer).filter(
        TournamentPlayer.tournament_id == tournament_id,
        TournamentPlayer.player_id == player_id
    ).first()

    if not tournament_player:
        return jsonify({"error": "Player not found in the tournament"}), 404

    try:
        g.db.delete(tournament_player)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Player removed from the tournament successfully"})
