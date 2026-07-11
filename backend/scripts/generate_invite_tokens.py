import sys
import os
import argparse
import random
import string
from datetime import datetime, timedelta

# Adjust python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.invite_token import InviteToken

def generate_random_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def main():
    parser = argparse.ArgumentParser(description="Generate Fynlo Beta Invite Tokens")
    parser.add_argument("--email", type=str, help="Optional email address to restrict the token to")
    parser.add_argument("--days", type=int, help="Optional number of days before the token expires")
    parser.add_argument("--count", type=int, default=1, help="Number of tokens to generate")
    args = parser.parse_args()

    # Create session
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Connecting to database to generate {args.count} invite tokens...")

    try:
        for _ in range(args.count):
            token_str = f"FYNLO-BETA-{generate_random_code(6)}"
            
            expires_at = None
            if args.days:
                expires_at = datetime.utcnow() + timedelta(days=args.days)

            invite = InviteToken(
                token=token_str,
                email=args.email.lower() if args.email else None,
                expires_at=expires_at
            )
            session.add(invite)
            session.commit()

            print(f"Generated Token: {token_str}")
            if args.email:
                print(f"  Restricted to: {args.email}")
            if expires_at:
                print(f"  Expires on:    {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    except Exception as e:
        session.rollback()
        print(f"Error generating tokens: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
