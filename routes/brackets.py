from flask import jsonify, request, g
from apiflask import APIBlueprint
from models import Bracket, SessionLocal, Player, BracketPlayer

brackets_bp = APIBlueprint("brackets", __name__)

@brackets_bp.before_request
def create_session():
    g.db = SessionLocal()

@brackets_bp.teardown_request
def close_session(exception=None):
    g.db.close()

@brackets_bp.route("/brackets", methods=["GET"])
def get_brackets():
    brackets = g.db.query(Bracket).all()
    return jsonify([{
        "id": bracket.id,
        "tournament_id": bracket.tournament_id,
        "name": bracket.name
    } for bracket in brackets])

@brackets_bp.route("/brackets", methods=["POST"])
def create_bracket():
    data = request.get_json()
    tournament_id = data.get("tournament_id")
    name = data.get("name")

    if not tournament_id or not name:
        return jsonify({"error": "tournament_id and name are required"}), 400

    bracket = Bracket(tournament_id=tournament_id, name=name)

    try:
        g.db.add(bracket)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": bracket.id,
        "tournament_id": bracket.tournament_id,
        "name": bracket.name
    }), 201

@brackets_bp.route("/brackets/<int:bracket_id>/players", methods=["GET"])
def get_bracket_players(bracket_id):
    bracket = g.db.query(Bracket).filter(Bracket.id == bracket_id).first()

    if not bracket:
        return jsonify({"error": "Bracket not found"}), 404

    players = [
        {
            "id": bp.player.id,
            "name": bp.player.name,
            "gender": bp.player.gender,
            "phone_number": bp.player.phone_number
        }
        for bp in bracket.bracket_players
    ]

    return jsonify(players)

@brackets_bp.route("/tournaments/<int:tournament_id>/brackets", methods=["GET"])
def get_brackets_by_tournament(tournament_id):
    brackets = g.db.query(Bracket).filter(Bracket.tournament_id == tournament_id).all()
    return jsonify([
        {
            "id": bracket.id,
            "name": bracket.name
        }
        for bracket in brackets
    ])

@brackets_bp.route("/brackets/<int:bracket_id>/players", methods=["POST"])
def add_player_to_bracket(bracket_id):
    data = request.get_json()
    player_id = data.get("player_id")

    if not player_id:
        return jsonify({"error": "player_id is required"}), 400

    bracket = g.db.query(Bracket).filter(Bracket.id == bracket_id).first()

    if not bracket:
        return jsonify({"error": "Bracket not found"}), 404

    player = g.db.query(Player).filter(Player.id == player_id).first()

    if not player:
        return jsonify({"error": "Player not found"}), 404

    # Check if the player is already in the bracket
    existing_entry = g.db.query(BracketPlayer).filter(
        BracketPlayer.bracket_id == bracket_id,
        BracketPlayer.player_id == player_id
    ).first()

    if existing_entry:
        return jsonify({"error": "Player is already in the bracket"}), 400

    # Add the player to the bracket
    bracket_player = BracketPlayer(bracket_id=bracket_id, player_id=player_id)

    try:
        g.db.add(bracket_player)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Player added to bracket successfully"}), 201
