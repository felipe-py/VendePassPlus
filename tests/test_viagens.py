import unittest

from app.models.viagem.GerenciadorViagem import GerenciadorViagens

class TestViagem(unittest.TestCase):
    
    def setUp(self) -> None:
        return super().setUp()
    
    def aumentarAssentos(self):
        data = GerenciadorViagens.ler_json()
        GerenciadorViagens.diminuir_assentos("1")

if __name__ == "__main__":
    unittest.main()