import base64
from pathlib import Path
import os
import uuid

APPDATA_DIR = Path(os.environ['APPDATA']) / 'PrintPOS'
LICENSE_PATH = APPDATA_DIR / 'printpos.lic'

MOBO_UUID = str(uuid.UUID(int=uuid.getnode()))
INSTANCE_NAME = MOBO_UUID.split('-')[-1]
FERNET_KEY = base64.urlsafe_b64encode(bytes(MOBO_UUID, 'utf-8')[-32:])
