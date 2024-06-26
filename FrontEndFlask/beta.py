import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("Conexión a Redis exitosa")
    r.set('test_key', 'test_value')
    print("Prueba de escritura en Redis exitosa")
    value = r.get('test_key')
    print(f"Prueba de lectura en Redis exitosa, valor: {value}")
except redis.ConnectionError as e:
    print(f"Error al conectar con Redis: {e}")
