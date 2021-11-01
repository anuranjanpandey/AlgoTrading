import hashlib

class hash:
    def __init__(self):
        pass

    def make_hashes(self, password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def check_hashes(self, password, hashed_text):
        if self.make_hashes(password) == hashed_text:
            return hashed_text
        return False