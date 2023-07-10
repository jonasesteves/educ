
class RefusedPaymentError(Exception):
    message = 'Desculpe. Seu pagamento não foi aprovado.'

    def __int__(self, message=None):
        if message is None:
            self.message = message
        super().__init__(self.message)
