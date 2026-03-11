import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://mpr.datamart.ams.usda.gov/services/v1.1/reports"

BEEF_REPORT = "2452"
PORK_REPORT = "2498"

START_DATE = datetime(2020, 1, 1)
END_DATE = datetime.today()

records = []

def fetch_report(report_id, date):
    url = f"{BASE_URL}/{report_id}/Summary"
    params = {
        "q": f"report_date={date.strftime('%m/%d/%Y')}",
        "allSections": "true"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        for section in data:
            rows = section.get("reportRows", [])

            for row in rows:
                if isinstance(row, list) and len(row) >= 2:
                    name = str(row[0])
                    price = row[-1]

                    try:
                        price = float(price)
                        records.append({
                            "date": date,
                            "cut_name": name,
                            "price": price
                        })
                    except:
                        pass

    except Exception as e:
        print("Error:", date, e)


current = START_DATE

while current <= END_DATE:
    print("Downloading", current)

    fetch_report(BEEF_REPORT, current)
    fetch_report(PORK_REPORT, current)

    current += timedelta(days=1)

df = pd.DataFrame(records)

df.to_csv("data/beef_prices.csv", index=False)

print("Saved", len(df), "rows")
