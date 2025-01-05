import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re

from numpy.matlib import zeros
from sympy.strategies.core import switch


class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []

        # Définir les modèles de jetons
        self.token_patterns = [
            ("SI", r"\bsi\b"),  # Mot "si" entier
            ("SINON", r"\bsinon\b"),  # Mot "sinon" entier
            ("POUR", r"\bpour\b"),  # Mot "pour" entier
            ("A", r"\bà\b"),  # Mot "à" pour les plages dans les boucles
            ("DE", r"\bde\b"),  # Mot "de" pour les plages dans les boucles
            ("TANTQUE", r"tantque"),
            ("EQUALS_EQUIV", r"==>"),
            ("TANTQUEFAIRE", r"tantquefaire"),
            ("AFFICHER", r"afficher"),
            ("FLOTTANT", r"\d+\.\d+"),
            ("ASSIGNATION", r"->"),
            ("NOMBRE", r"\d+"),
            ("OPERATEUR", r"[+\-*/=><!]"),
            ("DRAW_LINE", r"\bdrawLine\b"),
            ("DRAW_CURSOR", r"\bdrawCursor\b"),
            ("MOVE_CURSOR", r"\bmoveCursor\b"),
            ("ROTATE_CURSOR", r"\brotateCursor\b"),
            ("DRAW_SQUARE", r"\bdrawSquare\b"),
            ("DRAW_CIRCLE", r"\bdrawCircle\b"),
            ("DRAW_ARC", r"\bdrawArc\b"),
            ("PARENTHESE_OUV", r"\("),
            ("PARENTHESE_FERM", r"\)"),
            ("ACCOLADE_OUV", r"\{"),
            ("ACCOLADE_FERM", r"\}"),
            ("VIRGULE", r","),
            ("VARIABLE", r"[a-zA-Z_]\w*"),
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


def get_value_type(value):
    if isinstance(value, str):
        return "char"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value,float):
        return "float"
    elif isinstance(value, bool):
        return "bool"
    else:
        return "unknown"

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
        elif token[0] == "DRAW_LINE":
            return self.parse_draw_line()
        elif token[0] == "DRAW_CURSOR":
            return self.parse_draw_cursor()
        elif token[0] == "MOVE_CURSOR":
            return self.parse_move_cursor()
        elif token[0] == "ROTATE_CURSOR":
            return self.parse_rotate_cursor()
        elif token[0] == "DRAW_SQUARE":
            return self.parse_draw_square()
        elif token[0] == "DRAW_CIRCLE":
            return self.parse_draw_circle()
        elif token[0] == "DRAW_ARC":
            return self.parse_draw_arc()
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
        token = self.consume()
        if token[0] == "VARIABLE":
            return {"type": "Variable", "name": token[1]}
        elif token[0] == "NOMBRE":
            return {"type": "Literal", "value": int(token[1])}
        elif token[0] == "FLOTTANT":
            return {"type": "Literal", "value": float(token[1])}
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

    def parse_draw_line(self):
        self.consume("DRAW_LINE")
        self.consume("PARENTHESE_OUV")
        x1 = self.parse_expression()
        self.consume("VIRGULE")
        y1 = self.parse_expression()
        self.consume("VIRGULE")
        x2 = self.parse_expression()
        self.consume("VIRGULE")
        y2 = self.parse_expression()
        self.consume("PARENTHESE_FERM")
        return {"type": "DRAW_LINE", "params": [x1, y1, x2, y2]}

    def parse_while(self):
        self.consume("TANTQUE")
        condition = self.parse_expression()
        self.consume("ACCOLADE_OUV")
        body = self.parse_statements()
        self.consume("ACCOLADE_FERM")
        return {"type": "WhileLoop", "condition": condition, "body": body}


variable_already_defined = []

class CTranslator:
    def translate(self, ast):
        print(f"AST: {ast}")  # Débogage pour vérifier l'AST
        if ast["type"] == "Program":
            return "\n".join(self.translate(statement) for statement in ast["body"])

        elif ast["type"] == "IfStatement":
            code = f"if ({self.translate(ast['condition'])}){{\n{self.translate(ast['then']).replace('\n','\n')}\n}}"
            if ast.get("else"):  # Vérification si le bloc else existe
                code += f"\nelse {{\n    {self.translate(ast['else']).replace('\n', '\n    ')}\n}}"
            return code

        elif ast["type"] == "Assignment":
            if variable_already_defined.count(ast['variable']):
                return f"{ast['variable']} = {self.translate(ast['value'])};"
            else:
                match(ast["value"]["type"]):
                    case "Literal":
                        value_type = get_value_type(ast["value"]["value"])
                        print(f"value = {ast["value"]["value"]} value type = {value_type}")
                        variable_already_defined.append(ast['variable'])
                        return f"{value_type} {ast['variable']} = {self.translate(ast['value'])};"
                    case "BinaryExpression":
                        return f"float {ast['variable']} = {self.translate(ast['value'])};"

        elif ast["type"] == "PrintStatement":
            values = self.translate(ast["values"][0]).strip('"')  # Toujours récupérer la chaîne à afficher
            if len(ast["values"]) > 1:
                variable = self.translate(ast["values"][1])  # Si oui, récupérer la variable
                return f'printf("{values}\\n", {variable});'  # Afficher la chaîne et la variable
            else:
                return f'printf("{values}\\n");'  # Sinon, afficher juste la chaîne

        elif ast["type"] == "ForLoop":
            variable = ast["variable"]
            start = self.translate(ast["start"])
            end = self.translate(ast["end"])
            body = self.translate(ast["body"]).replace("\n", "\n    ")
            return f"for (int {variable} = {start}; {variable} <= {end}; {variable}++) {{\n    {body}\n}}"

        elif ast["type"] == "WhileLoop":
            body = self.translate(ast["body"]).replace("\n", "\n    ")
            return f"while ({self.translate(ast['condition'])}) {{\n    {body}\n}}"

        elif ast["type"] == "BinaryExpression":
            left = self.translate(ast["left"])
            operator = ast["operator"]
            right = self.translate(ast["right"])
            return f"{left} {operator} {right}"

        elif ast["type"] == "Literal":
            return str(ast["value"])

        elif ast["type"] == "Variable":
            return ast["name"]

        else:
            raise ValueError(f"Unknown AST node type: {ast['type']} in {ast}")


"""
class CTranslator:
    def __init__(self):
        self.variable_already_defined = []

    def translate(self, ast):
        print(f"AST: {ast}")  # Débogage pour vérifier l'AST


        if ast["type"] == "Program":
            return "\n".join(self.translate(statement) for statement in ast["body"])
        c_code = ""
        for node in ast:
            if node["type"] == "DRAW_LINE":
                c_code += self.translate_draw_line(node)
            elif node["type"] == "DRAW_CURSOR":
                c_code += self.translate_draw_cursor(node)
            elif node["type"] == "MOVE_CURSOR":
                c_code += self.translate_move_cursor(node)
            elif node["type"] == "ROTATE_CURSOR":
                c_code += self.translate_rotate_cursor(node)
            elif node["type"] == "DRAW_SQUARE":
                c_code += self.translate_draw_square(node)
            elif node["type"] == "DRAW_CIRCLE":
                c_code += self.translate_draw_circle(node)
            elif node["type"] == "DRAW_ARC":
                c_code += self.translate_draw_arc(node)
            elif node["type"] == "IfStatement":
                c_code += self.translate_if_statement(node)
            elif node["type"] == "Assignment":
                c_code += self.translate_assignment(node)

        return c_code

    def translate_draw_line(self, node):
        print(f"test {node["params"]}")

        x1 = node["params"][0]["value"]
        return f"drawLine(renderer, {x1});\n"

    def translate_draw_cursor(self, node):
        x, y = node["params"]
        return f"drawCursor(renderer, {x}, {y});\n"

    def translate_move_cursor(self, node):
        x, y, dx, dy = node["params"]
        return f"moveCursor(&{x}, &{y}, {dx}, {dy});\n"

    def translate_rotate_cursor(self, node):
        dx, dy, angle = node["params"]
        return f"rotateCursor(&{dx}, &{dy}, {angle});\n"

    def translate_draw_square(self, node):
        x, y, size = node["params"]
        return f"drawSquare(renderer, {x}, {y}, {size});\n"

    def translate_draw_circle(self, node):
        x, y, radius = node["params"]
        return f"drawCircle(renderer, {x}, {y}, {radius});\n"

    def translate_draw_arc(self, node):
        x, y, radius, startAngle, endAngle = node["params"]
        return f"drawArc(renderer, {x}, {y}, {radius}, {startAngle}, {endAngle});\n"

    def translate_if_statement(self, node):
        condition_code = self.translate(node["condition"])
        then_code = self.translate(node["then"]).replace("\n", "\n    ")
        code = f"if ({condition_code}) {{\n    {then_code}\n}}"
        if node.get("else"):
            else_code = self.translate(node["else"]).replace("\n", "\n    ")
            code += f"\nelse {{\n    {else_code}\n}}"
        return code

    def translate_assignment(self, node):
        variable = node["variable"]
        value_code = self.translate(node["value"])

        # Vérifier si la variable a déjà été définie
        if variable in self.variable_already_defined:
            return f"{variable} = {value_code};"
        else:
            self.variable_already_defined.append(variable)
            return f"float {variable} = {value_code};"
"""
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
            file_path = filedialog.asksaveasfilename(defaultextension=".draw",
                                                     filetypes=[("Fichiers Draw++", "*.draw")])
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
                    variable_already_defined = []
                    c_code = translator.translate(ast)
                    print("Code C généré :\n",c_code)
                    # Lire le contenu d'un autre fichier C (forme.c)
                    file_path = filedialog.askopenfilename(
                        title="Sélectionner le fichier C à importer",
                        filetypes=[("Fichiers C", "*.c")]
                    )
                    if file_path:
                        # Ouvrir et lire le fichier forme.c
                        with open(file_path, "r") as file:
                            forme_code = file.read()
                        print("Contenu de forme.c :\n", forme_code)

                        # Intégrer le contenu du fichier dans le code C principal
                        full_c_code = (
                            f"{forme_code}\n"  # Contenu de forme.c inséré ici
                            f"{c_code.strip()}\n"  # Code C généré
                            "    return 0;\n"
                            "}"
                        )
                    # exec(python_code)  # Exécution du code Python généré
                    # Demander à l'utilisateur où enregistrer le code C généré
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".c", filetypes=[("Fichiers C", "*.c")]
                    )
                    if file_path:
                        with open(file_path, "w") as file:
                            file.write(full_c_code)
                        messagebox.showinfo(
                            "Succès", "Le code C a été sauvegardé avec succès."
                        )
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
