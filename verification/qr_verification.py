import argon2

class QrVerification():

    def __init__(self,SERVER_SECRET):
        self.SERVER_SECRET = SERVER_SECRET
        self.hasher =  argon2.PasswordHasher(hash_len=4,salt_len=8,time_cost=1)

    def create_qr_string(self,private_id):
        qr_string =  f"{private_id}{self.SERVER_SECRET}".encode('utf-8')
        hashed_qr = self.hasher.hash(qr_string)
        sorted_qr = hashed_qr.split(",")
        return sorted_qr[2]
     
    def verify_qr_string(self,private_id,qr_string):
        user_qr =  f"{private_id}{self.SERVER_SECRET}".encode('utf-8')
        try:
            full_qr = f"$argon2id$v=19$m=65536,t=1,{qr_string}"
            self.hasher.verify(full_qr, user_qr)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False

# qrc = QrVerification("yahboom")

# qr_string = qrc.create_qr_string("1911081023")
# print(qr_string)
# is_ok = qrc.verify_qr_string("1911081023",qr_string)
# print("is ok :",is_ok)