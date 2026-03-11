import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://mpr.datamart.ams.usda.gov/services/v1.1/reports"

REPORTS = {
    "beef": "2452",
    "pork": "2498"
}

START_DATE = datetime(2020,1,1)
END_DATE = datetime.today()

records = []

def fetch_report(report_id, date):

    url = f"{BASE_URL}/{report_id}/Summary"

    params = {
        "q": f"report_date={date.strftime('%m/%d/%Y')}",
        "allSections": "true"
    }

    try:

        r = requests.get(url, params=params)
        data = r.json()

        if isinstance(data, dict):
            sections = data.get("reportSections", [])
        elif isinstance(data, list):
            sections = data
        else:
            return

        for section in sections:

            rows = section.get("reportRows", []) if isinstance(section, dict) else []

            for row in rows:

                if isinstance(row, dict):

                    name = row.get("label") or row.get("description")
                    price = row.get("value")

                elif isinstance(row, list):

                    if len(row) >= 2:
                        name = row[0]
                        price = row[-1]
                    else:
                        continue

                else:
                    continue

                try:
                    price = float(price)

                    records.append({
                        "date": date,
                        "cut_name": str(name),
                        "price": price
                    })

                except:
                    pass

    except Exception as e:
        print("Error:", date, e)

current = START_DATE

while current <= END_DATE:

    print("Downloading", current)

    for report in REPORTS.values():
        fetch_report(report, current)

    current += timedelta(days=1)

df = pd.DataFrame(records)

df = df.sort_values("date")

df.to_csv("data/beef_prices.csv", index=False)

print("Saved", len(df), "rows")
