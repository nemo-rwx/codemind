import os


class PaymentService:
    def process_payment(self, amount):
        print(amount)
        return os.path.exists("payment.txt")
