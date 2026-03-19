from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)


# Config MySQL
def get_db():
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="",  # ton mot de passe
        database="db_stage"

    )
    return db


# afficher la page d'accueil : etudiants + entreprises
@app.route("/")
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM etudiant")
    etudiants = cur.fetchall()

    cur_dict = db.cursor(pymysql.cursors.DictCursor)
    cur_dict.execute("SELECT * FROM entreprise")
    entreprises = cur_dict.fetchall()
    cur_dict.execute("SELECT * FROM stage")
    stages = cur_dict.fetchall()
    cur_dict.execute("SELECT * FROM responsable")
    responsables = cur_dict.fetchall()
    cur_dict.execute("""
        SELECT 
            ev.id_evaluation,
            s.sujet,
            CONCAT(r.nom, ' ', r.prenom) AS responsable,
            ev.note_rapport,
            ev.note_soutenance,
            ev.remarque,
            ev.decision
        FROM evaluation ev
        JOIN stage s ON ev.id_stage = s.id_stage
        JOIN responsable r ON ev.id_responsable = r.id_responsable
    """)
    evaluations = cur_dict.fetchall()
    cur_dict.execute("""
        SELECT 
            sv.id_suivi,
            sv.type_suivi,
            sv.taux_d_avancement,
            s.sujet,
            CONCAT(r.nom, ' ', r.prenom) AS responsable
        FROM suivi sv
        JOIN stage s ON sv.id_stage = s.id_stage
        JOIN responsable r ON sv.id_responsable = r.id_responsable
    """)
    suivis = cur_dict.fetchall()
    cur_dict.close()
    db.close()
    return render_template(
        "index.html",
        etudiants=etudiants,
        entreprises=entreprises,
        stages=stages,
        responsables=responsables,
        evaluations=evaluations,
        suivis=suivis,
    )


# ajouter etudiant
@app.route("/add", methods=["GET", "POST"])
def add():
    db = get_db()
    if request.method == "POST":
        Matricule = request.form["Matricule"]
        nom = request.form["nom"]
        Prenom = request.form["prenom"]
        date_naissance = request.form["date_naissance"]
        email = request.form["email"]
        num_telephone = request.form["num_telephone"]
        niveau = request.form["niveau"]
        specialite = request.form["specialite"]

        cur = db.cursor()
        cur.execute(
            "INSERT INTO etudiant (Matricule,nom,prenom,date_naissance,email,num_telephone,niveau,specialite) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (Matricule, nom, Prenom, date_naissance, email, num_telephone, niveau, specialite))
        db.commit()
        db.close()

        return redirect(url_for("index"))
    else:

        return render_template("add.html")


# modifier etudiant
# modifier etudiant
@app.route("/edit/<int:Matricule>", methods=["GET", "POST"])
def edit(Matricule):
    db = get_db()
    cur = db.cursor()
    id_orig = Matricule

    if request.method == "POST":
        Matricule_form = request.form.get("Matricule", id_orig)
        nom = request.form["nom"]
        Prenom = request.form["prenom"]
        date_naissance = request.form["date_naissance"]
        email = request.form["email"]
        num_telephone = request.form["num_telephone"]
        niveau = request.form["niveau"]
        specialite = request.form["specialite"]
        cur.execute(
            "UPDATE etudiant SET Matricule=%s, nom=%s, prenom=%s, date_naissance=%s, email=%s, num_telephone=%s, niveau=%s, specialite=%s WHERE Matricule=%s",
            (Matricule_form, nom, Prenom, date_naissance, email, num_telephone, niveau, specialite, id_orig))
        db.commit()
        db.close()
        return redirect(url_for("index"))

    else:
        cur.execute("SELECT Matricule, nom, prenom, date_naissance, email, num_telephone, niveau, specialite FROM etudiant WHERE Matricule=%s", (id_orig,))
        etudiant = cur.fetchone()
        db.close()
        return render_template("edit.html", etudiant=etudiant)


# supprimer etudiant
@app.route("/delete/<int:Matricule>")
def delete(Matricule):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM etudiant WHERE Matricule=%s", (Matricule,))
    db.commit()
    db.close()

    return redirect(url_for("index"))


# ajouter entreprise
@app.route("/add_comp", methods=["GET", "POST"])
def add_comp():
    db = get_db()
    if request.method == "POST":
        id_entreprise = request.form["id_entreprise"]
        nom_entreprise = request.form["nom_entreprise"]
        adresse = request.form["adresse"]
        email = request.form["email"]
        secteur_activite = request.form["secteur_activite"]

        cur = db.cursor()
        cur.execute(
            "INSERT INTO entreprise (id_entreprise,nom_entreprise,adresse,email,secteur_activite) VALUES (%s,%s,%s,%s,%s)",
            (id_entreprise, nom_entreprise, adresse, email, secteur_activite))
        db.commit()
        db.close()

        return redirect(url_for("index"))
    else:

        return render_template("add_comp.html")


# modifier entreprise
@app.route("/edit_comp/<int:id_entreprise>", methods=["GET", "POST"])
def edit_comp(id_entreprise):
    db = get_db()
    cur = db.cursor()
    id_orig = id_entreprise  # garder l'ID original pour la clause WHERE

    if request.method == "POST":
        id_entreprise_form = request.form.get("id_entreprise", id_orig)
        nom_entreprise = request.form["nom_entreprise"]
        adresse = request.form["adresse"]
        email = request.form["email"]
        secteur_activite = request.form["secteur_activite"]
        cur.execute(
            "UPDATE entreprise SET id_entreprise=%s, nom_entreprise=%s,adresse=%s, email=%s,secteur_activite=%s WHERE id_entreprise=%s",
            (id_entreprise_form, nom_entreprise, adresse, email, secteur_activite, id_orig))
        db.commit()
        db.close()

        return redirect(url_for("index"))

    else:
        cur_dict = db.cursor(pymysql.cursors.DictCursor)
        cur_dict.execute("SELECT * FROM entreprise WHERE id_entreprise=%s", (id_orig,))
        entreprise_record = cur_dict.fetchone()
        cur_dict.close()
    db.close()

    return render_template("edit_comp.html", entreprise=entreprise_record)


# supprimer entreprise
@app.route("/delete_comp/<int:id_entreprise>")
def delete_comp(id_entreprise):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM entreprise WHERE id_entreprise=%s", (id_entreprise,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


# ajouter stage
@app.route("/add_stage", methods=["GET", "POST"])
def add_stage():
    db = get_db()

    # Récupération des listes pour le formulaire
    with db.cursor() as cur:
        cur.execute("SELECT Matricule FROM etudiant")
        etudiant_ids = cur.fetchall()

    with db.cursor() as cur:
        cur.execute("SELECT nom_entreprise FROM entreprise")
        entreprises = cur.fetchall()

    if request.method == "POST":
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")
        type_stage = request.form.get("type_stage")
        sujet = request.form.get("sujet")
        Matricule = request.form.get("Matricule")
        nom_entreprise = request.form.get("nom_entreprise")
        rapport = request.form.get("rapport")

        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO stage (date_debut, date_fin, type_stage, sujet, Matricule, nom_entreprise, rapport) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (date_debut, date_fin, type_stage, sujet, Matricule, nom_entreprise, rapport)
            )
            db.commit()

        return redirect(url_for("index"))

    cur_dict = db.cursor(pymysql.cursors.DictCursor)
    cur_dict.execute("SELECT  Matricule FROM etudiant ORDER BY  Matricule")
    etudiant_ids = cur_dict.fetchall()
    cur_dict.execute(
        "SELECT id_entreprise, nom_entreprise FROM entreprise ORDER BY nom_entreprise, id_entreprise"
    )
    entreprises = cur_dict.fetchall()
    cur_dict.close()
    db.close()
    return render_template(
        "add_stage.html",
        etudiant_ids=etudiant_ids,
        entreprises=entreprises,
    )
# modifier stage
@app.route("/edit_stage/<int:id_stage>", methods=["GET", "POST"])
def edit_stage(id_stage):
    conn = get_db()
    id_orig = id_stage

    if request.method == "POST":
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")
        type_stage = request.form.get("type_stage")
        sujet = request.form.get("sujet")
        Matricule = request.form.get("Matricule")
        nom_entreprise = request.form.get("nom_entreprise")
        rapport = request.form.get("rapport")

        cur = conn.cursor()
        cur.execute("""
            UPDATE stage 
            SET date_debut=%s, date_fin=%s, type_stage=%s, sujet=%s, 
                Matricule=%s, nom_entreprise=%s, rapport=%s
            WHERE id_stage=%s
        """, (date_debut, date_fin, type_stage, sujet, Matricule, nom_entreprise, rapport, id_orig))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET: fetch the stage record
    cur_dict = conn.cursor(pymysql.cursors.DictCursor)
    cur_dict.execute("SELECT * FROM stage WHERE id_stage=%s", (id_orig,))
    stage = cur_dict.fetchone()

    # Dropdown: etudiants
    cur_dict.execute("""
        SELECT e.Matricule, e.nom, e.prenom 
        FROM etudiant e 
        ORDER BY e.Matricule
    """)
    etudiants = cur_dict.fetchall()

    # Dropdown: entreprises
    cur_dict.execute("""
        SELECT id_entreprise, nom_entreprise 
        FROM entreprise 
        ORDER BY nom_entreprise
    """)
    entreprises = cur_dict.fetchall()

    cur_dict.close()
    conn.close()
    return render_template("edit_stage.html", stage=stage, etudiants=etudiants, entreprises=entreprises)
# supprimer stage
@app.route("/delete_stage/<int:id_stage>")
def delete_stage(id_stage):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM stage WHERE id_stage=%s", (id_stage,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ajouter responsable
@app.route("/add_responsable", methods=["GET", "POST"])
def add_respo():
    db = get_db()
    if request.method == "POST":
        id_responsable = request.form["id_responsable"]
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        telephone = request.form["telephone"]
        cur = db.cursor()
        cur.execute(
            "INSERT INTO responsable (id_responsable,nom,prenom,email,telephone) VALUES (%s,%s,%s,%s,%s)",
            (id_responsable, nom, prenom, email, telephone))
        db.commit()
        db.close()

        return redirect(url_for("index"))
    else:
        return render_template("add_respo.html")


# modifier responsable
@app.route("/edit_responsable/<int:id_responsable>", methods=["GET", "POST"])
def edit_responsable(id_responsable):
    db = get_db()
    id_orig = id_responsable

    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        telephone = request.form["telephone"]
        cur = db.cursor()
        cur.execute(
            "UPDATE responsable SET nom=%s, prenom=%s, email=%s, telephone=%s WHERE id_responsable=%s",
            (nom, prenom, email, telephone, id_orig),
        )
        db.commit()
        db.close()
        return redirect(url_for("index"))
    else:
        cur_dict = db.cursor(pymysql.cursors.DictCursor)
        cur_dict.execute("SELECT * FROM responsable WHERE id_responsable=%s", (id_orig,))
        responsable_record = cur_dict.fetchone()
        cur_dict.close()
        db.close()
        return render_template("edit_respo.html", responsable=responsable_record)


# supprimer responsable
@app.route("/delete_responsable/<int:id_responsable>")
def delete_responsable(id_responsable):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM responsable WHERE id_responsable=%s", (id_responsable,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


# ajouter evaluation

@app.route("/add_eva", methods=["GET", "POST"])
def add_evaluation():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        id_stage = request.form.get('id_stage')
        id_responsable = request.form.get('id_responsable')

        if not id_stage or not id_responsable:
            return "Please select a stage and a responsable"

        id_stage = int(id_stage)
        id_responsable = int(id_responsable)
        note_rapport = request.form.get('note_rapport')
        note_soutenance = request.form.get('note_soutenance')
        remarque = request.form.get('remarque')
        decision = request.form.get('decision')

        sql = """
        INSERT INTO evaluation
        (id_stage, id_responsable, note_rapport, note_soutenance, remarque, decision)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_stage, id_responsable, note_rapport, note_soutenance, remarque, decision))
        conn.commit()
        conn.close()
        return redirect("/")

    # JOIN stage with etudiant to show subject + student name
    cursor.execute("""
        SELECT s.id_stage, s.sujet, e.nom, e.prenom
        FROM stage s
        JOIN etudiant e ON s.Matricule = e.Matricule
        ORDER BY s.id_stage
    """)
    sujets = cursor.fetchall()  # tuples: (id_stage, sujet, nom, prenom)

    # Fetch full name for responsable
    cursor.execute("SELECT id_responsable, nom, prenom FROM responsable ORDER BY nom")
    responsables = cursor.fetchall()  # tuples: (id_responsable, nom, prenom)

    conn.close()
    return render_template("add_eva.html", sujets=sujets, responsables=responsables)


# modifier evaluation
@app.route("/edit_eva/<int:id_evaluation>", methods=["GET", "POST"])
def edit_evaluation(id_evaluation):
    conn = get_db()
    id_orig = id_evaluation

    if request.method == "POST":
        id_stage = int(request.form.get('id_stage'))
        id_responsable = int(request.form.get('id_responsable'))
        note_rapport = request.form.get('note_rapport')
        note_soutenance = request.form.get('note_soutenance')
        remarque = request.form.get('remarque')
        decision = request.form.get('decision')

        cursor = conn.cursor()
        cursor.execute(
            """UPDATE evaluation 
               SET id_stage=%s, id_responsable=%s, note_rapport=%s, 
                   note_soutenance=%s, remarque=%s, decision=%s 
               WHERE id_evaluation=%s""",
            (id_stage, id_responsable, note_rapport, note_soutenance, remarque, decision, id_orig)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evaluation WHERE id_evaluation=%s", (id_orig,))
        evaluation = cursor.fetchone()

        cursor.execute("SELECT id_stage, sujet FROM stage")
        sujets = cursor.fetchall()

        cursor.execute("SELECT id_responsable, nom, prenom FROM responsable")
        responsables = cursor.fetchall()

        conn.close()
        return render_template("edit_eva.html", evaluation=evaluation, sujets=sujets, responsables=responsables)

    # supprimer evaluation


@app.route("/delete_eva/<int:id_evaluation>")

def delete_evaluation(id_evaluation):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluation WHERE id_evaluation=%s", (id_evaluation,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))
# afficher la liste des suivis
@app.route("/suivis")
def suivis():
    conn = get_db()
    cur_dict = conn.cursor(pymysql.cursors.DictCursor)
    cur_dict.execute("""
        SELECT 
            sv.id_suivi,
            sv.type_suivi,
            sv.taux_d_avancement,
            s.sujet,
            CONCAT(r.nom, ' ', r.prenom) AS responsable
        FROM suivi sv
        JOIN stage s ON sv.id_stage = s.id_stage
        JOIN responsable r ON sv.id_responsable = r.id_responsable
    """)
    suivis = cur_dict.fetchall()
    cur_dict.close()
    conn.close()
    return render_template("suivis.html", suivis=suivis)


# ajouter suivi
@app.route("/add_suivi", methods=["GET", "POST"])
def add_suivi():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        type_suivi = request.form.get("type_suivi")
        taux_d_avancement = request.form.get("taux_d_avancement")
        id_stage = int(request.form.get("id_stage"))
        id_responsable = int(request.form.get("id_responsable"))

        cursor.execute("""
            INSERT INTO suivi (type_suivi, taux_d_avancement, id_stage, id_responsable)
            VALUES (%s, %s, %s, %s)
        """, (type_suivi, taux_d_avancement, id_stage, id_responsable))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET: fetch stages + responsables for dropdowns
    cursor.execute("""
        SELECT s.id_stage, s.sujet, e.nom, e.prenom
        FROM stage s
        JOIN etudiant e ON s.Matricule = e.Matricule
        ORDER BY s.id_stage
    """)
    stages = cursor.fetchall()  # (id_stage, sujet, nom, prenom)

    cursor.execute("SELECT id_responsable, nom, prenom FROM responsable ORDER BY nom")
    responsables = cursor.fetchall()  # (id_responsable, nom, prenom)

    conn.close()
    return render_template("add_suivi.html", stages=stages, responsables=responsables)


# modifier suivi
@app.route("/edit_suivi/<int:id_suivi>", methods=["GET", "POST"])
def edit_suivi(id_suivi):
    conn = get_db()
    cursor = conn.cursor()
    id_orig = id_suivi

    if request.method == "POST":
        type_suivi = request.form.get("type_suivi")
        taux_d_avancement = request.form.get("taux_d_avancement")
        id_stage = int(request.form.get("id_stage"))
        id_responsable = int(request.form.get("id_responsable"))

        cursor.execute("""
            UPDATE suivi 
            SET type_suivi=%s, taux_d_avancement=%s, id_stage=%s, id_responsable=%s
            WHERE id_suivi=%s
        """, (type_suivi, taux_d_avancement, id_stage, id_responsable, id_orig))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET: fetch current suivi record
    cursor.execute("SELECT * FROM suivi WHERE id_suivi=%s", (id_orig,))
    suivi = cursor.fetchone()  # (id_suivi, type_suivi, taux_d_avancement, id_stage, id_responsable)

    cursor.execute("""
        SELECT s.id_stage, s.sujet, e.nom, e.prenom
        FROM stage s
        JOIN etudiant e ON s.Matricule = e.Matricule
        ORDER BY s.id_stage
    """)
    stages = cursor.fetchall()

    cursor.execute("SELECT id_responsable, nom, prenom FROM responsable ORDER BY nom")
    responsables = cursor.fetchall()

    conn.close()
    return render_template("edit_suivi.html", suivi=suivi, stages=stages, responsables=responsables)


# supprimer suivi
@app.route("/delete_suivi/<int:id_suivi>")
def delete_suivi(id_suivi):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suivi WHERE id_suivi=%s", (id_suivi,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
