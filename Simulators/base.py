import json

class MockBase:
    
    def __init__(self) -> None:
        with open('..Tests.Data.rabbitMessages.json') as j:
            self.data = json.load(j)