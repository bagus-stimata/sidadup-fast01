# repository/raw/farea_agg.py

from sqlalchemy import text

def count_active_area_per_division(db):
    """
    Contoh query raw aggregate:
    Hitung total FArea aktif group by fdivisionBean.
    """
    sql = """
        SELECT fdivisionBean, COUNT(*) as total_active
        FROM farea
        WHERE statusActive = 1
        GROUP BY fdivisionBean
    """
    result = db.execute(text(sql))
    rows = result.fetchall()
    return [{"fdivisionBean": row[0], "total_active": row[1]} for row in rows]