from datetime import datetime, timedelta

update_hours = ["020000", "060000", "100000", "140000", "180000", "220000"]

# Le vrai départ est le 10/11/2024 mais les pointages le premier jour ne sont pas réguliers on va les gérer à part
start_date = datetime(2024, 11, 11)

hours_exception = ["1304000"]

def list_of_dates_between_today_and_departure():
    """
    Génère une liste de toutes les dates entre la date actuelle et la date du départ, au format AAAAMMJJ.
    """
    delta = (start_date - datetime.now()).days
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y%m%d') for i in range(delta + 1)]
    return dates

def get_last_update():
    """Renvoie l'heure du dernier pointage la plus proche de l'heure actuelle.
    En prenant en compte le décallage de 1h. 
    Exemple le pointage de 14h n'est publiée qu'a 15h.
    """
    current_time = datetime.now().strftime("%H%M%S")

    current_time = (datetime.strptime(current_time, "%H%M%S") - timedelta(hours=1)).strftime("%H%M%S")

    for i in range(len(update_hours)-1, -1, -1):
        if current_time >= update_hours[i]:
            return update_hours[i]
    
    return update_hours[-1]

def get_current_date():
    return datetime.now().strftime("%Y%m%d")