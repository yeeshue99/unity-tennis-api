from flask import request, jsonify
from apiflask import APIBlueprint
from models import BracketPlayer

bracket_players_bp = APIBlueprint("bracket_players", __name__)

@bracket_players_bp.route("/bracket_players", methods=["POST"])
def add_bracket_player():
    data = request.get_json()
    bracket_id = data.get("bracket_id")
    player_id = data.get("player_id")

    if not bracket_id or not player_id:
        return jsonify({"error": "bracket_id and player_id are required"}), 400

    bracket_player = BracketPlayer(bracket_id=bracket_id, player_id=player_id)

    try:
        request.db.add(bracket_player) # pyright: ignore[reportAttributeAccessIssue]
        request.db.commit() # pyright: ignore[reportAttributeAccessIssue]
    except Exception as e:
        request.db.rollback() # pyright: ignore[reportAttributeAccessIssue]
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": bracket_player.id,
        "bracket_id": bracket_player.bracket_id,
        "player_id": bracket_player.player_id
    }), 201

@bracket_players_bp.route("/bracket_players/<int:bracket_player_id>", methods=["DELETE"])
def delete_bracket_player(bracket_player_id):
    bracket_player = request.db.query(BracketPlayer).filter(BracketPlayer.id == bracket_player_id).first() # pyright: ignore[reportAttributeAccessIssue]

    if not bracket_player:
        return jsonify({"error": "BracketPlayer not found"}), 404

    try:
        request.db.delete(bracket_player) # pyright: ignore[reportAttributeAccessIssue]
        request.db.commit() # pyright: ignore[reportAttributeAccessIssue]
    except Exception as e:
        request.db.rollback() # pyright: ignore[reportAttributeAccessIssue]
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Removed player from bracket successfully"})
