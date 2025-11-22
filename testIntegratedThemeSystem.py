import sys
import pygame

from MetaMindIQTrain.core.theme import Theme, ThemeProvider
from MetaMindIQTrain.modules.themeAwareExpandVision import ThemeAwareExpandVision
from MetaMindIQTrain.modules.themeAwareMorphMatrix import ThemeAwareMorphMatrix


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Integrated Theme System Test')

    clock = pygame.time.Clock()

    # Create two themes: dark and light
    darkTheme = Theme.createDarkTheme()
    # Attempt to create a light theme; if not available, fallback to dark
    try:
        lightTheme = Theme.createLightTheme()
    except AttributeError:
        lightTheme = darkTheme

    # Start with dark theme
    currentTheme = darkTheme
    themeProvider = ThemeProvider(currentTheme)

    # Create module instances
    expandVisionModule = ThemeAwareExpandVision(themeProvider, screen)
    morphMatrixModule = ThemeAwareMorphMatrix(themeProvider, screen)

    # Set active module
    activeModule = expandVisionModule

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle theme with 'T'
                if event.key == pygame.K_t:
                    if themeProvider.getTheme() == darkTheme:
                        currentTheme = lightTheme
                    else:
                        currentTheme = darkTheme
                    themeProvider = ThemeProvider(currentTheme)
                    # Update theme provider in both modules
                    expandVisionModule.themeProvider = themeProvider
                    morphMatrixModule.themeProvider = themeProvider
                # Switch active module: press 1 for expand vision, press 2 for morph matrix
                elif event.key == pygame.K_1:
                    activeModule = expandVisionModule
                elif event.key == pygame.K_2:
                    activeModule = morphMatrixModule
            activeModule.handleInteraction(event)

        # Clear the screen
        screen.fill((0, 0, 0))
        activeModule.update(dt)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main() 