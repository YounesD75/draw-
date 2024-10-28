import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sys
import io

class ConsoleRedirect(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)  # Scroll to the end

def update_line_numbers(text_area, line_numbers):
    line_numbers.config(state='normal')
    line_numbers.delete(1.0, tk.END)
    
    for i in range(1, int(text_area.index('end').split('.')[0])):
        line_numbers.insert(tk.END, f"{i}\n")
        
    line_numbers.config(state='disabled')

def bind_text_events(text_area, line_numbers):
    text_area.bind('<KeyRelease>', lambda event: update_line_numbers(text_area, line_numbers))
    text_area.bind('<ButtonRelease>', lambda event: update_line_numbers(text_area, line_numbers))

def create_text_with_line_numbers(tab):
    frame = tk.Frame(tab)
    frame.pack(fill='both', expand=True)
    
    line_numbers = tk.Text(frame, width=4, padx=5, state='disabled', wrap='none')
    line_numbers.pack(side='left', fill='y')
    
    text_area = tk.Text(frame, wrap='word', height=30, width=160)
    text_area.pack(side='left', fill='both', expand=True)
    
    bind_text_events(text_area, line_numbers)
    return text_area

def new_file():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Nouveau Fichier")
    create_text_with_line_numbers(tab)

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

def run_code():
    current_tab = notebook.select()
    text_area = notebook.nametowidget(current_tab).winfo_children()[0].winfo_children()[1]
    code = text_area.get(1.0, tk.END)

    # Clear the console
    console_output.delete(1.0, tk.END)
    
    try:
        # Redirect stdout and stderr to console_output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = ConsoleRedirect(console_output)
        sys.stderr = ConsoleRedirect(console_output)
        
        # Execute the code
        exec(code)
        
    except Exception as e:
        console_output.insert(tk.END, f"Erreur d'exécution: {e}\n")
    finally:
        # Reset stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

# Création de la fenêtre principale
root = tk.Tk()
root.title("Éditeur de texte avec Onglets")

# Configuration de la taille de la fenêtre
largeur_ecran = root.winfo_screenwidth()
hauteur_ecran = root.winfo_screenheight()
root.geometry(f"{largeur_ecran}x{hauteur_ecran}")

# Création du Notebook pour les onglets
notebook = ttk.Notebook(root)
notebook.pack(pady=10, fill='both', expand=True)

# Menu
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Nouveau", command=new_file)
file_menu.add_command(label="Ouvrir", command=open_file)
file_menu.add_command(label="Sauvegarder", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Quitter", command=root.quit)

menu_bar.add_cascade(label="Fichier", menu=file_menu)

# Ajouter un bouton pour exécuter le code
run_menu = tk.Menu(menu_bar, tearoff=0)
run_menu.add_command(label="Exécuter", command=run_code)
menu_bar.add_cascade(label="Exécuter", menu=run_menu)

root.config(menu=menu_bar)

# Zone de console en bas pour afficher les résultats de l'exécution
console_output = tk.Text(root, height=10, wrap='word', state='normal', bg='black', fg='white')
console_output.pack(fill='x', side='bottom')

# Lancement de l'application
root.mainloop()
