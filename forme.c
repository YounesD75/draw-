#include <SDL2/SDL.h>
#include <stdio.h>
#include <math.h>


// Declaration of global variables
int x = 400, y = 400;  // Initial position of the cursor
int dx = 100, dy = 90;  // Initial direction (horizontal movement)

// Function to draw a square
void drawSquare(SDL_Renderer *renderer, int x, int y, int size) {
    SDL_Rect square = {x, y, size, size};  // Set the position and size of the square
    SDL_RenderFillRect(renderer, &square);  // Draw the square
}

// Function to draw a circle
void drawCircle(SDL_Renderer *renderer, int x, int y, int radius) {
    for (int w = 0; w < 2 * radius; w++) {
        for (int h = 0; h < 2 * radius; h++) {
            int dx = radius - w;  // Horizontal distance from the center
            int dy = radius - h;  // Vertical distance from the center
            if ((dx * dx + dy * dy) <= (radius * radius)) {
                SDL_RenderDrawPoint(renderer, x + dx, y + dy);
            }
        }
    }
}

// Function to draw a line segment
void drawLine(SDL_Renderer *renderer, int x1, int y1, int x2, int y2) {
    SDL_RenderDrawLine(renderer, x1, y1, x2, y2);
}

// Function to draw an arc
void drawArc(SDL_Renderer *renderer, int x, int y, int radius, int startAngle, int endAngle) {
   // Ensure that the starting angle is smaller than the ending angle
    if (startAngle > endAngle) {
        int temp = startAngle;
        startAngle = endAngle;
        endAngle = temp;
    }

   // Draw the points of the arc
    for (int angle = startAngle; angle <= endAngle; angle++) {
        double rad = angle * M_PI / 180.0;  // Conversion to radians
        int dx = (int)(radius * cos(rad));  // Calculate the x coordinate
        int dy = (int)(radius * sin(rad));  // Calculate the y coordinate

        // Draw each point of the arc
        SDL_RenderDrawPoint(renderer, x + dx, y + dy);
    }
}


// Function to draw a cursor in the shape of a blue circle
void drawCursor(SDL_Renderer *renderer, int x, int y) {
    int radius = 5;  // Size of the cursor (circle)
    // Cursor color (blue here)
    SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255);  // Blue
    // Draw a circle
    for (int w = -radius; w < radius; w++) {
        for (int h = -radius; h < radius; h++) {
            if (w * w + h * h <= radius * radius) {  // Check if the point is inside the circle
                SDL_RenderDrawPoint(renderer, x + w, y + h);
            }
        }
    }
}

// Function to move the cursor using global variables
void moveCursor(int dx, int dy) {
    x += dx;
    y += dy;
}

// Function to rotate a point around the origin by a given angle in degrees
void rotateCursor(int angle) {
    double angleRad = angle * M_PI / 180.0;  // Convertir l'angle en radians
    double newDx = dx * cos(angleRad) - dy * sin(angleRad);
    double newDy = dx * sin(angleRad) + dy * cos(angleRad);
    dx = (int)newDx;
    dy = (int)newDy;
}

int main() {
    // Initialization of SDL
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "Erreur SDL_Init: %s\n", SDL_GetError());
        return 1;
    }

    // Creation of a window
    SDL_Window *window = SDL_CreateWindow("DRAW DESSIN",
                                          SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                          800, 800, SDL_WINDOW_SHOWN);
    if (!window) {
        fprintf(stderr, "Erreur SDL_CreateWindow: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    // Creation of a renderer to draw on the window
    SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        fprintf(stderr, "Erreur SDL_CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Set the background color (white here)
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_RenderClear(renderer);  // Fill the screen with white

    // Set the drawing color for lines (black here)
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);  // Black
