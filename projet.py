import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import io

# Classe pour rediriger les sorties vers le terminal (console)
class ConsoleRedirect(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)

# Fonction pour mettre à jour les numéros de ligne
def update_line_numbers(text_area, line_numbers):
    line_numbers.config(state='normal')
    line_numbers.delete(1.0, tk.END)
    for i in range(1, int(text_area.index('end').split('.')[0])):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state='disabled')

# Fonction pour lier les événements de texte
def bind_text_events(text_area, line_numbers):
    text_area.bind('<KeyRelease>', lambda event: update_line_numbers(text_area, line_numbers))
    text_area.bind('<ButtonRelease>', lambda event: update_line_numbers(text_area, line_numbers))

# Fonction pour créer la zone de texte avec numéros de ligne
def create_text_with_line_numbers(tab):
    editor_frame = tk.Frame(tab)
    editor_frame.pack(fill='both', expand=True)
    
    line_numbers = tk.Text(editor_frame, width=4, padx=5, state='disabled', wrap='none')
    line_numbers.pack(side='left', fill='y')
    
    text_area = tk.Text(editor_frame, wrap='word', height=20, width=100)
    text_area.pack(side='left', fill='both', expand=True)
    
    bind_text_events(text_area, line_numbers)
    
    return text_area

# Fonction pour ouvrir un fichier
def open_file():
    file_path = filedialog.askopenfilename(title="Ouvrir un fichier",
                                           filetypes=[("Tous les fichiers", "*.*")])
    if file_path:
        try:
            with open(file_path, 'r') as file:
                content = file.read()

                tab = ttk.Frame(notebook)
                notebook.add(tab, text=file_path.split("/")[-1])

                text_area = create_text_with_line_numbers(tab)
                text_area.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

def new_file():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Nouveau Fichier")
    create_text_with_line_numbers(tab)
    
# Fonction pour enregistrer un fichier
def save_file():
    current_tab = notebook.select()
    text_area = notebook.nametowidget(current_tab).winfo_children()[0].winfo_children()[1]
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("Tous les fichiers", "*.*")])
    if file_path:
        try:
            with open(file_path, 'w') as file:
                content = text_area.get(1.0, tk.END)
                file.write(content)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier : {e}")

# Fonction pour exécuter le code
# Fonction pour exécuter le code
def run_code():
    current_tab = notebook.select()  # Récupère l'onglet sélectionné
    
    # Accéder au widget correspondant à l'onglet sélectionné
    tab_widget = notebook.nametowidget(current_tab)
    
    # Affichons les enfants du tab_widget pour vérifier la hiérarchie des widgets
    print(f"Tab Widget children: {tab_widget.winfo_children()}")
    
    # Accéder au texte du widget `Text`
    # Le Frame du tab_widget contient un autre Frame (qui contient le widget `Text`)
    frame_widget = tab_widget.winfo_children()[0]  # Premier enfant : le Frame contenant le Text
    print(f"Frame widget children: {frame_widget.winfo_children()}")
    
    text_area = frame_widget.winfo_children()[1]  # Deuxième enfant : le widget `Text`
    
    # Vérification que text_area est bien un widget Text
    if isinstance(text_area, tk.Text):
        print("text_area est bien un widget Text.")
    else:
        print(f"Erreur : text_area n'est pas un widget Text, c'est : {type(text_area)}")
    
    # Effacer le terminal avant l'exécution du code
    console_output.delete(1.0, tk.END)

    # Récupérer le contenu du `text_area`
    code = text_area.get(1.0, tk.END)
    
    try:
        # Rediriger stdout et stderr vers le terminal
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = ConsoleRedirect(console_output)
        sys.stderr = ConsoleRedirect(console_output)
        
        # Exécuter le code
        exec(code)
        
    except Exception as e:
        console_output.insert(tk.END, f"Erreur d'exécution: {e}\n")
    finally:
        # Restaurer stdout et stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr






# Fonction pour dessiner des formes
def draw_shapes(canvas, shape):
    if shape == "segment":
        canvas.create_line(50, 50, 200, 50, fill="blue", width=3)
    elif shape == "carré":
        canvas.create_rectangle(100, 100, 200, 200, outline="green", width=2, fill="yellow")
    elif shape == "cercle":
        canvas.create_oval(250, 100, 350, 200, outline="red", fill="pink", width=2)
    elif shape == "point":
        canvas.create_oval(400, 150, 402, 152, fill="black")
    elif shape == "arc":
        canvas.create_arc(100, 250, 200, 350, start=0, extent=180, fill="purple", outline="orange", width=2)
    else:
        console_output.insert(tk.END, f"Commande inconnue : {shape}\n")

# Fonction pour exécuter les commandes saisies par l'utilisateur
def run_user_command():
    command = text_area.get(1.0, tk.END).strip().lower()  # Lire la commande dans la zone texte
    if command:
        draw_shapes(canvas, command)  # Exécuter la commande correspondante
        console_output.insert(tk.END, f"Forme dessinée : {command}\n")
    else:
        console_output.insert(tk.END, "Aucune commande saisie.\n")

# Fonction pour effacer le canvas
def clear_canvas():
    canvas.delete("all")
    console_output.insert(tk.END, "Canvas effacé.\n")

# Fonction de gestion de la fermeture de l'application
def on_closing():
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment fermer l'IDE ?"):
        root.quit()  # Quitter la boucle principale Tkinter
        root.destroy()  # Détruire la fenêtre principale et libérer les ressources

# Création de la fenêtre principale
root = tk.Tk()
root.title("IDE avec Canvas et Terminal")

# Création du PanedWindow principal
paned_window = tk.PanedWindow(root, orient="vertical")
paned_window.pack(fill="both", expand=True)

# Canvas en haut (sans poids)
canvas = tk.Canvas(paned_window, height=200, bg="lightgrey")
paned_window.add(canvas)  # Pas de "weight" ici

# Création du notebook pour gérer les onglets
notebook = ttk.Notebook(paned_window)
paned_window.add(notebook)

# Création du deuxième PanedWindow pour diviser la zone centrale en éditeur et terminal
splitter = tk.PanedWindow(paned_window, orient="horizontal")
paned_window.add(splitter)

# Zone de texte (éditeur de code)
editor_frame = ttk.Frame(splitter)
text_area = create_text_with_line_numbers(editor_frame)
splitter.add(editor_frame)

# Terminal en bas
console_output = tk.Text(splitter, height=10, wrap='word', state='normal', bg='black', fg='white')
splitter.add(console_output)

# Menu de l'application
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Nouveau", command=new_file)
file_menu.add_command(label="Ouvrir", command=open_file)
file_menu.add_command(label="Sauvegarder", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Quitter", command=on_closing)

menu_bar.add_cascade(label="Fichier", menu=file_menu)

run_menu = tk.Menu(menu_bar, tearoff=0)
run_menu.add_command(label="Exécuter", command=run_code)
menu_bar.add_cascade(label="Exécuter", menu=run_menu)

root.config(menu=menu_bar)

# Boutons pour exécuter et effacer
editor_frame = tk.Frame(root)
editor_frame.pack()

execute_button = tk.Button(editor_frame, text="Dessiner", command=run_user_command)
execute_button.pack(side="left", padx=5)

clear_button = tk.Button(editor_frame, text="Effacer", command=clear_canvas)
clear_button.pack(side="left", padx=5)

root.mainloop()
