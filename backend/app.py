from flask import Flask, request
from flask_cors import CORS
import mysql.connector
import joblib
import os

app = Flask(__name__)
CORS(app)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="queueless_hospital"
    )


# ============================================================
# AI MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "queue_model.pkl"
)

FEATURES_PATH = os.path.join(
    os.path.dirname(__file__),
    "model_features.pkl"
)

try:
    queue_model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)

    print("===================================")
    print("AI QUEUE MODEL LOADED SUCCESSFULLY")
    print("===================================")
    print("Model features:", model_features)

except Exception as e:
    queue_model = None
    model_features = None

    print("===================================")
    print("WARNING: AI MODEL COULD NOT LOAD")
    print("===================================")
    print("Reason:", e)


# ============================================================
# AI WAITING TIME PREDICTION
# ============================================================

def predict_wait_time(people_ahead, service_time):

    if people_ahead <= 0:
        return 0

    if queue_model is None:
        return round(people_ahead * service_time)

    try:

        prediction = queue_model.predict([
            [people_ahead, service_time]
        ])

        predicted_time = float(prediction[0])

        predicted_time = max(
            0,
            predicted_time
        )

        return round(predicted_time)

    except Exception as e:

        print(
            "AI prediction error:",
            e
        )

        return round(
            people_ahead * service_time
        )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return "QueueLess AI Hospital Backend is Running!"


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        if not name or not email or not phone or not password:

            return {
                "message":
                    "All fields are required"
            }, 400

        connection = get_db_connection()

        cursor = connection.cursor()

        query = """
            INSERT INTO users
            (name, email, phone, password, role)
            VALUES
            (%s, %s, %s, %s, 'patient')
        """

        cursor.execute(
            query,
            (
                name,
                email,
                phone,
                password
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return {
            "message":
                "Registration successful"
        }, 201

    except mysql.connector.IntegrityError:

        return {
            "message":
                "Email already registered"
        }, 409

    except Exception as e:

        return {
            "message":
                "Registration failed: "
                + str(e)
        }, 500


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        email = data.get(
            "email",
            ""
        ).strip()

        password = data.get(
            "password",
            ""
        )

        if not email or not password:

            return {
                "message":
                    "Email and password are required"
            }, 400

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                id,
                name,
                email,
                phone,
                password,
                role

            FROM users

            WHERE email = %s

            LIMIT 1
        """

        cursor.execute(
            query,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            cursor.close()
            connection.close()

            return {
                "message":
                    "Invalid email or password"
            }, 401

        if user["password"] != password:

            cursor.close()
            connection.close()

            return {
                "message":
                    "Invalid email or password"
            }, 401

        user.pop(
            "password",
            None
        )

        cursor.close()
        connection.close()

        print(
            "LOGIN SUCCESS:",
            user["email"],
            "| ROLE:",
            user["role"]
        )

        return {
            "message":
                "Login successful",

            "user":
                user
        }, 200

    except Exception as e:

        print(
            "LOGIN ERROR:",
            e
        )

        return {
            "message":
                "Login failed: "
                + str(e)
        }, 500


# ============================================================
# GET SERVICES
# ============================================================

@app.route("/services", methods=["GET"])
def get_services():

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                id,
                service_name,
                description

            FROM services

            WHERE is_active = 1

            ORDER BY id
        """

        cursor.execute(query)

        services = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "services":
                services
        }, 200

    except Exception as e:

        return {
            "message":
                "Could not load services: "
                + str(e)
        }, 500


# ============================================================
# GET DOCTORS
# ============================================================

@app.route("/doctors", methods=["GET"])
def get_doctors():

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                id,
                name,
                specialization,
                service_id,
                is_available

            FROM doctors

            ORDER BY id
        """

        cursor.execute(query)

        doctors = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "doctors":
                doctors
        }, 200

    except Exception as e:

        return {
            "message":
                "Could not load doctors: "
                + str(e)
        }, 500


# ============================================================
# GENERATE TOKEN
# ============================================================

@app.route("/generate-token", methods=["POST"])
def generate_token():

    try:

        data = request.get_json()

        user_id = data.get("user_id")
        service_id = data.get("service_id")
        doctor_id = data.get("doctor_id")

        if not user_id or not service_id or not doctor_id:

            return {
                "message":
                    "User, service and doctor are required"
            }, 400

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # CHECK SERVICE
        # ----------------------------------------------------

        service_query = """
            SELECT
                id,
                service_name

            FROM services

            WHERE id = %s

            AND is_active = 1
        """

        cursor.execute(
            service_query,
            (service_id,)
        )

        service = cursor.fetchone()

        if not service:

            cursor.close()
            connection.close()

            return {
                "message":
                    "Invalid or inactive service"
            }, 404

        # ----------------------------------------------------
        # CHECK DOCTOR
        # ----------------------------------------------------

        doctor_query = """
            SELECT
                id,
                name,
                specialization

            FROM doctors

            WHERE id = %s

            AND service_id = %s

            AND is_available = 1
        """

        cursor.execute(
            doctor_query,
            (
                doctor_id,
                service_id
            )
        )

        doctor = cursor.fetchone()

        if not doctor:

            cursor.close()
            connection.close()

            return {
                "message":
                    "Selected doctor is not available for this service"
            }, 404

        # ----------------------------------------------------
        # GENERATE TOKEN NUMBER
        # ----------------------------------------------------

        token_query = """
            SELECT
                COALESCE(
                    MAX(token_number),
                    0
                ) + 1 AS next_token

            FROM tokens

            WHERE service_id = %s

            AND doctor_id = %s
        """

        cursor.execute(
            token_query,
            (
                service_id,
                doctor_id
            )
        )

        result = cursor.fetchone()

        token_number = result[
            "next_token"
        ]

        # ----------------------------------------------------
        # INSERT TOKEN
        # ----------------------------------------------------

        insert_query = """
            INSERT INTO tokens
            (
                token_number,
                user_id,
                service_id,
                doctor_id,
                status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'waiting'
            )
        """

        cursor.execute(
            insert_query,
            (
                token_number,
                user_id,
                service_id,
                doctor_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return {

            "message":
                "Token generated successfully",

            "token_number":
                token_number,

            "service_id":
                service_id,

            "service":
                service["service_name"],

            "doctor_id":
                doctor_id,

            "doctor":
                doctor["name"],

            "status":
                "waiting"

        }, 201

    except Exception as e:

        return {
            "message":
                "Token generation failed: "
                + str(e)
        }, 500


# ============================================================
# GET MY CURRENT TOKEN
# ============================================================

@app.route("/my-token/<int:user_id>", methods=["GET"])
def get_my_token(user_id):

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                t.id,
                t.token_number,
                t.status,
                t.created_at,
                t.service_id,
                t.doctor_id,
                s.service_name,
                d.name AS doctor_name,
                d.specialization

            FROM tokens t

            JOIN services s
                ON t.service_id = s.id

            JOIN doctors d
                ON t.doctor_id = d.id

            WHERE t.user_id = %s

            AND t.status IN
            ('waiting', 'called')

            ORDER BY t.id DESC

            LIMIT 1
        """

        cursor.execute(
            query,
            (user_id,)
        )

        token = cursor.fetchone()

        cursor.close()
        connection.close()

        if token:

            return {
                "token":
                    token
            }, 200

        return {
            "token":
                None,

            "message":
                "No active token"

        }, 200

    except Exception as e:

        return {
            "message":
                "Could not retrieve token: "
                + str(e)
        }, 500


# ============================================================
# PATIENT QUEUE STATUS
# ============================================================

@app.route("/queue-status/<int:user_id>", methods=["GET"])
def queue_status(user_id):

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # GET PATIENT'S ACTIVE TOKEN
        # ----------------------------------------------------

        # ------------------------------------------------------
        # ALWAYS FETCH THE PATIENT'S MOST RECENT TOKEN,
        # REGARDLESS OF STATUS.
        #
        # This is what lets the dashboard reflect a token
        # the moment staff mark it completed / skipped /
        # cancelled, instead of the token silently
        # disappearing from the response.
        # ------------------------------------------------------

        patient_query = """
            SELECT
                t.id,
                t.token_number,
                t.service_id,
                t.doctor_id,
                t.status,
                t.created_at,
                s.service_name,
                d.name AS doctor_name,
                d.specialization

            FROM tokens t

            JOIN services s
                ON t.service_id = s.id

            JOIN doctors d
                ON t.doctor_id = d.id

            WHERE t.user_id = %s

            ORDER BY t.id DESC

            LIMIT 1
        """

        cursor.execute(
            patient_query,
            (user_id,)
        )

        patient_token = cursor.fetchone()

        # ----------------------------------------------------
        # NO ACTIVE TOKEN
        # ----------------------------------------------------

        if not patient_token:

            cursor.close()
            connection.close()

            return {

                "token":
                    None,

                "current_token":
                    0,

                "people_ahead":
                    0,

                "estimated_wait":
                    0,

                "service_time":
                    0,

                "ai_prediction_used":
                    False,

                "queue_source":
                    "actual_database_queue",

                "ai_role":
                    "waiting_time_estimation_only",

                "message":
                    "No active token"

            }, 200

        service_id = patient_token[
            "service_id"
        ]

        doctor_id = patient_token[
            "doctor_id"
        ]

        token_number = patient_token[
            "token_number"
        ]

        # ----------------------------------------------------
        # FIND CURRENTLY CALLED TOKEN
        # ----------------------------------------------------

        current_query = """
            SELECT
                id,
                token_number

            FROM tokens

            WHERE service_id = %s

            AND doctor_id = %s

            AND status = 'called'

            ORDER BY
                called_at DESC,
                id DESC

            LIMIT 1
        """

        cursor.execute(
            current_query,
            (
                service_id,
                doctor_id
            )
        )

        current = cursor.fetchone()

        if current:

            current_token = current[
                "token_number"
            ]

        else:

            current_token = 0

        # ----------------------------------------------------
        # PEOPLE AHEAD
        #
        # ONLY WAITING PATIENTS WITH A LOWER TOKEN NUMBER
        # ARE COUNTED.
        #
        # COMPLETED / CALLED / SKIPPED / CANCELLED
        # PATIENTS ARE NOT COUNTED.
        # ----------------------------------------------------

        ahead_query = """
            SELECT
                COUNT(*) AS people_ahead

            FROM tokens

            WHERE service_id = %s

            AND doctor_id = %s

            AND status = 'waiting'

            AND token_number < %s
        """

        cursor.execute(
            ahead_query,
            (
                service_id,
                doctor_id,
                token_number
            )
        )

        people_ahead = int(
            cursor.fetchone()[
                "people_ahead"
            ]
        )

        # ----------------------------------------------------
        # PATIENT IS BEING SERVED, OR THE VISIT HAS
        # ALREADY REACHED A FINAL STATE
        # (completed / skipped / cancelled).
        #
        # In every one of these cases there is no
        # "wait" left to estimate.
        # ----------------------------------------------------

        terminal_or_active_statuses = (
            "called",
            "completed",
            "skipped",
            "cancelled",
        )

        if patient_token["status"] in terminal_or_active_statuses:

            people_ahead = 0

            estimated_wait = 0

            service_time = 0

            ai_prediction_used = False

        else:

            # ------------------------------------------------
            # AVERAGE SERVICE TIME
            # ------------------------------------------------

            service_time_query = """
                SELECT
                    AVG(
                        TIMESTAMPDIFF(
                            MINUTE,
                            called_at,
                            completed_at
                        )
                    ) AS average_service_time

                FROM tokens

                WHERE service_id = %s

                AND doctor_id = %s

                AND status = 'completed'

                AND called_at IS NOT NULL

                AND completed_at IS NOT NULL
            """

            cursor.execute(
                service_time_query,
                (
                    service_id,
                    doctor_id
                )
            )

            service_time_result = (
                cursor.fetchone()
            )

            if (
                service_time_result
                and
                service_time_result[
                    "average_service_time"
                ] is not None
            ):

                service_time = float(
                    service_time_result[
                        "average_service_time"
                    ]
                )

                service_time = max(
                    1,
                    service_time
                )

            else:

                service_time = 10

            # ------------------------------------------------
            # AI PREDICTION
            # ------------------------------------------------

            estimated_wait = predict_wait_time(
                people_ahead,
                service_time
            )

            ai_prediction_used = (
                queue_model is not None
            )

        # ----------------------------------------------------
        # CLOSE DATABASE
        # ----------------------------------------------------

        cursor.close()
        connection.close()

        # ----------------------------------------------------
        # RETURN DATA TO PATIENT DASHBOARD
        # ----------------------------------------------------

        return {

            "token": {

                "id":
                    patient_token["id"],

                "token_number":
                    patient_token["token_number"],

                "service_id":
                    patient_token["service_id"],

                "service_name":
                    patient_token["service_name"],

                "doctor_id":
                    patient_token["doctor_id"],

                "doctor_name":
                    patient_token["doctor_name"],

                "specialization":
                    patient_token["specialization"],

                "status":
                    patient_token["status"],

                "created_at":
                    patient_token["created_at"]

            },

            "current_token":
                current_token,

            "people_ahead":
                people_ahead,

            "estimated_wait":
                estimated_wait,

            "service_time":
                round(
                    service_time,
                    1
                ),

            "ai_prediction_used":
                ai_prediction_used,

            "queue_source":
                "actual_database_queue",

            "ai_role":
                "waiting_time_estimation_only"

        }, 200

    except Exception as e:

        print(
            "QUEUE STATUS ERROR:",
            e
        )

        return {

            "message":
                "Could not retrieve queue status: "
                + str(e)

        }, 500


# ============================================================
# STAFF QUEUE
# ============================================================

@app.route("/staff/queue/<int:service_id>", methods=["GET"])
def staff_queue(service_id):

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                t.id,
                t.token_number,
                t.user_id,
                t.service_id,
                t.doctor_id,
                t.status,
                t.created_at,
                t.called_at,
                t.completed_at,

                u.name AS patient_name,

                s.service_name,

                d.name AS doctor_name,

                d.specialization

            FROM tokens t

            JOIN users u
                ON t.user_id = u.id

            JOIN services s
                ON t.service_id = s.id

            JOIN doctors d
                ON t.doctor_id = d.id

            WHERE t.service_id = %s

            ORDER BY

                CASE

                    WHEN t.status = 'called'
                    THEN 1

                    WHEN t.status = 'waiting'
                    THEN 2

                    WHEN t.status = 'completed'
                    THEN 3

                    ELSE 4

                END,

                t.doctor_id ASC,

                t.token_number ASC
        """

        cursor.execute(
            query,
            (service_id,)
        )

        queue = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "queue":
                queue
        }, 200

    except Exception as e:

        return {
            "message":
                "Could not retrieve staff queue: "
                + str(e)
        }, 500


# ============================================================
# STAFF CALL NEXT PATIENT
# ============================================================

@app.route("/staff/call-next", methods=["POST"])
def staff_call_next():

    try:

        data = request.get_json()

        service_id = data.get(
            "service_id"
        )

        doctor_id = data.get(
            "doctor_id"
        )

        if not service_id or not doctor_id:

            return {
                "message":
                    "Service ID and doctor ID are required"
            }, 400

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # CHECK CURRENT PATIENT
        # ----------------------------------------------------

        current_query = """
            SELECT
                id,
                token_number

            FROM tokens

            WHERE service_id = %s

            AND doctor_id = %s

            AND status = 'called'

            LIMIT 1
        """

        cursor.execute(
            current_query,
            (
                service_id,
                doctor_id
            )
        )

        current = cursor.fetchone()

        if current:

            cursor.close()
            connection.close()

            return {

                "message":
                    "A patient is already being served",

                "token_number":
                    current["token_number"]

            }, 409

        # ----------------------------------------------------
        # FIND NEXT PATIENT
        # ----------------------------------------------------

        next_query = """
            SELECT
                id,
                token_number,
                user_id

            FROM tokens

            WHERE service_id = %s

            AND doctor_id = %s

            AND status = 'waiting'

            ORDER BY token_number ASC

            LIMIT 1
        """

        cursor.execute(
            next_query,
            (
                service_id,
                doctor_id
            )
        )

        patient = cursor.fetchone()

        if not patient:

            cursor.close()
            connection.close()

            return {
                "message":
                    "No patients waiting"
            }, 404

        # ----------------------------------------------------
        # CALL PATIENT
        # ----------------------------------------------------

        update_query = """
            UPDATE tokens

            SET
                status = 'called',
                called_at = NOW()

            WHERE id = %s
        """

        cursor.execute(
            update_query,
            (patient["id"],)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return {

            "message":
                "Next patient called",

            "token_number":
                patient["token_number"],

            "user_id":
                patient["user_id"]

        }, 200

    except Exception as e:

        return {

            "message":
                "Could not call next patient: "
                + str(e)

        }, 500


# ============================================================
# STAFF COMPLETE PATIENT
# ============================================================

@app.route("/staff/complete/<int:token_id>", methods=["POST"])
def staff_complete(token_id):

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        query = """
            UPDATE tokens

            SET
                status = 'completed',
                completed_at = NOW()

            WHERE id = %s

            AND status = 'called'
        """

        cursor.execute(
            query,
            (token_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:

            cursor.close()
            connection.close()

            return {
                "message":
                    "Token not found or already completed"
            }, 404

        cursor.close()
        connection.close()

        return {
            "message":
                "Patient completed successfully"
        }, 200

    except Exception as e:

        return {
            "message":
                "Could not complete patient: "
                + str(e)
        }, 500


# ============================================================
# TEST DATABASE
# ============================================================

@app.route("/test-db")
def test_db():

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT DATABASE()"
        )

        database = cursor.fetchone()

        cursor.close()
        connection.close()

        return (
            "Database connected successfully: "
            + str(database[0])
        )

    except Exception as e:

        return (
            "Database connection failed: "
            + str(e)
        ), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )