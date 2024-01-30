from datetime import timedelta, datetime
current_date = datetime.today()
current_date += timedelta(days=100)
current_date.strftime("%Y-%m-%d")
print(current_date)