# james_kivy_shop.py
# Kivy-based JAMES WORKSHOP POS with Login/Signup (JSON)
# Requires: pip install kivy pillow requests

import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.metrics import dp
from decimal import Decimal, ROUND_HALF_UP
import json, os, time, threading, requests

# ---------------- CONFIG ----------------
BOT_TOKEN = "8562247919:AAHXA48ZUqE7DSS4pKAzXZlQfTy5thHm_18"
CHAT_ID = "8131153576"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
for f in (USERS_FILE, ORDERS_FILE):
    if not os.path.exists(f):
        with open(f, "w") as fh:
            json.dump({}, fh)

# ---------------- PRODUCTS ----------------
PRODUCTS = [
    {"id": "king_kuba_50", "name": "King Kuba 50pcs (mix)", "price": 370, "category": "Food",
     "image": "https://m.media-amazon.com/images/I/71tFZT4mKSL._AC_SL1500_.jpg"},
    {"id": "king_kuba_25", "name": "King Kuba 25pcs", "price": 200, "category": "Food",
     "image": "https://m.media-amazon.com/images/I/71tFZT4mKSL._AC_SL1500_.jpg"},
    {"id": "particle_500g", "name": "Particle 500g", "price": 145, "category": "Food",
     "image": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Maize_Flour.jpg"},
    {"id": "koo_sweets", "name": "Koo Sweets", "price": 140, "category": "Food",
     "image": "https://images-na.ssl-images-amazon.com/images/I/81EYz5aBj8L._AC_SL1500_.jpg"},
    {"id": "cool_cow", "name": "Cool Cow", "price": 100, "category": "Food",
     "image": "https://www.jumia.co.ke/mlp-cool-cow-sweets//"},
    {"id": "tajiri_pop", "name": "Tajiri Pop", "price": 190, "category": "Food",
     "image": "https://upload.wikimedia.org/wikipedia/commons/0/07/Candy-2803709_1920.jpg"},
    {"id": "glucose_50", "name": "Glucose 50g (dozen)", "price": 200, "category": "Food",
     "image": "https://images-na.ssl-images-amazon.com/images/I/71WceB3dlnL._AC_SL1500_.jpg"},
    {"id": "glucose_10", "name": "Glucose 10g", "price": 180, "category": "Food",
     "image": "https://images-na.ssl-images-amazon.com/images/I/71WceB3dlnL._AC_SL1500_.jpg"},
    {"id": "gomba", "name": "Gomba chewing gum", "price": 135, "category": "Food",
     "image": "https://viwanda.ke/images/product/special-gomba-b-gum-100pcs-2/10753_1.jpg"},
    {"id": "mara_moja", "name": "Mara Moja", "price": 350, "category": "Food",
     "image": "https://kenyashop.co.ke/wp-content/uploads/2023/04/mara-moja-painkiller-tablets.jpg"},
]

CATEGORIES = ["All"] + sorted({p["category"] for p in PRODUCTS})

# ---------------- Helpers ----------------
def money(v):
    d = Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:.2f}"

def send_telegram(message_text):
    try:
        requests.post(TELEGRAM_URL, data={"chat_id": CHAT_ID, "text": message_text}, timeout=8)
    except Exception as e:
        print("Telegram send failed:", e)

# ---------------- Screens ----------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        self.add_widget(layout)
        layout.add_widget(Label(text="JAMES WORKSHOP LOGIN", font_size=24))
        self.user_input = TextInput(hint_text="Username", multiline=False)
        self.pass_input = TextInput(hint_text="4-digit password", password=True, multiline=False)
        layout.add_widget(self.user_input)
        layout.add_widget(self.pass_input)
        btn = Button(text="Login")
        btn.bind(on_release=self.do_login)
        layout.add_widget(btn)
        switch_btn = Button(text="Sign Up Instead")
        switch_btn.bind(on_release=lambda x: self.manager.transition_to_signup())
        layout.add_widget(switch_btn)

    def do_login(self, instance):
        users = json.load(open(USERS_FILE, "r"))
        u = self.user_input.text.strip()
        p = self.pass_input.text.strip()
        if u not in users:
            self.show_error("Username not found")
            return
        if users[u]["password"] != p:
            self.show_error("Wrong password")
            return
        self.manager.user = u
        self.manager.current = "shop"

    def show_error(self, msg):
        from kivy.uix.popup import Popup
        popup = Popup(title="Error",
                      content=Label(text=msg),
                      size_hint=(.7,.3))
        popup.open()

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        self.add_widget(layout)
        layout.add_widget(Label(text="SIGN UP", font_size=24))
        self.user_input = TextInput(hint_text="Username 8-12 chars", multiline=False)
        self.pass_input = TextInput(hint_text="4-digit password", password=True, multiline=False)
        self.confirm_input = TextInput(hint_text="Confirm password", password=True, multiline=False)
        layout.add_widget(self.user_input)
        layout.add_widget(self.pass_input)
        layout.add_widget(self.confirm_input)
        btn = Button(text="Create Account")
        btn.bind(on_release=self.do_signup)
        layout.add_widget(btn)
        switch_btn = Button(text="Back to Login")
        switch_btn.bind(on_release=lambda x: self.manager.transition_to_login())
        layout.add_widget(switch_btn)

    def do_signup(self, instance):
        u = self.user_input.text.strip()
        p = self.pass_input.text.strip()
        c = self.confirm_input.text.strip()
        users = json.load(open(USERS_FILE, "r"))
        if not (8 <= len(u) <= 12):
            self.show_error("Username 8-12 chars")
            return
        if u in users:
            self.show_error("Username exists")
            return
        if not (p.isdigit() and len(p)==4):
            self.show_error("Password must be 4 digits")
            return
        if p != c:
            self.show_error("Passwords do not match")
            return
        users[u] = {"password": p}
        json.dump(users, open(USERS_FILE, "w"), indent=2)
        self.manager.transition_to_login()

    def show_error(self,msg):
        from kivy.uix.popup import Popup
        popup = Popup(title="Error", content=Label(text=msg), size_hint=(.7,.3))
        popup.open()

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.layout = BoxLayout(orientation="horizontal")
        self.add_widget(self.layout)

        # Left: categories
        left = BoxLayout(orientation="vertical", size_hint=(0.2,1), padding=dp(8), spacing=dp(6))
        left.add_widget(Label(text="Categories", size_hint_y=None, height=dp(30)))
        self.cat_box = BoxLayout(orientation="vertical", spacing=dp(4))
        left.add_widget(self.cat_box)
        self.layout.add_widget(left)

        # Center: products
        center = BoxLayout(orientation="vertical", size_hint=(0.5,1), padding=dp(4))
        self.product_scroll = ScrollView()
        self.prod_grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.prod_grid.bind(minimum_height=self.prod_grid.setter('height'))
        self.product_scroll.add_widget(self.prod_grid)
        center.add_widget(self.product_scroll)
        self.layout.add_widget(center)

        # Right: cart
        right = BoxLayout(orientation="vertical", size_hint=(0.3,1), padding=dp(4))
        self.cart_grid = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.cart_grid.bind(minimum_height=self.cart_grid.setter('height'))
        right.add_widget(Label(text="Cart", size_hint_y=None, height=dp(30)))
        scroll = ScrollView()
        scroll.add_widget(self.cart_grid)
        right.add_widget(scroll)
        self.layout.add_widget(right)

        # Load categories and products
        self.load_categories()
        self.show_products("All")

    def load_categories(self):
        self.cat_box.clear_widgets()
        for c in CATEGORIES:
            btn = Button(text=c, size_hint_y=None, height=dp(30))
            btn.bind(on_release=lambda x,c=c:self.show_products(c))
            self.cat_box.add_widget(btn)

    def show_products(self, category):
        self.prod_grid.clear_widgets()
        items = PRODUCTS if category=="All" else [p for p in PRODUCTS if p["category"]==category]
        for p in items:
            box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(220))
            img = AsyncImage(source=p["image"], size_hint_y=None, height=dp(140))
            box.add_widget(img)
            box.add_widget(Label(text=f"{p['name']}\nKES {money(p['price'])}", size_hint_y=None, height=dp(40)))
            btn = Button(text="Add to Cart", size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda x,p=p: self.add_to_cart(p))
            box.add_widget(btn)
            self.prod_grid.add_widget(box)

    def add_to_cart(self, product):
        existing = next((i for i in self.cart if i["id"]==product["id"]), None)
        if existing:
            existing["qty"] += 1
        else:
            self.cart.append({"id":product["id"], "name":product["name"], "price":product["price"], "qty":1})
        self.render_cart()

    def render_cart(self):
        self.cart_grid.clear_widgets()
        for item in self.cart:
            box = BoxLayout(size_hint_y=None, height=dp(40))
            box.add_widget(Label(text=f"{item['name']} x{item['qty']}"))
            btn = Button(text="Remove", size_hint_x=None, width=dp(80))
            btn.bind(on_release=lambda x,item=item:self.remove_cart_item(item))
            box.add_widget(btn)
            self.cart_grid.add_widget(box)

    def remove_cart_item(self, item):
        self.cart.remove(item)
        self.render_cart()

class JamesApp(App):
    def build(self):
        self.user = None
        sm = ScreenManager()
        self.sm = sm
        sm.user = None
        sm.transition_to_login = lambda: setattr(sm, "current", "login")
        sm.transition_to_signup = lambda: setattr(sm, "current", "signup")
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(ShopScreen(name="shop"))
        return sm

if __name__ == "__main__":
    JamesApp().run()
