from typing import Optional
import pkcs11
from celery import Celery, shared_task
from models import engine, insert_new_sn
from config import settings


celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BACKEND_URL)

lib = pkcs11.lib(settings.PKCS11_LIB_PATH)
token = lib.get_token(token_label=settings.TOKEN_LABEL)

USE_TOKEN = True
def _get_checksum(input_str: str, session: Optional[pkcs11.Session] = None) -> str:
    input_bytes = bytearray(input_str, 'ASCII')
    iv = self.keystore.get_sn_iv()

    if USE_TOKEN:
        input_bytes = bytes(input_bytes)
        iv = bytes(iv)

        secret_key = session.get_key(label=settings.TOKEN_KEY_LABEL)
        enc_data = secret_key.encrypt(data=input_bytes, mechanism=pkcs11.Mechanism.AES_CBC, mechanism_param=iv)
    else:
        cipher = AES.new(key=self.keystore.get_sn_key(), mode=AES.MODE_CBC, iv=iv)
        enc_data = cipher.encrypt(input_bytes)

    checksum = 0
    for i in range(8):
        checksum = checksum ^ int.from_bytes(enc_data[i * 2:i * 2 + 2], byteorder='little')

    return str(checksum).zfill(6)

def generate_sn(code_model: str, number: int, session: Optional[pkcs11.Session] = None) -> str:
    number = str(number).zfill(6)
    checksum = _get_checksum(f"{code_model}{number}000000", session=session)

    return f"{str(checksum).zfill(6)}{code_model}{number}"


@celery.task
def generate_sn_task(code_model: str, number: int, count: int) -> bool:
    with token.open(user_pin=settings.TOKEN_PASS, rw=True) as session:
        with engine.begin() as db_connection:
            serial_numbers = []
            for i in range(number, number + count):
                serial_numbers.append({
                    "code_model": code_model,
                    "sn_number": i,
                    "serial_number": generate_sn(code_model, i, session)
                })
                # i-number+1 - номер итерации
                if settings.GENERATING_PACKAGE_SIZE != 0 and (i-number+1) % settings.GENERATING_PACKAGE_SIZE == 0:
                    insert_new_sn(serial_numbers, db_connection)
                    serial_numbers.clear()

            if len(serial_numbers) > 0:
                insert_new_sn(serial_numbers, db_connection)

    return True
