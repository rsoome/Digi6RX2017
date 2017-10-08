# A token for indicating whether a thread should cancel it's job or not.
class CancellationToken:
    def __init__(self):
        self.isCanceled = False

    def cancel(self):
        self.isCanceled = True
