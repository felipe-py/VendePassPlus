import unittest

from models.cliente.Cliente import Cliente

class TestCliente(unittest.TestCase):

    def setUp(self):
        # Esse método é executado antes de cada teste. Aqui você pode preparar os dados.
        
        self.cliente = Cliente(1,22)

    def test_login_sucesso(self):
        # Testa o login com credenciais corretas
        clientes_registrados = Cliente.carregar_clientes()
        self.assertTrue(Cliente.login(1,22,clientes_registrados))

    def test_login_falha_id_incorreto(self):
        # Testa o login com o id incorreto
        clientes_registrados = Cliente.carregar_clientes()
        self.assertFalse(Cliente.login(3,22,clientes_registrados))

    def test_login_falha_senha_incorreta(self):
        # Testa o login com a senha incorreta
        clientes_registrados = Cliente.carregar_clientes()
        self.assertFalse(Cliente.login(1,44,clientes_registrados))

if __name__ == "__main__":
    unittest.main()
