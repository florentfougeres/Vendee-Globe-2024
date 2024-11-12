

from datetime import datetime, timedelta

update_hours = ["020000", "060000", "100000", "140000", "180000", "220000"]

# Le vrai départ est le 10/11/2024 mais les pointages le premier jour ne sont pas réguliers on va les gérer à part
start_date = datetime(2024, 11, 11)

hours_exception = ["1304000"]

def liste_dates():
    """
    Génère une liste de toutes les dates entre la date actuelle et la date du départ, au format AAAAMMJJ.
    """
    delta = (start_date - datetime.now()).days
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y%m%d') for i in range(delta + 1)]
    return dates