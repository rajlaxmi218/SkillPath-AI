"""
Temporary diagnostic script to test Aiven MySQL connection.

Safeguards:
- Prompts for password securely at runtime via getpass (never saved, logged, or hardcoded).
- Handles Windows PowerShell terminal input errors and KeyboardInterrupt cleanly without falling back to a visible prompt.
- Uses SQLAlchemy URL.create() to safely encode special characters in credentials.
- Configures PyMySQL SSL using the provided ca.pem certificate.
- Sets connect_timeout: 10 inside PyMySQL connect_args.
- Only executes `SELECT VERSION()` to verify connectivity.
- Disposes of the SQLAlchemy engine in a finally block.
- Catches sqlalchemy.exc.OperationalError separately and extracts sanitized error codes/messages.
- Sanitizes all diagnostic outputs: removes hostnames, IP addresses, usernames, passwords, file paths, and URLs.
- Does not modify any databases, tables, records, or existing project files.
"""

import getpass
import os
import re
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError

HOST = "mysql-1a2f6f2d-aditiuplenchwar2076-35e2.d.aivencloud.com"
PORT = 15209
USERNAME = "avnadmin"
DATABASE = "defaultdb"
CA_CERT_PATH = r"D:\Projects\SKILLPATHAI\SKILLPATHAI\backend\ca.pem"


def sanitize_message(raw_msg: str, sensitive_strings: list) -> str:
    """Removes sensitive strings, URLs, IPs, and local paths from error messages."""
    sanitized = raw_msg
    for s in sensitive_strings:
        if s:
            sanitized = sanitized.replace(s, "[REDACTED]")

    # Redact potential URLs (e.g. mysql+pymysql://...)
    sanitized = re.sub(r"[a-zA-Z0-9_+.-]+://[^\s@]+@[^\s/]+/[^\s]*", "[REDACTED_URL]", sanitized)
    # Redact IPv4 addresses
    sanitized = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[REDACTED_IP]", sanitized)
    # Redact Windows / Unix file paths
    sanitized = re.sub(r"[A-Za-z]:\\[^:\n\r\t]+", "[REDACTED_PATH]", sanitized)
    sanitized = re.sub(r"/(?:[^/\s]+/)+[^/\s]+", "[REDACTED_PATH]", sanitized)

    return sanitized


def test_connection():
    if not os.path.exists(CA_CERT_PATH):
        print("Warning: CA certificate file not found at the specified path.")
        print("Please verify the ca.pem location.")
        return

    password = None
    try:
        password = getpass.getpass("Enter Aiven MySQL password for avnadmin (input is hidden): ")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return
    except (EOFError, getpass.GetPassWarning, OSError) as e:
        print(f"\nTerminal input error during secure password prompt: [{type(e).__name__}]")
        print("Please run the script in a standard interactive Windows console/terminal.")
        return
    except Exception as e:
        print(f"\nUnexpected input error: [{type(e).__name__}]. Exiting safely.")
        return

    if not password:
        print("Error: Password cannot be empty.")
        return

    sensitive_tokens = [password, HOST, USERNAME, DATABASE, str(PORT), CA_CERT_PATH]

    # Use URL.create to safely encode special characters in the password
    db_url = URL.create(
        drivername="mysql+pymysql",
        username=USERNAME,
        password=password,
        host=HOST,
        port=PORT,
        database=DATABASE,
    )

    connect_args = {
        "ssl": {
            "ca": CA_CERT_PATH
        },
        "connect_timeout": 10
    }

    engine = None
    print("\nAttempting secure SSL connection to Aiven MySQL...")
    try:
        engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True
        )

        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()")).scalar()
            print("Successfully connected to Aiven MySQL!")
            print(f"MySQL Server Version: {result}")

    except OperationalError as oe:
        print(f"Connection failed: [OperationalError]")
        
        # Extract underlying driver error details if present (e.g. PyMySQL Error Code)
        orig_err = getattr(oe, "orig", None)
        error_code = None
        if orig_err and hasattr(orig_err, "args") and len(orig_err.args) > 0:
            if isinstance(orig_err.args[0], int):
                error_code = orig_err.args[0]
            elif isinstance(orig_err.args[0], tuple) and len(orig_err.args[0]) > 0:
                error_code = orig_err.args[0][0]

        if error_code is not None:
            print(f"Underlying MySQL / Driver Error Code: {error_code}")
            
            # Common MySQL error codes explanation
            explanations = {
                1045: "Access denied (authentication failed). Please double check the username and password.",
                1049: "Unknown database name. Please verify the target database exists on Aiven.",
                2003: "Can't connect to MySQL server (host unreachable or connection timed out). Check firewall / network / port.",
                2005: "Unknown MySQL server host. The hostname could not be resolved via DNS.",
                2006: "MySQL server has gone away (connection dropped during handshake).",
                2013: "Lost connection to MySQL server during query / TLS handshake.",
                2026: "SSL connection error. Verify CA certificate validity or SSL settings."
            }
            if error_code in explanations:
                print(f"Diagnostic note: {explanations[error_code]}")

        # Sanitize exception message
        clean_msg = sanitize_message(str(oe), sensitive_tokens)
        # Keep only the primary error sentence for clarity
        summary_line = clean_msg.splitlines()[0] if clean_msg else "Unknown operational error"
        print(f"Sanitized detail: {summary_line}")

    except Exception as e:
        print(f"Connection failed: [{type(e).__name__}]")
        clean_msg = sanitize_message(str(e), sensitive_tokens)
        summary_line = clean_msg.splitlines()[0] if clean_msg else "Unknown error"
        print(f"Sanitized detail: {summary_line}")

    finally:
        # Securely dispose engine connection pool and purge password variable from memory
        if engine is not None:
            engine.dispose()
        if password is not None:
            del password


if __name__ == "__main__":
    test_connection()
