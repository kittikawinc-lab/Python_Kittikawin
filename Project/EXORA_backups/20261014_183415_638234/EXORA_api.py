# คำอธิบาย import: นำเข้า urllib.request: urllib.request — ส่งคำขอ HTTP ไปยังบริการอัตราแลกเปลี่ยน
import urllib.request
# คำอธิบาย import: นำเข้า json: json — แปลงข้อมูล JSON ที่รับจาก API
import json


API = "https://api.frankfurter.dev/v2/rates"


# คำอธิบาย def getexr: ขออัตราอ้างอิงจาก Frankfurter และคืนผลสำเร็จ/ข้อผิดพลาดพร้อมข้อมูลราคา
# รับค่า: base, currencies
def getexr(base="THB", currencies=None):

    if currencies is None:
        currencies = [
            "USD",
            "EUR",
            "GBP",
            "JPY",
            "CNY",
            "KRW",
            "SGD",
            "AUD",
            "CAD"
        ]

    quotes = ",".join(currencies)

    url = f"{API}?base={base}&quotes={quotes}"

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "EXORA-CurrencyExchange/1.0"
            }
        )

        with urllib.request.urlopen(request, timeout=10) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        rates = {}
        dates = {}

        if isinstance(data, list):

            for item in data:

                quote = item.get("quote")
                rate = item.get("rate")

                if item.get('base') != base or quote in rates:
                    raise ValueError('Unexpected exchange-rate response')

                if quote and rate is not None:

                    rates[quote] = float(rate)
                    dates[quote] = item.get('date')

        return {
            "success": True,
            "base": base,
            "rates": rates,
            "dates": dates,
            "date": data[0].get("date") if data else None
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "base": base,
            "rates": {}
        }


# คำอธิบาย def get_exchange_rates: เรียก getexr ผ่านชื่อฟังก์ชันที่รองรับโค้ดเดิม
# รับค่า: base, currencies
def get_exchange_rates(base="THB", currencies=None):

    return getexr(
        base=base,
        currencies=currencies
    )
