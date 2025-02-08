import pygame
import sys
import config
import nim
import nim_ai


ai = nim_ai.train(piles=[1, 3, 5, 7, 0], train_episodes=10000)

# Main game loop
running = True
while running:
    # Define the piles
    piles = [1, 3, 5, 7, 0]
    piles_extended = []
    for i in range(len(piles)):
        pile_extended = [j for j in range(piles[i])]
        piles_extended.append(pile_extended)

    blocks_selected_row = -1
    blocks_selected = []

    # Calculate the width and height of the screen based on the content
    piles_max_length = max(piles)
    SCREEN_WIDTH = config.LEFT_MARGIN * 2 + piles_max_length * config.BLOCK_SIZE + (piles_max_length - 1) * config.SPACING
    SCREEN_HEIGHT = config.TOP_MARGIN * 2 + len(piles) * config.BLOCK_SIZE + (len(piles) - 1) * config.SPACING + 100 # Add 100 for the confirm button

    # Position and size of the confirm button
    CONFIRM_BUTTON_X = (SCREEN_WIDTH - 150) // 2
    CONFIRM_BUTTON_Y = SCREEN_HEIGHT - 80
    CONFIRM_BUTTON_WIDTH = 150
    CONFIRM_BUTTON_HEIGHT = 50

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nim Game")
    font = pygame.font.Font(None, 36)

    game = nim.Nim(piles=piles)

    ai_flag = True
    if ai_flag:
        ai_player = 1
    else:
        ai_player = -1

    playing = True
    while playing:
        if game.player == ai_player and game.winner is None:
            action = ai.choose_action(piles, epsilon=False)
            game.move(action)
            piles_extended[action[0]] = piles_extended[action[0]][:-action[1]]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if (CONFIRM_BUTTON_X <= x <= CONFIRM_BUTTON_X + CONFIRM_BUTTON_WIDTH and
                        CONFIRM_BUTTON_Y <= y <= CONFIRM_BUTTON_Y + CONFIRM_BUTTON_HEIGHT):
                    if(game.winner is not None):
                        playing = False
                        break

                    if len(blocks_selected) > 0:
                        game.move((blocks_selected_row, len(blocks_selected)))

                        piles_extended[blocks_selected_row] = [j for j in piles_extended[blocks_selected_row] if j not in blocks_selected]
                        piles = [len(pile) for pile in piles_extended]
                        blocks_selected_row = -1
                        blocks_selected = []
                else:
                    # Check which block is clicked
                    for i, pile in enumerate(piles_extended):
                        for j in pile:
                            block_x = config.LEFT_MARGIN + j * (config.BLOCK_SIZE + config.SPACING)
                            block_y = config.TOP_MARGIN + i * (config.BLOCK_SIZE + config.SPACING)
                            if block_x <= x <= block_x + config.BLOCK_SIZE and block_y <= y <= block_y + config.BLOCK_SIZE:
                                if blocks_selected_row == -1 or len(blocks_selected) == 0:
                                    blocks_selected_row = i
                                    blocks_selected.append(j)
                                elif blocks_selected_row == i:
                                    if j in blocks_selected:
                                        blocks_selected.remove(j)
                                    else:
                                        blocks_selected.append(j)

        # Fill the screen with a white background
        screen.fill(config.BG_COLOR)

        # Draw each pile
        for i, pile in enumerate(piles_extended):
            for j in pile:
                block_x = config.LEFT_MARGIN + j * (config.BLOCK_SIZE + config.SPACING)
                block_y = config.TOP_MARGIN + i * (config.BLOCK_SIZE + config.SPACING)
                color = config.PILE_SELECTED_COLOR if (i == blocks_selected_row and j in blocks_selected) else config.PILE_COLOR
                pygame.draw.rect(screen, color, (block_x, block_y, config.BLOCK_SIZE, config.BLOCK_SIZE))

        # Draw the confirm button
        pygame.draw.rect(screen, config.TEXT_COLOR, (CONFIRM_BUTTON_X, CONFIRM_BUTTON_Y, CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT))
        confirm_text = font.render("Confirm", True, config.BG_COLOR) if game.winner is None else font.render("Restart", True, config.BG_COLOR)
        text_rect = confirm_text.get_rect(center=(CONFIRM_BUTTON_X + CONFIRM_BUTTON_WIDTH // 2, CONFIRM_BUTTON_Y + CONFIRM_BUTTON_HEIGHT // 2))
        screen.blit(confirm_text, text_rect)

        # Display the current player information
        player_text = font.render(f"Current Player: Player {game.player + 1}", True, config.TEXT_COLOR)
        screen.blit(player_text, (10, 10))

        # Check if the game is over
        if game.winner is not None:
            winner_text = font.render(f"Player {game.winner + 1} wins!", True, config.TEXT_COLOR)
            text_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(winner_text, text_rect)

        # Update the display
        pygame.display.flip()

    pygame.display.flip()

pygame.quit()
sys.exit()