import json
from typing import List, Optional, Tuple

class NoAVL:
    def __init__(self, nome_jogador: str, pontuacao_recorde: int):
        self.nome_jogador = nome_jogador
        self.pontuacao_recorde = pontuacao_recorde
        self.altura = 1
        self.esquerda = None
        self.direita = None
        self.historico_avls = []
        self.contador_mortes = 0
        self.record_eventos = 0
        self.chefes_derrotados = 0
        self.total_avls = 0

class ArvoreAVL:
    def __init__(self):
        self.raiz = None
    
    def obter_altura(self, no: NoAVL) -> int:
        return no.altura if no else 0

    def atualizar_altura(self, no: NoAVL):
        no.altura = 1 + max(self.obter_altura(no.esquerda), self.obter_altura(no.direita))

    def obter_balanceamento(self, no: NoAVL) -> int:
        return self.obter_altura(no.esquerda) - self.obter_altura(no.direita) if no else 0

    def rotacionar_direita(self, y: NoAVL) -> NoAVL:
        x = y.esquerda
        T2 = x.direita
        
        x.direita = y
        y.esquerda = T2
        
        self.atualizar_altura(y)
        self.atualizar_altura(x)
        
        return x

    def rotacionar_esquerda(self, x: NoAVL) -> NoAVL:
        y = x.direita
        T2 = y.esquerda
        
        y.esquerda = x
        x.direita = T2
        
        self.atualizar_altura(x)
        self.atualizar_altura(y)
        
        return y

    def inserir(self, nome_jogador: str, pontuacao: int):
        self.raiz = self._inserir_recursivo(self.raiz, nome_jogador, pontuacao)

    def _inserir_recursivo(self, no: NoAVL, nome_jogador: str, pontuacao: int) -> NoAVL:
        if not no:
            novo_no = NoAVL(nome_jogador, pontuacao)
            novo_no.historico_avls.append(pontuacao)
            novo_no.total_avls = 1
            return novo_no
        
        if nome_jogador < no.nome_jogador:
            no.esquerda = self._inserir_recursivo(no.esquerda, nome_jogador, pontuacao)
        elif nome_jogador > no.nome_jogador:
            no.direita = self._inserir_recursivo(no.direita, nome_jogador, pontuacao)
        else:
            # Jogador já existe, atualiza recorde se necessário
            if pontuacao > no.pontuacao_recorde:
                no.pontuacao_recorde = pontuacao
            no.historico_avls.append(pontuacao)
            no.total_avls = len(no.historico_avls)
            return no
        
        self.atualizar_altura(no)
        balanceamento = self.obter_balanceamento(no)
        
        if balanceamento > 1 and nome_jogador < no.esquerda.nome_jogador:
            return self.rotacionar_direita(no)
        if balanceamento < -1 and nome_jogador > no.direita.nome_jogador:
            return self.rotacionar_esquerda(no)
        if balanceamento > 1 and nome_jogador > no.esquerda.nome_jogador:
            no.esquerda = self.rotacionar_esquerda(no.esquerda)
            return self.rotacionar_direita(no)
        if balanceamento < -1 and nome_jogador < no.direita.nome_jogador:
            no.direita = self.rotacionar_direita(no.direita)
            return self.rotacionar_esquerda(no)
        
        return no

    def buscar(self, nome_jogador: str) -> Optional[NoAVL]:
        return self._buscar_recursivo(self.raiz, nome_jogador)
    
    def _buscar_recursivo(self, no: NoAVL, nome_jogador: str) -> Optional[NoAVL]:
        if not no or no.nome_jogador == nome_jogador:
            return no
        
        if nome_jogador < no.nome_jogador:
            return self._buscar_recursivo(no.esquerda, nome_jogador)
        return self._buscar_recursivo(no.direita, nome_jogador)

    def top_n_pontuacoes(self, n: int) -> List[Tuple[str, int, int, int, int]]:
        resultados = []
        self._obter_top_n_recursivo(self.raiz, n, resultados)
        return resultados
    
    def _obter_top_n_recursivo(self, no: NoAVL, n: int, resultados: List[Tuple[str, int, int, int, int]]):
        """Percorre a árvore em ordem decrescente (direita-raiz-esquerda)"""
        if no and len(resultados) < n:
            # Primeiro vai para a direita (maiores valores)
            self._obter_top_n_recursivo(no.direita, n, resultados)
            
            if len(resultados) < n:
                # Adiciona o nó atual
                resultados.append((
                    no.nome_jogador, 
                    no.pontuacao_recorde,
                    no.record_eventos,
                    no.chefes_derrotados,
                    no.total_avls
                ))
                # Depois vai para a esquerda
                self._obter_top_n_recursivo(no.esquerda, n, resultados)

    def contar_jogadores(self) -> int:
        return self._contar_recursivo(self.raiz)
    
    def _contar_recursivo(self, no: NoAVL) -> int:
        if not no:
            return 0
        return 1 + self._contar_recursivo(no.esquerda) + self._contar_recursivo(no.direita)

    def imprimir_arvore(self, nivel: int = 0, prefixo: str = "", no: NoAVL = None):
        if no is None:
            no = self.raiz
            if no is None:
                print("Árvore vazia")
                return
        
        if no.direita:
            self.imprimir_arvore(nivel + 1, "┌── ", no.direita)
        
        print(" " * (nivel * 4) + prefixo + f"{no.nome_jogador} ({no.pontuacao_recorde})")
        
        if no.esquerda:
            self.imprimir_arvore(nivel + 1, "└── ", no.esquerda)

    def salvar_para_json(self, arquivo: str):
        dados = self._serializar_recursivo(self.raiz)
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def _serializar_recursivo(self, no: NoAVL) -> dict:
        if not no:
            return None
        
        return {
            "nome_jogador": no.nome_jogador,
            "pontuacao_recorde": no.pontuacao_recorde,
            "altura": no.altura,
            "historico_avls": no.historico_avls,
            "contador_mortes": no.contador_mortes,
            "record_eventos": no.record_eventos,
            "chefes_derrotados": no.chefes_derrotados,
            "total_avls": no.total_avls,
            "esquerda": self._serializar_recursivo(no.esquerda),
            "direita": self._serializar_recursivo(no.direita)
        }

    def carregar_de_json(self, arquivo: str):
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        self.raiz = self._deserializar_recursivo(dados)
    
    def _deserializar_recursivo(self, dados: dict) -> NoAVL:
        if not dados:
            return None
        
        no = NoAVL(dados["nome_jogador"], dados["pontuacao_recorde"])
        no.altura = dados["altura"]
        no.historico_avls = dados["historico_avls"]
        no.contador_mortes = dados["contador_mortes"]
        no.record_eventos = dados["record_eventos"]
        no.chefes_derrotados = dados["chefes_derrotados"]
        no.total_avls = dados["total_avls"]
        no.esquerda = self._deserializar_recursivo(dados["esquerda"])
        no.direita = self._deserializar_recursivo(dados["direita"])
        
        return no
