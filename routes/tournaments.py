from flask import jsonify, request, g
from apiflask import APIBlueprint
from models import Tournament, SessionLocal

tournaments_bp = APIBlueprint("tournaments", __name__)

@tournaments_bp.before_request
def create_session():
    g.db = SessionLocal()

@tournaments_bp.teardown_request
def close_session(exception=None):
    g.db.close()

@tournaments_bp.route("/tournaments", methods=["GET"])
def get_tournaments():
    tournaments = g.db.query(Tournament).filter(Tournament.status.in_(["PLANNING", "IN_PROGRESS"])).all()
    return jsonify([{
        "id": tournament.id,
        "name": tournament.name,
        "start_date": tournament.start_date,
        "end_date": tournament.end_date,
        "format": tournament.format,
        "status": tournament.status
    } for tournament in tournaments])

@tournaments_bp.route("/tournaments", methods=["POST"])
def create_tournament():
    data = request.get_json()
    new_tournament = Tournament(
        name=data["name"],
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        format=data["format"],
        status=data["status"]
    )
    g.db.add(new_tournament)
    g.db.commit()
    return jsonify({
        "id": new_tournament.id,
        "name": new_tournament.name,
        "start_date": new_tournament.start_date,
        "end_date": new_tournament.end_date,
        "format": new_tournament.format,
        "status": new_tournament.status
    }), 201

@tournaments_bp.route("/tournaments/<int:tournament_id>", methods=["PUT"])
def update_tournament(tournament_id):
    data = request.get_json()
    tournament = g.db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404

    tournament.name = data.get("name", tournament.name)
    tournament.start_date = data.get("start_date", tournament.start_date)
    tournament.end_date = data.get("end_date", tournament.end_date)
    tournament.format = data.get("format", tournament.format)
    tournament.status = data.get("status", tournament.status)

    g.db.commit()

    return jsonify({
        "id": tournament.id,
        "name": tournament.name,
        "start_date": tournament.start_date,
        "end_date": tournament.end_date,
        "format": tournament.format,
        "status": tournament.status
    })
