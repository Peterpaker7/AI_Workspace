how_much_need=int(input("Enter the amount : ₹"))
bank_balance=500
if bank_balance>=how_much_need:
    print("Here's your money!!!  ₹",how_much_need)
    print("Here's your bank balance ₹",bank_balance-how_much_need)
elif bank_balance<how_much_need:
    print("Insuffient balance")


     