import asyncio
import uuid
import sys
import os

# Add src to sys.path to import app modules
sys.path.append(os.path.abspath("src"))

from app.db import ams_db
from app.model.ams_models import RebuildAccountRequestItem
from app.database import init_pg_database, close_pg_database, get_pg_database

async def verify_rebuild():
    print("Testing rebuild_accounts logic...")
    await init_pg_database()
    db = get_pg_database()
    
    try:
        # 1. Setup mock data
        # We need a company, a person, an address, an email, a phone, etc.
        # For simplicity, we'll try to use existing IDs if possible, or create temp ones.
        
        # Let's find an existing account to "rebuild"
        old_account = await db.fetch_one("SELECT id, nickname, notes FROM ams.ams_account LIMIT 1")
        if not old_account:
            print("No accounts found in DB to test rebuild.")
            return

        print(f"Old account: {old_account['nickname']} ({old_account['id']})")

        # Get some other IDs to link
        person = await db.fetch_one("SELECT id FROM ams.ams_person LIMIT 1")
        address = await db.fetch_one("SELECT id FROM ams.ams_address LIMIT 1")
        company = await db.fetch_one("SELECT id FROM ams.company LIMIT 1")
        email = await db.fetch_one("SELECT id FROM ams.ams_email WHERE status = 'AVAILABLE' LIMIT 1")
        phone = await db.fetch_one("SELECT id FROM ams.phone_number WHERE status = 'Active' LIMIT 1")
        
        if not all([person, address, company, email, phone]):
            print("Missing related entities in DB to fully test rebuild mapping.")
            # We can still proceed if some are missing, but linking will be limited
        
        new_nickname = f"TEST_{uuid.uuid4().hex[:6]}"
        
        request_item = RebuildAccountRequestItem(
            old_account_id=str(old_account['id']),
            new_nickname=new_nickname,
            company_id=str(company['id']) if company else None,
            ams_person_id=str(person['id']) if person else None,
            ams_address_id=str(address['id']) if address else None,
            phone_number_id=str(phone['id']) if phone else None,
            email_id=str(email['id']) if email else None,
            tags=[]
        )

        # 2. Execute rebuild
        print(f"Rebuilding to {new_nickname}...")
        results = await ams_db.rebuild_accounts([request_item])
        print(f"Rebuild result: {results}")

        # 3. Verify
        new_acc_id = results[0]['id']
        new_acc = await db.fetch_one("SELECT * FROM ams.ams_account WHERE id = :id", {"id": new_acc_id})
        print(f"New account notes: {new_acc['notes']}")
        
        updated_old_acc = await db.fetch_one("SELECT notes FROM ams.ams_account WHERE id = :id", {"id": old_account['id']})
        print(f"Updated old account notes: {updated_old_acc['notes']}")

        if rebuilt_note := f"rebuilt on \"{new_nickname}\"" in updated_old_acc['notes']:
            print("SUCCESS: Old account notes updated correctly.")
        else:
            print("FAILURE: Old account notes not updated correctly.")

        if f"from \"{old_account['nickname']}\"" in new_acc['notes']:
            print("SUCCESS: New account notes set correctly.")
        else:
            print("FAILURE: New account notes not set correctly.")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        await close_pg_database()

if __name__ == "__main__":
    asyncio.run(verify_rebuild())
