from typing import Optional
from flask import jsonify, request, g
from apiflask import APIBlueprint
from pydantic import BaseModel, Field
from models import Matchup, SessionLocal, Bracket

matchups_bp = APIBlueprint("matchups", __name__)

@matchups_bp.before_request
def create_session():
    g.db = SessionLocal()

@matchups_bp.teardown_request
def close_session(exception=None):
    g.db.close()

@matchups_bp.route("/matchups", methods=["GET"])
def get_matchups():
    matchups = g.db.query(Matchup).all()
    return jsonify([{
        "id": matchup.id,
        "status": matchup.status,
        "score": matchup.score
    } for matchup in matchups])

class MatchupSearchQuery(BaseModel):
    PENDING: Optional[bool] = Field(default=False, description="Filter for pending matchups")
    PLANNING: Optional[bool] = Field(default=True, description="Filter for planning matchups")
    COMPLETED: Optional[bool] = Field(default=True, description="Filter for completed matchups")
    ALL: Optional[bool] = Field(default=False, description="Return all matchups")


@matchups_bp.route("/brackets/<int:bracket_id>/matchups", methods=["GET"])
@matchups_bp.input(MatchupSearchQuery, location="query")
def get_matchups_by_bracket(bracket_id, query_data):
    show_pending = query_data.PENDING
    show_planning = query_data.PLANNING
    show_completed = query_data.COMPLETED
    show_all = query_data.ALL

    query = g.db.query(Matchup).filter(Matchup.bracket_id == bracket_id)

    if not show_all:
        status_filters = []

        if show_pending:
            status_filters.append("PENDING")
        if show_planning:
            status_filters.append("PLANNING")
        if show_completed:
            status_filters.append("COMPLETED")

        smallest_round = g.db.query(Matchup.round).filter(Matchup.bracket_id == bracket_id).filter(Matchup.status == "PLANNING").order_by(Matchup.round.asc()).first()
        print(smallest_round)
        
        if smallest_round:
            query = query.filter(Matchup.round == smallest_round[0])

        if status_filters:
            query = query.filter(Matchup.status.in_(status_filters))

    matchups = query.all()

    if not matchups:
        return jsonify({"error": "No matchups found for the given bracket"}), 404

    return jsonify([
        {
            "id": matchup.id,
            "bracket_id": matchup.bracket_id,
            "player1": {
                "id": matchup.player1.id,
                "name": matchup.player1.name,
                "gender": matchup.player1.gender,
                "phone_number": matchup.player1.phone_number
            } if matchup.player1 else None,
            "player2": {
                "id": matchup.player2.id,
                "name": matchup.player2.name,
                "gender": matchup.player2.gender,
                "phone_number": matchup.player2.phone_number
            } if matchup.player2 else None,
            "player1_partner": {
                "id": matchup.player1_partner.id,
                "name": matchup.player1_partner.name,
                "gender": matchup.player1_partner.gender,
                "phone_number": matchup.player1_partner.phone_number
            } if matchup.player1_partner else None,
            "player2_partner": {
                "id": matchup.player2_partner.id,
                "name": matchup.player2_partner.name,
                "gender": matchup.player2_partner.gender,
                "phone_number": matchup.player2_partner.phone_number
            } if matchup.player2_partner else None,
            "winner": {
                "id": matchup.winner.id,
                "name": matchup.winner.name,
                "gender": matchup.winner.gender,
                "phone_number": matchup.winner.phone_number
            } if matchup.winner else None,
            "score": matchup.score,
            "status": matchup.status,
            "round": matchup.round
        }
        for matchup in matchups
    ])

@matchups_bp.route("/matchups", methods=["POST"])
def create_matchup():
    data = request.get_json()
    bracket_id = data.get("bracket_id")
    player1_id = data.get("player1_id")
    player2_id = data.get("player2_id")
    player1_partner_id = data.get("player1_partner_id")
    player2_partner_id = data.get("player2_partner_id")
    winner_id = data.get("winner_id")
    score = data.get("score")
    status = data.get("status")

    if not bracket_id or not player1_id or not player2_id or not status:
        return jsonify({"error": "bracket_id, player1_id, player2_id, and status are required"}), 400

    matchup = Matchup(
        bracket_id=bracket_id,
        player1_id=player1_id,
        player2_id=player2_id,
        player1_partner_id=player1_partner_id,
        player2_partner_id=player2_partner_id,
        winner_id=winner_id,
        score=score,
        status=status
    )

    try:
        g.db.add(matchup)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": matchup.id,
        "bracket_id": matchup.bracket_id,
        "player1_id": matchup.player1_id,
        "player2_id": matchup.player2_id,
        "player1_partner_id": matchup.player1_partner_id,
        "player2_partner_id": matchup.player2_partner_id,
        "winner_id": matchup.winner_id,
        "score": matchup.score,
        "status": matchup.status
    }), 201

@matchups_bp.route("/matchups/generate", methods=["POST"])
def generate_matchups():
    data = request.get_json()
    bracket_id = data.get("bracket_id")
    format = data.get("format")

    if not bracket_id or not format:
        return jsonify({"error": "bracket_id and format are required"}), 400

    # Fetch players in the bracket
    bracket = g.db.query(Bracket).filter(Bracket.id == bracket_id).first()

    if not bracket:
        return jsonify({"error": "Bracket not found"}), 404

    players = [bp.player for bp in bracket.bracket_players]

    if not players:
        return jsonify({"error": "No players found in the bracket"}), 404

    # Delete existing matchups for the bracket
    try:
        g.db.query(Matchup).filter(Matchup.bracket_id == bracket_id).delete()
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": f"Failed to delete existing matchups: {e}"}), 500

    matchups = []

    if format == "ROUND_ROBIN":
        num_players = len(players)
        if num_players % 2 != 0:
            players.append(None)  # Add a dummy player for odd number of players

        num_rounds = len(players) - 1
        for round_num in range(num_rounds):
            round_matches = []
            for i in range(len(players) // 2):
                player1 = players[i]
                player2 = players[-(i + 1)]

                if player1 and player2:  # Skip matches with the dummy player
                    round_matches.append(
                        Matchup(
                            bracket_id=bracket_id,
                            player1_id=player1.id,
                            player2_id=player2.id,
                            round=round_num + 1,
                            status="PENDING"
                        )
                    )

            # Rotate players for the next round
            players = [players[0], players[-1], *players[1:-1]]
            matchups.extend(round_matches)
    elif format == "SWISS":
        # Placeholder for SWISS format logic
        return jsonify({"error": "SWISS format not implemented yet"}), 501
    else:
        return jsonify({"error": "Invalid format"}), 400

    try:
        g.db.bulk_save_objects(matchups)
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify([
        {
            "id": matchup.id,
            "bracket_id": matchup.bracket_id,
            "player1_id": matchup.player1_id,
            "player2_id": matchup.player2_id,
            "status": matchup.status
        }
        for matchup in matchups
    ]), 201

@matchups_bp.route("/matchups/<int:matchup_id>", methods=["PUT"])
def update_matchup(matchup_id):
    data = request.get_json()

    matchup = g.db.query(Matchup).filter(Matchup.id == matchup_id).first()

    if not matchup:
        return jsonify({"error": "Matchup not found"}), 404

    # Update fields if provided in the request
    matchup.player1_id = data.get("player1_id", matchup.player1_id)
    matchup.player2_id = data.get("player2_id", matchup.player2_id)
    matchup.player1_partner_id = data.get("player1_partner_id", matchup.player1_partner_id)
    matchup.player2_partner_id = data.get("player2_partner_id", matchup.player2_partner_id)
    matchup.winner_id = data.get("winner_id", matchup.winner_id)
    matchup.score = data.get("score", matchup.score)
    matchup.status = data.get("status", matchup.status)

    try:
        g.db.commit()

        # Check if there are no other matchups in the same round in the PLANNING phase
        same_round_planning = g.db.query(Matchup).filter(
            Matchup.bracket_id == matchup.bracket_id,
            Matchup.round == matchup.round,
            Matchup.status == "PLANNING"
        ).count()

        if same_round_planning == 0:
            # Update all matchups in the next round from PENDING to PLANNING
            next_round_matchups = g.db.query(Matchup).filter(
                Matchup.bracket_id == matchup.bracket_id,
                Matchup.round == matchup.round + 1,
                Matchup.status == "PENDING"
            ).all()

            for next_matchup in next_round_matchups:
                next_matchup.status = "PLANNING"

            g.db.commit()

    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": matchup.id,
        "bracket_id": matchup.bracket_id,
        "player1_id": matchup.player1_id,
        "player2_id": matchup.player2_id,
        "player1_partner_id": matchup.player1_partner_id,
        "player2_partner_id": matchup.player2_partner_id,
        "winner_id": matchup.winner_id,
        "score": matchup.score,
        "status": matchup.status
    }), 200
