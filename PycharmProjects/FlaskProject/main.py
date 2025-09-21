# main.py
# SMS Analyst – Flask backend (SQLite + SQLAlchemy + JWT)
# Features:
# - SMS commands: START/STOP/HELP/LANG/IN/OUT/GOAL/SAVE/BAL/REPORT(WEEK|MONTH)/OPPORTUNITY/YES <id> [amount]
# - Multi-language replies (Kirundi default; FR/EN)
# - Idempotency per minute for mutating commands
# - Investment opportunities + opt-ins
# - JWT login (admin/user), bcrypt password hashing, CORS for Flutter
# - Admin APIs: /admin/stats, /admin/users
# - DB self-healing: adds missing columns/tables on startup
# - CLI: flask --app main.py initdb  |  flask --app main.py create-admin

import os, re, hashlib, sqlite3
import datetime as dt
from collections import defaultdict

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt
)
from datetime import timedelta
from passlib.hash import bcrypt

# ------------------ App / DB Config ------------------
app = Flask(__name__)
DB_URI = os.environ.get("SMS_DB", "sqlite:///sms_analyst.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "dev-secret-change-me")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
jwt = JWTManager(app)
db = SQLAlchemy(app)

# ------------------ Models ------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True, nullable=False, index=True)
    lang = db.Column(db.String, default="rw")  # 'rw','fr','en'
    opted_out = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String)        # for admin/console login
    role = db.Column(db.String, default="user") # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name = db.Column(db.String, nullable=False)
    target = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="active")  # active, archived
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_goal_user_name"),)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type = db.Column(db.String, nullable=False)  # IN, OUT, SAVE
    amount = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"))
    note = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Opportunity(db.Model):
    __tablename__ = "opportunities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    min_amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String)           # coop, agri, retail
    expected_return = db.Column(db.String)    # "5%/month"
    risk_level = db.Column(db.String)         # low, med, high
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

class UserInvestment(db.Model):
    __tablename__ = "user_investments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="interested")  # interested, committed, declined
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Idempotency(db.Model):
    __tablename__ = "idempotency"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    fingerprint = db.Column(db.String, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    kind = db.Column(db.String)         # 'cmd','report','opp_view','opt_in','opt_out'
    payload = db.Column(db.String)
    ts = db.Column(db.DateTime, default=dt.datetime.utcnow)

# ------------------ DB Schema Self-Healing ------------------
def ensure_db_schema():
    """Self-heal missing columns/tables using SQLAlchemy connection."""
    with app.app_context():
        # Create any missing tables first
        db.create_all()

        with db.engine.begin() as conn:

            def has_column(table: str, col: str) -> bool:
                rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
                # row: (cid, name, type, notnull, dflt_value, pk)
                return any(r[1] == col for r in rows)

            # Users: opted_out/lang/password_hash/role
            if not has_column("users", "opted_out"):
                print("[DB] Adding users.opted_out …")
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN opted_out BOOLEAN DEFAULT 0")

            if not has_column("users", "lang"):
                print("[DB] Adding users.lang …")
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'rw'")

            if not has_column("users", "password_hash"):
                print("[DB] Adding users.password_hash …")
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN password_hash TEXT")

            if not has_column("users", "role"):
                print("[DB] Adding users.role …")
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

            # Helper tables
            conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS idempotency (
              id INTEGER PRIMARY KEY,
              user_id INTEGER,
              fingerprint TEXT UNIQUE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_idem_fingerprint ON idempotency(fingerprint)")

            conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY,
              user_id INTEGER,
              kind TEXT,
              payload TEXT,
              ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        # Print actual SQLite path for sanity
        try:
            url = db.engine.url
            if url.database:
                print(f"[DB] Using SQLite file: {os.path.abspath(url.database)}")
        except Exception:
            pass

# ------------------ Utils ------------------
AMOUNT_RE = re.compile(r"(\d[\d,\.]*)")

def parse_amount(s: str):
    m = AMOUNT_RE.search(s)
    if not m: return None
    raw = m.group(1).replace(",", "").replace(".", "")
    try:
        val = int(raw)
        return val if val > 0 else None
    except:
        return None

def parse_amounts_all(s: str):
    return [int(x.replace(",", "").replace(".", "")) for x in re.findall(r"\d[\d,\.]*", s)]

def normalize_tag(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "", s.upper())[:24] if s else ""

def get_or_create_user(phone: str) -> "User":
    u = User.query.filter_by(phone=phone).one_or_none()
    if u: return u
    u = User(phone=phone)
    db.session.add(u); db.session.commit()
    return u

def idempotent_fingerprint(phone: str, message: str) -> str:
    minute = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")  # minute bucket
    return hashlib.sha256(f"{phone}|{message.strip()}|{minute}".encode()).hexdigest()

def aggregates(user_id: int, start=None, end=None):
    q = Transaction.query.filter_by(user_id=user_id)
    if start: q = q.filter(Transaction.created_at >= start)
    if end:   q = q.filter(Transaction.created_at < end)
    total_in = total_out = total_save = 0
    per_tag = defaultdict(int)
    for t in q:
        if t.type == "IN":
            total_in += t.amount
        elif t.type == "OUT":
            total_out += t.amount
            if t.tag:
                per_tag[t.tag] += t.amount
        elif t.type == "SAVE":
            total_save += t.amount
    return total_in, total_out, total_save, dict(per_tag)

def surplus_cashflow(total_in, total_out, total_save) -> int:
    return total_in - total_out - total_save

def format_money(n: int) -> str:
    return f"{n:,}".replace(",", " ")

# Password helpers
def set_password(u: User, raw: str):
    u.password_hash = bcrypt.hash(raw)

def check_password(u: User, raw: str) -> bool:
    if not u.password_hash: return False
    return bcrypt.verify(raw, u.password_hash)

# ------------------ Language Templates ------------------
T = {
    "rw": {
        "welcome": "Murakaza neza kuri SMS Analyst. Koresha: IN/OUT/SAVE/GOAL. Urug: OUT 2000 FOOD. Ureke ubutumwa: STOP. IFASHA: andika HELP.",
        "help": "Amabwiriza: IN <amafaranga> [tag], OUT <amafaranga> [tag], GOAL <izina> <target>, SAVE <amafaranga> <izina>, BAL, REPORT WEEK|MONTH, OPPORTUNITY, YES <id> [amount], LANG RW|FR|EN.",
        "lang_set": "Ururimi: Kirundi.",
        "lang_set_fr": "Langue: Français.",
        "lang_set_en": "Language: English.",
        "stopped": "Wahagaritse ubutumwa. Andika START gusubira.",
        "confirm_in": "Twakiriye IN {amt} FBU ({tag}).",
        "confirm_out": "Twakiriye OUT {amt} FBU ({tag}).",
        "goal_set": "Intego ishyizwe: {name} = {target} FBU.",
        "save_ok": "Ubikusanyije: {amt} FBU kuri {name}. {saved}/{target} FBU ({pct}%).",
        "bal": "IN {total_in} | OUT {total_out} | SAVE {total_save} | SURPLUS {surplus} FBU.",
        "report": "Raporo: IN {total_in}, OUT {total_out}, SAVE {total_save}, SURPLUS {surplus}. Top: {top}. {insight}",
        "opp_header": "Amahirwe:",
        "opp_item": "{i}) {name}, min {min} FBU, {ret} ({risk})",
        "yes_ok": "Twakiriye ku {name} {amt} FBU ({risk}). Ibi ni ibitekerezo, si inama y’ishoramari.",
        "not_found": "Ntibyumvikanye. Gerageza: OUT 2000 FOOD cyangwa HELP.",
        "no_goal": "Intego {name} ntiboneka.",
        "amb_goal": "Hari amahitamo menshi asatira '{name}'. Ongera usobanure.",
        "dup": "Ubutumwa bwari bwakiriwe.",
        "opted_out_block": "Wahagaritse ubutumwa. Andika START gusubira.",
    },
    "fr": {
        "welcome": "Bienvenue sur SMS Analyst. Utilisez: IN/OUT/SAVE/GOAL. Ex: OUT 2000 FOOD. STOP pour se désinscrire. AIDE: envoyez HELP.",
        "help": "Commandes: IN <montant> [tag], OUT <montant> [tag], GOAL <nom> <cible>, SAVE <montant> <nom>, BAL, REPORT WEEK|MONTH, OPPORTUNITY, YES <id> [montant], LANG RW|FR|EN.",
        "lang_set": "Langue: Français.",
        "stopped": "Vous avez arrêté les messages. Envoyez START pour reprendre.",
        "confirm_in": "Reçu IN {amt} FBU ({tag}).",
        "confirm_out": "Reçu OUT {amt} FBU ({tag}).",
        "goal_set": "Objectif défini: {name} = {target} FBU.",
        "save_ok": "Épargne: {amt} FBU vers {name}. {saved}/{target} FBU ({pct}%).",
        "bal": "IN {total_in} | OUT {total_out} | SAVE {total_save} | SURPLUS {surplus} FBU.",
        "report": "Rapport: IN {total_in}, OUT {total_out}, SAVE {total_save}, SURPLUS {surplus}. Top: {top}. {insight}",
        "opp_header": "Opportunités:",
        "opp_item": "{i}) {name}, min {min} FBU, {ret} ({risk})",
        "yes_ok": "Inscription à {name} {amt} FBU ({risk}). Idées, pas de conseil financier.",
        "not_found": "Commande non reconnue. Essayez: OUT 2000 FOOD ou HELP.",
        "no_goal": "Objectif {name} introuvable.",
        "amb_goal": "Plusieurs objectifs proches de '{name}'. Précisez.",
        "dup": "Message déjà reçu.",
        "opted_out_block": "Vous êtes désinscrit. Envoyez START pour reprendre.",
    },
    "en": {
        "welcome": "Welcome to SMS Analyst. Use: IN/OUT/SAVE/GOAL. Eg: OUT 2000 FOOD. STOP to opt out. HELP for help.",
        "help": "Commands: IN <amount> [tag], OUT <amount> [tag], GOAL <name> <target>, SAVE <amount> <name>, BAL, REPORT WEEK|MONTH, OPPORTUNITY, YES <id> [amount], LANG RW|FR|EN.",
        "lang_set": "Language: English.",
        "stopped": "You have opted out. Send START to resume.",
        "confirm_in": "Received IN {amt} FBU ({tag}).",
        "confirm_out": "Received OUT {amt} FBU ({tag}).",
        "goal_set": "Goal set: {name} = {target} FBU.",
        "save_ok": "Saved {amt} FBU to {name}. {saved}/{target} FBU ({pct}%).",
        "bal": "IN {total_in} | OUT {total_out} | SAVE {total_save} | SURPLUS {surplus} FBU.",
        "report": "Report: IN {total_in}, OUT {total_out}, SAVE {total_save}, SURPLUS {surplus}. Top: {top}. {insight}",
        "opp_header": "Opportunities:",
        "opp_item": "{i}) {name}, min {min} FBU, {ret} ({risk})",
        "yes_ok": "Recorded {amt} FBU for {name} ({risk}). Ideas only, not financial advice.",
        "not_found": "Not understood. Try: OUT 2000 FOOD or HELP.",
        "no_goal": "Goal {name} not found.",
        "amb_goal": "Multiple goals similar to '{name}'. Please clarify.",
        "dup": "Message already received.",
        "opted_out_block": "You are opted out. Send START to resume.",
    },
}

def tr(user: User, key: str, **kw) -> str:
    pack = T.get(user.lang or "rw", T["rw"])
    s = pack.get(key) or T["rw"].get(key, "")
    return s.format(**kw) if kw else s

# ------------------ SMS Handlers ------------------
def handle_start(user: User):
    user.opted_out = False
    db.session.commit()
    return tr(user, "welcome")

def handle_stop(user: User):
    user.opted_out = True
    db.session.commit()
    db.session.add(Event(user_id=user.id, kind="opt_out", payload="STOP")); db.session.commit()
    return tr(user, "stopped")

def handle_help(user: User):
    return tr(user, "help")

def handle_lang(user: User, msg: str):
    code = msg.split()[-1].lower()
    user.lang = {"rw": "rw", "fr": "fr", "en": "en"}.get(code, user.lang)
    db.session.commit()
    if user.lang == "rw": return T["rw"]["lang_set"]
    if user.lang == "fr": return T["rw"]["lang_set_fr"]
    return T["rw"]["lang_set_en"]

def handle_in(user: User, msg: str):
    amt = parse_amount(msg)
    if not amt: return tr(user, "not_found")
    parts = msg.strip().split()
    tag = normalize_tag(parts[-1]) if len(parts) >= 2 else ""
    db.session.add(Transaction(user_id=user.id, type="IN", amount=amt, tag=tag))
    db.session.add(Event(user_id=user.id, kind="cmd", payload="IN"))
    db.session.commit()
    return tr(user, "confirm_in", amt=format_money(amt), tag=(tag or "NO_TAG"))

def handle_out(user: User, msg: str):
    amt = parse_amount(msg)
    if not amt: return tr(user, "not_found")
    parts = msg.strip().split()
    tag = normalize_tag(parts[-1]) if len(parts) >= 2 else ""
    db.session.add(Transaction(user_id=user.id, type="OUT", amount=amt, tag=tag))
    db.session.add(Event(user_id=user.id, kind="cmd", payload="OUT"))
    db.session.commit()
    return tr(user, "confirm_out", amt=format_money(amt), tag=(tag or "NO_TAG"))

def handle_goal(user: User, msg: str):
    # GOAL <name> <target>
    amt = parse_amount(msg)
    if not amt: return tr(user, "not_found")
    name = re.sub(r"(?i)\bGOAL\b", "", msg).replace(str(amt), "").strip()
    name = re.sub(r"\s+", " ", name).strip()
    if not name: return tr(user, "not_found")
    g = Goal.query.filter_by(user_id=user.id, name=name).one_or_none()
    if not g:
        g = Goal(user_id=user.id, name=name, target=amt)
        db.session.add(g)
    else:
        g.target = amt
    db.session.add(Event(user_id=user.id, kind="cmd", payload="GOAL"))
    db.session.commit()
    return tr(user, "goal_set", name=g.name, target=format_money(g.target))

def handle_save(user: User, msg: str):
    # SAVE <amount> <goal name...>
    amt = parse_amount(msg)
    if not amt: return tr(user, "not_found")
    name = re.sub(r"(?i)\bSAVE\b", "", msg).replace(str(amt), "").strip()
    name = re.sub(r"\s+", " ", name).strip()
    if not name: return tr(user, "not_found")
    q = Goal.query.filter(Goal.user_id==user.id, Goal.status=="active", Goal.name.ilike(f"%{name}%"))
    goals = q.all()
    if not goals: return tr(user, "no_goal", name=name)
    if len(goals) > 1: return tr(user, "amb_goal", name=name)
    g = goals[0]
    db.session.add(Transaction(user_id=user.id, type="SAVE", amount=amt, goal_id=g.id))
    db.session.add(Event(user_id=user.id, kind="cmd", payload="SAVE"))
    db.session.commit()
    saved = db.session.query(func.coalesce(func.sum(Transaction.amount),0))\
        .filter_by(user_id=user.id, goal_id=g.id, type="SAVE").scalar() or 0
    pct = round(100.0 * saved / g.target, 1) if g.target else 0.0
    return tr(user, "save_ok", amt=format_money(amt), name=g.name,
              saved=format_money(saved), target=format_money(g.target), pct=pct)

def handle_bal(user: User):
    ti, to, ts, _ = aggregates(user.id)
    return tr(user, "bal",
              total_in=format_money(ti), total_out=format_money(to),
              total_save=format_money(ts), surplus=format_money(surplus_cashflow(ti, to, ts)))

def handle_report(user: User, msg: str):
    now = dt.datetime.utcnow()
    span = 7 if "WEEK" in msg.upper() else 30
    start = now - dt.timedelta(days=span)
    # current
    ti, to, ts, per_tag = aggregates(user.id, start=start, end=now)
    # baseline prior window
    base_start = start - dt.timedelta(days=span)
    base_ti, base_to, base_ts, _ = aggregates(user.id, start=base_start, end=start)

    surplus = surplus_cashflow(ti, to, ts)
    top = "nta byiciro." if user.lang == "rw" else ("aucune catégorie." if user.lang=="fr" else "no categories.")
    insight = ""
    if to > 0 and per_tag:
        top_tag = max(per_tag, key=per_tag.get)
        top_amt = per_tag[top_tag]
        top = f"{top_tag}:{format_money(top_amt)} FBU"
        msgs = []
        if base_to and base_to > 0:
            change = round(100 * (to - base_to) / max(1, base_to))
            if abs(change) >= 25:
                if user.lang == "rw":
                    msgs.append(f"Ibyasohotse byahindutse {change}% ugereranije n'igiheruka.")
                elif user.lang == "fr":
                    msgs.append(f"Dépenses en variation de {change}% vs période précédente.")
                else:
                    msgs.append(f"Spending changed {change}% vs prior period.")
        share = round(100 * top_amt / max(1, to))
        if user.lang == "rw":
            msgs.append(f"{top_tag} bingana na {share}% by'ibyo usohora.")
        elif user.lang == "fr":
            msgs.append(f"{top_tag} représente {share}% des dépenses.")
        else:
            msgs.append(f"{top_tag} is {share}% of spending.")
        insight = " ".join(msgs)
    else:
        insight = "Nta byo gusohora byabonetse." if user.lang=="rw" else ("Aucune dépense détectée." if user.lang=="fr" else "No spending detected.")

    db.session.add(Event(user_id=user.id, kind="report", payload=f"{span}d")); db.session.commit()
    return tr(user, "report",
              total_in=format_money(ti), total_out=format_money(to),
              total_save=format_money(ts), surplus=format_money(surplus),
              top=top, insight=insight)

def handle_opportunity(user: User):
    ops = Opportunity.query.filter_by(is_active=True).all()
    if not ops:
        return "Nta mahirwe aboneka ubu." if user.lang=="rw" else ("Aucune opportunité pour l’instant." if user.lang=="fr" else "No opportunities available.")
    lines = [tr(user, "opp_header")]
    for i, op in enumerate(ops, start=1):
        lines.append(tr(user, "opp_item", i=i, name=op.name,
                        min=format_money(op.min_amount), ret=op.expected_return, risk=op.risk_level.upper()))
    db.session.add(Event(user_id=user.id, kind="opp_view", payload=str(len(ops)))); db.session.commit()
    return " ".join(lines)

def handle_yes(user: User, msg: str):
    nums = parse_amounts_all(msg)
    if not nums:
        return tr(user, "not_found")
    op_id = nums[0]
    op = Opportunity.query.get(op_id)
    if not op or not op.is_active:
        return "Amahirwe ntabonetse." if user.lang=="rw" else ("Opportunité indisponible." if user.lang=="fr" else "Opportunity not available.")
    amt = nums[1] if len(nums) >= 2 else op.min_amount
    amt = max(amt, op.min_amount)
    db.session.add(UserInvestment(user_id=user.id, opportunity_id=op.id, amount=amt, status="interested"))
    db.session.add(Event(user_id=user.id, kind="opt_in", payload=f"{op.id}:{amt}")); db.session.commit()
    return tr(user, "yes_ok", name=op.name, amt=format_money(amt), risk=op.risk_level.upper())

# ------------------ Routing & Dispatch ------------------
COMMANDS = [
    (r"^STOP$", lambda u, m: handle_stop(u)),
    (r"^START$", lambda u, m: handle_start(u)),
    (r"^HELP$", lambda u, m: handle_help(u)),
    (r"^LANG\s+(RW|FR|EN)$", lambda u, m: handle_lang(u, m)),
    (r"^BAL$", lambda u, m: handle_bal(u)),
    (r"^REPORT(\s+WEEK|\s+MONTH)?$", lambda u, m: handle_report(u, m)),
    (r"^OPPORTUNITY$", lambda u, m: handle_opportunity(u)),
    (r"^YES\s+\d+(\s+[\d,\.]+)?$", lambda u, m: handle_yes(u, m)),
    (r"^IN\s+", lambda u, m: handle_in(u, m)),
    (r"^OUT\s+", lambda u, m: handle_out(u, m)),
    (r"^GOAL\s+", lambda u, m: handle_goal(u, m)),
    (r"^SAVE\s+", lambda u, m: handle_save(u, m)),
]

@app.route("/health", methods=["GET"])
def health():
    return jsonify(ok=True)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify(error="invalid_json"), 400

    phone = (data.get("from") or "").strip() or "DEMO-USER"
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="missing_message"), 400

    user = get_or_create_user(phone)

    # If opted out, only allow START/LANG/HELP responses; otherwise block
    if user.opted_out and not re.match(r"^(START|LANG\s+(RW|FR|EN)|HELP)$", message.strip(), flags=re.I):
        return jsonify(reply=tr(user, "opted_out_block"))

    # Idempotency for mutating commands
    mutating = bool(re.match(r"^(IN|OUT|GOAL|SAVE)\b", message.strip(), flags=re.I))
    if mutating:
        fp = idempotent_fingerprint(phone, message)
        if Idempotency.query.filter_by(fingerprint=fp).first():
            return jsonify(reply=tr(user, "dup"))
        db.session.add(Idempotency(user_id=user.id, fingerprint=fp))
        db.session.commit()

    # Dispatch
    for pattern, handler in COMMANDS:
        if re.match(pattern, message, flags=re.I):
            try:
                reply = handler(user, message)
            except Exception as e:
                reply = f"Ikosa ry'imbere: {e.__class__.__name__}"
            return jsonify(reply=reply)

    return jsonify(reply=tr(user, "not_found"))

# ------------------ Auth ------------------
@app.post("/auth/register")
def auth_register():
    data = request.get_json(force=True) or {}
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "user").strip().lower()
    if not phone or not password:
        return jsonify(error="missing_credentials"), 400
    if role not in ("user", "admin"):
        role = "user"
    u = User.query.filter_by(phone=phone).one_or_none()
    if u:
        return jsonify(error="phone_exists"), 409
    u = User(phone=phone, role=role)
    set_password(u, password)
    db.session.add(u); db.session.commit()
    return jsonify(ok=True)

@app.post("/auth/login")
def auth_login():
    data = request.get_json(force=True) or {}
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    if not phone or not password:
        return jsonify(error="missing_credentials"), 400
    u = User.query.filter_by(phone=phone).one_or_none()
    if not u or not check_password(u, password):
        return jsonify(error="invalid_credentials"), 401
    claims = {"role": u.role, "phone": u.phone, "uid": u.id}
    token = create_access_token(identity=u.id, additional_claims=claims, expires_delta=timedelta(days=3))
    return jsonify(access_token=token, role=u.role, phone=u.phone)

def require_admin():
    claims = get_jwt()
    return bool(claims and claims.get("role") == "admin")

# ------------------ Admin APIs ------------------
@app.get("/admin/stats")
@jwt_required()
def admin_stats():
    if not require_admin():
        return jsonify(error="forbidden"), 403
    users = User.query.count()
    tx = Transaction.query.count()
    opts = Opportunity.query.count()
    optins = UserInvestment.query.count()
    return jsonify(users=users, transactions=tx, opportunities=opts, opt_ins=optins)

@app.get("/admin/users")
@jwt_required()
def admin_users():
    if not require_admin():
        return jsonify(error="forbidden"), 403
    q = User.query.order_by(User.created_at.desc()).limit(200).all()
    return jsonify(users=[{
        "id": u.id, "phone": u.phone, "role": u.role,
        "created_at": (u.created_at.isoformat() if u.created_at else None)
    } for u in q])

# -------------- CLI: DB init & seed --------------
@app.cli.command("initdb")
def initdb():
    with app.app_context():
        db.create_all()
        if Opportunity.query.count() == 0:
            db.session.add_all([
                Opportunity(name="Coop School Fund", description="Community education fund",
                            min_amount=5000, category="coop", expected_return="5%/month", risk_level="low", is_active=True),
                Opportunity(name="Fruit Trading Pool", description="Seasonal produce trading",
                            min_amount=10000, category="agri", expected_return="7%/month", risk_level="med", is_active=True),
                Opportunity(name="Retail Inventory Cycle", description="Short-term stock cycling",
                            min_amount=20000, category="retail", expected_return="9%/month", risk_level="high", is_active=True),
            ])
            db.session.commit()
        print("DB initialized & opportunities seeded.")

@app.cli.command("create-admin")
def create_admin():
    phone = os.environ.get("ADMIN_PHONE", "+25700000000")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    with app.app_context():
        u = User.query.filter_by(phone=phone).one_or_none()
        if not u:
            u = User(phone=phone, role="admin")
            set_password(u, password)
            db.session.add(u)
        else:
            u.role = "admin"
            set_password(u, password)
        db.session.commit()
        print(f"Admin created: {phone} / {password} (change it!)")

# -------------- Demo: /simulate --------------
@app.route("/simulate", methods=["POST"])
def simulate():
    payload = request.get_json(force=True) or {}
    phone = payload.get("from", "+257TEST")
    seq = payload.get("seq", [
        "START",
        "IN 50000 SALARY",
        "OUT 20000 FOOD",
        "REPORT WEEK",
        "OPPORTUNITY",
        "YES 2 15000",
    ])
    outs = []
    for m in seq:
        r = app.test_client().post("/ask", json={"from": phone, "message": m})
        outs.append(r.get_json().get("reply"))
    return jsonify(outs=outs)

# -------------- Main --------------
if __name__ == "__main__":
    ensure_db_schema()
    app.run(host="0.0.0.0", port=5000, debug=True)
