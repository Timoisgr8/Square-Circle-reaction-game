import pygame
import random
import time

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square vs Circle")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Statistics
stats = {"reaction_times": [], "score": 0}


def save_round_results(score, reaction_time):
    with open("data.txt", "a") as file:
        file.write(f"{score}, {reaction_time:.2f}\n")


def load_results():
    try:
        with open("data.txt", "r") as file:
            results = file.readlines()
            return [tuple(map(float, line.split(", "))) for line in results]
    except FileNotFoundError:
        return []


def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Square vs Circle", font, BLACK, screen, WIDTH//2, HEIGHT//4)
        draw_text("1. Play", font, BLACK, screen, WIDTH//2, HEIGHT//2 - 20)
        draw_text("2. Statistics", font, BLACK,
                  screen, WIDTH//2, HEIGHT//2 + 20)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game()
                elif event.key == pygame.K_2:
                    show_statistics()


def show_statistics():
    results = load_results()
    while True:
        screen.fill(WHITE)

        if results:
            total_score = sum(score for score, _ in results)
            total_reaction_time = sum(
                reaction_time for _, reaction_time in results)
            
            accuracy = (total_score / (len(results) * 20)) * 100
            avg_reaction_time = total_reaction_time / \
                len(results) if results else 0

            draw_text(f"Accuracy: {accuracy:.2f}%", font,
                      BLACK, screen, WIDTH//2, HEIGHT//3)
            draw_text(f"Avg Reaction Time: {avg_reaction_time:.2f} ms",
                      font, BLACK, screen, WIDTH//2, HEIGHT//2)

            y_offset = HEIGHT // 2 + 50
            for score, reaction_time in results:
                draw_text(f"Score: {score}, Reaction Time: {reaction_time:.2f} ms",
                          font, BLACK, screen, WIDTH//2, y_offset)
                y_offset += 40
        else:
            draw_text("No data available", font, BLACK,
                      screen, WIDTH//2, HEIGHT//3)

        draw_text("Press B to go back", font, BLACK,
                  screen, WIDTH//2, HEIGHT - 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                return


def game():
    stats["reaction_times"] = []
    stats["score"] = 0

    controls = {"circle": pygame.K_RIGHT, "square": pygame.K_LEFT}
    if random.choice([True, False]):
        controls = {"circle": pygame.K_LEFT, "square": pygame.K_RIGHT}

    screen.fill(WHITE)
    draw_text("If circle: Press Right" if controls["circle"] ==
              pygame.K_RIGHT else "If circle: Press Left", font, BLACK, screen, WIDTH//2, HEIGHT//2 - 100)
    draw_text("If square: Press Left" if controls["square"] ==
              pygame.K_LEFT else "If square: Press Right", font, BLACK, screen, WIDTH//2, HEIGHT//2 - 130)
    draw_text("Press SPACE to start", font, BLACK, screen, WIDTH//2, HEIGHT//2)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    countdown()
    trials = 20
    for _ in range(trials):
        result = play_round(controls)
        if result:
            print("Got a point")
            stats["score"] += 1
        else:
            print("FAILED")
        delay = random.random() * 2 + 0.1
        time.sleep(delay)

    if stats["reaction_times"]:
        avg_reaction_time = sum(
            stats["reaction_times"]) / len(stats["reaction_times"])
    else:
        avg_reaction_time = 0

    save_round_results(stats["score"], avg_reaction_time)
    main_menu()


def countdown():
    for i in range(3, 0, -1):
        screen.fill(WHITE)
        draw_text(str(i), font, BLACK, screen, random.randint(
            50, WIDTH-50), random.randint(50, HEIGHT-50))
        pygame.display.flip()
        pygame.time.delay(1000)


def play_round(controls):
    shape_type = random.choice(["circle", "square"])
    color = random.choice([RED, GREEN, BLUE])
    size = random.randint(30, 100)
    x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
    
    key_pressed = False
    correct = False

    screen.fill(WHITE)
    if shape_type == "circle":
        pygame.draw.circle(screen, color, (x, y), size // 2)
    else:
        pygame.draw.rect(screen, color, (x, y, size, size))
    pygame.display.flip()


    start_ticks = pygame.time.get_ticks()
    response_time = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and not key_pressed:
                key_pressed = True

                response_time = pygame.time.get_ticks() - start_ticks
                if (shape_type == "circle" and event.key == controls["circle"]) or \
                   (shape_type == "square" and event.key == controls["square"]):
                    stats["reaction_times"].append(
                        response_time / 1000.0 * 1000)
                    correct = True
                    flash_border(GREEN)
                else:
                    correct = False
                    flash_border(RED)

        elapsed_time = pygame.time.get_ticks() - start_ticks
        if elapsed_time >= 500:
            if not key_pressed:
                flash_border(RED)
            break

    return correct 


def flash_border(color):
    border_thickness = 20
    pygame.draw.rect(screen, color, (0, 0, WIDTH, border_thickness))
    pygame.draw.rect(screen, color, (0, HEIGHT -
                     border_thickness, WIDTH, border_thickness))
    pygame.draw.rect(screen, color, (0, 0, border_thickness, HEIGHT))
    pygame.draw.rect(screen, color, (WIDTH - border_thickness,
                     0, border_thickness, HEIGHT))
    pygame.display.flip()
    pygame.time.delay(100)
    screen.fill(WHITE)
    pygame.display.flip()


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)


if __name__ == "__main__":
    main_menu()
