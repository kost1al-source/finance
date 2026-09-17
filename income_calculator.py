import ctypes
import tkinter as tk
from tkinter import ttk


BG = "#eaf3f1"
PANEL = "#ffffff"
INK = "#153238"
MUTED = "#6a7e80"
LINE = "#dbe8e6"
TEAL = "#0f766e"
TEAL_DARK = "#0b5d57"
TEAL_SOFT = "#e4f4f1"
ORANGE_SOFT = "#fff2e8"
ORANGE = "#a65c26"
RED = "#c75c53"


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def parse_value(raw: str) -> float:
    try:
        return max(0.0, float(raw.replace(" ", "").replace(",", ".")))
    except (TypeError, ValueError):
        return 0.0


def format_number(value: float, decimals: int = 2) -> str:
    if abs(value) < 0.005:
        value = 0
    if decimals == 0 or abs(value - round(value)) < 0.005:
        result = f"{round(value):,}".replace(",", " ")
    else:
        result = f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")
        result = result.rstrip("0").rstrip(",")
    return result


class IncomeCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчёт недельных доходов по авто")
        self.geometry("1120x760")
        self.minsize(850, 650)
        self.configure(bg=BG)
        self.option_add("*Font", ("Segoe UI", 10))
        self.option_add("*TCombobox*Listbox.Font", ("Segoe UI", 10))

        self.variables = {
            "gross": tk.StringVar(value="28000"),
            "distance": tk.StringVar(value="1000"),
            "consumption": tk.StringVar(value="7.2"),
            "fuel_price": tk.StringVar(value="38.5"),
            "commission": tk.StringVar(value="4200"),
            "rent": tk.StringVar(value="1800"),
        }
        self.result_vars = {
            "fuel": tk.StringVar(value="0"),
            "tax": tk.StringVar(value="0"),
            "net": tk.StringVar(value="0"),
            "gross": tk.StringVar(value="0 КС"),
            "fuel_summary": tk.StringVar(value="0 КС"),
            "tax_summary": tk.StringVar(value="0 КС"),
            "rent_summary": tk.StringVar(value="0 КС"),
            "margin": tk.StringVar(value="0%"),
        }
        self.entries = []
        self.build_styles()
        self.build_ui()
        for variable in self.variables.values():
            variable.trace_add("write", lambda *_: self.update_calculation())
        self.update_calculation()

    def build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Main.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Title.TLabel", background=BG, foreground=INK, font=("Segoe UI", 26, "bold"))
        style.configure("Eyebrow.TLabel", background=BG, foreground=TEAL, font=("Segoe UI", 9, "bold"))
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=INK, font=("Segoe UI", 15, "bold"))
        style.configure("PanelText.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Field.TLabel", background=PANEL, foreground=INK, font=("Segoe UI", 10, "bold"))
        style.configure("Note.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Unit.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("Section.TLabel", background=PANEL, foreground=TEAL_DARK, font=("Segoe UI", 9, "bold"))
        style.configure("Calc.TLabel", background="#f4f9f8", foreground=TEAL_DARK, font=("Segoe UI", 11, "bold"))
        style.configure("CalcNote.TLabel", background="#f4f9f8", foreground=MUTED, font=("Segoe UI", 8))
        style.configure("SummaryTitle.TLabel", background=TEAL_DARK, foreground="white", font=("Segoe UI", 17, "bold"))
        style.configure("SummaryLabel.TLabel", background=TEAL_DARK, foreground="#b7ddd7", font=("Segoe UI", 9))
        style.configure("SummaryValue.TLabel", background=TEAL_DARK, foreground="white", font=("Segoe UI", 11, "bold"))
        style.configure("HeroLabel.TLabel", background="#164b4c", foreground="#b7ddd7", font=("Segoe UI", 9))
        style.configure("HeroValue.TLabel", background="#164b4c", foreground="white", font=("Segoe UI", 35, "bold"))
        style.configure("Foot.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Reset.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 6))

    def build_ui(self):
        root = ttk.Frame(self, style="Main.TFrame", padding=(28, 24, 28, 20))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        header = ttk.Frame(root, style="Main.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.columnconfigure(1, weight=1)

        mark = tk.Canvas(header, width=48, height=48, bg=TEAL, highlightthickness=0)
        mark.grid(row=0, column=0, rowspan=2, padx=(0, 13))
        mark.create_text(24, 24, text="₽", fill="white", font=("Segoe UI", 22, "bold"))
        ttk.Label(header, text="РАБОЧИЙ РАСЧЁТ", style="Eyebrow.TLabel").grid(row=0, column=1, sticky="sw")
        ttk.Label(header, text="Недельные доходы по авто", style="Title.TLabel").grid(row=1, column=1, sticky="nw")
        status = tk.Label(header, text="●  Расчёт обновляется сразу", bg="#ffffff", fg=TEAL_DARK, padx=12, pady=7, font=("Segoe UI", 9, "bold"))
        status.grid(row=0, column=2, rowspan=2, sticky="e")

        content = ttk.Frame(root, style="Main.TFrame")
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=13)
        content.columnconfigure(1, weight=9)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=PANEL, highlightbackground="#c6dcd8", highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 11))
        left.columnconfigure(0, weight=1)
        self.build_input_panel(left)

        right = tk.Frame(content, bg=TEAL_DARK, highlightbackground=TEAL_DARK, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        self.build_summary_panel(right)

        ttk.Label(root, text="Введите значения за одну неделю в КС. Расчётные поля нельзя изменить вручную.", style="Foot.TLabel").grid(row=2, column=0, sticky="w", pady=(12, 0))

    def build_input_panel(self, parent):
        top = ttk.Frame(parent, style="Panel.TFrame", padding=(22, 20, 22, 14))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="Данные за неделю", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Введите свои значения — остальное посчитается автоматически.", style="PanelText.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))
        reset = ttk.Button(top, text="Сбросить", style="Reset.TButton", command=self.reset_values)
        reset.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

        fields = ttk.Frame(parent, style="Panel.TFrame", padding=(15, 0, 15, 8))
        fields.grid(row=1, column=0, sticky="ew")
        fields.columnconfigure(0, weight=1)
        field_data = [
            ("gross", "Грубый доход", "Все поступления за неделю", "КС"),
            ("distance", "Пробег", "Расстояние за неделю", "км"),
            ("consumption", "Средний расход", "Расход топлива автомобиля", "л/100 км"),
            ("fuel_price", "Цена топлива", "Стоимость одного литра", "КС/литр"),
            ("commission", "Комиссия", "Комиссия сервиса за неделю", "КС"),
            ("rent", "Пронайм", "Аренда автомобиля за неделю", "КС"),
        ]
        for row, data in enumerate(field_data):
            self.add_input_row(fields, row, *data)

        calc_title = ttk.Frame(parent, style="Panel.TFrame", padding=(26, 10, 26, 9))
        calc_title.grid(row=2, column=0, sticky="ew")
        ttk.Separator(calc_title, orient="horizontal").grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(calc_title, text="РАССЧИТЫВАЕТСЯ АВТОМАТИЧЕСКИ", style="Section.TLabel").grid(row=1, column=0, sticky="w")

        calc = tk.Frame(parent, bg="#f4f9f8")
        calc.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 18))
        calc.columnconfigure(0, weight=1)
        for row, data in enumerate([
            ("Стоимость топлива", "Пробег × расход ÷ 100 × цена", "fuel", "КС"),
            ("DPН", "Комиссия × 21%", "tax", "КС"),
            ("Чистый доход", "Грубый доход − расходы", "net", "КС"),
        ]):
            self.add_calc_row(calc, row, *data)
        formula = tk.Label(parent, text="Формула: чистый доход = грубый доход − (топливо + DPН + пронайм)", bg=ORANGE_SOFT, fg=ORANGE, anchor="w", padx=12, pady=8, font=("Segoe UI", 8))
        formula.grid(row=4, column=0, sticky="ew", padx=27, pady=(0, 20))

    def add_input_row(self, parent, row, key, title, note, unit):
        wrapper = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 1))
        wrapper.columnconfigure(0, weight=1)
        wrapper.columnconfigure(1, weight=0)
        wrapper.columnconfigure(2, weight=0)
        copy = ttk.Frame(wrapper, style="Panel.TFrame")
        copy.grid(row=0, column=0, sticky="ew", padx=(12, 6), pady=9)
        ttk.Label(copy, text=title, style="Field.TLabel").pack(anchor="w")
        ttk.Label(copy, text=note, style="Note.TLabel").pack(anchor="w", pady=(2, 0))
        entry = tk.Entry(wrapper, textvariable=self.variables[key], justify="right", width=13, bg="#fbfdfd", fg=INK, insertbackground=TEAL, relief="flat", highlightthickness=1, highlightbackground="#cbdeda", highlightcolor=TEAL, font=("Segoe UI", 11, "bold"))
        entry.grid(row=0, column=1, sticky="e", padx=(4, 10), pady=12, ipady=7)
        entry.bind("<FocusIn>", lambda event: entry.configure(bg="#ffffff"))
        entry.bind("<FocusOut>", lambda event: entry.configure(bg="#fbfdfd"))
        self.entries.append(entry)
        ttk.Label(wrapper, text=unit, style="Unit.TLabel", width=9).grid(row=0, column=2, sticky="w", padx=(0, 10))

    def add_calc_row(self, parent, row, title, note, key, unit):
        line = tk.Frame(parent, bg="#f4f9f8")
        line.grid(row=row, column=0, sticky="ew", padx=12, pady=(8 if row == 0 else 4, 5))
        line.columnconfigure(0, weight=1)
        copy = tk.Frame(line, bg="#f4f9f8")
        copy.grid(row=0, column=0, sticky="w")
        ttk.Label(copy, text=title, style="Calc.TLabel").pack(anchor="w")
        ttk.Label(copy, text=note, style="CalcNote.TLabel").pack(anchor="w", pady=(1, 0))
        value = tk.Label(line, textvariable=self.result_vars[key], bg="#ffffff", fg=TEAL_DARK, width=13, anchor="e", padx=10, pady=8, font=("Segoe UI", 11, "bold"))
        value.grid(row=0, column=1, sticky="e", padx=(10, 7))
        ttk.Label(line, text=unit, style="Unit.TLabel", background="#f4f9f8", width=5).grid(row=0, column=2, sticky="w")

    def build_summary_panel(self, parent):
        inner = tk.Frame(parent, bg=TEAL_DARK)
        inner.grid(row=0, column=0, sticky="nsew", padx=25, pady=24)
        inner.columnconfigure(0, weight=1)
        tk.Label(inner, text="ГЛАВНЫЙ РЕЗУЛЬТАТ", bg=TEAL_DARK, fg="#9bded1", anchor="w", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(inner, text="Сколько останется за неделю", style="SummaryTitle.TLabel").grid(row=1, column=0, sticky="w", pady=(7, 21))

        hero = tk.Frame(inner, bg="#164b4c")
        hero.grid(row=2, column=0, sticky="ew")
        tk.Label(hero, text="Чистый доход", bg="#164b4c", fg="#b7ddd7", anchor="w", font=("Segoe UI", 10)).pack(fill="x", padx=18, pady=(17, 0))
        tk.Label(hero, textvariable=self.result_vars["net"], bg="#164b4c", fg="white", anchor="w", font=("Segoe UI", 34, "bold")).pack(fill="x", padx=18, pady=(2, 0))
        tk.Label(hero, text="КС после основных расходов", bg="#164b4c", fg="#b7ddd7", anchor="w", font=("Segoe UI", 9)).pack(fill="x", padx=18, pady=(0, 17))

        self.add_summary_line(inner, 3, "Грубый доход", "gross")
        self.add_summary_line(inner, 4, "Топливо", "fuel_summary")
        self.add_summary_line(inner, 5, "DPН", "tax_summary")
        self.add_summary_line(inner, 6, "Пронайм", "rent_summary")

        margin = tk.Frame(inner, bg=TEAL_DARK)
        margin.grid(row=7, column=0, sticky="ew", pady=(18, 0))
        tk.Frame(margin, bg="#3b8179", height=1).pack(fill="x")
        line = tk.Frame(margin, bg=TEAL_DARK)
        line.pack(fill="x", pady=(13, 0))
        tk.Label(line, text="Доля чистого дохода", bg=TEAL_DARK, fg="#b7ddd7", anchor="w", font=("Segoe UI", 9)).pack(side="left")
        tk.Label(line, textvariable=self.result_vars["margin"], bg=TEAL_DARK, fg="#d7f5ec", anchor="e", font=("Segoe UI", 10, "bold")).pack(side="right")

        tip = tk.Frame(inner, bg="#0a4d4b")
        tip.grid(row=8, column=0, sticky="ew", pady=(20, 0))
        tk.Label(tip, text="i", bg="#0a4d4b", fg="#f4be7d", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(12, 8), pady=12)
        tk.Label(tip, text="Измените любое поле слева, чтобы сразу увидеть новый результат.", bg="#0a4d4b", fg="#d7eeea", justify="left", anchor="w", wraplength=250, font=("Segoe UI", 8)).pack(side="left", fill="x", expand=True, padx=(0, 12), pady=12)

    def add_summary_line(self, parent, row, title, key):
        line = tk.Frame(parent, bg=TEAL_DARK)
        line.grid(row=row, column=0, sticky="ew", pady=(14 if row == 3 else 0, 0))
        line.columnconfigure(0, weight=1)
        ttk.Label(line, text=title, style="SummaryLabel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(line, textvariable=self.result_vars[key], style="SummaryValue.TLabel").grid(row=0, column=1, sticky="e")

    def reset_values(self):
        defaults = {
            "gross": "28000",
            "distance": "1000",
            "consumption": "7.2",
            "fuel_price": "38.5",
            "commission": "4200",
            "rent": "1800",
        }
        for key, value in defaults.items():
            self.variables[key].set(value)
        if self.entries:
            self.entries[0].focus_set()

    def update_calculation(self):
        gross = parse_value(self.variables["gross"].get())
        distance = parse_value(self.variables["distance"].get())
        consumption = parse_value(self.variables["consumption"].get())
        fuel_price = parse_value(self.variables["fuel_price"].get())
        commission = parse_value(self.variables["commission"].get())
        rent = parse_value(self.variables["rent"].get())
        fuel = distance * consumption / 100 * fuel_price
        tax = commission * 0.21
        net = gross - (fuel + tax + rent)
        margin = max(0, net / gross * 100) if gross else 0

        self.result_vars["fuel"].set(format_number(fuel))
        self.result_vars["tax"].set(format_number(tax))
        self.result_vars["net"].set(format_number(net, 0))
        self.result_vars["gross"].set(f"{format_number(gross)} КС")
        self.result_vars["fuel_summary"].set(f"{format_number(fuel)} КС")
        self.result_vars["tax_summary"].set(f"{format_number(tax)} КС")
        self.result_vars["rent_summary"].set(f"{format_number(rent)} КС")
        self.result_vars["margin"].set(f"{format_number(margin)}%")


if __name__ == "__main__":
    enable_dpi_awareness()
    app = IncomeCalculator()
    app.mainloop()
