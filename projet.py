import tkinter as tk
from tkinter import filedialog, messagebox

def new_file():
    text_area.delete(1.0, tk.END)

def open_file():
    file_path = filedialog.askopenfilename(title="Ouvrir un fichier",
                                            filetypes=[("Tous les fichiers", "*.*")])
    if file_path:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt"), ("Tous les fichiers", "*.*")])
    if file_path:
        try:
            with open(file_path, 'w') as file:
                content = text_area.get(1.0, tk.END)
                file.write(content)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier : {e}")

def create_file():
    # Ici vous pouvez définir ce que fait le bouton "Créer un fichier"
    messagebox.showinfo("Info", "Création d'un nouveau fichier.")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Éditeur de texte")

# Configuration de la taille de la fenêtre
largeur_ecran = root.winfo_screenwidth()
hauteur_ecran = root.winfo_screenheight()
root.geometry(f"{largeur_ecran}x{hauteur_ecran}")

# Zone de texte
text_area = tk.Text(root, wrap='word', height=40, width=180)
text_area.pack(padx=10, pady=10)

# Menu
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Nouveau", command=new_file)
file_menu.add_command(label="Ouvrir", command=open_file)
file_menu.add_command(label="Sauvegarder", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Quitter", command=root.quit)

menu_bar.add_cascade(label="Fichier", menu=file_menu)
root.config(menu=menu_bar)

# Création d'un bouton
frame = tk.Frame(root, bg="blue")
frame.pack(pady=10)

# Lancement de l'application
root.mainloop()
