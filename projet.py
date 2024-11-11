import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sys
import io
import re

class ConsoleRedirect(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)

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

def suggest_correction(e):
    """Generate suggestions based on the specific type of syntax error."""
    if "unexpected EOF while parsing" in e.msg:
        return "Erreur de syntaxe : vérifiez si une parenthèse, un crochet ou une accolade est manquant en fin de fichier."
    elif "invalid syntax" in e.msg:
        if ":" in str(e):
            return "Erreur de syntaxe : assurez-vous d'avoir un ':' après une définition de fonction, une boucle ou une condition."
        elif re.search(r"unterminated string literal", e.msg):
            return "Erreur de syntaxe : une chaîne de caractères semble être ouverte mais non fermée."
        elif "can't assign to" in e.msg:
            return "Erreur d'affectation : peut-être une tentative d'affecter une valeur à une expression invalide."
        elif re.search(r"unexpected indent", e.msg):
            return "Erreur de syntaxe : vérifiez les indentations incorrectes."
        elif re.search(r"expected an indented block", e.msg):
            return "Erreur de syntaxe : un bloc indenté est attendu (après une condition, une fonction ou une boucle)."
    elif "SyntaxError" in str(e):
        return "Erreur de syntaxe, veuillez vérifier la structure de votre code."
    return "Erreur non identifiée, veuillez vérifier votre code."

def highlight_syntax_error(text_area, console_output):
    code = text_area.get(1.0, tk.END)
    text_area.tag_remove("error", 1.0, tk.END)  # Remove previous error highlighting
    
    try:
        compile(code, "<string>", "exec")  # Compile without executing to check syntax
        return True  # No syntax error
    except SyntaxError as e:
        # Highlight the line with the syntax error
        line_number = e.lineno
        start_index = f"{line_number}.0"
        end_index = f"{line_number}.end"
        
        text_area.tag_add("error", start_index, end_index)
        text_area.tag_config("error", underline=True, foreground="red")
        
        # Show the error and suggestion in the console output
        console_output.insert(tk.END, f"Erreur de syntaxe ligne {line_number}: {e.msg}\n")
        return False  # Syntax error found

def run_code():
    current_tab = notebook.select()
    text_area = notebook.nametowidget(current_tab).winfo_children()[0].winfo_children()[1]
    console_output.delete(1.0, tk.END)  # Clear the console

    if not highlight_syntax_error(text_area, console_output):
        return  # Stop execution if syntax error is found
    
    code = text_area.get(1.0, tk.END)
    
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

def on_closing():
    """Handle proper closure of the application when the window is closed."""
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment fermer l'IDE ?"):
        root.quit()  # Quit the Tkinter main loop
        root.destroy()  # Destroy the root window and release resources

# Création de la fenêtre principale
root = tk.Tk()
root.title("Éditeur de texte avec Onglets")

# Configuration de la taille de la fenêtre
largeur_ecran = root.winfo_screenwidth()
hauteur_ecran = root.winfo_screenheight()
root.geometry(f"{largeur_ecran}x{hauteur_ecran}")

# Configure the closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

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
file_menu.add_command(label="Quitter", command=on_closing)

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

# Assure la fermeture propre du programme après la fermeture de la fenêtre principale
sys.exit()
