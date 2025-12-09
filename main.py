import random
import json
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ===== ENUMS E ESTRUTURAS =====

class Raridade(Enum):
    COMUM = 1
    INCOMUM = 2
    RARO = 3
    CHEFE = 4

class Condicao(Enum):
    NENHUMA = 0
    VENENO = 1
    FRENESI = 2
    QUEIMADURA = 3
    MEDO = 4
    FOGO = 5
    ELETRICO = 6
    ATORDOADO = 7

class TipoEvento(Enum):
    INIMIGO_COMUM = 1
    EVENTO_COMUM = 2
    MINI_CHEFE = 3
    FOGUEIRA = 4
    EVENTO_RARO = 5
    CHEFE = 6

# ===== CLASSES PRINCIPAIS =====

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

class Arma:
    def __init__(self, nome: str, dano: int, custo_stamina: int, tipo: str = "corpo_a_corpo", chance_atordoar: float = 0.0, balas: int = 0, balas_maximas: int = 20):
        self.nome = nome
        self.dano = dano
        self.custo_stamina = custo_stamina
        self.tipo = tipo 
        self.chance_atordoar = chance_atordoar
        self.balas = balas
        self.balas_maximas = balas_maximas
        self.dano_base = dano
        self.limites_melhorias = {
            "Fragmento de Ferro": 3,
            "Pedaco de Ferro": 3,
            "Lajota de Ferro": 3
        }
        self.melhorias_aplicadas = {
            "Fragmento de Ferro": 0,
            "Pedaco de Ferro": 0,
            "Lajota de Ferro": 0
        }

class Item:
    def __init__(self, nome: str, tipo: str, efeito: str, valor: int):
        self.nome = nome
        self.tipo = tipo
        self.efeito = efeito
        self.valor = valor

class Inimigo:
    def __init__(self, nome: str, vida: int, dano: int, raridade: Raridade, recompensa_almas: int, 
                 padrao_ataque: List[str] = None, condicoes: List[Condicao] = None):
        self.nome = nome
        self.vida = vida
        self.dano = dano
        self.raridade = raridade
        self.recompensa_almas = recompensa_almas
        self.padrao_ataque = padrao_ataque or ["ataque", "ataque", "ataque_pesado"]
        self.indice_padrao_atual = 0
        self.condicoes = condicoes or []
        self.vida_maxima = vida
        self.eh_chefe = (raridade == Raridade.CHEFE)
        self._vida_inicial = vida
        self.turnos_atordoado = 0
        self.chance_atordoar_jogador = 0.05

class Jogador:
    def __init__(self, nome: str):
        self.nome = nome
        self.vida_maxima = 100
        self.vida = 100
        self.dano_base = 10
        self.dano = 10
        self.defesa = 5
        self.pocoes_cura = 5
        self.pocoes_cura_maximas = 5
        self.stamina_maxima = 100
        self.stamina = 100
        self.almas = 0
        self.nivel = 1
        self.pontuacao_avl_atual = 0
        self.sanidade = 0
        self.condicoes = []
        self.arma_mao_direita = Arma("Bastão Enferrujado", 5, 10)
        self.arma_mao_esquerda = Arma("Pistola", 2, 1, "distancia", 0.30, 20, 20) 
        self.arma_atual = self.arma_mao_direita  
        self.contador_melhorias = 0
        self.fogueiras_encontradas = 0
        self.defesa_temporaria = 0
        self.esquivar_proximo_ataque = False
        self.inventario = []
        self.armas_encontradas = ["Bastão Enferrujado", "Pistola"]
        self.chance_atordoar_base = 0.05
        self.chance_atordoar_acumulada = 0.05
        self.amuleto_antigo = False 
        self.turnos_atordoado = 0
        self.contador_ataques = 0
        self.anel_clorantio = False
        self.anel_favor = False
        self.lenco_dourado = False
        self.conhecimento_louco = False
        self.segredo_bandido = False
        self.requiem = False
        self.ressuscitou = False
        self.turnos_extras = 0
        self.record_eventos_atual = 0
        self.chefes_derrotados_atual = 0
        self.ferros_guardados = {
            "Fragmento de Ferro": 0,
            "Pedaco de Ferro": 0,
            "Lajota de Ferro": 0
        }
        
    def receber_dano(self, dano: int) -> int:
        if self.esquivar_proximo_ataque:
            self.esquivar_proximo_ataque = False
            return 0
            
        defesa_total = self.defesa + self.defesa_temporaria
        dano_real = max(1, dano - defesa_total)
        self.vida -= dano_real
        return dano_real
    
    def obter_dano_total(self):
        if self.arma_atual.tipo == "corpo_a_corpo":
            return max(1, self.dano + self.arma_atual.dano)
        else:
            return max(1, self.arma_atual.dano)

    def curar(self) -> bool:
        if self.pocoes_cura > 0 and self.vida < self.vida_maxima:
            quantidade_cura = min(40, self.vida_maxima - self.vida)
            self.vida += quantidade_cura
            self.pocoes_cura -= 1
            return True
        return False
    
    def restaurar_stamina(self, quantidade: int):
        self.stamina = min(self.stamina_maxima, self.stamina + quantidade)
    
    def adicionar_sanidade(self, quantidade: int):
        self.sanidade = max(0, min(100, self.sanidade + quantidade))
    
    def adicionar_arma(self, nome_arma: str):
        if nome_arma not in self.armas_encontradas:
            self.armas_encontradas.append(nome_arma)
            print(f"✅ Nova arma desbloqueada: {nome_arma}!")

    def adicionar_condicao(self, condicao: Condicao):
        if condicao not in self.condicoes:
            self.condicoes.append(condicao)
            if condicao == Condicao.MEDO:
                self.dano = max(1, self.dano_base - 3)
                print("😨 Medo reduz seu dano!")
            elif condicao == Condicao.FRENESI:
                print("💥 FRENESI! Seu dano dobra, mas você perde vida a cada turno!")
                self.dano = self.dano_base * 2
    
    def adicionar_almas(self, quantidade: int):
        self.almas += quantidade
        self.pontuacao_avl_atual += quantidade
    
    def resetar_almas_ao_morrer(self):
        almas_perdidas = self.almas
        self.almas = 0
        return almas_perdidas
    
    def remover_condicao(self, condicao: Condicao):
        if condicao in self.condicoes:
            self.condicoes.remove(condicao)
            if condicao == Condicao.MEDO:
                self.dano = self.dano_base
                print("😌 Medo dissipado! Dano restaurado.")
            elif condicao == Condicao.FRENESI:
                self.dano = self.dano_base
                print("💫 Frenesi passa! Dano volta ao normal.")
    
    def adicionar_ao_inventario(self, item: Item):
        if item.tipo == "arma":
            self.inventario.append(item)
            if item.nome not in self.armas_encontradas:
                self.armas_encontradas.append(item.nome)

    def curar_condicoes_na_fogueira(self):
        condicoes_removidas = len(self.condicoes)
        self.condicoes.clear()
        self.dano = self.dano_base 
        self.turnos_atordoado = 0
        if condicoes_removidas > 0:
            print(f"✨ {condicoes_removidas} condições foram curadas!")        
    
    def processar_condicoes(self):
        dano_recebido = 0
        for condicao in self.condicoes[:]:
            if condicao == Condicao.VENENO:
                dano_recebido += 5
                print("💀 Você sofre 5 de dano por veneno!")
            elif condicao == Condicao.QUEIMADURA:
                dano_recebido += 3
                print("🔥 Você sofre 3 de dano por queimadura!")
            elif condicao == Condicao.FRENESI:
                dano_frenesi = int(self.vida_maxima * 0.1)
                if self.vida > 1:
                    dano_recebido += min(dano_frenesi, self.vida - 1)
                    print(f"💥 Frenesi causa {min(dano_frenesi, self.vida - 1)} de dano!")
        
        if dano_recebido > 0:
            self.vida -= dano_recebido
        
        condicoes_temporarias = [Condicao.VENENO, Condicao.QUEIMADURA]
        self.condicoes = [c for c in self.condicoes if c not in condicoes_temporarias]
        
        self.defesa_temporaria = 0

    def aumentar_chance_atordoar(self):
        self.contador_ataques += 1
        self.chance_atordoar_acumulada = min(0.5, 0.05 + (self.contador_ataques * 0.002))
        return self.chance_atordoar_acumulada

    def resetar_chance_atordoar(self):
        self.contador_ataques = 0
        self.chance_atordoar_acumulada = 0.05

    def tem_arma_equipada(self, tipo: str = "ambas") -> bool:
        if tipo == "direita":
            return self.arma_mao_direita is not None
        elif tipo == "esquerda":
            return self.arma_mao_esquerda is not None
        else:
            return self.arma_mao_direita is not None or self.arma_mao_esquerda is not None

    def mostrar_status(self):
        print(f"\n📊 STATUS DE {self.nome}")
        print("=" * 40)
        print(f"❤️ Vida: {self.vida}/{self.vida_maxima}")
        print(f"⚡ Stamina: {self.stamina}/{self.stamina_maxima}")
        print(f"🗡️ Dano Base: {self.dano_base}")
        print(f"🛡️ Defesa: {self.defesa}")
        print(f"🧪 Poções: {self.pocoes_cura}/{self.pocoes_cura_maximas}")
        print(f"💎 Almas: {self.almas}")
        print(f"😶 Sanidade: {self.sanidade}")
        
        chance_atordoar_total = self.chance_atordoar_base
        if self.arma_atual:
            chance_atordoar_total += self.arma_atual.chance_atordoar
        print(f"🎯 Chance Atordoar: {chance_atordoar_total*100:.1f}%")
        
        if self.arma_mao_direita:
            chance_atordoar_direita = self.chance_atordoar_base + self.arma_mao_direita.chance_atordoar
            print(f"⚔️ Arma Direita: {self.arma_mao_direita.nome} (Dano: +{self.arma_mao_direita.dano}, Atordoar: {chance_atordoar_direita*100:.1f}%)")
        if self.arma_mao_esquerda:
            chance_atordoar_esquerda = self.chance_atordoar_base + self.arma_mao_esquerda.chance_atordoar
            print(f"🔫 Arma Esquerda: {self.arma_mao_esquerda.nome} (Dano: +{self.arma_mao_esquerda.dano}, Balas: {self.arma_mao_esquerda.balas}/{self.arma_mao_esquerda.balas_maximas}, Atordoar: {chance_atordoar_esquerda*100:.1f}%)")
        
        itens_especiais = []
        if self.amuleto_antigo: itens_especiais.append("Amuleto Antigo")
        if self.anel_clorantio: itens_especiais.append("Anel Clorantio")
        if self.anel_favor: itens_especiais.append("Anel do Favor")
        if self.lenco_dourado: itens_especiais.append("Lenço Dourado")
        if self.conhecimento_louco: itens_especiais.append("Conhecimento de Louco")
        if self.segredo_bandido: itens_especiais.append("Segredo do Bandido")
        if self.requiem: itens_especiais.append("Réquiem")
        
        if itens_especiais:
            print(f"💎 Itens Especiais: {', '.join(itens_especiais)}")
        
        ferros_guardados_info = []
        for ferro, quantidade in self.ferros_guardados.items():
            if quantidade > 0:
                ferros_guardados_info.append(f"{ferro}: {quantidade}")
        
        if ferros_guardados_info:
            print(f"🛡️ Ferros Guardados: {', '.join(ferros_guardados_info)}")

class EventoJogo:
    def __init__(self, tipo_evento: TipoEvento, descricao: str, raridade: Raridade, 
                 inimigo: Inimigo = None, recompensa_almas: int = 0, efeito_sanidade: int = 0,
                 item: Item = None, eh_armadilha: bool = False, eh_escolha_chefe: bool = False,
                 eh_evento_especial: bool = False):
        self.tipo_evento = tipo_evento
        self.descricao = descricao
        self.raridade = raridade
        self.inimigo = inimigo
        self.recompensa_almas = recompensa_almas
        self.efeito_sanidade = efeito_sanidade
        self.item = item
        self.eh_armadilha = eh_armadilha
        self.eh_escolha_chefe = eh_escolha_chefe
        self.eh_evento_especial = eh_evento_especial

class SobreviventeInsalubre:
    def __init__(self):
        self.ranking = None
        self.total_mortes = 0
        self.historico_jogadores = {}
        self.armas = {
            "Bastão Enferrujado": Arma("Bastão Enferrujado", 5, 10),
            "Cutelo Serrato": Arma("Cutelo Serrato", 10, 15),
            "Machado Radioativo": Arma("Machado Radioativo", 15, 20),
            "Greatsword": Arma("Greatsword", 25, 30),
            "Metralhadora": Arma("Metralhadora", 30, 40, "distancia", 0.30, 50, 50), 
            "Claymore": Arma("Claymore", 27, 28),
            "UltraGreatsword": Arma("UltraGreatsword", 40, 32),
            "Uchigatana": Arma("Uchigatana", 13, 15),
            "Pistola": Arma("Pistola", 2, 1, "distancia", 0.30, 20, 20), 
            "Bacamarte": Arma("Bacamarte", 5, 1, "distancia", 0.30, 15, 20)  
        }
        self.itens = self.inicializar_itens()
        self.jogador_atual = None
        self.recarga_fogueira = 0
        self.turno_atual = 0
        self.inicializar_inimigos()
        self.inicializar_eventos()
        self.melhorias_usadas_na_fogueira = False
        self.escala_dificuldade = 1.0
        self.contador_buff_inimigos = 0
    
    def inicializar_itens(self):
        itens = {
            "Fragmento de Ferro": Item("Fragmento de Ferro", "melhoria", "dano", 5),
            "Pedaco de Ferro": Item("Pedaco de Ferro", "melhoria", "dano", 10),
            "Lajota de Ferro": Item("Lajota de Ferro", "melhoria", "dano", 30),
            "Pocao de Cura": Item("Pocao de Cura", "consumivel", "vida", 40),
            "Antidoto": Item("Antidoto", "consumivel", "curar_veneno", 0),
            "Vestigio de Alma": Item("Vestigio de Alma", "consumivel", "almas", 100),
            "Vestigio Grande de Alma": Item("Vestigio Grande de Alma", "consumivel", "almas", 300),
            "Alma de Guerreiro": Item("Alma de Guerreiro", "consumivel", "almas", 500),
            "Alma de Chefe": Item("Alma de Chefe", "consumivel", "almas", 2500),
            "Elixir de Forca": Item("Elixir de Forca", "consumivel", "dano_temporario", 10),
            "Poeira Estelar": Item("Poeira Estelar", "consumivel", "sanidade", -20),
            "Cutelo Serrato": Item("Cutelo Serrato", "arma", "equipar_arma", 10),
            "Machado Radioativo": Item("Machado Radioativo", "arma", "equipar_arma", 15),
            "Greatsword": Item("Greatsword", "arma", "equipar_arma", 25),
            "Metralhadora": Item("Metralhadora", "arma", "equipar_arma", 30),
            "Claymore": Item("Claymore", "arma", "equipar_arma", 27), 
            "UltraGreatsword": Item("UltraGreatsword", "arma", "equipar_arma", 40),
            "Uchigatana": Item("Uchigatana", "arma", "equipar_arma", 13),
            "Bacamarte": Item("Bacamarte", "arma", "equipar_arma", 5),
            "Amuleto Antigo": Item("Amuleto Antigo", "especial", "vida_maxima", 10),
            "Balas": Item("Balas", "municao", "recarregar", 10),
            "Frasco de Cura": Item("Frasco de Cura", "especial", "aumentar_pocoes", 1),
            "Anel Clorantio": Item("Anel Clorantio", "especial", "reduzir_stamina", 10),
            "Anel do Favor": Item("Anel do Favor", "especial", "aumentar_vida_stamina", 20),
            "Lenço Dourado": Item("Lenço Dourado", "especial", "aumentar_critico", 10),
            "Pente Largo": Item("Pente Largo", "especial", "aumentar_balas", 5),
            "Conhecimento de Louco": Item("Conhecimento de Louco", "especial", "aumentar_atributos", 1),
            "Segredo do Bandido": Item("Segredo do Bandido", "especial", "turno_extra", 10),
            "Réquiem": Item("Réquiem", "especial", "ressuscitar", 1),
            "Crânio Amaldiçoado": Item("Crânio Amaldiçoado", "especial", "max_sanidade", 99),
        }
        return itens
    
    def inicializar_inimigos(self):
        self.modelos_inimigos = {
            "Rato": {"vida": 20, "dano": 5, "raridade": Raridade.COMUM, "recompensa_almas": 50, "padrao": ["arranhao", "arranhao", "mordida"]},
            "Cachorro Zumbi": {"vida": 30, "dano": 8, "raridade": Raridade.COMUM, "recompensa_almas": 70, "padrao": ["mordida", "investida", "uivo"]},
            "Lobisomem": {"vida": 50, "dano": 12, "raridade": Raridade.COMUM, "recompensa_almas": 100, "padrao": ["garra", "garra", "pulo"]},
            "Homem Contaminado": {"vida": 40, "dano": 10, "raridade": Raridade.COMUM, "recompensa_almas": 80, "padrao": ["ataque", "grito", "ataque"]},
            "Mutante": {"vida": 60, "dano": 15, "raridade": Raridade.COMUM, "recompensa_almas": 120, "padrao": ["esmagar", "investida", "rugido"]},
            "Guerreiro Corrompido": {"vida": 120, "dano": 25, "raridade": Raridade.INCOMUM, "recompensa_almas": 200, "padrao": ["corte", "golpe_escudo", "corte_pesado", "provocacao"]},
            "Mutante Enfurecido": {"vida": 150, "dano": 30, "raridade": Raridade.INCOMUM, "recompensa_almas": 250, "padrao": ["esmagar", "investida", "ataque_frenesi", "rugido"]},
            "Cao Radioativo Gigante": {"vida": 100, "dano": 35, "raridade": Raridade.INCOMUM, "recompensa_almas": 220, "padrao": ["mordida", "sopro_radioativo", "investida", "uivo"]},
            "Senhor das Cinzas": {"vida": 300, "dano": 40, "raridade": Raridade.CHEFE, "recompensa_almas": 1000, "padrao": ["corte_fogo", "nuvem_cinzas", "ataque_combo", "ultimate"]},
            "Abominacao de Lodo": {"vida": 400, "dano": 35, "raridade": Raridade.CHEFE, "recompensa_almas": 1200, "padrao": ["ataque_lodo", "cuspe_acido", "absorver", "transformar"]},
            "Colosso de Ferro Contaminado": {"vida": 500, "dano": 45, "raridade": Raridade.CHEFE, "recompensa_almas": 1500, "padrao": ["martelada", "investida", "terremoto", "furia"]},
            "Criatura Fantasma": {"vida": 250, "dano": 50, "raridade": Raridade.CHEFE, "recompensa_almas": 2000, "padrao": ["ataque_fase", "teletransporte", "ilusao", "drenar_alma"]},
            "Criatura Bizarra": {"vida": 180, "dano": 40, "raridade": Raridade.RARO, "recompensa_almas": 500, "padrao": ["explosao_psiquica", "distorcao_realidade", "ataque_loucura"]}
        }
    
    def criar_inimigo(self, nome_inimigo: str) -> Inimigo:
        modelo = self.modelos_inimigos[nome_inimigo]
        
        vida_base = modelo["vida"]
        dano_base = modelo["dano"]
        recompensa_base = modelo["recompensa_almas"]
        
        if self.turno_atual >= 40:
            self.contador_buff_inimigos = (self.turno_atual - 40) // 20
            bonus_dificuldade = 1.0 + (self.contador_buff_inimigos * 0.2)
        else:
            bonus_dificuldade = 1.0
            
        escala_total = self.escala_dificuldade * bonus_dificuldade
        
        vida_escalada = int(vida_base * escala_total)
        dano_escalado = int(dano_base * escala_total)
        recompensa_escalada = int(recompensa_base * escala_total)
        
        inimigo = Inimigo(
            nome_inimigo,
            vida_escalada,
            dano_escalado,
            modelo["raridade"],
            recompensa_escalada,
            modelo["padrao"].copy()
        )
        inimigo.vida_maxima = vida_escalada
        
        if nome_inimigo == "Lobisomem" and Condicao.QUEIMADURA in (modelo.get("condicoes") or []):
            if Condicao.QUEIMADURA in inimigo.condicoes:
                inimigo.condicoes.remove(Condicao.QUEIMADURA)
        
        return inimigo

    def inicializar_eventos(self):
        self.eventos = {
            TipoEvento.INIMIGO_COMUM: [
                "Um {inimigo} surge das sombras!",
                "{inimigo} aparece bloqueando seu caminho!",
                "De repente, {inimigo} ataca!"
            ],
            TipoEvento.EVENTO_COMUM: [
                "Você encontra um bau antigo...",
                "Um caminho tranquilo se abre à frente",
                "Você escuta sons estranhos ao longe",
                "Uma brisa fria sopra em sua direção",
                "Você encontra um item esquecido no chão!",
                "Uma bolsa abandonada contém suprimentos!",
                "Restos de um acampamento revelam itens úteis!",
                "Um cadaver possui itens ainda utilizáveis...",
                "Uma pequena caverna esconde tesouros!",
                "Você pisa em algo metálico - é um item!",
                "Uma arma enferrujada está encostada na parede...",
                "Você encontra um arsenal abandonado!",
                "Um guerreiro caído deixou sua arma para trás..."
            ],
            TipoEvento.MINI_CHEFE: [
                "UM MINI-CHEFE APARECE: {inimigo}!",
                "{inimigo} emerge, preparado para batalha!",
                "O terreno treme com a chegada de {inimigo}!"
            ],
            TipoEvento.FOGUEIRA: [
                "✨ Você encontra uma FOGUEIRA! Pode descansar e salvar seu progresso.",
                "Uma chama reconfortante brilha à frente - é uma Fogueira!",
                "No meio da escuridão, uma Fogueira oferece refúgio."
            ],
            TipoEvento.EVENTO_RARO: [
                "💫 EVENTO RARO: Um Comerciante Fantasma oferece itens!",
                "💎 EVENTO RARO: Você encontra um Fragmento de Alma!",
                "⚠️ EVENTO RARO: Armadilha mortal! Escape rápido!",
                "👻 EVENTO RARO: Uma aparição misteriosa...",
                "🔮 EVENTO RARO: Bau amaldiçoado - risco e recompensa!",
                "🎁 EVENTO RARO: Tesouro escondido encontrado!",
                "⚡ EVENTO RARO: Energia ancestral emana de um artefato!",
                "🏺 EVENTO RARO: Vaso ancestral contém itens preciosos!",
                "💎 EVENTO RARO: Cristais brilhantes emanam poder!"
            ],
            TipoEvento.CHEFE: [
                "💀 CHEFE ENCONTRADO: {inimigo} SE APROXIMA!",
                "🌋 O AR FICA PESADO... {inimigo} CHEGOU!",
                "⚡ PREPARE-SE PARA O CHEFE: {inimigo}!"
            ]
        }

    # ===== SISTEMA AVL =====

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

    def inserir_avl(self, no: NoAVL, nome_jogador: str, pontuacao: int) -> NoAVL:
        if not no:
            novo_no = NoAVL(nome_jogador, pontuacao)
            novo_no.historico_avls.append(pontuacao)
            novo_no.total_avls = 1
            return novo_no
        
        if nome_jogador < no.nome_jogador:
            no.esquerda = self.inserir_avl(no.esquerda, nome_jogador, pontuacao)
        elif nome_jogador > no.nome_jogador:
            no.direita = self.inserir_avl(no.direita, nome_jogador, pontuacao)
        else:
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

    def encontrar_jogador(self, no: NoAVL, nome_jogador: str) -> Optional[NoAVL]:
        if not no or no.nome_jogador == nome_jogador:
            return no
        
        if nome_jogador < no.nome_jogador:
            return self.encontrar_jogador(no.esquerda, nome_jogador)
        return self.encontrar_jogador(no.direita, nome_jogador)

    def obter_top_n_pontuacoes(self, no: NoAVL, n: int, resultados: List[Tuple[str, int, int, int, int]]):
        if no and len(resultados) < n:
            self.obter_top_n_pontuacoes(no.direita, n, resultados)
            if len(resultados) < n:
                resultados.append((
                    no.nome_jogador, 
                    no.pontuacao_recorde,
                    no.record_eventos,
                    no.chefes_derrotados,
                    no.total_avls
                ))
                self.obter_top_n_pontuacoes(no.esquerda, n, resultados)

    def imprimir_ranking(self, n: int = 10):
        print(f"\n🏆 TOP {n} JOGADORES - ÁRVORE AVL 🏆")
        print("=" * 70)
        
        resultados = []
        self.obter_top_n_pontuacoes(self.ranking, n, resultados)
        
        for i, (nome, pontuacao, record_eventos, chefes, total_avls) in enumerate(resultados, 1):
            no_jogador = self.encontrar_jogador(self.ranking, nome)
            mortes = no_jogador.contador_mortes if no_jogador else 0
            print(f"{i:2d}. {nome:<20} {pontuacao:>8} almas | ☠️ {mortes}  mortes | 📊 {record_eventos} eventos | 🏹 {chefes} chefes | 🌳 {total_avls} AVLs")
        
        if not resultados:
            print("Nenhum jogador registrado ainda...")

    def imprimir_historico_jogador(self):
        if not self.jogador_atual:
            print("Nenhum jogador ativo.")
            return
            
        no_jogador = self.encontrar_jogador(self.ranking, self.jogador_atual.nome)
        if not no_jogador or not no_jogador.historico_avls:
            print(f"\n📊 {self.jogador_atual.nome} ainda não tem AVLs registradas.")
            return
        
        print(f"\n📊 HISTÓRICO DE AVLs - {self.jogador_atual.nome}")
        print("=" * 50)
        print(f"Recorde Pessoal: {no_jogador.pontuacao_recorde} almas")
        print(f"Recorde de eventos: {no_jogador.record_eventos}")
        print(f"Chefes Derrotados: {no_jogador.chefes_derrotados}")
        print(f"Total de AVLs: {no_jogador.total_avls}")
        print(f"Total de Mortes: {no_jogador.contador_mortes}")
        
        avls_recentes = no_jogador.historico_avls[-10:]
        print(f"\nÚltimas {len(avls_recentes)} AVLs:")
        for i, pontuacao in enumerate(reversed(avls_recentes), 1):
            print(f"{i:2d}. {pontuacao:>8} almas")
        
        if len(no_jogador.historico_avls) > 1:
            pontuacao_media = sum(no_jogador.historico_avls) / len(no_jogador.historico_avls)
            print(f"\n📈 Média de todas as AVLs: {pontuacao_media:.1f} almas")

    # ===== SISTEMA DE EVENTOS =====

    def gerar_evento(self) -> EventoJogo:
        self.turno_atual += 1
        
        if self.turno_atual >= 40 and (self.turno_atual - 40) % 20 == 0:
            self.contador_buff_inimigos = (self.turno_atual - 40) // 20
            bonus_dificuldade = 1.0 + (self.contador_buff_inimigos * 0.2)
            print(f"💀 DIFICULDADE AUMENTADA! Inimigos estão {self.contador_buff_inimigos * 20}% mais fortes! (Buff #{self.contador_buff_inimigos})")
        
        if self.jogador_atual:
            self.jogador_atual.restaurar_stamina(2)
        
        modificador_sanidade = self.jogador_atual.sanidade / 100.0
        chance_chefe = 0.03 + (modificador_sanidade * 0.05)
        
        if self.turno_atual <= 15:
            chance_chefe = 0
        
        chance_raro = 0.08 + (modificador_sanidade * 0.1)
        chance_mini_chefe = 0.05 + (modificador_sanidade * 0.05)
        
        modificador_fogueira = 1.0
        if self.recarga_fogueira > 0:
            modificador_fogueira = 0.1
            self.recarga_fogueira -= 1
            
        chance_fogueira = (0.2 - (modificador_sanidade * 0.1)) * modificador_fogueira
        
        rolagem = random.random()
        
        if rolagem < chance_chefe:
            tipo_evento = TipoEvento.CHEFE
        elif rolagem < chance_chefe + chance_mini_chefe:
            tipo_evento = TipoEvento.MINI_CHEFE
        elif rolagem < chance_chefe + chance_mini_chefe + chance_raro:
            tipo_evento = TipoEvento.EVENTO_RARO
        elif rolagem < chance_chefe + chance_mini_chefe + chance_raro + chance_fogueira:
            tipo_evento = TipoEvento.FOGUEIRA
        elif rolagem < 0.6:
            tipo_evento = TipoEvento.INIMIGO_COMUM
        else:
            tipo_evento = TipoEvento.EVENTO_COMUM
        
        return self.criar_evento_especifico(tipo_evento)

    def criar_evento_especifico(self, tipo_evento: TipoEvento) -> EventoJogo:
        if tipo_evento in [TipoEvento.INIMIGO_COMUM, TipoEvento.MINI_CHEFE, TipoEvento.CHEFE]:
            if tipo_evento == TipoEvento.CHEFE:
                pool_inimigos = [nome for nome, modelo in self.modelos_inimigos.items() 
                            if modelo["raridade"] == Raridade.CHEFE]
                nome_inimigo = random.choice(pool_inimigos) if pool_inimigos else list(self.modelos_inimigos.keys())[0]
                inimigo = self.criar_inimigo(nome_inimigo)
                descricao = f"💀 VOCÊ ENCONTROU UM CHEFE: {inimigo.nome}!\nDeseja enfrentá-lo agora?"
                efeito_sanidade = 5
                return EventoJogo(tipo_evento, descricao, inimigo.raridade, inimigo, 
                               inimigo.recompensa_almas, efeito_sanidade, eh_escolha_chefe=True)
                
            elif tipo_evento == TipoEvento.MINI_CHEFE:
                pool_inimigos = [nome for nome, modelo in self.modelos_inimigos.items() 
                            if modelo["raridade"] == Raridade.INCOMUM]
                efeito_sanidade = 3
            else:
                pool_inimigos = [nome for nome, modelo in self.modelos_inimigos.items() 
                            if modelo["raridade"] == Raridade.COMUM]
                efeito_sanidade = 1
            
            if tipo_evento != TipoEvento.CHEFE:
                nome_inimigo = random.choice(pool_inimigos) if pool_inimigos else list(self.modelos_inimigos.keys())[0]
                inimigo = self.criar_inimigo(nome_inimigo)
                descricao = random.choice(self.eventos[tipo_evento]).format(inimigo=inimigo.nome)
                return EventoJogo(tipo_evento, descricao, inimigo.raridade, inimigo, 
                               inimigo.recompensa_almas, efeito_sanidade)
        
        elif tipo_evento == TipoEvento.FOGUEIRA:
            descricao = random.choice(self.eventos[tipo_evento])
            if self.jogador_atual.pontuacao_avl_atual > 0:
                self.ranking = self.inserir_avl(self.ranking, self.jogador_atual.nome, 
                                             self.jogador_atual.pontuacao_avl_atual)
            
            self.recarga_fogueira = 5
            return EventoJogo(tipo_evento, descricao, Raridade.INCOMUM, 
                           recompensa_almas=0, efeito_sanidade=-20)
        
        elif tipo_evento == TipoEvento.EVENTO_RARO:
            descricao = random.choice(self.eventos[tipo_evento])
            recompensa_almas = 0
            item = None
            eh_armadilha = False
            eh_evento_especial = False

            if "Tesouro escondido encontrado" in descricao:
                itens_tesouro = [
                    "Amuleto Antigo", "Anel Clorantio", "Anel do Favor", 
                    "Lenço Dourado", "Pente Largo", "Conhecimento de Louco",
                    "Segredo do Bandido", "Réquiem", "Crânio Amaldiçoado"
                ]
                pesos = [15, 10, 5, 12, 20, 8, 15, 3, 2]
                nome_item = random.choices(itens_tesouro, weights=pesos, k=1)[0]
                item = self.itens[nome_item]
                descricao += f"\n💎 Você encontrou: {item.nome}!"
                efeito_sanidade = 5
                
            elif "Energia ancestral" in descricao:
                efeito_sanidade = 5
                item = self.itens["Amuleto Antigo"]
                descricao += f"\n📦 Você encontrou: {item.nome}!"
            elif "aparição misteriosa" in descricao:
                efeito_sanidade = 5
            elif "Armadilha" in descricao:
                efeito_sanidade = 5
                eh_armadilha = True
            else:
                efeito_sanidade = 5

            if self.jogador_atual.sanidade > 60:
                eventos_raros = {
                    "👽 CRIATURA BIZARRA aparece! Sanidade alta atrai perigos...": 
                        lambda: EventoJogo(tipo_evento, "👽 CRIATURA BIZARRA aparece! Sanidade alta atrai perigos...", 
                                        Raridade.RARO, self.criar_inimigo("Criatura Bizarra"), 500, 25),
                    "🌌 PORTAL DIMENSIONAL se abre! Criaturas de outro plano emergem!": 
                        lambda: EventoJogo(tipo_evento, "🌌 PORTAL DIMENSIONAL se abre! Criaturas de outro plano emergem!", 
                                        Raridade.RARO, None, 0, 30, eh_evento_especial=True),
                    "💀 ENTIDADE ANCESTRAL desperta! Fuja ou enfrente o impossível!": 
                        lambda: EventoJogo(tipo_evento, "💀 ENTIDADE ANCESTRAL desperta! Fuja ou enfrente o impossível!", 
                                        Raridade.CHEFE, None, 0, 40, eh_evento_especial=True)
                }
                
                if descricao in eventos_raros:
                    return eventos_raros[descricao]()
            
            if "Comerciante Fantasma" in descricao:
                item = self.gerar_item_comerciante_fantasma()
                descricao += f"\n🎁 O comerciante oferece: {item.nome}!"
            elif "Fragmento de Alma" in descricao:
                item = self.itens["Vestigio de Alma"]
            elif any(palavra_chave in descricao for palavra_chave in ["Bau", "Artefato", "Vaso", "Cristais"]):
                item = self.gerar_item_bau(evento_raro=True)
                if item:
                    descricao += f"\n📦 Você encontrou: {item.nome}!"
            
            return EventoJogo(tipo_evento, descricao, Raridade.RARO, 
                           recompensa_almas=recompensa_almas, efeito_sanidade=efeito_sanidade, 
                           item=item, eh_armadilha=eh_armadilha)
        
        else:
            descricao = random.choice(self.eventos[tipo_evento])
            item = None
            
            eventos_com_armas = [
                "guerreiro caído", "arsenal abandonado", "arma enferrujada"
            ]
            
            if any(evento in descricao.lower() for evento in eventos_com_armas):
                armas_possiveis = [nome for nome in self.armas.keys() if nome not in ["Bastão Enferrujado", "Pistola"]]
                armas_nao_encontradas = [arma for arma in armas_possiveis if arma not in self.jogador_atual.armas_encontradas]
                
                if armas_nao_encontradas and random.random() < 0.7:
                    nome_arma = random.choice(armas_nao_encontradas)
                elif armas_possiveis:
                    nome_arma = random.choice(armas_possiveis)
                else:
                    nome_arma = None
                    
                if nome_arma:
                    item = self.itens.get(nome_arma)
                    if item:
                        descricao += f"\n⚔️ Você encontrou: {item.nome}!"
                        self.jogador_atual.adicionar_arma(nome_arma)
            
            eventos_itens_gerais = [
                "pequena caverna", "restos de um acampamento", "cadaver possui itens",
                "bau antigo", "item esquecido"
            ]
            
            if any(evento in descricao.lower() for evento in eventos_itens_gerais) and not item:
                itens_comuns = [
                    "Fragmento de Ferro", "Pedaco de Ferro", "Lajota de Ferro",
                    "Pocao de Cura", "Antidoto", "Vestigio de Alma", 
                    "Vestigio Grande de Alma", "Alma de Guerreiro", "Elixir de Forca",
                    "Poeira Estelar", "Balas", "Frasco de Cura"
                ]
                nome_item = random.choice(itens_comuns)
                item = self.itens[nome_item]
                descricao += f"\n🎁 Você encontrou: {item.nome}!"
            
            if "Você pisa em algo metálico" in descricao and not item:
                rolagem_item = random.random()
                if rolagem_item < 0.05:  
                    item = self.itens["Lajota de Ferro"]
                elif rolagem_item < 0.25:  
                    item = self.itens["Pedaco de Ferro"]
                elif rolagem_item < 0.45:
                    item = self.itens["Vestigio de Alma"]
                elif rolagem_item < 0.65:
                    item = self.itens["Vestigio Grande de Alma"]
                else:  
                    item = self.itens["Fragmento de Ferro"]
                    
            elif "Uma bolsa abandonada contém suprimentos!" in descricao and not item:
                item = self.itens["Frasco de Cura"]
            
            palavras_chave_itens = ['bau', 'item', 'bolsa', 'acampamento', 'suprimentos', 
                           'esquecido', 'cadaver', 'caverna', 'metalico', 'arsenal', 'enferrujada']
            
            if any(palavra_chave in descricao.lower() for palavra_chave in palavras_chave_itens) and not item:
                if random.random() < 0.8:
                    item_temp = self.gerar_item_bau(evento_raro=False)
                    if item_temp:
                        item = item_temp
            
            if item and not any(evento in descricao.lower() for evento in eventos_com_armas + eventos_itens_gerais):
                descricao += f"\n🎁 Você encontrou: {item.nome}!"
            
            return EventoJogo(tipo_evento, descricao, Raridade.COMUM, 
                           recompensa_almas=0, efeito_sanidade=0, item=item)

    def gerar_item_bau(self, evento_raro: bool = False) -> Optional[Item]:
        if random.random() < 0.8:
            if self.turno_atual >= 30 and random.random() < 0.3:
                return self.itens["Lajota de Ferro"]
            elif self.turno_atual >= 15 and random.random() < 0.4:
                return self.itens["Pedaco de Ferro"]
            else:
                if random.random() < 0.25:
                    armas_possiveis = [nome for nome in self.armas.keys() if nome not in ["Bastão Enferrujado", "Pistola"]]
                    if armas_possiveis:
                        nome_arma = random.choice(armas_possiveis)
                        if self.jogador_atual:
                            self.jogador_atual.adicionar_arma(nome_arma)
                        return self.itens.get(nome_arma, self.itens["Fragmento de Ferro"])
                else:
                    itens_possiveis = ["Fragmento de Ferro", "Pocao de Cura", "Antidoto", "Vestigio de Alma", "Balas"]
                    if self.turno_atual >= 20:
                        itens_possiveis.extend(["Vestigio Grande de Alma", "Alma de Guerreiro"])
                    if self.turno_atual >= 40:
                        itens_possiveis.append("Alma de Chefe")
                    
                    if evento_raro and random.random() < 0.1:
                        itens_raros = ["Crânio Amaldiçoado", "Réquiem", "Segredo do Bandido"]
                        itens_possiveis.extend(itens_raros)
                    
                    nome_item = random.choice(itens_possiveis)
                    return self.itens[nome_item]
        return None

    def lidar_com_evento_especial(self, evento: EventoJogo) -> bool:
        if "PORTAL DIMENSIONAL" in evento.descricao:
            print("🌀 Realidade se distorce ao seu redor!")
            print("👁️  Criaturas indescritíveis emergem do portal!")
            self.jogador_atual.adicionar_sanidade(30)
            inimigo = self.criar_inimigo("Criatura Bizarra")
            return self.combate(inimigo)
            
        elif "ENTIDADE ANCESTRAL" in evento.descricao:
            print("💀 UMA PRESENÇA ANCESTRAL DESPERTA!")
            print("A realidade treme com sua chegada!")
            
            if random.random() < 0.05:
                print("🎯 Por um milagre, você consegue escapar da entidade!")
                return True
            else:
                print("😱 A Entidade Ancestral te alcança!")
                print("💸 TODAS as suas almas são consumidas!")
                print("😵 Sua sanidade desaba!")
                print("❤️ Você fica com 1 de vida!")
                
                almas_perdidas = self.jogador_atual.almas
                self.jogador_atual.almas = 0
                self.jogador_atual.sanidade = max(0, self.jogador_atual.sanidade - 40)
                self.jogador_atual.vida = 1
                self.jogador_atual.adicionar_condicao(Condicao.MEDO)
                self.jogador_atual.adicionar_condicao(Condicao.FRENESI)
                
                print(f"💀 Perdeu {almas_perdidas} almas!")
                print("😨 Efeitos: MEDO e FRENESI!")
                return self.jogador_atual.vida > 0
        
        return True

    def lidar_com_escolha_arma(self, item_arma: Item) -> bool:
        print(f"\n⚔️ Você encontrou: {item_arma.nome} (Dano: +{item_arma.valor})")
        print("1. Equipar agora")
        print("2. Guardar no inventário")
        print("3. Deixar para trás")
        
        escolha = input("Escolha uma ação: ").strip()
        
        if escolha == "1":
            if item_arma.nome in ["Pistola", "Bacamarte", "Metralhadora"]:
                arma_nova = self.armas[item_arma.nome]
                if self.jogador_atual.arma_mao_esquerda:
                    dano_extra = self.jogador_atual.arma_mao_esquerda.dano - self.jogador_atual.arma_mao_esquerda.dano_base
                    arma_nova.dano = arma_nova.dano_base + dano_extra
                    arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_esquerda.melhorias_aplicadas.copy()
                    arma_nova.limites_melhorias = self.jogador_atual.arma_mao_esquerda.limites_melhorias.copy()
                self.jogador_atual.arma_mao_esquerda = arma_nova
                print(f"✅ Você equipou {item_arma.nome} na mão esquerda! (Dano: +{arma_nova.dano})")
            else:
                arma_nova = self.armas[item_arma.nome]
                if self.jogador_atual.arma_mao_direita:
                    dano_extra = self.jogador_atual.arma_mao_direita.dano - self.jogador_atual.arma_mao_direita.dano_base
                    arma_nova.dano = arma_nova.dano_base + dano_extra
                    arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_direita.melhorias_aplicadas.copy()
                    arma_nova.limites_melhorias = self.jogador_atual.arma_mao_direita.limites_melhorias.copy()
                self.jogador_atual.arma_mao_direita = arma_nova
                self.jogador_atual.arma_atual = arma_nova
                print(f"✅ Você equipou {item_arma.nome} na mão direita! (Dano: +{arma_nova.dano})")
            return True
            
        elif escolha == "2":
            self.jogador_atual.adicionar_ao_inventario(item_arma)
            print(f"\n🎒 Você guardou {item_arma.nome} no inventário.")
            return True
            
        elif escolha == "3":
            print(f"❌ Você deixou {item_arma.nome} para trás.")
            return True
            
        else:
            print("Escolha inválida!")
            return self.lidar_com_escolha_arma(item_arma)

    def lidar_com_evento_armadilha(self) -> bool:
        print("\n⚠️ ARMADILHA MORTAL!")
        print("Você caiu em uma armadilha perigosa!")
        
        chance_escapar = 0.30 
        
        if random.random() < chance_escapar:
            print("🎯 Você conseguiu escapar no último segundo!")
            self.jogador_atual.adicionar_sanidade(10)
            return True
        else:
            print("💥 Você não conseguiu evitar a armadilha!")
            
            if random.random() < 0.05:
                print("💀 A armadilha era fatal! Você morreu instantaneamente!")
                self.jogador_atual.vida = 0
                return False
            
            dano_armadilha = random.randint(20, 40)
            dano_real = self.jogador_atual.receber_dano(dano_armadilha)
            print(f"💔 A armadilha causa {dano_real} de dano!")
            self.jogador_atual.adicionar_sanidade(15)
            
            if random.random() < 0.4:
                condicao = random.choice([Condicao.VENENO, Condicao.QUEIMADURA, Condicao.MEDO])
                self.jogador_atual.adicionar_condicao(condicao)
                print(f"⚠️ A armadilha te deixou {condicao.name}!")
            
            return self.jogador_atual.vida > 0

    def lidar_com_escolha_chefe(self, inimigo: Inimigo) -> bool:
        print(f"\n💀 CHEFE DETECTADO: {inimigo.nome}")
        print(f"Recompensa: {inimigo.recompensa_almas} almas | Vida: {inimigo.vida}")
        print("\n1. Enfrentar o chefe agora!")
        print("2. Fugir (perde 20% das almas)")
        
        escolha = input("Escolha sua ação: ").strip()
        
        if escolha == "1":
            print(f"\n⚔️ Você decide enfrentar {inimigo.nome}! Boa sorte!")
            return True
        else:
            almas_perdidas = int(self.jogador_atual.almas * 0.2)
            self.jogador_atual.almas = max(0, self.jogador_atual.almas - almas_perdidas)
            self.jogador_atual.pontuacao_avl_atual = max(0, self.jogador_atual.pontuacao_avl_atual - almas_perdidas)
            
            print(f"\n🏃‍♂️ Você foge do chefe! Perdeu {almas_perdidas} almas no processo.")
            return False

    def gerar_item_comerciante_fantasma(self) -> Item:
        itens_possiveis = [
            "Fragmento de Ferro", "Pedaco de Ferro", "Pocao de Cura", 
            "Antidoto", "Vestigio de Alma", "Elixir de Forca", "Poeira Estelar", "Balas"
        ]
        nome_item = random.choice(itens_possiveis)
        return self.itens[nome_item]

    def aplicar_efeito_item(self, item: Item):
        print(f"🎁 Usando {item.nome}: {item.efeito}")
        
        if item.nome == "Amuleto Antigo":
            self.jogador_atual.amuleto_antigo = True
            aumento_vida = int(self.jogador_atual.vida_maxima * 0.1)
            self.jogador_atual.vida_maxima += aumento_vida
            self.jogador_atual.vida += aumento_vida
            print(f"❤️ Vida máxima aumentada em 10%! (+{aumento_vida} vida)")
        elif item.nome == "Balas":
            if self.jogador_atual.arma_mao_esquerda:
                balas_encontradas = random.randint(1, 10)
                balas_atuais = self.jogador_atual.arma_mao_esquerda.balas
                balas_maximas = self.jogador_atual.arma_mao_esquerda.balas_maximas
                balas_adicionadas = min(balas_encontradas, balas_maximas - balas_atuais)
                self.jogador_atual.arma_mao_esquerda.balas += balas_adicionadas
                print(f"🔫 +{balas_adicionadas} balas para {self.jogador_atual.arma_mao_esquerda.nome}! (Total: {self.jogador_atual.arma_mao_esquerda.balas}/{balas_maximas})")
        elif item.nome == "Frasco de Cura":
            self.jogador_atual.pocoes_cura_maximas += 1
            self.jogador_atual.pocoes_cura = self.jogador_atual.pocoes_cura_maximas
            print(f"🧪 Capacidade de poções aumentada para {self.jogador_atual.pocoes_cura_maximas}! Poções totalmente restauradas!")
        
        elif item.nome == "Crânio Amaldiçoado":
            self.jogador_atual.sanidade = 99
            print("💀 Crânio Amaldiçoado ativado! Sua sanidade foi fixada em 99!")
        
        elif item.nome == "Anel Clorantio":
            self.jogador_atual.anel_clorantio = True
            print("💍 Anel Clorantio equipado! -10% de custo de stamina em todas as ações!")
        elif item.nome == "Anel do Favor":
            self.jogador_atual.anel_favor = True
            aumento_vida = int(self.jogador_atual.vida_maxima * 0.2)
            aumento_stamina = int(self.jogador_atual.stamina_maxima * 0.2)
            self.jogador_atual.vida_maxima += aumento_vida
            self.jogador_atual.stamina_maxima += aumento_stamina
            self.jogador_atual.vida += aumento_vida
            self.jogador_atual.stamina += aumento_stamina
            print(f"💍 Anel do Favor equipado! +20% vida e stamina! (+{aumento_vida} vida, +{aumento_stamina} stamina)")
        elif item.nome == "Lenço Dourado":
            self.jogador_atual.lenco_dourado = True
            print("👑 Lenço Dourado equipado! +10% de chance de crítico!")
        elif item.nome == "Pente Largo":
            if self.jogador_atual.arma_mao_esquerda:
                self.jogador_atual.arma_mao_esquerda.balas_maximas += 5
                self.jogador_atual.arma_mao_esquerda.balas = min(self.jogador_atual.arma_mao_esquerda.balas, self.jogador_atual.arma_mao_esquerda.balas_maximas)
                print(f"🔫 Pente Largo adicionado! Capacidade de balas aumentada para {self.jogador_atual.arma_mao_esquerda.balas_maximas}!")
        elif item.nome == "Conhecimento de Louco":
            self.jogador_atual.conhecimento_louco = True
            self.jogador_atual.dano_base += 1
            self.jogador_atual.defesa += 1
            self.jogador_atual.vida_maxima += 10
            self.jogador_atual.stamina_maxima += 10
            self.jogador_atual.adicionar_sanidade(20)
            print("📚 Conhecimento de Louco absorvido! +1 para todos atributos, mas +20 de sanidade!")
        elif item.nome == "Segredo do Bandido":
            self.jogador_atual.segredo_bandido = True
            self.jogador_atual.defesa = max(1, self.jogador_atual.defesa - int(self.jogador_atual.defesa * 0.1))
            print("🎭 Segredo do Bandido aprendido! +1 turno por combate, mas -10% defesa!")
        elif item.nome == "Réquiem":
            self.jogador_atual.requiem = True
            print("💀 Réquiem adquirido! Você pode ressuscitar uma vez por combate!")
        
        elif item.tipo == "consumivel":
            if item.efeito == "vida":
                self.jogador_atual.vida = min(self.jogador_atual.vida_maxima, 
                                               self.jogador_atual.vida + item.valor)
                print(f"❤️ +{item.valor} de vida!")
            elif item.efeito == "curar_veneno":
                if Condicao.VENENO in self.jogador_atual.condicoes:
                    self.jogador_atual.condicoes.remove(Condicao.VENENO)
                    print("🧪 Veneno curado!")
            elif item.efeito == "almas":
                self.jogador_atual.adicionar_almas(item.valor)
                print(f"💎 +{item.valor} almas!")
            elif item.efeito == "dano_temporario":
                self.jogador_atual.dano += item.valor
                print(f"⚡ +{item.valor} de dano temporário!")
            elif item.efeito == "sanidade":
                self.jogador_atual.adicionar_sanidade(item.valor)
                if item.valor > 0:
                    print(f"😶 Sanidade +{item.valor}")
                else:
                    print(f"😌 Sanidade {item.valor}")
        
        elif item.tipo == "melhoria":
            if item.efeito == "dano":
                if self.jogador_atual.arma_atual:
                    arma = self.jogador_atual.arma_atual
                    melhorias_atuais = arma.melhorias_aplicadas[item.nome]
                    limite = arma.limites_melhorias[item.nome]  
                    
                    if melhorias_atuais < limite:
                        arma.dano += item.valor
                        arma.melhorias_aplicadas[item.nome] += 1
                        print(f"🗡️ Dano da {arma.nome} aumentado em +{item.valor}! ({arma.melhorias_aplicadas[item.nome]}/{limite})")
                    else:
                        print(f"❌ {arma.nome} já atingiu o limite de {item.nome}!")
                        print("Deseja guardar este ferro para usar em outra arma?")
                        print("1. Sim, guardar no inventário")
                        print("2. Não, descartar")
                        
                        escolha = input("Escolha: ").strip()
                        if escolha == "1":
                            self.jogador_atual.ferros_guardados[item.nome] += 1
                            print(f"🛡️ {item.nome} guardado! Total: {self.jogador_atual.ferros_guardados[item.nome]}")
                        else:
                            print(f"❌ {item.nome} descartado.")
                
        elif item.tipo == "arma":
            if item.nome in self.armas:
                if item.nome in ["Pistola", "Bacamarte", "Metralhadora"]:
                    arma_nova = self.armas[item.nome]
                    if self.jogador_atual.arma_mao_esquerda:
                        dano_extra = self.jogador_atual.arma_mao_esquerda.dano - self.jogador_atual.arma_mao_esquerda.dano_base
                        arma_nova.dano = arma_nova.dano_base + dano_extra
                        arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_esquerda.melhorias_aplicadas.copy()
                        arma_nova.limites_melhorias = self.jogador_atual.arma_mao_esquerda.limites_melhorias.copy()
                    self.jogador_atual.arma_mao_esquerda = arma_nova
                    print(f"🔫 Você equipou {item.nome} na mão esquerda! (Dano: +{arma_nova.dano})")
                else:
                    arma_nova = self.armas[item.nome]
                    if self.jogador_atual.arma_mao_direita:
                        dano_extra = self.jogador_atual.arma_mao_direita.dano - self.jogador_atual.arma_mao_direita.dano_base
                        arma_nova.dano = arma_nova.dano_base + dano_extra
                        arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_direita.melhorias_aplicadas.copy()
                        arma_nova.limites_melhorias = self.jogador_atual.arma_mao_direita.limites_melhorias.copy()
                    self.jogador_atual.arma_mao_direita = arma_nova
                    self.jogador_atual.arma_atual = arma_nova
                    print(f"⚔️ Você equipou {item.nome} na mão direita! (Dano: +{arma_nova.dano})")

    def lidar_com_evento(self, evento: EventoJogo) -> bool:
        print(f"\n{'='*60}")
        print(f"EVENTO: {evento.descricao}")
        print(f"{'='*60}")
        
        if evento.efeito_sanidade != 0:
            self.jogador_atual.adicionar_sanidade(evento.efeito_sanidade)
            if evento.efeito_sanidade > 0:
                print(f"😶 Sanidade +{evento.efeito_sanidade}")
            else:
                print(f"😌 Sanidade {evento.efeito_sanidade}")
        
        if evento.eh_evento_especial:
            return self.lidar_com_evento_especial(evento)
        
        if evento.eh_escolha_chefe:
            aceitar_chefe = self.lidar_com_escolha_chefe(evento.inimigo)
            if not aceitar_chefe:
                return True
        
        if evento.eh_armadilha:
            return self.lidar_com_evento_armadilha()
        
        if evento.item:
            if evento.item.tipo == "arma":
                return self.lidar_com_escolha_arma(evento.item)
            else:
                self.aplicar_efeito_item(evento.item)
        
        if evento.tipo_evento == TipoEvento.FOGUEIRA:
            return self.lidar_com_fogueira()
        elif evento.inimigo:
            resultado_combate = self.combate(evento.inimigo)
            if resultado_combate is False and self.jogador_atual.vida > 0:
                return True
            return resultado_combate
        
        if "aparição misteriosa" in evento.descricao.lower():
            print("👻 Uma sensação de medo percorre sua espinha!")
            self.jogador_atual.adicionar_condicao(Condicao.MEDO)
            print("😨 Efeito: MEDO aplicado!")
        
        return True

    # ===== SISTEMA DE COMBATE =====

    def combate(self, inimigo: Inimigo) -> bool:
        print(f"\n⚔️ COMBATE INICIADO: {self.jogador_atual.nome} vs {inimigo.nome}!")
        print(f"Vida: {self.jogador_atual.vida}/{self.jogador_atual.vida_maxima} | "
            f"Stamina: {self.jogador_atual.stamina}/{self.jogador_atual.stamina_maxima} | "
            f"Inimigo: {inimigo.vida}/{inimigo.vida_maxima}")
        
        self.jogador_atual.dano = self.jogador_atual.dano_base
        inimigo.indice_padrao_atual = 0
        self.jogador_atual.resetar_chance_atordoar()
        self.jogador_atual.ressuscitou = False
        self.jogador_atual.turnos_extras = 1 if self.jogador_atual.segredo_bandido else 0
        
        turno = 0
        while self.jogador_atual.vida > 0 and inimigo.vida > 0:
            turno += 1
            print(f"\n--- Turno {turno} ---")
            
            if self.jogador_atual.turnos_extras > 0 and inimigo.vida > 0 and self.jogador_atual.vida > 0:
                self.jogador_atual.turnos_extras -= 1
                print("🎭 SEGREDO DO BANDIDO! Turno extra!")
                jogador_continua = self.turno_jogador(inimigo)
                if not jogador_continua:
                    return False
                if inimigo.vida <= 0:
                    break
            
            if self.jogador_atual.turnos_atordoado > 0:
                self.jogador_atual.turnos_atordoado -= 1
                print(f"💫 Você está atordoado e perde o turno!")
                self.turno_inimigo(inimigo)
                continue
            
            jogador_continua = self.turno_jogador(inimigo)
            if not jogador_continua:
                return False
            
            if inimigo.vida <= 0:
                break
                
            if self.jogador_atual.vida > 0:
                self.turno_inimigo(inimigo)
            
            self.jogador_atual.processar_condicoes()
            self.jogador_atual.restaurar_stamina(3 + self.jogador_atual.nivel)
            
            print(f"\nStatus: Vida {max(0, self.jogador_atual.vida)} | "
                f"Stamina {self.jogador_atual.stamina} | "
                f"Inimigo {max(0, inimigo.vida)}")
        
        self.jogador_atual.vida = max(0, self.jogador_atual.vida)
        inimigo.vida = max(0, inimigo.vida)
        
        if self.jogador_atual.vida <= 0 and self.jogador_atual.requiem and not self.jogador_atual.ressuscitou:
            print("\n💀 RÉQUIEM ATIVADO! Você ressuscita com 50% de vida!")
            self.jogador_atual.vida = self.jogador_atual.vida_maxima // 2
            self.jogador_atual.ressuscitou = True
            print(f"❤️ Vida restaurada para {self.jogador_atual.vida}!")
            return self.combate(inimigo)
        
        if self.jogador_atual.vida > 0 and inimigo.vida <= 0:
            almas_ganhas = inimigo.recompensa_almas
            self.jogador_atual.adicionar_almas(almas_ganhas)
            
            bonus_sanidade = min(10, inimigo.raridade.value * 2)
            self.jogador_atual.adicionar_sanidade(bonus_sanidade)
            
            print(f"\n✅ VITÓRIA! Você derrotou {inimigo.nome}!")
            print(f"💰 +{almas_ganhas} almas ganhas! (Total: {self.jogador_atual.almas})")
            print(f"😶 +{bonus_sanidade} de sanidade")
            
            if inimigo.eh_chefe:
                self.jogador_atual.chefes_derrotados_atual += 1
            
            if Condicao.MEDO in self.jogador_atual.condicoes:
                self.jogador_atual.remover_condicao(Condicao.MEDO)
            if Condicao.FRENESI in self.jogador_atual.condicoes:
                self.jogador_atual.remover_condicao(Condicao.FRENESI)
                
            if inimigo.eh_chefe and random.random() < 0.3:
                alma_chefe = self.itens["Alma de Chefe"]
                print(f"💎 {inimigo.nome} dropou uma {alma_chefe.nome}!")
                self.aplicar_efeito_item(alma_chefe)
                
            return True
        elif self.jogador_atual.vida <= 0:
            print(f"\n💀 DERROTA! {inimigo.nome} te derrotou...")
            self.jogador_atual.sanidade = max(0, self.jogador_atual.sanidade - 10)
            return False
        else:
            return False

    def turno_jogador(self, inimigo: Inimigo) -> bool:
        tipo_arma = "🔫" if self.jogador_atual.arma_atual.tipo == "distancia" else "⚔️"
        balas_info = ""
        
        if not self.jogador_atual.tem_arma_equipada("direita") and self.jogador_atual.arma_atual.tipo == "corpo_a_corpo":
            print("❌ Você não tem uma arma de corpo a corpo equipada!")
            return True
            
        if self.jogador_atual.arma_atual.tipo == "distancia":
            if not self.jogador_atual.arma_mao_esquerda:
                print("❌ Você não tem uma arma de distância equipada!")
                return True
            balas_info = f" | Balas: {self.jogador_atual.arma_mao_esquerda.balas}/{self.jogador_atual.arma_mao_esquerda.balas_maximas}"
            
        print(f"\nSua vez - Arma: {tipo_arma} {self.jogador_atual.arma_atual.nome}{balas_info}")
        print(f"Poções: {self.jogador_atual.pocoes_cura}/{self.jogador_atual.pocoes_cura_maximas}❤️ | Stamina: {self.jogador_atual.stamina}⚡")
        print("1. Atacar")
        if self.jogador_atual.arma_mao_esquerda:
            print("2. Atirar")
        else:
            print("2. Atirar (❌ Sem arma de distância)")
        print("3. Defender")
        print("4. Curar")
        print("5. Esquivar")
        
        if inimigo.eh_chefe:
            print("6. Tentar contra-ataque (arriscado)")
        else:
            print("6. Fugir (50% chance)")
        
        escolha = input("Escolha uma ação: ").strip()
        
        if escolha == "1":
            if not self.jogador_atual.tem_arma_equipada("direita"):
                print("❌ Você não tem uma arma de corpo a corpo equipada!")
                return True
                
            if self.jogador_atual.stamina >= self.jogador_atual.arma_atual.custo_stamina:
                resultado = self.executar_ataque(inimigo)
                return resultado
            else:
                print("\n❌ Stamina insuficiente!")
                return True
                
        elif escolha == "2":
            if not self.jogador_atual.arma_mao_esquerda:
                print("❌ Você não tem uma arma de distância equipada!")
                return True
                
            if self.jogador_atual.arma_mao_esquerda.balas <= 0:
                print("❌ Sem balas!")
                return True
                
            if self.jogador_atual.stamina >= self.jogador_atual.arma_mao_esquerda.custo_stamina:
                self.jogador_atual.arma_mao_esquerda.balas -= 1
                
                arma_original = self.jogador_atual.arma_atual
                self.jogador_atual.arma_atual = self.jogador_atual.arma_mao_esquerda
                resultado = self.executar_ataque(inimigo)
                self.jogador_atual.arma_atual = arma_original
                return resultado
            else:
                print("\n❌ Stamina insuficiente!")
                return True
              
        elif escolha == "3":
            self.jogador_atual.defesa_temporaria = 10
            self.jogador_atual.restaurar_stamina(20)
            print(f"🛡️ Você se defende! +10 defesa temporária (+20 stamina)")
            return True
            
        elif escolha == "4":
            if self.jogador_atual.curar():
                print(f"❤️ Você usa uma poção de cura! ({self.jogador_atual.pocoes_cura}/{self.jogador_atual.pocoes_cura_maximas} restantes)")
            else:
                print("❌ Sem poções de cura disponíveis!")
            return True
        
        elif escolha == "5":
            if self.jogador_atual.stamina >= 15:
                self.jogador_atual.stamina -= 15
                self.jogador_atual.esquivar_proximo_ataque = True
                print("🤸 Você se prepara para esquivar do próximo ataque! (-15 stamina)")
                return True
            else:
                print("Stamina insuficiente!")
                return True
                           
        elif escolha == "6":
            if inimigo.eh_chefe:
                if random.random() < 0.3:
                    dano_base = self.jogador_atual.obter_dano_total() * 2
                    dano_total = max(1, dano_base)
                    inimigo.vida -= dano_total
                    print(f"💥 CONTRA-ATAQUE CRÍTICO! {dano_total} de dano!")
                else:
                    print("❌ Contra-ataque falhou! Você ficou exposto.")
                    self.jogador_atual.receber_dano(inimigo.dano)
                return True
            else:
                if random.random() < 0.5:
                    print("\n🏃‍♂️ Fuga bem sucedida!")
                    return False
                else:
                    print("\n❌ Fuga falhou!")
                    return True
        else:
            print("Ação inválida ou stamina insuficiente!")
            return True

    def executar_ataque(self, inimigo: Inimigo) -> bool:
        dano_total = self.jogador_atual.obter_dano_total()
        
        if self.jogador_atual.arma_atual.tipo == "corpo_a_corpo":
            chance_atordoar_total = self.jogador_atual.chance_atordoar_acumulada
        else:
            chance_atordoar_total = self.jogador_atual.arma_atual.chance_atordoar + self.jogador_atual.chance_atordoar_base
        
        stamina_gasta = self.jogador_atual.arma_atual.custo_stamina
        if self.jogador_atual.anel_clorantio:
            stamina_gasta = max(1, int(stamina_gasta * 0.9))
        
        self.jogador_atual.stamina -= stamina_gasta
        
        inimigo.vida -= dano_total
        
        tipo_ataque = "\n🔫 Atirou" if self.jogador_atual.arma_atual.tipo == "distancia" else "\n🗡️ Atacou"
        balas_info = f" | Balas restantes: {self.jogador_atual.arma_mao_esquerda.balas}/{self.jogador_atual.arma_mao_esquerda.balas_maximas}" if self.jogador_atual.arma_atual.tipo == "distancia" else ""
        
        print(f"{tipo_ataque} causando {dano_total} de dano! (-{stamina_gasta} stamina){balas_info}")
        print(f"⚡ Stamina atual: {self.jogador_atual.stamina}/{self.jogador_atual.stamina_maxima}")
        
        if random.random() < chance_atordoar_total:
            inimigo.turnos_atordoado = 2
            print("💫 INIMIGO ATORDOADO! Ele perderá 2 turnos!")
        
        return True

    def turno_inimigo(self, inimigo: Inimigo):
        if inimigo.turnos_atordoado > 0:
            inimigo.turnos_atordoado -= 1
            print(f"💫 {inimigo.nome} está atordoado e perde o turno!")
            return
        
        tipo_ataque = inimigo.padrao_ataque[inimigo.indice_padrao_atual]
        inimigo.indice_padrao_atual = (inimigo.indice_padrao_atual + 1) % len(inimigo.padrao_ataque)
        
        dano = inimigo.dano
        if tipo_ataque == "ataque_pesado":
            dano = int(inimigo.dano * 1.5)
            print(f"💥 {inimigo.nome} usa ATAQUE PESADO!")
        elif tipo_ataque == "investida":
            dano = int(inimigo.dano * 1.3)
            print(f"⚡ {inimigo.nome} avança rapidamente!")
        else:
            print(f"👊 {inimigo.nome} ataca!")
        
        dano_real = self.jogador_atual.receber_dano(dano)
        if dano_real > 0:
            print(f"💔 Você sofre {dano_real} de dano!")
        else:
            print(f"🎯 Você desviou do ataque!")
        
        if random.random() < inimigo.chance_atordoar_jogador:
            self.jogador_atual.turnos_atordoado = 1
            print("💫 Você foi ATORDOADO! Perderá 1 turno!")
        
        if random.random() < 0.2:
            condicoes_possiveis = [Condicao.VENENO, Condicao.QUEIMADURA, Condicao.MEDO]
            if inimigo.nome == "Lobisomem" and Condicao.QUEIMADURA in condicoes_possiveis:
                condicoes_possiveis.remove(Condicao.QUEIMADURA)
            
            if inimigo.eh_chefe:
                condicoes_possiveis.append(Condicao.FRENESI)
            
            condicao = random.choice(condicoes_possiveis)
            self.jogador_atual.adicionar_condicao(condicao)
            print(f"⚠️ Condição aplicada: {condicao.name}!")

    def processar_fim_avl(self, contador_avls: int, eventos_sobrevividos: int):
        jogador_morreu = (self.jogador_atual.vida <= 0)
        
        no_jogador = self.encontrar_jogador(self.ranking, self.jogador_atual.nome)
        if no_jogador:
            if eventos_sobrevividos > no_jogador.record_eventos:
                no_jogador.record_eventos = eventos_sobrevividos
            no_jogador.chefes_derrotados += self.jogador_atual.chefes_derrotados_atual
            no_jogador.total_avls = len(no_jogador.historico_avls)
        
        if jogador_morreu:
            self.total_mortes += 1
            if no_jogador:
                no_jogador.contador_mortes += 1
            almas_perdidas = self.jogador_atual.resetar_almas_ao_morrer()
            
            print(f"\n💀 AVL {contador_avls} FINALIZADA - VOCÊ MORREU")
            print(f"💸 Você perdeu {almas_perdidas} almas não salvas!")
            print(f"☠️ Total de mortes: {no_jogador.contador_mortes if no_jogador else 1}")
            sanidade_anterior = self.jogador_atual.sanidade
            self.jogador_atual.sanidade = max(0, self.jogador_atual.sanidade - 10)
            print(f"😶 Sanidade reduzida de {sanidade_anterior} para {self.jogador_atual.sanidade}")
        else:
            print(f"\n🏁 AVL {contador_avls} FINALIZADA - VOCÊ SOBREVIVEU")
            
        print(f"📊 Eventos sobrevividos: {eventos_sobrevividos}")
        print(f"🏹 Chefes derrotados: {self.jogador_atual.chefes_derrotados_atual}")
        print(f"🏆 Pontuação final: {self.jogador_atual.pontuacao_avl_atual}")
        print(f"🔥 Fogueiras encontradas: {self.jogador_atual.fogueiras_encontradas}")
        print(f"🧠 Sanidade máxima alcançada: {self.jogador_atual.sanidade}")
        
        if self.jogador_atual.pontuacao_avl_atual > 0:
            existente = self.encontrar_jogador(self.ranking, self.jogador_atual.nome)
            if not existente or self.jogador_atual.pontuacao_avl_atual > existente.pontuacao_recorde:
                self.ranking = self.inserir_avl(self.ranking, self.jogador_atual.nome, 
                                             self.jogador_atual.pontuacao_avl_atual)
                print(f"💾 Novo recorde salvo: {self.jogador_atual.pontuacao_avl_atual} almas!")

    # ===== SISTEMA DE FOGUEIRA =====

    def lidar_com_fogueira(self) -> bool:
        self.melhorias_usadas_na_fogueira = False
        
        while True:
            print(f"\n🔥 FOGUEIRA - Almas: {self.jogador_atual.almas}")
            print("=" * 40)
            print("1. Descansar (restaurar vida e poções)")
            if not self.melhorias_usadas_na_fogueira:
                print("2. Melhorar atributos (APENAS UMA VEZ)")
            else:
                print("2. Melhorar atributos (JÁ UTILIZADO)")
            print("3. Trocar arma")
            print("4. Usar ferros guardados")  
            print("5. Ver Status")
            print("6. Ver Ranking da Árvore AVL")
            print("7. Ver Meu Histórico de AVLs")
            print("8. Continuar jornada")
            
            escolha = input("\nEscolha uma ação: ").strip()
            
            if escolha == "1":
                self.jogador_atual.vida = self.jogador_atual.vida_maxima
                self.jogador_atual.pocoes_cura = self.jogador_atual.pocoes_cura_maximas
                self.jogador_atual.stamina = self.jogador_atual.stamina_maxima
                self.jogador_atual.curar_condicoes_na_fogueira()
                self.jogador_atual.adicionar_sanidade(-30)
                
                self.jogador_atual.fogueiras_encontradas += 1
                print(f"\n❤️ Vida e poções restauradas! ({self.jogador_atual.pocoes_cura_maximas} poções) Sanidade reduzida.")
                print("💾 Progresso salvo na Árvore AVL!")
                
            elif escolha == "2":
                if not self.melhorias_usadas_na_fogueira:
                    self.menu_melhorias()
                    self.melhorias_usadas_na_fogueira = True
                else:
                    print("❌ Você já utilizou os upgrades nesta fogueira!")
                    
            elif escolha == "3":
                self.menu_armas()
                
            elif escolha == "4": 
                self.usar_ferros_guardados()
                
            elif escolha == "5":
                self.jogador_atual.mostrar_status()
                
            elif escolha == "6":
                self.imprimir_ranking(5)
                
            elif escolha == "7":
                self.imprimir_historico_jogador()
                
            elif escolha == "8":
                print("\n🚶‍♂️ Você continua sua jornada...")
                return True
            else:
                print("Opção inválida!")

    def menu_melhorias(self):
        while True:
            print("\n🛠️ MELHORIAS - Gastar almas para evoluir")
            print(f"Almas disponíveis: {self.jogador_atual.almas}")
            print("1. +1 Dano Base (100 almas)")
            print("2. +10 Vida máxima (80 almas)")
            print("3. +5 Defesa (120 almas)")
            print("4. +1 Poção de cura (150 almas)")
            print("5. +1% Chance de Atordoar para Armas (200 almas)")
            print("6. Voltar")
            
            escolha = input("Escolha melhoria: ").strip()
            
            if escolha == "6":
                break
                
            if escolha == "1" and self.jogador_atual.almas >= 100:
                self.jogador_atual.dano_base += 1
                self.jogador_atual.dano += 1
                self.jogador_atual.almas -= 100
                print("\n🗡️ Dano base aumentado em +1!")
            elif escolha == "2" and self.jogador_atual.almas >= 80:
                self.jogador_atual.vida_maxima += 10
                self.jogador_atual.vida += 10
                self.jogador_atual.almas -= 80
                print("\n❤️ Vida máxima aumentada em +10!")
            elif escolha == "3" and self.jogador_atual.almas >= 120:
                self.jogador_atual.defesa += 5
                self.jogador_atual.almas -= 120
                print("\n🛡️ Defesa aumentada em +5!")
            elif escolha == "4" and self.jogador_atual.almas >= 150:
                self.jogador_atual.pocoes_cura_maximas += 1
                self.jogador_atual.pocoes_cura = self.jogador_atual.pocoes_cura_maximas
                self.jogador_atual.almas -= 150
                print(f"\n🧪 +1 Poção de cura! (Total: {self.jogador_atual.pocoes_cura_maximas})")
            elif escolha == "5" and self.jogador_atual.almas >= 200:
                if self.jogador_atual.chance_atordoar_base < 0.8:
                    self.jogador_atual.chance_atordoar_base += 0.001  
                    if self.jogador_atual.arma_mao_esquerda:
                        self.jogador_atual.arma_mao_esquerda.chance_atordoar += 0.01
                    print(f"\n🎯 Chance de atordoar aumentada!")
                    print(f"   - Chance base: {self.jogador_atual.chance_atordoar_base*100:.1f}%")
                    if self.jogador_atual.arma_mao_esquerda:
                        print(f"   - Arma esquerda: {self.jogador_atual.arma_mao_esquerda.chance_atordoar*100:.1f}%")
                    self.jogador_atual.almas -= 200
                else:
                    print("\n❌ Chance de atordoar já está no máximo (80%)!")
            else:
                print("\n❌ Almas insuficientes ou escolha inválida!")

    def usar_ferros_guardados(self):
        while True:
            print(f"\n🛡️ FERROS GUARDADOS")
            print("=" * 30)
            
            tem_ferros = False
            for ferro, quantidade in self.jogador_atual.ferros_guardados.items():
                if quantidade > 0:
                    print(f"{ferro}: {quantidade}")
                    tem_ferros = True
            
            if not tem_ferros:
                print("Nenhum ferro guardado no momento.")
                break
            
            print("\nEscolha um ferro para usar:")
            print("1. Fragmento de Ferro")
            print("2. Pedaco de Ferro") 
            print("3. Lajota de Ferro")
            print("4. Voltar")
            
            escolha = input("Escolha: ").strip()
            
            if escolha == "4":
                break
            
            ferro_map = {
                "1": "Fragmento de Ferro",
                "2": "Pedaco de Ferro", 
                "3": "Lajota de Ferro"
            }
            
            ferro_nome = ferro_map.get(escolha)
            if not ferro_nome:
                print("Escolha inválida!")
                continue
            
            if self.jogador_atual.ferros_guardados[ferro_nome] <= 0:
                print(f"❌ Você não tem {ferro_nome} guardado!")
                continue
            
            print(f"\nAplicar {ferro_nome} em qual arma?")
            armas_disponiveis = []
            
            if self.jogador_atual.arma_mao_direita:
                armas_disponiveis.append(("Direita", self.jogador_atual.arma_mao_direita))
            if self.jogador_atual.arma_mao_esquerda:
                armas_disponiveis.append(("Esquerda", self.jogador_atual.arma_mao_esquerda))
            
            for i, (mao, arma) in enumerate(armas_disponiveis, 1):
                melhorias_atuais = arma.melhorias_aplicadas[ferro_nome]
                limite = arma.limites_melhorias[ferro_nome] 
                print(f"{i}. Mão {mao}: {arma.nome} (Dano: +{arma.dano}, {ferro_nome}: {melhorias_atuais}/{limite})")
            
            print(f"{len(armas_disponiveis) + 1}. Voltar")
            
            try:
                escolha_arma = int(input("Escolha arma: "))
                if escolha_arma == len(armas_disponiveis) + 1:
                    continue
                
                if 1 <= escolha_arma <= len(armas_disponiveis):
                    mao, arma = armas_disponiveis[escolha_arma - 1]
                    item_ferro = self.itens[ferro_nome]
                    
                    if arma.melhorias_aplicadas[ferro_nome] < arma.limites_melhorias[ferro_nome]:
                        arma.dano += item_ferro.valor
                        arma.melhorias_aplicadas[ferro_nome] += 1
                        self.jogador_atual.ferros_guardados[ferro_nome] -= 1
                        print(f"✅ {ferro_nome} aplicado na {arma.nome}! Dano: +{arma.dano} ({arma.melhorias_aplicadas[ferro_nome]}/{arma.limites_melhorias[ferro_nome]})")
                    else:
                        print(f"❌ {arma.nome} já atingiu o limite de {ferro_nome}!")
                else:
                    print("Escolha inválida!")
            except (ValueError, IndexError):
                print("Escolha inválida!")

    def menu_armas(self):
        while True:
            print("\n⚔️ ARMAS - Escolha sua arma")
            print(f"Arma atual (mão direita): {self.jogador_atual.arma_mao_direita.nome if self.jogador_atual.arma_mao_direita else 'Nenhuma'} (Dano: +{self.jogador_atual.arma_mao_direita.dano if self.jogador_atual.arma_mao_direita else 0})")
            print(f"Arma atual (mão esquerda): {self.jogador_atual.arma_mao_esquerda.nome if self.jogador_atual.arma_mao_esquerda else 'Nenhuma'} (Dano: +{self.jogador_atual.arma_mao_esquerda.dano if self.jogador_atual.arma_mao_esquerda else 0})")
            
            print("\n🪓 ARMAS DE MÃO DIREITA (Corpo a Corpo):")
            armas_direita = []
            indice = 1
            for nome_arma in self.jogador_atual.armas_encontradas:
                arma = self.armas.get(nome_arma)
                if arma and arma.tipo == "corpo_a_corpo":
                    print(f"{indice}. ⚔️ {nome_arma} (Dano: +{arma.dano}, Stamina: {arma.custo_stamina})")
                    armas_direita.append(nome_arma)
                    indice += 1
            
            print("\n🔫 ARMAS DE MÃO ESQUERDA (Distância):")
            armas_esquerda = []
            for nome_arma in self.jogador_atual.armas_encontradas:
                arma = self.armas.get(nome_arma)
                if arma and arma.tipo == "distancia":
                    balas_info = f" | Balas: {arma.balas}/{arma.balas_maximas}" if arma.tipo == "distancia" else ""
                    print(f"{indice}. 🔫 {nome_arma} (Dano: +{arma.dano}, Stamina: {arma.custo_stamina}{balas_info})")
                    armas_esquerda.append(nome_arma)
                    indice += 1
            
            print(f"\n{indice}. Voltar")
            
            try:
                escolha = int(input("Escolha arma: "))
                if escolha == indice:
                    break
                    
                if 1 <= escolha <= len(armas_direita):
                    nome_arma = armas_direita[escolha - 1]
                    arma_nova = self.armas[nome_arma]
                    if self.jogador_atual.arma_mao_direita:
                        dano_extra = self.jogador_atual.arma_mao_direita.dano - self.jogador_atual.arma_mao_direita.dano_base
                        arma_nova.dano = arma_nova.dano_base + dano_extra
                        arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_direita.melhorias_aplicadas.copy()
                        arma_nova.limites_melhorias = self.jogador_atual.arma_mao_direita.limites_melhorias.copy()
                    self.jogador_atual.arma_mao_direita = arma_nova
                    self.jogador_atual.arma_atual = arma_nova
                    print(f"✅ Arma equipada na mão direita: {nome_arma} (Dano: +{arma_nova.dano})")
                elif len(armas_direita) < escolha <= len(armas_direita) + len(armas_esquerda):
                    nome_arma = armas_esquerda[escolha - len(armas_direita) - 1]
                    arma_nova = self.armas[nome_arma]
                    if self.jogador_atual.arma_mao_esquerda:
                        dano_extra = self.jogador_atual.arma_mao_esquerda.dano - self.jogador_atual.arma_mao_esquerda.dano_base
                        arma_nova.dano = arma_nova.dano_base + dano_extra
                        arma_nova.melhorias_aplicadas = self.jogador_atual.arma_mao_esquerda.melhorias_aplicadas.copy()
                        arma_nova.limites_melhorias = self.jogador_atual.arma_mao_esquerda.limites_melhorias.copy()
                    self.jogador_atual.arma_mao_esquerda = arma_nova
                    print(f"✅ Arma equipada na mão esquerda: {nome_arma} (Dano: +{arma_nova.dano})")
                else:
                    print("Escolha inválida!")
            except (ValueError, IndexError):
                print("Escolha inválida!")

    # ===== SISTEMA DE SANIDADE =====

    def obter_efeitos_sanidade(self):
        sanidade = self.jogador_atual.sanidade
        efeitos = []
        
        if sanidade > 80:
            efeitos.append("👁️  Criaturas bizarras aparecem frequentemente")
            efeitos.append("💀 Chance de inimigos 1-hit kill")
            efeitos.append("⚡ Penalidades de defesa e esquiva")
        elif sanidade > 60:
            efeitos.append("👻 Mini-chefes em áreas comuns")
            efeitos.append("🎯 Ataques críticos inimigos aumentados")
            efeitos.append("🌌 Eventos sobrenaturais intensos")
        elif sanidade > 40:
            efeitos.append("😰 Inimigos mais agressivos")
            efeitos.append("💎 Eventos raros mais frequentes")
        
        return efeitos

    # ===== FLUXO PRINCIPAL DO JOGO =====

    def criar_jogador(self):
        nome = input("\nDigite o nome do seu personagem: ").strip()
        if not nome:
            nome = "AVL Perdida"
        
        self.jogador_atual = Jogador(nome)
        
        existente = self.encontrar_jogador(self.ranking, nome)
        if existente:
            print(f"Bem-vindo de volta, {nome}! Seu recorde é {existente.pontuacao_recorde} almas.")
        else:
            print(f"Novo AVL criado: {nome}")
        
        print("\n🎮 JOGADOR CRIADO!")
        print(f"Nome: {self.jogador_atual.nome}")
        print(f"Vida: {self.jogador_atual.vida}")
        print(f"Dano Base: {self.jogador_atual.dano_base}")
        print(f"Arma Mão Direita: {self.jogador_atual.arma_mao_direita.nome} (Dano: +{self.jogador_atual.arma_mao_direita.dano})")
        print(f"Arma Mão Esquerda: {self.jogador_atual.arma_mao_esquerda.nome} (Dano: +{self.jogador_atual.arma_mao_esquerda.dano})")
        print(f"Poções: {self.jogador_atual.pocoes_cura}/{self.jogador_atual.pocoes_cura_maximas}")

    def obter_entrada_sim_nao_valida(self, prompt: str) -> str:
        while True:
            escolha = input(prompt).strip().lower()
            if escolha in ['s', 'n']:
                return escolha
            else:
                print("❌ Por favor, digite apenas 's' para SIM ou 'n' para NÃO")

    def loop_jogo(self):
        print("\n🌑 INSALUBRE SURVIVOR 🌑")
        print("A Árvore AVL aguarda sua jornada...")
        
        contador_avls = 0
        while True:
            contador_avls += 1
            print(f"\n🏃‍♂️ AVL {contador_avls} INICIADA")
            
            self.jogador_atual.ferros_guardados = {
                "Fragmento de Ferro": 0,
                "Pedaco de Ferro": 0,
                "Lajota de Ferro": 0
            }
            
            self.jogador_atual.vida = self.jogador_atual.vida_maxima
            self.jogador_atual.stamina = self.jogador_atual.stamina_maxima
            self.jogador_atual.pontuacao_avl_atual = 0
            self.jogador_atual.condicoes.clear()
            self.jogador_atual.pocoes_cura = self.jogador_atual.pocoes_cura_maximas
            self.jogador_atual.almas = 0
            self.jogador_atual.record_eventos_atual = 0
            self.jogador_atual.chefes_derrotados_atual = 0
            self.turno_atual = 0
            self.recarga_fogueira = 0
            self.escala_dificuldade = 1.0
            self.contador_buff_inimigos = 0
            
            eventos_sobrevividos = 0
            continuar_jogo = True
            
            while continuar_jogo and self.jogador_atual.vida > 0:
                eventos_sobrevividos += 1
                self.jogador_atual.record_eventos_atual = eventos_sobrevividos
                
                print(f"\n📍 Evento {eventos_sobrevividos} | "
                      f"Vida: {self.jogador_atual.vida} | "
                      f"Almas: {self.jogador_atual.almas} | "
                      f"Sanidade: {self.jogador_atual.sanidade}")
                
                efeitos_sanidade = self.obter_efeitos_sanidade()
                if efeitos_sanidade:
                    print("Efeitos da Sanidade:", " | ".join(efeitos_sanidade))
                
                input("\nPressione Enter para continuar...")
                
                evento = self.gerar_evento()
                continuar_jogo = self.lidar_com_evento(evento)
            
            self.processar_fim_avl(contador_avls, eventos_sobrevividos)
            
            escolha_continuar = self.obter_entrada_sim_nao_valida("\nDeseja iniciar uma nova AVL? (s/n): ")
            if escolha_continuar != 's':
                break

    def menu_principal(self):
        while True:
            print("\n" + "="*60)
            print("🌑 INSALUBRE SURVIVOR")
            print("="*60)
            print("1. Iniciar Nova AVL")
            print("2. Ver Ranking da Árvore AVL")
            print("3. Estatísticas do Mundo")
            print("4. Sair")
            
            escolha = input("\nEscolha uma opção: ").strip()
            
            if escolha == "1":
                self.criar_jogador()
                self.loop_jogo()
            elif escolha == "2":
                self.imprimir_ranking()
            elif escolha == "3":
                self.mostrar_estatisticas()
            elif escolha == "4":
                print("\nQue suas AVLs ecoem pela eternidade...")
                break
            else:
                print("Opção inválida!")

    def mostrar_estatisticas(self):
        print("\n📊 ESTATÍSTICAS DO MUNDO INSALUBRE")
        print("="*40)
        print(f"Total de mortes: {self.total_mortes}")
        print(f"Total de jogadores: {self.contar_jogadores(self.ranking)}")
        
        if self.jogador_atual:
            no_jogador = self.encontrar_jogador(self.ranking, self.jogador_atual.nome)
            if no_jogador:
                print(f"\n📈 ESTATÍSTICAS DE {self.jogador_atual.nome}:")
                print(f"Recorde pessoal: {no_jogador.pontuacao_recorde} almas")
                print(f"Recorde de eventos: {no_jogador.record_eventos}")
                print(f"Chefes derrotados: {no_jogador.chefes_derrotados}")
                print(f"Total de AVLs: {no_jogador.total_avls}")
                print(f"Total de mortes: {no_jogador.contador_mortes}")
                if no_jogador.historico_avls:
                    pontuacao_media = sum(no_jogador.historico_avls) / len(no_jogador.historico_avls)
                    print(f"Média de pontuação: {pontuacao_media:.1f} almas")

    def contar_jogadores(self, no: NoAVL) -> int:
        if not no:
            return 0
        return 1 + self.contar_jogadores(no.esquerda) + self.contar_jogadores(no.direita)

# ===== API FLASK PARA O RANKING (SEM flask-cors) =====
from flask import Flask, jsonify, request, make_response
import threading
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Middleware CORS manual
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Rota para lidar com OPTIONS (pré-flight)
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Variável global para o jogo
jogo_global = None

def iniciar_api():
    """Inicia a API Flask em uma thread separada"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def obter_data_entrada_aleatoria():
    """Data de entrada aleatória (últimos 30 dias)"""
    dias_atras = random.randint(1, 30)
    data = datetime.now() - timedelta(days=dias_atras)
    return data.strftime("%Y-%m-%d")

def obter_ultima_atividade_aleatoria():
    """Última atividade aleatória (últimas 24 horas)"""
    horas_atras = random.randint(0, 24)
    data = datetime.now() - timedelta(hours=horas_atras)
    return data.strftime("%Y-%m-%d %H:%M")

def calcular_conquistas_reais(no_jogador):
    """Calcula conquistas baseadas nos dados reais do jogador"""
    conquistas = 0
    
    # Conquista 1: Pontuação alta
    if no_jogador.pontuacao_recorde >= 10000:
        conquistas += 1
    
    # Conquista 2: Muitos chefes derrotados
    if no_jogador.chefes_derrotados >= 10:
        conquistas += 1
    
    # Conquista 3: Muitos eventos sobrevividos
    if no_jogador.record_eventos >= 50:
        conquistas += 1
    
    # Conquista 4: Muitas AVLs
    if no_jogador.total_avls >= 10:
        conquistas += 1
    
    # Conquista 5: Poucas mortes
    if no_jogador.contador_mortes <= 3 and no_jogador.total_avls >= 5:
        conquistas += 1
    
    return min(10, conquistas + random.randint(0, 2))  # Adiciona 0-2 conquistas aleatórias

@app.route('/api/ranking', methods=['GET'])
def obter_ranking():
    """Retorna o ranking completo dos jogadores"""
    global jogo_global
    
    if not jogo_global or not jogo_global.ranking:
        return jsonify({
            "jogadores": [],
            "total": 0,
            "estatisticas": {
                "total_jogadores": 0,
                "pontuacao_media": 0,
                "total_chefes": 0,
                "total_eventos": 0,
                "taxa_vitoria_media": 0,
                "jogadores_ativos": 0
            }
        })
    
    resultados = []
    
    def coletar_jogadores(no):
        if no:
            coletar_jogadores(no.esquerda)
            
            # Calcular taxa de vitória (simplificada)
            total_avls = no.total_avls
            mortes = no.contador_mortes
            vitorias = max(0, total_avls - mortes)
            taxa_vitoria = int((vitorias / total_avls * 100)) if total_avls > 0 else 0
            
            # Usar dados reais do jogo, não aleatórios
            jogador_data = {
                "id": len(resultados) + 1,
                "nome": no.nome_jogador,
                "pontuacao": no.pontuacao_recorde,
                "chefes": no.chefes_derrotados,
                "eventos": no.record_eventos,
                "mortes": mortes,
                "avls": total_avls,
                "taxa_vitoria": taxa_vitoria,
                "classe": "Guerreiro",  # Classe padrão
                "classe_id": "warrior",
                "classe_color": "#ff6b6b",
                "status": "offline",
                "status_name": "Offline",
                "status_color": "#666",
                "nivel": calcular_nivel(no.pontuacao_recorde),
                "sanidade": 50,  # Valor padrão
                "apelido": f"Jogador_{no.nome_jogador}",
                "tempo_jogo": calcular_tempo_jogo(total_avls),
                "equipamento": {
                    "arma_principal": "Espada Longa",
                    "dano": calcular_dano(no.pontuacao_recorde)
                },
                "data_entrada": obter_data_entrada_aleatoria(),
                "ultima_atividade": obter_ultima_atividade_aleatoria(),
                "conquistas": calcular_conquistas_reais(no)
            }
            
            resultados.append(jogador_data)
            coletar_jogadores(no.direita)
    
    coletar_jogadores(jogo_global.ranking)
    
    # Ordenar por pontuação (maior primeiro)
    resultados.sort(key=lambda x: x["pontuacao"], reverse=True)
    
    # Adicionar ranking
    for i, jogador in enumerate(resultados):
        jogador["rank"] = i + 1
    
    # Calcular estatísticas REAIS
    if resultados:
        pontuacao_media = sum(j["pontuacao"] for j in resultados) // len(resultados)
        total_chefes = sum(j["chefes"] for j in resultados)
        total_eventos = sum(j["eventos"] for j in resultados)
        taxa_vitoria_media = sum(j["taxa_vitoria"] for j in resultados) // len(resultados)
        jogadores_ativos = 0  # Sempre 0 pois não temos tracking de status real
    else:
        pontuacao_media = total_chefes = total_eventos = taxa_vitoria_media = jogadores_ativos = 0
    
    return jsonify({
        "jogadores": resultados,
        "total": len(resultados),
        "estatisticas": {
            "total_jogadores": len(resultados),
            "pontuacao_media": pontuacao_media,
            "total_chefes": total_chefes,
            "total_eventos": total_eventos,
            "taxa_vitoria_media": taxa_vitoria_media,
            "jogadores_ativos": jogadores_ativos
        }
    })

@app.route('/api/jogador/<nome>', methods=['GET'])
def obter_jogador(nome):
    """Retorna detalhes de um jogador específico"""
    global jogo_global
    
    if not jogo_global:
        return jsonify({"error": "Jogo não inicializado"}), 500
    
    no_jogador = jogo_global.encontrar_jogador(jogo_global.ranking, nome)
    
    if not no_jogador:
        return jsonify({"error": "Jogador não encontrado"}), 404
    
    # Calcular estatísticas
    total_avls = no_jogador.total_avls
    mortes = no_jogador.contador_mortes
    vitorias = max(0, total_avls - mortes)
    taxa_vitoria = int((vitorias / total_avls * 100)) if total_avls > 0 else 0
    
    # Histórico de pontuações
    historico = no_jogador.historico_avls[-10:] if no_jogador.historico_avls else []
    
    # Obter dados complementares
    classe_info = obter_classe_aleatoria()
    status_info = obter_status_aleatorio()
    
    jogador_info = {
        "nome": no_jogador.nome_jogador,
        "classe": classe_info["nome"],
        "classe_id": classe_info["id"],
        "classe_color": classe_info["color"],
        "apelido": obter_apelido_aleatorio(),
        "status": status_info["id"],
        "status_name": status_info["name"],
        "status_color": status_info["color"],
        "nivel": calcular_nivel(no_jogador.pontuacao_recorde),
        "pontuacao": no_jogador.pontuacao_recorde,
        "chefes": no_jogador.chefes_derrotados,
        "eventos": no_jogador.record_eventos,
        "mortes": mortes,
        "avls": total_avls,
        "taxa_vitoria": taxa_vitoria,
        "tempo_jogo": calcular_tempo_jogo(total_avls),
        "data_entrada": obter_data_entrada(),
        "ultima_atividade": obter_ultima_atividade(),
        "conquistas": calcular_conquistas(no_jogador),
        "sanidade": random.randint(10, 90),
        "equipamento": {
            "mainHand": {
                "name": obter_arma_aleatoria(),
                "damage": calcular_dano(no_jogador.pontuacao_recorde)
            },
            "offHand": {
                "name": obter_arma_aleatoria() if random.random() > 0.5 else None,
                "damage": calcular_dano(no_jogador.pontuacao_recorde) // 2 if random.random() > 0.5 else 0
            } if random.random() > 0.3 else None,
            "armadura": obter_armadura_aleatoria()
        },
        "stats": {
            "strength": calcular_atributo("forca", no_jogador),
            "agility": calcular_atributo("agilidade", no_jogador),
            "intelligence": calcular_atributo("inteligencia", no_jogador),
            "vitality": calcular_atributo("vitalidade", no_jogador)
        },
        "historico": historico,
        "melhor_pontuacao": max(historico) if historico else 0,
        "pior_pontuacao": min(historico) if historico else 0,
        "media_pontuacao": sum(historico) / len(historico) if historico else 0,
        "achievements": calcular_conquistas(no_jogador),
        "playtime": calcular_tempo_jogo(total_avls),
        "level": calcular_nivel(no_jogador.pontuacao_recorde),
        "joinDate": obter_data_entrada(),
        "lastActive": obter_ultima_atividade()
    }
    
    return jsonify(jogador_info)

@app.route('/api/estatisticas', methods=['GET'])
def obter_estatisticas_gerais():
    """Retorna estatísticas gerais do jogo"""
    global jogo_global
    
    if not jogo_global:
        return jsonify({"error": "Jogo não inicializado"}), 500
    
    return jsonify({
        "total_mortes": jogo_global.total_mortes,
        "total_jogadores": jogo_global.contar_jogadores(jogo_global.ranking),
        "versao_jogo": "1.0.0",
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Funções auxiliares para gerar dados aleatórios
def obter_classe_aleatoria():
    classes = [
        {"id": "warrior", "nome": "Guerreiro", "color": "#ff6b6b"},
        {"id": "mage", "nome": "Mago", "color": "#4ecdc4"},
        {"id": "archer", "nome": "Arqueiro", "color": "#45b7d1"},
        {"id": "paladin", "nome": "Paladino", "color": "#ffd166"},
        {"id": "rogue", "nome": "Ladino", "color": "#96ceb4"},
        {"id": "berserker", "nome": "Berserker", "color": "#ff5252"},
        {"id": "necromancer", "nome": "Necromante", "color": "#a78bfa"},
        {"id": "knight", "nome": "Cavaleiro", "color": "#667eea"},
        {"id": "assassin", "nome": "Assassino", "color": "#43e97b"},
        {"id": "druid", "nome": "Druida", "color": "#38f9d7"}
    ]
    return random.choice(classes)

def obter_apelido_aleatorio():
    apelidos = ["Lâmina Sombria", "Senhor das Chamas", "Caçador Noturno", 
                "Guardião Ancestral", "Voz do Abismo", "Andarilho Solitário",
                "Mão da Justiça", "Olho da Tempestade", "Corvo Sábio", "Lobo Prateado"]
    return random.choice(apelidos)

def obter_status_aleatorio():
    status = [
        {"id": "online", "name": "Online", "color": "#43e97b"},
        {"id": "offline", "name": "Offline", "color": "#666"},
        {"id": "ingame", "name": "Em Jogo", "color": "#4facfe"}
    ]
    pesos = [0.3, 0.4, 0.3]
    return random.choices(status, weights=pesos)[0]

def obter_arma_aleatoria():
    armas = ["Espada Longa", "Cajado Arcano", "Arco Composto", "Martelo Sagrado",
             "Adagas Gêmeas", "Machado de Batalha", "Foice da Morte", "Lança de Cavaleiro",
             "Katana", "Cajado da Natureza", "Claymore", "Bacamarte", "Pistola"]
    return random.choice(armas)

def obter_armadura_aleatoria():
    armaduras = ["Armadura de Placas", "Túnica Arcana", "Couro Reforçado", 
                 "Manto Élfico", "Armadura Óssea", "Vestes Sagradas"]
    return random.choice(armaduras)

def calcular_nivel(pontuacao):
    return min(100, max(1, pontuacao // 1000 + 1))

def calcular_tempo_jogo(total_avls):
    return total_avls * 30 + random.randint(0, 100)  # 30 minutos por AVL em média

def calcular_dano(pontuacao):
    return min(500, max(10, pontuacao // 100 + random.randint(5, 20)))

def obter_data_entrada():
    dias_atras = random.randint(1, 365)
    data = datetime.now() - timedelta(days=dias_atras)
    return data.strftime("%Y-%m-%d")

def obter_ultima_atividade():
    horas_atras = random.randint(0, 168)  # 0 a 7 dias
    data = datetime.now() - timedelta(hours=horas_atras)
    return data.strftime("%Y-%m-%d")

def calcular_conquistas(no_jogador):
    conquistas = 0
    if no_jogador.pontuacao_recorde > 10000:
        conquistas += 1
    if no_jogador.chefes_derrotados > 10:
        conquistas += 1
    if no_jogador.record_eventos > 50:
        conquistas += 1
    if no_jogador.total_avls > 20:
        conquistas += 1
    return min(10, conquistas + random.randint(1, 5))

def calcular_atributo(tipo, no_jogador):
    base = 10
    if tipo == "forca":
        base += no_jogador.chefes_derrotados // 2
    elif tipo == "agilidade":
        base += no_jogador.record_eventos // 10
    elif tipo == "inteligencia":
        base += no_jogador.total_avls // 3
    elif tipo == "vitalidade":
        base += no_jogador.pontuacao_recorde // 2000
    
    return min(100, max(10, base + random.randint(-3, 3)))

# ===== EXECUÇÃO PRINCIPAL =====

if __name__ == "__main__":
    jogo_global = SobreviventeInsalubre()
    
    # Perguntar se quer iniciar a API
    print("\n" + "="*60)
    print("🌑 INSALUBRE SURVIVOR - COM API DE RANKING")
    print("="*60)
    print("🌐 DESEJA INICIAR A API DO RANKING?")
    print("1. Sim, iniciar API e jogo")
    print("2. Apenas o jogo (sem API)")
    print("3. Apenas a API (sem jogo)")
    print("4. Testar conexão com frontend")
    
    escolha = input("\nEscolha: ").strip()
    
    if escolha == "1":
        # Iniciar API em thread separada
        api_thread = threading.Thread(target=iniciar_api, daemon=True)
        api_thread.start()
        print("\n✅ API iniciada em http://127.0.0.1:5000")
        print("📊 Endpoints disponíveis:")
        print("   • GET /api/ranking        - Ranking completo")
        print("   • GET /api/jogador/<nome> - Detalhes do jogador")
        print("   • GET /api/estatisticas   - Estatísticas gerais")
        print("\n🌐 Acesse o ranking no navegador com o arquivo HTML fornecido")
        print("⏳ Aguardando 3 segundos para inicialização da API...")
        time.sleep(3)
        jogo_global.menu_principal()
        
    elif escolha == "2":
        jogo_global.menu_principal()
        
    elif escolha == "3":
        # Apenas API para testes
        print("\n🌐 INICIANDO APENAS A API...")
        print("📊 Acesse os endpoints em:")
        print("   • http://127.0.0.1:5000/api/ranking")
        print("   • http://127.0.0.1:5000/api/jogador/[nome]")
        print("   • http://127.0.0.1:5000/api/estatisticas")
        print("\n📁 Use o arquivo HTML fornecido para visualizar o ranking")
        iniciar_api()
        
    elif escolha == "4":
        # Modo teste rápido
        print("\n🔧 MODO TESTE RÁPIDO")
        print("Criando alguns jogadores de exemplo...")
        
        # Adicionar alguns jogadores de exemplo
        nomes_exemplo = ["Shadow", "Luna", "Thor", "Venom", "Nova", "Zephyr", "Orion", "Valkyrie"]
        for nome in nomes_exemplo:
            pontuacao = random.randint(5000, 25000)
            chefes = random.randint(5, 50)
            eventos = random.randint(20, 200)
            avls = random.randint(5, 30)
            mortes = random.randint(1, avls // 2)
            
            # Criar nó AVL manualmente
            novo_no = NoAVL(nome, pontuacao)
            novo_no.chefes_derrotados = chefes
            novo_no.record_eventos = eventos
            novo_no.total_avls = avls
            novo_no.contador_mortes = mortes
            novo_no.historico_avls = [random.randint(1000, pontuacao) for _ in range(avls)]
            
            # Inserir na árvore
            jogo_global.ranking = jogo_global.inserir_avl(jogo_global.ranking, nome, pontuacao)
            
            # Atualizar o nó inserido com os dados adicionais
            no_inserido = jogo_global.encontrar_jogador(jogo_global.ranking, nome)
            if no_inserido:
                no_inserido.chefes_derrotados = chefes
                no_inserido.record_eventos = eventos
                no_inserido.total_avls = avls
                no_inserido.contador_mortes = mortes
                no_inserido.historico_avls = [random.randint(1000, pontuacao) for _ in range(avls)]
        
        print(f"✅ {len(nomes_exemplo)} jogadores de exemplo criados!")
        
        # Iniciar API
        api_thread = threading.Thread(target=iniciar_api, daemon=True)
        api_thread.start()
        print("\n✅ API iniciada em http://127.0.0.1:5000")
        print("📊 Teste os endpoints:")
        print("   • http://127.0.0.1:5000/api/ranking")
        print("   • http://127.0.0.1:5000/api/jogador/Shadow")
        print("\n⏳ Iniciando jogo em 2 segundos...")
        time.sleep(2)
        jogo_global.menu_principal()
        
    else:
        print("Opção inválida! Iniciando apenas o jogo...")
        jogo_global.menu_principal()