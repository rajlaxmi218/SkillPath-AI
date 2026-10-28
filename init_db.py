"""
Database Initialization Script for SkillPathAI

Creates the 7 application tables in the target database:
- users
- profiles
- assessments
- roadmaps
- topics
- progress
- quiz_results

Safeguards:
- Supports interactive password entry via getpass to target Aiven directly, OR uses an active DATABASE_URL.
- Positively validates that the target host is Aiven and database is 'defaultdb'.
- Explicitly binds the execution to an active connection context (`Base.metadata.create_all(bind=conn)` within `engine.begin()`).
- Refreshes inspection using explicit `SHOW TABLES` and a fresh connection.
- Never targets local MySQL.
- Does not drop or delete existing tables or data.
- Never prints or logs credentials.
"""

import sys
import os
import getpass
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.mysql import Base
import models.user
import models.profile
import models.assessment
import models.roadmap
import models.topic
import models.progress
import models.quiz_result

AIVEN_HOST = "mysql-1a2f6f2d-aditiuplenchwar2076-35e2.d.aivencloud.com"
AIVEN_PORT = 15209
AIVEN_USER = "avnadmin"
AIVEN_DB = "defaultdb"
CA_CERT_PATH = os.path.join(backend_dir, "ca.pem")


def get_target_engine():
    # If DATABASE_URL is explicitly set in environment, use it
    env_url = os.getenv("DATABASE_URL")
    if env_url and env_url.strip():
        url = env_url.strip()
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        connect_args = {}
        if os.path.exists(CA_CERT_PATH):
            connect_args["ssl"] = {"ca": CA_CERT_PATH}
        else:
            import certifi
            connect_args["ssl"] = {"ca": certifi.where()}
        return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

    # Otherwise prompt for the Aiven password securely
    print("=" * 60)
    print("SKILLPATHAI - Aiven Cloud Database Initialization")
    print(f"Target Host: {AIVEN_HOST}")
    print(f"Target Port: {AIVEN_PORT}")
    print(f"Target User: {AIVEN_USER}")
    print(f"Target Database: {AIVEN_DB}")
    print("=" * 60)

    password = None
    try:
        password = getpass.getpass(f"Enter Aiven MySQL password for '{AIVEN_USER}' (hidden): ")
    except Exception as e:
        print(f"\nPassword input aborted: {e}")
        return None

    if not password:
        print("Error: Password cannot be empty.")
        return None

    db_url = URL.create(
        drivername="mysql+pymysql",
        username=AIVEN_USER,
        password=password,
        host=AIVEN_HOST,
        port=AIVEN_PORT,
        database=AIVEN_DB,
    )

    connect_args = {
        "ssl": {"ca": CA_CERT_PATH} if os.path.exists(CA_CERT_PATH) else {},
        "connect_timeout": 15
    }
    if "ssl" not in connect_args or not connect_args["ssl"]:
        import certifi
        connect_args["ssl"] = {"ca": certifi.where()}

    target_engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
    del password
    return target_engine


def init_database():
    engine = get_target_engine()
    if engine is None:
        print("Initialization aborted.")
        return False

    host = engine.url.host or ""
    db_name = engine.url.database or ""

    # Strict target verification check: Must NOT be local MySQL
    if host.lower() in ("localhost", "127.0.0.1", ""):
        print("\n[SAFETY ABORT] Target host is local MySQL. Cloud initialization aborted to protect local database.")
        return False

    if "aivencloud.com" not in host.lower() and host != AIVEN_HOST:
        print(f"\n[SAFETY ABORT] Target host '{host}' is not a verified Aiven host.")
        return False

    if db_name.lower() != AIVEN_DB:
        print(f"\n[SAFETY ABORT] Target database '{db_name}' is not '{AIVEN_DB}'.")
        return False

    print(f"\n[Target Confirmed] Host: {host} | Database: {db_name}")
    print("Connecting to target database...")

    try:
        # Step 1: Verify connectivity, active database, and current tables
        with engine.connect() as conn:
            ver = conn.execute(text("SELECT VERSION()")).scalar()
            active_db = conn.execute(text("SELECT DATABASE()")).scalar()
            print(f"Connection verified! MySQL Version: {ver} | Active DB: {active_db}")

            # Inspect existing tables before creation
            raw_existing = conn.execute(text("SHOW TABLES")).scalars().all()
            existing_tables = set(raw_existing)
            print(f"Existing tables before creation: {list(existing_tables) if existing_tables else 'None'}")

        print("\nRegistered SQLAlchemy models to ensure:")
        for t in Base.metadata.sorted_tables:
            status = "(already exists)" if t.name in existing_tables else "(to be created)"
            print(f"  - {t.name} {status}")

        # Step 2: Execute DDL inside engine.begin() so connection and commit semantics are explicit
        print("\nExecuting table creation (checkfirst=True, existing tables are preserved)...")
        with engine.begin() as conn:
            Base.metadata.create_all(bind=conn, checkfirst=True)
        print("DDL execution completed.")

        # Step 3: Verify created tables on a fresh connection using direct SQL and Inspector
        print("\nVerifying database state...")
        with engine.connect() as verify_conn:
            active_db_post = verify_conn.execute(text("SELECT DATABASE()")).scalar()
            actual_tables_list = verify_conn.execute(text("SHOW TABLES")).scalars().all()
            post_tables = set(actual_tables_list)
            print(f"Database: {active_db_post} | Tables present: {list(post_tables)}")

            expected = {"users", "profiles", "assessments", "roadmaps", "topics", "progress", "quiz_results"}
            missing = expected - post_tables

            if not missing:
                print("\n[SUCCESS] All 7 application tables confirmed on Aiven MySQL:")
                for t in sorted(expected):
                    print(f"  [OK] {t}")
                return True
            else:
                print(f"\n[WARNING] Missing tables after creation: {missing}")
                return False

    except Exception as e:
        print(f"\nInitialization failed: [{type(e).__name__}] {e}")
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
