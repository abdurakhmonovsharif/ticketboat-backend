import traceback
from typing import List, Dict, Any
from app.database import get_pg_realtime_catalog_database
from app.model.shadows_config import ShadowsConfigCreate

async def get_all_configs() -> List[Dict[str, Any]]:
    """Get all shadows configs from database"""
    try:
        query = """
            SELECT id, exchange, override_type, override_value, config_type, config_value, 
                   created_at, updated_at
            FROM shadows_config
            ORDER BY exchange, override_type, config_type
        """
        db = get_pg_realtime_catalog_database()
        results = await db.fetch_all(query=query)
        return [
            {
                "id": row["id"],
                "exchange": row["exchange"],
                "override_type": row["override_type"],
                "override_value": row["override_value"],
                "config_type": row["config_type"],
                "config_value": float(row["config_value"]) if row["config_value"] is not None else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            }
            for row in results
        ]
    except Exception as e:
        traceback.print_exc()
        raise Exception("Error fetching shadows configs") from e

async def get_configs_by_exchange(exchange: str) -> List[Dict[str, Any]]:
    """Get all configs for a specific exchange"""
    try:
        query = """
            SELECT id, exchange, override_type, override_value, config_type, config_value,
                   created_at, updated_at
            FROM shadows_config
            WHERE exchange = :exchange
            ORDER BY override_type, config_type
        """
        db = get_pg_realtime_catalog_database()
        results = await db.fetch_all(query=query, values={"exchange": exchange})
        return [
            {
                "id": row["id"],
                "exchange": row["exchange"],
                "override_type": row["override_type"],
                "override_value": row["override_value"],
                "config_type": row["config_type"],
                "config_value": float(row["config_value"]) if row["config_value"] is not None else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            }
            for row in results
        ]
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error fetching configs for exchange {exchange}") from e

async def get_exchanges() -> List[Dict[str, str]]:
    """Get list of all unique exchanges"""
    try:
        query = """
            SELECT DISTINCT exchange
            FROM shadows_config
            ORDER BY exchange
        """
        db = get_pg_realtime_catalog_database()
        results = await db.fetch_all(query=query)
        return [{"name": row["exchange"]} for row in results]
    except Exception as e:
        traceback.print_exc()
        raise Exception("Error fetching exchanges") from e

async def create_config(config: ShadowsConfigCreate) -> Dict[str, Any]:
    """Create a new config"""
    try:
        query = """
            INSERT INTO shadows_config (exchange, override_type, override_value, config_type, config_value)
            VALUES (:exchange, :override_type, :override_value, :config_type, :config_value)
            RETURNING id, exchange, override_type, override_value, config_type, config_value, 
                      created_at, updated_at
        """
        db = get_pg_realtime_catalog_database()
        result = await db.fetch_one(
            query=query,
            values={
                "exchange": config.exchange,
                "override_type": config.override_type,
                "override_value": config.override_value,
                "config_type": config.config_type,
                "config_value": config.config_value,
            },
        )
        return {
            "id": result["id"],
            "exchange": result["exchange"],
            "override_type": result["override_type"],
            "override_value": result["override_value"],
            "config_type": result["config_type"],
            "config_value": float(result["config_value"]) if result["config_value"] is not None else None,
            "created_at": result["created_at"].isoformat() if result["created_at"] else None,
            "updated_at": result["updated_at"].isoformat() if result["updated_at"] else None,
        }
    except Exception as e:
        traceback.print_exc()
        raise Exception("Error creating config") from e

async def update_config(config_id: int, config_value: float) -> Dict[str, Any]:
    """Update a config's value"""
    try:
        query = """
            UPDATE shadows_config
            SET config_value = :config_value, updated_at = NOW()
            WHERE id = :id
            RETURNING id, exchange, override_type, override_value, config_type, config_value,
                      created_at, updated_at
        """
        db = get_pg_realtime_catalog_database()
        result = await db.fetch_one(query=query, values={"config_value": config_value, "id": config_id})
        if not result:
            raise Exception(f"Config with id {config_id} not found")
        return {
            "id": result["id"],
            "exchange": result["exchange"],
            "override_type": result["override_type"],
            "override_value": result["override_value"],
            "config_type": result["config_type"],
            "config_value": float(result["config_value"]) if result["config_value"] is not None else None,
            "created_at": result["created_at"].isoformat() if result["created_at"] else None,
            "updated_at": result["updated_at"].isoformat() if result["updated_at"] else None,
        }
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error updating config {config_id}") from e

async def delete_config(config_id: int) -> None:
    """Delete a config"""
    try:
        query = "DELETE FROM shadows_config WHERE id = :id"
        db = get_pg_realtime_catalog_database()
        await db.execute(query=query, values={"id": config_id})
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error deleting config {config_id}") from e

async def delete_exchange(exchange: str) -> None:
    """Delete an exchange and all its configs"""
    try:
        query = "DELETE FROM shadows_config WHERE exchange = :exchange"
        db = get_pg_realtime_catalog_database()
        await db.execute(query=query, values={"exchange": exchange})
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error deleting exchange {exchange}") from e

