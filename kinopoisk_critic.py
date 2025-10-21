import threading
import time
from collections import Counter

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# -------------------------
# --- СБОР ДАННЫХ
# -------------------------
def fetch_page_source(url, max_wait=10, expand=True):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    
    try:
        driver.get(url)
    except Exception as e:
        print("Warning loading page:", e)
    
    wait = WebDriverWait(driver, max_wait)

    if expand:
        for _ in range(6):
            try:
                buttons = driver.find_elements(By.XPATH,
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ещё')"
                    " or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'еще')"
                    " or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'показать')]")
                clicked = False
                for b in buttons:
                    try:
                        if b.is_displayed():
                            b.click()
                            clicked = True
                            time.sleep(1)
                    except ElementClickInterceptedException:
                        continue
                if not clicked:
                    break
            except Exception:
                break

    try:
        wait.until(lambda d: len(d.page_source) > 1000)
    except TimeoutException:
        pass

    html = driver.page_source
    driver.quit()
    return html

def extract_reviews(html):
    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    # По классам
    for tag in soup.find_all(True, {"class": lambda v: v and ('review' in v.lower() or 'отзыв' in v.lower())}):
        txt = tag.get_text(separator="\n").strip()
        if len(txt) >= 40:
            candidates.append(txt)

    # По article
    for art in soup.find_all("article"):
        txt = art.get_text(separator="\n").strip()
        if len(txt) >= 40:
            candidates.append(txt)

    # div с p
    for div in soup.find_all("div"):
        ps = div.find_all("p")
        if len(ps) >= 1:
            combined = "\n".join([p.get_text().strip() for p in ps])
            if len(combined) >= 40:
                candidates.append(combined)

    # Очистка дубликатов
    cleaned = []
    seen = set()
    for c in candidates:
        c2 = ' '.join(c.split())
        if len(c2) < 40 or c2 in seen:
            continue
        seen.add(c2)
        cleaned.append(c2)
    return cleaned

def fetch_reviews(url):
    html = fetch_page_source(url)
    return extract_reviews(html)

# -------------------------
# --- АНАЛИЗ
# -------------------------
class SentimentAnalyzer:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        model_name = "cointegrated/rubert-base-cased-nli-threeway"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipe = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer, device=self.device, return_all_scores=False)

    def predict(self, text):
        try:
            r = self.pipe(text[:512])
        except Exception:
            return "Нейтральный"
        label = r[0]['label'].lower()
        if "entail" in label:
            return "Положительный"
        if "contradict" in label:
            return "Отрицательный"
        if "neutral" in label:
            return "Нейтральный"
        if label.startswith("label_"):
            idx = int(label.split("_")[1])
            return ["Отрицательный","Нейтральный","Положительный"][idx]
        return "Нейтральный"

    def analyze_batch(self, texts):
        return [self.predict(t) for t in texts]

# -------------------------
# --- РЕКОМЕНДАЦИЯ
# -------------------------
def final_recommendation(counter: Counter, total: int):
    pos = counter.get("Положительный", 0)
    neg = counter.get("Отрицательный", 0)
    if total == 0:
        return "Нет достаточных данных.", "black"
    pct_pos = pos*100/total
    pct_neg = neg*100/total
    if pct_pos >= 60:
        return f"Рекомендуется к просмотру ({pct_pos:.0f}% положительных).", "green"
    if pct_neg >= 50 and neg > pos:
        return f"Лучше воздержаться ({pct_neg:.0f}% отрицательных).", "red"
    return f"На свой страх и риск (Положительных: {pct_pos:.0f}%, Отрицательных: {pct_neg:.0f}%).", "orange"

# -------------------------
# --- GUI с дизайном
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("🎬 Нейро-Критик Кинопоиска")
        root.geometry("1000x700")
        root.configure(bg="#f0f4f7")

        # Верх: URL и кнопка
        frame_top = tk.Frame(root, bg="#f0f4f7", pady=10)
        frame_top.pack(side=tk.TOP, fill=tk.X)
        tk.Label(frame_top, text="🔗 URL Кинопоиск:", bg="#f0f4f7", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        self.url_var = tk.StringVar()
        self.entry = ttk.Entry(frame_top, textvariable=self.url_var, width=70)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.btn = tk.Button(frame_top, text="Анализ", bg="#4CAF50", fg="white", font=("Arial",10,"bold"),
                             command=self.on_analyze)
        self.btn.pack(side=tk.LEFT, padx=5)

        # Панель
        panel = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левый: отзывы
        left = tk.Frame(panel, bg="#e8f0fe", width=520)
        panel.add(left, weight=1)
        tk.Label(left, text="Отзывы:", bg="#e8f0fe", font=("Arial",11,"bold")).pack(anchor=tk.W, padx=6, pady=(6,0))
        self.reviews_box = scrolledtext.ScrolledText(left, wrap=tk.WORD, width=60, height=30, bg="#ffffff")
        self.reviews_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Правый: диаграмма и рекомендация
        right = tk.Frame(panel, bg="#d9e4f5", width=480)
        panel.add(right, weight=0)
        tk.Label(right, text="Статистика:", bg="#d9e4f5", font=("Arial",11,"bold")).pack(anchor=tk.W, padx=6, pady=(6,0))
        self.fig = Figure(figsize=(4.5,3.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(padx=6, pady=6)
        self.rec_label = tk.Label(right, text="Рекомендация: —", bg="#d9e4f5", font=("Arial",12,"bold"))
        self.rec_label.pack(anchor=tk.W, padx=6, pady=6)

        # Статус
        self.status_var = tk.StringVar(value="Готово.")
        tk.Label(root, textvariable=self.status_var, bg="#cfd8dc", anchor=tk.W, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

        # Анализатор в фоне
        self.analyzer = None
        threading.Thread(target=self.load_model, daemon=True).start()

    def load_model(self):
        self.status_var.set("Загрузка модели...")
        try:
            self.analyzer = SentimentAnalyzer()
            self.status_var.set("Модель загружена. Готово.")
        except Exception as e:
            self.status_var.set(f"Ошибка: {e}")

    def on_analyze(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Ввод", "Введите URL")
            return
        if not url.lower().startswith(("http://","https://")):
            url = "https://" + url
        self.btn.config(state=tk.DISABLED)
        self.status_var.set("Сбор отзывов...")
        threading.Thread(target=self.run_analysis, args=(url,), daemon=True).start()

    def run_analysis(self, url):
        try:
            reviews = fetch_reviews(url)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось собрать отзывы: {e}")
            self.btn.config(state=tk.NORMAL)
            self.status_var.set("Ошибка сбора")
            return
        if not reviews:
            messagebox.showinfo("Нет данных", "Отзывы не найдены")
            self.btn.config(state=tk.NORMAL)
            self.status_var.set("Нет отзывов")
            return

        while self.analyzer is None:
            time.sleep(0.5)

        labels = self.analyzer.analyze_batch(reviews)
        cnt = Counter(labels)
        rec_text, rec_color = final_recommendation(cnt, len(labels))

        self.root.after(0, lambda: self.update_ui(reviews, labels, cnt, rec_text, rec_color))

    def update_ui(self, reviews, labels, cnt, rec_text, rec_color):
        self.reviews_box.configure(state=tk.NORMAL)
        self.reviews_box.delete("1.0", tk.END)
        for i,(r,l) in enumerate(zip(reviews,labels),1):
            color = {"Положительный":"green","Нейтральный":"gray","Отрицательный":"red"}.get(l,"black")
            self.reviews_box.insert(tk.END, f"{i}. [{l}]\n", ("tag",))
            self.reviews_box.tag_configure("tag", foreground=color, font=("Arial",10,"bold"))
            self.reviews_box.insert(tk.END, f"{r}\n\n")
        self.reviews_box.configure(state=tk.DISABLED)

        # Диаграмма
        self.ax.clear()
        labels_pie = []
        sizes = []
        colors_pie = []
        color_map = {"Положительный":"#4CAF50","Нейтральный":"#9E9E9E","Отрицательный":"#F44336"}
        for lab in ("Положительный","Нейтральный","Отрицательный"):
            v = cnt.get(lab,0)
            if v>0:
                labels_pie.append(f"{lab} ({v})")
                sizes.append(v)
                colors_pie.append(color_map.get(lab,"gray"))
        if sizes:
            self.ax.pie(sizes, labels=labels_pie, autopct='%1.0f%%', startangle=90, colors=colors_pie)
            self.ax.axis('equal')
        else:
            self.ax.text(0.5,0.5,"Нет данных",ha='center',va='center')
        self.canvas.draw()

        self.rec_label.config(text="Рекомендация: " + rec_text, fg=rec_color)
        self.status_var.set(f"Анализ завершён: {len(labels)} отзывов.")
        self.btn.config(state=tk.NORMAL)

# -------------------------
# --- Запуск
# -------------------------
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
