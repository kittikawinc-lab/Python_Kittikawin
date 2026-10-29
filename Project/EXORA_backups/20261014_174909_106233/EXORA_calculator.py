# คำอธิบาย def calculator: คำนวณยอดแลกเงินตามราคาที่รับเข้าในโมดูลคำนวณรุ่นเดิม
# รับค่า: transaction_type, from_currency, to_currency, amount, from_rate, to_rate
def calculator(transaction_type,from_currency,to_currency,amount,from_rate,to_rate):
    amount = float(amount)
    if amount <= 0 :
        raise ValueError("จำนวนเงินจำเป็นต้องมากกว่า 0")
    if from_currency == to_currency :
        return amount, 1.0
    if transaction_type == "BUY":
        if from_currency == "THB":
            result = amount / to_rate
            rate = to_rate
            return result, rate
        elif to_currency == "THB":
            result = amount * from_rate
            rate = from_rate
            return result, rate 
        else:    
            thb_amount = amount * from_rate
            result = thb_amount / to_rate
            rate = from_rate / to_rate
            return result, rate
    elif transaction_type == "SELL":
        if to_currency == "THB":
            result = amount * from_rate
            rate = from_rate
            return result, rate
        elif from_currency == "THB":
            result = amount / to_rate
            rate = to_rate
            return result, rate
        else:
            thb_amount = amount * from_rate
            result = thb_amount / to_rate
            rate = from_rate / to_rate
            return result, rate
    else:
        raise ValueError("ประเภทการทำรายการไม่ถูกต้อง")

