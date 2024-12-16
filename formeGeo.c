#include <SDL2/SDL.h>
#include <stdio.h>
#include <math.h>

// Fonction pour dessiner un carré
void drawSquare(SDL_Renderer *renderer, int x, int y, int size) {
    SDL_Rect square = {x, y, size, size};  // Définir la position et la taille du carré
    SDL_RenderFillRect(renderer, &square);  // Dessiner le carré
}

// Fonction pour dessiner un cercle
void drawCircle(SDL_Renderer *renderer, int x, int y, int radius) {
    for (int w = 0; w < 2 * radius; w++) {
        for (int h = 0; h < 2 * radius; h++) {
            int dx = radius - w;  // Distance horizontale par rapport au centre
            int dy = radius - h;  // Distance verticale par rapport au centre
            if ((dx * dx + dy * dy) <= (radius * radius)) {
                SDL_RenderDrawPoint(renderer, x + dx, y + dy);
            }
        }
    }
}

// Fonction pour dessiner un segment de droite
void drawLine(SDL_Renderer *renderer, int x1, int y1, int x2, int y2) {
    SDL_RenderDrawLine(renderer, x1, y1, x2, y2);
}

// Fonction pour dessiner un arc
void drawArc(SDL_Renderer *renderer, int x, int y, int radius, int startAngle, int endAngle) {
    // On s'assure que l'angle de départ est plus petit que l'angle de fin
    if (startAngle > endAngle) {
        int temp = startAngle;
        startAngle = endAngle;
        endAngle = temp;
    }

    // Dessiner les points de l'arc
    for (int angle = startAngle; angle <= endAngle; angle++) {
        double rad = angle * M_PI / 180.0;  // Conversion en radians
        int dx = (int)(radius * cos(rad));  // Calcul de la coordonnée x
        int dy = (int)(radius * sin(rad));  // Calcul de la coordonnée y

        // Dessiner chaque point de l'arc
        SDL_RenderDrawPoint(renderer, x + dx, y + dy);
    }
}

int main() {
    // Initialisation de SDL
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "Erreur SDL_Init: %s\n", SDL_GetError());
        return 1;
    }

    // Création d'une fenêtre
    SDL_Window *window = SDL_CreateWindow("Formes en SDL2",
                                          SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                          800, 800, SDL_WINDOW_SHOWN);
    if (!window) {
        fprintf(stderr, "Erreur SDL_CreateWindow: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    // Création d'un rendu pour dessiner sur la fenêtre
    SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        fprintf(stderr, "Erreur SDL_CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Définir la couleur de dessin (rouge ici)
   SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);  // Rouge opaque

    // Dessiner un carré
    drawSquare(renderer, 100, 100, 200);  // Position (100,100), taille 200

    // Dessiner un cercle
    drawCircle(renderer, 400, 400, 100);  // Centre (400,400), rayon 100

    // Dessiner un segment
    drawLine(renderer, 100, 100, 700, 700);  // Segment entre (100, 100) et (700, 700)

    // Dessiner un arc
    drawArc(renderer, 400, 400, 100, 0, 90);  // Arc de cercle de 0 à 90 degrés

    // Afficher le dessin
    SDL_RenderPresent(renderer);

    // Boucle d'événements pour garder la fenêtre ouverte
    SDL_Event e;
    int quit = 0;
    while (!quit) {
        // Vérifier les événements
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                quit = 1;  // Quitter lorsque la fenêtre est fermée
            }
        }
    }

    // Nettoyer et quitter
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
