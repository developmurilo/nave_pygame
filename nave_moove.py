import pygame
import random
from pygame.locals import *

# Inicializa o Pygame e os módulos de som
pygame.init()
pygame.mixer.init()

# Carrega sons para eventos do jogo
shot_laser = pygame.mixer.Sound("laser.ogg")  # Som para o tiro laser
shot_buble = pygame.mixer.Sound("bubble.wav")  # Som para o tiro de bolha
field = pygame.mixer.Sound("force_field.ogg")  # Som de ativação do campo de força
explodes_asteroid = pygame.mixer.Sound("explode_asteroid.ogg")  # Som de explosão de asteroides
collide_ship = pygame.mixer.Sound("colisao.ogg")  # Som de colisão da nave

# Configura música de fundo
pygame.mixer.music.load("music_game.ogg")  # Caminho da música de fundo
pygame.mixer.music.set_volume(0.5)  # Define o volume da música
pygame.mixer.music.play(loops=-1, start=0.0)  # Toca a música em loop infinito

# Configura a tela do jogo
screen = pygame.display.set_mode((800, 600))  # Define a resolução da tela
pygame.display.set_caption("Nave no espaço")  # Título da janela do jogo

# Carrega imagens de fundo e de fim de jogo
background = pygame.image.load("Fundo-galaxia.jpg")  # Fundo da galáxia
game_over = pygame.image.load("game_over.png")  # Tela de "game over"
clock = pygame.time.Clock()  # Relógio para controlar a taxa de atualização do jogo

# Fonte para textos
font = pygame.font.Font(None, 36)
font_pequena = pygame.font.Font(None, 20)

# Classe da nave espacial controlada pelo jogador
class NaveEspacial(pygame.sprite.Sprite):
    def __init__(self, name, position, speed):
        super().__init__()
        self.name = name  # Nome da nave
        self.alive = True  # Status de vida
        self.position = pygame.Vector2(position)  # Posição da nave
        self.speed = speed  # Velocidade de movimento
        self.shield = 100  # Pontos de escudo

        # Carrega imagens da nave e do campo de força
        self.image = pygame.image.load("nave-espacial.png")
        self.image = pygame.transform.scale(self.image, (50, 50))  # Redimensiona a imagem
        self.force_field_image = pygame.image.load("campo_de_forca.png")
        self.force_field_image = pygame.transform.scale(self.force_field_image, (100, 100))

        self.rect = self.image.get_rect(center=self.position)  # Define o retângulo da nave
        
        # Configuração do campo de força
        self.force_field = False  # Campo de força inicialmente desativado
        self.force_field_duration = 10000  # Duração do campo de força em milissegundos
        self.force_field_cooldown = 30000  # Tempo de espera para reutilização
        self.force_field_timer = 0  # Temporizador do campo de força
        self.last_activation_time = -self.force_field_cooldown  # Controle do tempo de ativação

    def activate_force_field(self):
        # Ativa o campo de força se estiver fora do tempo de espera
        current_time = pygame.time.get_ticks()
        if current_time - self.last_activation_time >= self.force_field_cooldown:
            self.force_field = True
            self.force_field_timer = self.force_field_duration
            self.last_activation_time = current_time

    def update(self):
        # Atualiza a posição da nave com base nas teclas pressionadas
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: self.position.x -= self.speed  
        if keys[K_RIGHT]: self.position.x += self.speed  
        if keys[K_UP]: self.position.y -= self.speed  
        if keys[K_DOWN]: self.position.y += self.speed  

        # Atualiza o status do campo de força
        if self.force_field:
            self.force_field_timer -= clock.get_time()
            if self.force_field_timer <= 0:
                self.force_field = False

        # Atualiza a posição do retângulo da nave
        self.rect.center = self.position

    def draw(self, screen):
        # Desenha a nave na tela
        screen.blit(self.image, self.rect)
        # Desenha o campo de força se estiver ativo
        if self.force_field:
            force_field_rect = self.force_field_image.get_rect(center=self.rect.center)
            screen.blit(self.force_field_image, force_field_rect)
            # Exibe o tempo restante do campo de força
            force_field_time_left = self.force_field_timer // 1000
            countdown_text = font.render(f'Campo de Força: {force_field_time_left}s', True, (0, 255, 255))
            screen.blit(countdown_text, (10, 50))

# Classe para tiros normais
class Tiro(pygame.sprite.Sprite):
    def __init__(self, position, speed_y=-8):
        super().__init__()
        self.image = pygame.image.load("Feixe_luz.PNG")  # Imagem do tiro
        self.image = pygame.transform.scale(self.image, (25, 35))  # Redimensiona a imagem
        self.rect = self.image.get_rect(center=position)
        self.speed_y = speed_y  # Velocidade vertical do tiro

    def update(self):
        # Move o tiro na tela
        self.rect.y += self.speed_y
        # Remove o tiro se sair da tela
        if self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()

# Classe para tiros de bolhas
class TiroBolha(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        # Cria uma superfície circular para representar a bolha
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 255, 128), (15, 15), 15)
        self.rect = self.image.get_rect(center=position)
        self.speed_y = -2  # Velocidade mais lenta para a bolha

    def update(self):
        # Move a bolha na tela
        self.rect.y += self.speed_y
        # Remove a bolha se sair da tela
        if self.rect.bottom < 0:
            self.kill()

# Classe para asteroides
class Asteroide(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Define o tamanho aleatório do asteroide
        self.size = random.choice([30, 50, 70, 100])
        self.image = pygame.image.load("asteroide.png")  # Carrega a imagem do asteroide
        self.image = pygame.transform.scale(self.image, (self.size, self.size))  # Redimensiona
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 800 - self.size)  # Posição inicial aleatória no eixo X
        self.rect.y = -self.size  # Começa fora da tela no topo
        self.speed = random.randint(3, 10)  # Velocidade aleatória de queda

    def update(self):
        # Move o asteroide para baixo
        self.rect.y += self.speed
        # Remove o asteroide se sair da tela
        if self.rect.top > 600:
            self.kill()


# Criação da nave controlada pelo jogador
nave = NaveEspacial(name="Fenix", position=(400, 300), speed=5)

# Grupos de sprites para gerenciamento e renderização
all_sprites = pygame.sprite.Group()  # Todos os sprites (nave, tiros, asteroides, etc.)
all_sprites.add(nave)
tiros = pygame.sprite.Group()  # Grupo para tiros normais
bolhas = pygame.sprite.Group()  # Grupo para tiros de bolha
asteroides = pygame.sprite.Group()  # Grupo para asteroides

# Inicializa o temporizador para spawn de asteroides
asteroide_spawn_timer = 0

# Variáveis de pontuação
score = 0  # Pontuação inicial
asteroid_scores = {30: 10, 50: 20, 70: 30, 100: 40}  # Pontuação baseada no tamanho do asteroide
last_score_display = ""  # Última pontuação obtida, exibida brevemente

# Loop principal do jogo
running = True
while running:
    # Processa eventos (teclado, mouse, etc.)
    for event in pygame.event.get():
        if event.type == QUIT:  # Fecha o jogo
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:  # Disparo de tiro normal
                novo_tiro = Tiro(nave.rect.center)
                all_sprites.add(novo_tiro)
                tiros.add(novo_tiro)
                shot_laser.play()  # Som do tiro laser
            elif event.key == K_u:  # Ativa o campo de força
                nave.activate_force_field()
                field.play()  # Som do campo de força
            elif event.key == K_i:  # Disparo de tiro de bolha
                nova_bolha = TiroBolha(nave.rect.center)
                all_sprites.add(nova_bolha)
                bolhas.add(nova_bolha)
                shot_buble.play()  # Som do tiro de bolha

    # Criação de novos asteroides em intervalos regulares
    asteroide_spawn_timer += 1
    if asteroide_spawn_timer > 30:  # Intervalo entre asteroides
        novo_asteroide = Asteroide()
        all_sprites.add(novo_asteroide)
        asteroides.add(novo_asteroide)
        asteroide_spawn_timer = 0

    # Atualiza todos os sprites no jogo
    all_sprites.update()

    # Verifica colisões entre tiros normais e asteroides
    for tiro, asteroides_destruidos in pygame.sprite.groupcollide(tiros, asteroides, True, True).items():
        for asteroide in asteroides_destruidos:
            pontos = asteroid_scores.get(asteroide.size, 0)  # Calcula pontos baseados no tamanho
            score += pontos  # Incrementa pontuação
            last_score_display = f"+{pontos} Pontos"  # Exibe pontuação recente
            explodes_asteroid.play()  # Som de explosão do asteroide

    # Verifica colisões entre tiros de bolha e asteroides
    for bolha, asteroides_destruidos in pygame.sprite.groupcollide(bolhas, asteroides, True, True).items():
        for asteroide in asteroides_destruidos:
            pontos = asteroid_scores.get(asteroide.size, 0)
            score += pontos
            last_score_display = f"+{pontos} Pontos"
            explodes_asteroid.play()

    # Verifica colisões entre a nave e os asteroides
    if pygame.sprite.spritecollide(nave, asteroides, True) and not nave.force_field:
        nave.shield -= 10  # Reduz o escudo da nave
        collide_ship.play()  # Som de colisão
        if nave.shield <= 0:  # Verifica se a nave perdeu todo o escudo
            nave.alive = False  # Marca a nave como destruída

    # Renderiza o plano de fundo
    screen.blit(background, (0, 0))

    # Desenha todos os sprites na tela
    all_sprites.draw(screen)

    # Desenha a nave (incluindo campo de força, se ativo)
    nave.draw(screen)

    # Exibe o nível do escudo da nave
    shield_text = font.render(f'Escudo: {nave.shield}', True, (255, 255, 255))
    screen.blit(shield_text, (10, 10))

    legendas = font_pequena.render("Legenda:|  Setas: Movimentar nave, |  Espaço: Tiro normal, |  I: Tiro de bolhas |  U: Ativar escudo", True,(255,255,255))
    screen.blit(legendas,(10,570))

    # Exibe a pontuação total
    score_text = font.render(f'Pontuação: {int(score)}', True, (255, 255, 0))
    screen.blit(score_text, (10, 90))

    # Exibe a pontuação mais recente
    if last_score_display:
        last_score_text = font.render(last_score_display, True, (0, 255, 0))
        screen.blit(last_score_text, (10, 130))

    # Exibe tela de "Game Over" se a nave for destruída
    if not nave.alive:
        screen.blit(game_over, (0, 0))
        screen.blit(score_text, (300, 400))

    # Atualiza a tela
    pygame.display.flip()

    # Define o FPS do jogo
    clock.tick(60)

# Encerra o jogo
pygame.quit()

