import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re

class DrawPlusPlusEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ Editor")
        
        # Maximiser la fenêtre au démarrage
        self.root.state("zoomed")
        
        # Menus
        self.create_menu()
        
        # Onglets pour gérer plusieurs fichiers
        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(expand=1, fill="both")
        
        # Créer un onglet par défaut
        self.new_file()
    
    def open_file(self):
        print("Ouverture de fichier...")
        file_path = filedialog.askopenfilename(
            filetypes=[  
                ("Fichiers Draw++", "*.draw"),  
                ("Tous les fichiers", "*.*"),
            ]
        )
        
        if file_path:  # Si un fichier est sélectionné
            print(f"Fichier sélectionné : {file_path}")
            try:
                with open(file_path, "r") as file:
                    content = file.read()  
                
                new_tab = tk.Frame(self.tab_control)
                text_area = tk.Text(new_tab, wrap="word")
                text_area.insert("1.0", content)  # Insérer le contenu dans le texte
                text_area.pack(expand=1, fill="both", side="right")
                
                self.tab_control.add(new_tab, text=file_path.split("/")[-1])
                self.tab_control.select(new_tab)
            
            except Exception as e:
                print(f"Erreur lors de l'ouverture du fichier : {e}")
                tk.messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_file)
        file_menu.add_command(label="Ouvrir", command=self.open_file)
        file_menu.add_command(label="Sauvegarder", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Ajouter le menu "Fichier" et "Exécuter"
        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Exécuter", command=self.run_code)
        menu_bar.add_cascade(label="Exécuter", menu=run_menu)
        
        self.root.config(menu=menu_bar)

    def new_file(self):
        # Crée un nouvel onglet avec une zone de texte et les numéros de ligne
        new_tab = tk.Frame(self.tab_control)
        
        frame = tk.Frame(new_tab)
        frame.pack(fill="both", expand=True)

        # Zone de texte pour le code
        text_area = tk.Text(frame, wrap="word", undo=True)
        text_area.pack(side="right", fill="both", expand=True)

        # Zone pour les numéros de ligne
        line_numbers = tk.Text(frame, width=4, padx=2, takefocus=0, borderwidth=0, relief="flat")
        line_numbers.pack(side="left", fill="y")

        text_area.bind("<KeyRelease>", lambda event, text_area=text_area, line_numbers=line_numbers: self.update_line_numbers(event, text_area, line_numbers))
        
        # Associer le widget Text à l'onglet actuel via un dictionnaire
        self.tab_control.add(new_tab, text="Sans titre")
        self.tab_control.select(new_tab)

        # Récupérer et enregistrer la référence du widget de texte pour pouvoir y accéder plus tard
        self.tab_control.nametowidget(new_tab).text_widget = text_area
    
    def save_file(self):
        print("Sauvegarde du fichier...")
        current_tab = self.tab_control.select()
        if current_tab:
            # Accéder au widget Text à partir de l'onglet sélectionné
            frame = self.tab_control.nametowidget(current_tab)
            text_widget = getattr(frame, 'text_widget', None)
            
            if text_widget:
                content = text_widget.get("1.0", "end-1c")
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".draw", 
                    filetypes=[ 
                        ("Fichiers Draw++", "*.draw"),
                        ("Tous les fichiers", "*.*"),
                    ],
                )

                if file_path:
                    try:
                        with open(file_path, "w") as file:
                            file.write(content)
                        self.tab_control.tab(current_tab, text=file_path.split("/")[-1])
                    except Exception as e:
                        print(f"Erreur lors de la sauvegarde du fichier : {e}")
                        tk.messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier : {e}")

    def run_code(self):
        current_tab = self.tab_control.select()
        if current_tab:
        # Accéder au widget Text à partir de l'onglet sélectionné
            frame = self.tab_control.nametowidget(current_tab)
            text_widget = getattr(frame, 'text_widget', None)

        # Vérifier si un widget Text est trouvé
        if text_widget:
            code = text_widget.get("1.0", "end-1c")

            if code.strip():  # Vérifier que le code n'est pas vide
                try:
                    # Traduire le code Draw++ en Python
                    translated_code = traducteur(code)
                    
                    # Vérifier si translated_code est bien une chaîne de caractères
                    if isinstance(translated_code, str):
                        exec(translated_code)  # Exécuter le code traduit
                    else:
                        tk.messagebox.showerror("Erreur", "Le code traduit n'est pas une chaîne valide.")
                except Exception as e:
                    tk.messagebox.showerror("Erreur", f"Erreur d'exécution : {e}")
            else:
                tk.messagebox.showwarning("Avertissement", "Le code est vide !")
        else:
            tk.messagebox.showerror("Erreur", "Aucun champ de texte trouvé dans l'onglet actuel.")

    
    def update_line_numbers(self, event, text_area, line_numbers):
        # Fonction pour mettre à jour les numéros de ligne
        line_numbers.delete(1.0, "end")
        lines = text_area.get("1.0", "end-1c").splitlines()
        for i, line in enumerate(lines, 1):
            line_numbers.insert("end", f"{i}\n")
        
import re

import re

def traducteur(code):
    # Traduction des instructions conditionnelles
    code = re.sub(r'\bsi\s+(.*?)\s*\{', r'if \1:', code)  # "si" devient "if"
    code = re.sub(r'\bsinon\s*\{', r'else:', code)  # "sinon" devient "else"
    
    # Traduction des boucles "pour"
    code = re.sub(r'\bpour\s+(.*?)\s+de\s+(.*)\s+à\s+(.*)\s*\{', r'for \1 in range(\2, \3):', code)  # "pour" devient "for"
    
    # Traduction de "tantque"
    code = re.sub(r'\btantque\s+(.*?)\s*\{', r'while \1:', code)  # "tantque" devient "while"
    # ne marche pas
    # Traduction de "tantquefaire" -> "while True" avec un break
    code = re.sub(r'\btantquefaire\s*\{', r'while True:', code)  # "tantquefaire" devient "while True"
    # ne marche pas
    # Traduction des instructions d'assignation
    code = re.sub(r'\b(\w+)\s*->\s*(.*?)\s*', r'\1 = \2', code)  # Affectation
    
    # Traduction de "print"
    code = re.sub(r'\bafficher\s*\((.*?)\)\s*', r'print(\1)', code)  # "print" inchangé (utilisé en Python)

    # Suppression des accolades pour le bloc
    code = re.sub(r'\{', '', code)
    code = re.sub(r'\}', '', code)
    
    return code








# Exécution du programme
if __name__ == "__main__":
    root = tk.Tk()
    editor = DrawPlusPlusEditor(root)
    root.mainloop()
