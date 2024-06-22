import sql


user = input()
psswd = input()

try:
    out = sql.respaldar_db(user, psswd)
    print('Operación terminada', f'{out[-5:]}')
except (AttributeError, sql.Error) as e:
    print('Fallo en operación', str(e))
