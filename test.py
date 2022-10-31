from json import load

from cryptography.fernet import Fernet


def get_logpas() -> tuple[str, str]:
    fernet = Fernet(b'oRZIsmCF4_Zy0ThR4gk-tRG-AAZR7knaBAqeI85dYdo=')
    with open(r'.\config.json', 'r', encoding='utf-8') as store:
        json = load(store)
        return fernet.decrypt(json['credentials']['login'].encode()).decode(), \
               fernet.decrypt(json['credentials']['password'].encode()).decode()
