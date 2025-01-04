import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []

        # Définir les modèles de jetons
        self.token_patterns = [
            ("SI", r"\bsi\b"),          # Mot "si" entier
            ("SINON", r"\bsinon\b"),    # Mot "sinon" entier
            ("POUR", r"\bpour\b"),      # Mot "pour" entier
            ("A", r"\bà\b"),  # Mot "à" pour les plages dans les boucles
    	    ("DE", r"\bde\b"),  # Mot "de" pour les plages dans les boucles
            ("TANTQUE", r"tantque"),
            ("EQUALS_EQUIV", r"==>"),
            ("TANTQUEFAIRE", r"tantquefaire"),
            ("AFFICHER", r"afficher"),
            ("ASSIGNATION", r"->"),
            ("NOMBRE", r"\d+"),
            ("VARIABLE", r"[a-zA-Z_]\w*"),
            ("OPERATEUR", r"[+\-*/=><!]"),
            ("PARENTHESE_OUV", r"\("),
            ("PARENTHESE_FERM", r"\)"),
            ("ACCOLADE_OUV", r"\{"),
            ("ACCOLADE_FERM", r"\}"),
            ("VIRGULE", r","),
            ("CHAINE", r'"[^"]*"'),  # Modèle pour les chaînes de caractères (entre guillemets)
            ("ESPACE", r"\s+"),  # On ignore les espaces
        ]

    def tokenize(self):
        code = self.code
        tokens = []  # Liste vide pour les jetons

        while code:  # Tant qu'il reste du code à analyser
            match = None

            # Essayer de faire correspondre un modèle de jeton
            for token_type, pattern in self.token_patterns:
                regex = re.compile(pattern)
                match = regex.match(code)

                if match:
                    value = match.group(0)  # Extraire la valeur correspondante
                    if token_type != "ESPACE":  # Ignorer les espaces
                        tokens.append((token_type, value))  # Ajouter le jeton à la liste
                    code = code[len(value):]  # Avancer dans le code
                    break

            if not match:  # Si aucun jeton ne correspond
                raise SyntaxError(f"Caractère inattendu : {code[0]}")

        tokens.append(("EOF", None))  # Ajouter un jeton de fin (EOF)
        return tokens

# Exemple d'utilisation
"""code = "si x > 5 { afficher('x est supérieur à 5') } sinon { afficher('x est inférieur ou égal à 5') }"
tokenizer = Tokenizer(code)
tokens = tokenizer.tokenize()

print(tokens)"""



# --- Parser ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consume(self, expected_type=None):
        current_token = self.tokens[self.pos]
        if expected_type and current_token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {current_token[0]}")
        self.pos += 1
        return current_token

    def peek(self):
        return self.tokens[self.pos]

    def parse(self):
        return self.parse_statements()

    def parse_statements(self):
        statements = []
        while self.peek()[0] not in ("EOF", "ACCOLADE_FERM"):
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
     token = self.peek()
    
     if token[0] == "SI":
        return self.parse_if()
     elif token[0] == "AFFICHER":
        return self.parse_print()
     elif token[0] == "VARIABLE":
        # Vérifiez si c'est une assignation ou une expression autonome
        next_token = self.tokens[self.pos + 1]
        if next_token[0] == "ASSIGNATION":
            return self.parse_assignment()
        else:
            return self.parse_expression()  # Traitez comme une expression autonome
     elif token[0] == "POUR":
        return self.parse_for()
     elif token[0] == "TANTQUE":
        return self.parse_while()
     elif token[0] in ("NOMBRE", "CHAINE"):
        # Permettre une expression autonome
        return self.parse_expression()
    
     raise SyntaxError(f"Unexpected token: {token}")


    def parse_if(self):
     self.consume("SI")
     condition = self.parse_expression()
     self.consume("ACCOLADE_OUV")
     then_branch = self.parse_statements()
     self.consume("ACCOLADE_FERM")
     if self.peek()[0] == "SINON":
        # print("Bloc 'SINON' détecté.")  # Débogage
        self.consume("SINON")
        self.consume("ACCOLADE_OUV")
        else_branch = self.parse_statements()
        self.consume("ACCOLADE_FERM")
     elif self.peek()[0] != "SINON": 
        else_branch = None
     return {"type": "IfStatement", "condition": condition, "then": then_branch, "else": else_branch}


    def parse_expression(self):
        left = self.parse_primary()  # Analyse du premier opérande

        while self.peek()[0] in ("OPERATEUR", "EQUALS_EQUIV"):  # Vérifier les opérateurs y compris '==>'
            operator = self.consume()[1]  # Consomme l'opérateur
            if operator == "==>":
                operator = "=="  # Remplace '==>' par '=='
            right = self.parse_primary()  # Analyse de l'opérande droit
            left = {"type": "BinaryExpression", "operator": operator, "left": left, "right": right}

        return left



    def parse_primary(self):
    # Analyse des éléments primaires comme des variables, nombres ou chaînes
        token = self.consume()
        if token[0] == "VARIABLE":
            return {"type": "Variable", "name": token[1]}
        elif token[0] == "NOMBRE":
            return {"type": "Literal", "value": int(token[1])}
        elif token[0] == "CHAINE":
            return {"type": "Literal", "value": token[1]}
        raise SyntaxError(f"Unexpected token in expression: {token}")





    def parse_assignment(self):
        variable = self.consume("VARIABLE")
        self.consume("ASSIGNATION")
        value = self.parse_expression()
        return {"type": "Assignment", "variable": variable[1], "value": value}

    def parse_print(self):
        self.consume("AFFICHER")
        self.consume("PARENTHESE_OUV")
    
        expressions = []
        while self.peek()[0] != "PARENTHESE_FERM":
            expr = self.parse_expression()  # Cela inclura maintenant les variables
            expressions.append(expr)
            if self.peek()[0] == "VIRGULE":
                self.consume("VIRGULE")
    
        self.consume("PARENTHESE_FERM")
    
    # Retourne un PrintStatement, mais pour chaque expression à afficher, les chaînes et variables sont traitées
        return {"type": "PrintStatement", "values": expressions}


    def parse_for(self):
        self.consume("POUR")  # Consomme le mot 'pour'
        variable = self.consume("VARIABLE")[1]  # Identifie la variable (ex: i)
        self.consume("DE")  # Consomme le mot 'de'
        start = self.parse_expression()  # Analyse le début de la plage
        self.consume("A")  # Consomme le mot 'à'
        end = self.parse_expression()  # Analyse la fin de la plage
        self.consume("ACCOLADE_OUV")  # Consomme '{'
        body = self.parse_statements()  # Analyse les instructions du corps
        self.consume("ACCOLADE_FERM")  # Consomme '}'

        return {
        	"type": "ForLoop",
        	"variable": variable,
        	"start": start,
        	"end": end,
        	"body": body,
    	}

    def parse_while(self):
        self.consume("TANTQUE")
        condition = self.parse_expression()
        self.consume("ACCOLADE_OUV")
        body = self.parse_statements()
        self.consume("ACCOLADE_FERM")
        return {"type": "WhileLoop", "condition": condition, "body": body}

"""
# --- Translator ---
class Translator:
    def translate(self, ast):
        print(f"AST: {ast}")  # Débogage pour vérifier l'AST
        if ast["type"] == "Program":
            return "\n".join(self.translate(statement) for statement in ast["body"])
        elif ast["type"] == "IfStatement":
          code = f"if {self.translate(ast['condition'])}:\n    {self.translate(ast['then'])}"
          if ast["else"]:
            code += f"\nelse:\n    {self.translate(ast['else'])}"
          return code
        elif ast["type"] == "Assignment":
            return f"{ast['variable']} = {self.translate(ast['value'])}"
        elif ast["type"] == "PrintStatement":
            return f"print({self.translate(ast['value'])})"
        elif ast["type"] == "ForLoop":
            variable = ast["variable"]
            start = self.translate(ast["start"])
            end = self.translate(ast["end"])
            body = self.translate(ast["body"])
            return f"for {variable} in range({start}, {end}):\n    {body}"
        elif ast["type"] == "WhileLoop":
            return f"while {self.translate(ast['condition'])}:\n    {self.translate(ast['body'])}"
        elif ast["type"] == "BinaryExpression":
            left = self.translate(ast["left"])
            operator = ast["operator"]
            right = self.translate(ast["right"])
            return f"({left} {operator} {right})"
        elif ast["type"] == "Literal":
            return ast["value"]
        elif ast["type"] == "Variable":
            return ast["name"]
        raise ValueError(f"Unknown AST node type: {ast['type']}")
"""

class CTranslator:
    def translate(self, ast):
        print(f"AST: {ast}")  # Débogage pour vérifier l'AST
        if ast["type"] == "Program":
            return "\n".join(self.translate(statement) for statement in ast["body"])
        elif ast["type"] == "IfStatement":
            code = f"if ({self.translate(ast['condition'])}) {{\n    {self.translate(ast['then'])}\n}}"
            if ast["else"]:
                code += f"\nelse {{\n    {self.translate(ast['else'])}\n}}"
            return code
        elif ast["type"] == "Assignment":
            return f"{ast['variable']} = {self.translate(ast['value'])};"
        elif ast["type"] == "PrintStatement":
            return f'printf("{self.translate(ast["values"][0])}\\n");'
        elif ast["type"] == "ForLoop":
            variable = ast["variable"]
            start = self.translate(ast["start"])
            end = self.translate(ast["end"])
            body = self.translate(ast["body"])
            return f"for (int {variable} = {start}; {variable} <= {end}; {variable}++) {{\n    {body}\n}}"
        elif ast["type"] == "WhileLoop":
            return f"while ({self.translate(ast['condition'])}) {{\n    {self.translate(ast['body'])}\n}}"
        elif ast["type"] == "BinaryExpression":
            left = self.translate(ast["left"])
            operator = ast["operator"]
            right = self.translate(ast["right"])
            return f"({left} {operator} {right})"
        elif ast["type"] == "Literal":
            return str(ast["value"])
        elif ast["type"] == "Variable":
            return ast["name"]
        raise ValueError(f"Unknown AST node type: {ast['type']}")

# --- GUI Editor ---
class DrawPlusPlusEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ Editor")
        # self.root.state("zoomed")
        self.root.attributes("-zoomed", True)

        self.create_menu()

        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(expand=1, fill="both")

        self.new_file()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_file)
        file_menu.add_command(label="Ouvrir", command=self.open_file)
        file_menu.add_command(label="Sauvegarder", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Exécuter", command=self.run_code)
        menu_bar.add_cascade(label="Exécuter", menu=run_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        new_tab = tk.Frame(self.tab_control)
        text_area = tk.Text(new_tab, wrap="word", undo=True)
        text_area.pack(side="right", fill="both", expand=True)

        # Stocker la référence de la zone de texte dans l'onglet
        new_tab.text_area = text_area  # Référence directe à la zone de texte
        self.tab_control.add(new_tab, text="Sans titre")
        self.tab_control.select(new_tab)


    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers Draw++", "*.draw"), ("Tous les fichiers", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            self.new_file()
            text_area = self.get_current_text_area()
            text_area.insert("1.0", content)

    def save_file(self):
        current_tab = self.tab_control.select()
        if current_tab:
            text_area = self.get_current_text_area()
            content = text_area.get("1.0", "end-1c")
            file_path = filedialog.asksaveasfilename(defaultextension=".draw", filetypes=[("Fichiers Draw++", "*.draw")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(content)

    def run_code(self):
        current_tab = self.tab_control.select()
        if current_tab:
            tab_widget = self.tab_control.nametowidget(current_tab)

            # Accéder directement à la zone de texte dans l'onglet
            text_area = getattr(tab_widget, "text_area", None)
            if text_area:
                code = text_area.get("1.0", "end-1c")
                print("Code à analyser :", code)  # Debug: Voir le code
                try:
                    tokenizer = Tokenizer(code)
                    tokens = tokenizer.tokenize()
                    print("Tokens : ", tokens)  # Debug: Voir les jetons
                    parser = Parser(tokens)
                    ast = parser.parse()
                    translator = CTranslator()
                    c_code = translator.translate(ast)
                    print("Code C généré :\n", c_code)
                    #exec(python_code)  # Exécution du code Python généré
                except SyntaxError as e:
                    messagebox.showerror("Erreur de syntaxe", f"Erreur de syntaxe : {str(e)}")
                except Exception as e:
                    messagebox.showerror("Erreur d'exécution", f"Erreur d'exécution : {str(e)}")
            else:
                messagebox.showerror("Erreur", "Impossible de trouver la zone de texte dans l'onglet actuel.")

    def get_current_text_area(self):
        # Récupère directement la zone de texte de l'onglet actif
        current_tab = self.tab_control.select()
        if current_tab:
            return getattr(self.tab_control.nametowidget(current_tab), "text_area", None)
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawPlusPlusEditor(root)
    root.mainloop()
