"""
Arayüz Pencereleri ve Bu Pencerelerin işleyişinin yer aldığı modül
"""

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys

from cryptography.fernet import InvalidToken #Master Password doğrulamada messagebox.showerror fırlatabilmesi için eklendi

from keykeeper_main import save_master_password, verify_master_password, add_password, get_passwords, decrypt_data, return_key, change_password, change_master_password, delete_password

HOVER_COLOR = "#D0D0D0" #Butonların üstüne gelindiğinde alacağı renk
BACKGROUND_COLOR = "#F3F3F3" #Pencerenin arkaplan rengi
MODERN_FONT = ("Segoe UI", 10) #Uygulamanın standart fontu
TITLE_FONT = ("Segoe UI", 10, "bold") #Uygulama pencerelerinin başlık fontu
MAIN_TITLE_FONT = ('Segoe UI',12,"bold") #Ana uygulamanın başlık fontu

class AdvancedUI: #Hover ve focus eylemleri için yazılmış bir sınıf
    def on_entry_focus_in(event):
        event.widget.config(background="#FFFFFF")
    
    def on_entry_focus_out(event):
        event.widget.config(background="#FAFAFA")
    
    def on_button_hover_in(button):
        button.config(background=HOVER_COLOR)
    def on_button_hover_out(button):
        button.config(background=BACKGROUND_COLOR)

class MasterPasswordWindow: #Master password'un oluşturulduğu, doğrulandığı veya değiştirildiği arayüz
    def __init__(self, master, masterpass_exists):
        self.master = master
        self.window = Toplevel(master) #Uygulamanın üstünde yer alması için Toplevel olarak oluşturuldu
        self.window.resizable(False, False) #Pencere boyutlandırılamaz
        self.window.transient(master) #Pencereyi uygulamanın üstüne atar
        self.window.geometry("250x120")
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.protocol("WM_DELETE_WINDOW", self.handle_destroy) #Pencereyi kapatmak için özel protokol davranışı

        self.attempts = 3 #Master Password dogrulama hakkı
        if masterpass_exists == False: #passwords.json dosyası tespit edilemediğinde
            self.window.title("New Master Password")
            label_text = "Set The Master Password"
            button_text = "Confirm"
            button_command = self.new_master_pass
        elif masterpass_exists == True: #passwords.json dosyası tespit edildiğinde
                self.window.title("Enter Master Password")
                label_text = "Enter The Master Password"
                button_text = "Verify"
                button_command = self.verify_master_pass
        elif masterpass_exists == "new": #Yeni master password belirleneceği durumda
                self.window.title("New Master Password")
                label_text = "Set The New Master Password"
                button_text = "Set Password"
                button_command = self.change_master_pass

        label = Label(self.window, text=label_text, font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label.pack(pady=(10, 5))

        self.password = StringVar() #kullanım kolaylığı açısından Tkinter'da yer alan String değişkeni tipi (self.password.get() olarak kullanılır, aksi takdirde hashlenemez)
        self.entry = Entry(self.window, textvariable=self.password, show="*", font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA") #Master password girdisi, modernleştirildi
        self.entry.pack(pady=(0, 10))

        self.button = Button(self.window, text=button_text, command=button_command, font=MODERN_FONT, relief=FLAT, borderwidth=0, foreground="black", activeforeground="#888888", background=BACKGROUND_COLOR, activebackground=HOVER_COLOR, padx=10, pady=5) #Buton, modernleştirildi
        self.button.pack()

        self.entry.bind("<FocusIn>", lambda e: AdvancedUI.on_entry_focus_in(e))
        self.entry.bind("<FocusOut>",lambda e: AdvancedUI.on_entry_focus_out(e))

        self.button.bind("<Enter>", lambda e, b=self.button: AdvancedUI.on_button_hover_in(b))
        self.button.bind("<Leave>", lambda e, b=self.button: AdvancedUI.on_button_hover_out(b))

        self.window.bind("<Return>", lambda e: button_command()) #Enter'a basınca butonun işlevi otomatik olarak gerçekleştirilebilsin diye

    def change_master_pass(self): #Master password'un değiştirilme işleminin yönetildiği method
        if len(self.password.get()) > 3: #En az 3 karakter sınırı getirdim. Bu sınır kullanıcı adı, identifier ve şifrede de bulunmakta
            try:
                newpass = self.password.get()
                change_master_password(newpass) #Düzenlenmiş ana modüldeki change_master_password methodunu çağırır
                messagebox.showinfo("Success", "Master Password Successfully Changed and All Data Has Been Re-Encrypted!")
                self.window.destroy()
            except: #Master şifre yenileme esnasında bir hata olursa bu kod bloğu çalışır
                messagebox.showerror("Error", "Master Password Not Changed!")
        else: #En az 3 karakter sınırı aşılmadıysa bu kod bloğu çalışır
            messagebox.showerror("Error", "Master Password Is Too Short!")
    def new_master_pass(self): #Passwords.json dosyası yoksa bu metod çalışarak bir passwords.json dosyası ve bir master şifre oluşturur
        if len(self.password.get()) > 3:
            try:
                self.masterpass = self.password.get()
                save_master_password(self.masterpass) #Ana modüldeki save_master_password methodunu başlatır
                messagebox.showinfo("Success", "Master Password Successfully Saved!")
                self.master.attributes('-alpha',1) #Ana uygulamanın opaklığını 1 yaparak uygulamayı kullanıma açık hale getirir
                self.window.destroy() #Bu ekranı kapatır
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Master Password Not Saved!")
        else:
            messagebox.showerror("Error", "Master Password Is Too Short!")
        pass

    def verify_master_pass(self): #Passwords.json dosyası varsa mevcut master şifreyi doğrulamak için bu metod çalışır
        if len(self.password.get()) == 0:
            messagebox.showerror("Error", "Master Password Is Empty!")
        else:
            if self.attempts > 0: #Orijinal uygulamada bulunan 3 deneme hakkı aynen kullanılmaktadır
                try:
                    verify_master_password(self.password.get()) #Ana modüldeki verify_master_password methodunu başlatır
                    messagebox.showinfo("Success","Master Password Verified!")
                    self.master.attributes('-alpha',1)
                    self.window.destroy()
                except InvalidToken: #Yanlış şifre girildiğinde çıkan InvalidToken hatası
                    messagebox.showwarning("Warning","Wrong password, attempts left= " + str(self.attempts))
                    self.attempts -= 1
            else: #3 deneme hakkı kalmadıysa bu kod bloğu çalışır
                messagebox.showerror("Error","Three incorrect attempts made. Exiting the program.")
                sys.exit()
    
    def handle_destroy(self):
        sys.exit() #Bütün uygulamadan çıkar

class AddPasswordWindow: #Şifre ekleme ekranı
    def __init__(self, master):
        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.pack_propagate(False)
        self.window.transient(master)
        self.window.geometry("250x350")
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.title("Add Password")

        label_identifier = Label(self.window, text="Identifier", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_identifier.pack(pady=(10, 5))

        self.identifier = StringVar() #Şifre için bir identifier ekler
        self.entry_1 = Entry(self.window, textvariable=self.identifier, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_1.pack(pady=(0, 10))

        label_username = Label(self.window, text="Username", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_username.pack(pady=(10, 5))

        self.username = StringVar() #Şifrenin kullanıldığı yerdeki kullanıcı adını ekler
        self.entry_2 = Entry(self.window, textvariable=self.username, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_2.pack(pady=(0, 10))

        label_password = Label(self.window, text="Password", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_password.pack(pady=(10, 5))

        self.password = StringVar() #Şifreyi ekler
        self.entry_3 = Entry(self.window, textvariable=self.password, show="*", font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_3.pack(pady=(0, 10))

        label_description = Label(self.window, text="Description", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_description.pack(pady=(10, 5))

        self.text = Text(self.window, wrap="word", height=3, width=30, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA") #Şifreyle ilgili açıklamayı ekler
        self.text.pack(pady=(0, 10))

        # Bu butonla new_pass aracılığıyla add_password tetiklenir
        self.button = Button(self.window, text="Add", font=MODERN_FONT, relief=FLAT, borderwidth=0, foreground="black", activeforeground="#888888", background=BACKGROUND_COLOR, activebackground=HOVER_COLOR, padx=10, pady=5,command=self.new_pass)
        self.button.pack()

        # Odaklanma ve hover etkileri
        self.entry_1.bind("<FocusIn>", lambda e: self.entry_1.configure(background="#FFFFFF"))
        self.entry_1.bind("<FocusOut>", lambda e: self.entry_1.configure(background="#FAFAFA"))
        self.entry_2.bind("<FocusIn>", lambda e: self.entry_2.configure(background="#FFFFFF"))
        self.entry_2.bind("<FocusOut>", lambda e: self.entry_2.configure(background="#FAFAFA"))
        self.entry_3.bind("<FocusIn>", lambda e: self.entry_3.configure(background="#FFFFFF"))
        self.entry_3.bind("<FocusOut>", lambda e: self.entry_3.configure(background="#FAFAFA"))
        self.text.bind("<FocusIn>", lambda e: self.text.configure(background="#FFFFFF"))
        self.text.bind("<FocusOut>", lambda e: self.text.configure(background="#FAFAFA"))
        self.button.bind("<Enter>", lambda e: self.button.configure(background=HOVER_COLOR))
        self.button.bind("<Leave>", lambda e: self.button.configure(background=BACKGROUND_COLOR))
    
    def new_pass(self):
        if len(self.identifier.get()) > 3 and len(self.username.get()) > 3 and len(self.password.get()) > 3:
            try:
                add_password(self.identifier.get(), self.username.get(), self.password.get(), self.text.get("1.0", "end"))
                messagebox.showinfo("Success", "Password Successfully Added!")
                self.window.destroy()
            except:
                messagebox.showerror("Error", "Password Not Added!")
        else:
            messagebox.showerror("Error", "Password Not Added!")

class ListPasswordsWindow: #Şifre listeleme ekranı
    def __init__(self, master):
        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.pack_propagate(False)
        self.window.transient(master)
        self.window.geometry("500x350")
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.title("List Passwords")

        self.tree = ttk.Treeview(self.window, columns=("Identifier","Username", "Password", "Description"), show="headings") #Tablo tarzı bir görüntüde listelenmesi için tkinter.ttk kütüphanesinin Treeview widget'ını kullandım
        # Başlıkları tanımla
        self.tree.heading("Identifier", anchor="center", text="Identifier")
        self.tree.heading("Username", anchor="center", text="Username")
        self.tree.heading("Password", anchor="center", text="Password")
        self.tree.heading("Description", anchor="center", text="Description")

        self.tree.column("Identifier", width=100)
        self.tree.column("Username", width=100)
        self.tree.column("Password", width=100)
        self.tree.column("Description", width=200)

        # Dikey kaydırma çubuğu
        scrollbar = Scrollbar(self.window, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Yatay Kaydırma Çubuğu (bilgilerin ekrandan taşması ihtimaline karşı)
        scrollbar_x = Scrollbar(self.window, orient=HORIZONTAL, command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x", anchor="w")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        self.tree.pack(side="left", fill="both", expand=True)

        self.list_passwords() #Bu metod çağırılarak Treeview doldurulur
    
    def list_passwords(self):
        for identifier, info in get_passwords().items(): #Ana modüldeki get_passwords metodundan dönen değerleri sırayla Treeview'e atar
            if not identifier == "_master_password":
                self.tree.insert("", "end", values=(identifier, info["username"], decrypt_data(return_key(),info["password"]), info["description"]))

class ChangePasswordWindow: #Şifre değiştirme ekranı
    def __init__(self, master):
        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.pack_propagate(False)
        self.window.transient(master)
        self.window.geometry("250x390")
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.title("Change Password")

        self.verified = False

        label_identifier = Label(self.window, text="Identifier", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_identifier.pack(pady=(10, 5))

        self.identifier = StringVar() #Değiştirilecek şifrenin identifier'ı
        self.entry_1 = Entry(self.window, textvariable=self.identifier, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_1.pack(pady=(0, 10))
        #Bu buton ile değiştirilmesi istenen şifrenin varlığı doğrulanır
        self.verify_button = Button(self.window, text="Verify", font=MODERN_FONT, relief=FLAT, borderwidth=0, foreground="black", activeforeground="#888888", background=BACKGROUND_COLOR, activebackground=HOVER_COLOR, padx=10, pady=5, command=self.verify)
        self.verify_button.pack()
        #Değiştirilecek şifrenin varlığı doğrulandıktan sonra label_username, entry_2, label_password, entry_3, label_description ve butonlar kullanıma açılır
        label_username = Label(self.window, text="Username", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_username.pack(pady=(10, 5))

        self.username = StringVar()
        self.entry_2 = Entry(self.window, textvariable=self.username, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_2.pack(pady=(0, 10))

        label_password = Label(self.window, text="Password", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_password.pack(pady=(10, 5))

        self.password = StringVar()
        self.entry_3 = Entry(self.window, textvariable=self.password, show="*", font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.entry_3.pack(pady=(0, 10))

        label_description = Label(self.window, text="Description", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label_description.pack(pady=(10, 5))

        self.text = Text(self.window, wrap="word", height=3, width=30, font=MODERN_FONT, relief=FLAT, borderwidth=1, background="#FAFAFA")
        self.text.pack(pady=(0, 10))

        self.button = Button(self.window, text="Modify Password", font=MODERN_FONT, relief=FLAT, borderwidth=0, foreground="black", activeforeground="#888888", background=BACKGROUND_COLOR, activebackground=HOVER_COLOR, padx=10, pady=5, command=self.handle_change)
        self.button.pack()

        #İlk etapta bu widgetlar kapatılır
        self.entry_2.configure(state="disabled")
        self.entry_3.configure(state="disabled")
        self.text.configure(state="disabled")

        self.entry_1.bind("<FocusIn>", lambda e: self.entry_1.configure(background="#FFFFFF"))
        self.entry_1.bind("<FocusOut>", lambda e: self.entry_1.configure(background="#FAFAFA"))
        self.entry_2.bind("<FocusIn>", lambda e: self.entry_2.configure(background="#FFFFFF"))
        self.entry_2.bind("<FocusOut>", lambda e: self.entry_2.configure(background="#FAFAFA"))
        self.entry_3.bind("<FocusIn>", lambda e: self.entry_3.configure(background="#FFFFFF"))
        self.entry_3.bind("<FocusOut>", lambda e: self.entry_3.configure(background="#FAFAFA"))
        self.text.bind("<FocusIn>", lambda e: self.text.configure(background="#FFFFFF"))
        self.text.bind("<FocusOut>", lambda e: self.text.configure(background="#FAFAFA"))
        self.button.bind("<Enter>", lambda e: AdvancedUI.on_button_hover_in(self.button))
        self.button.bind("<Leave>", lambda e: AdvancedUI.on_button_hover_out(self.button))
        self.verify_button.bind("<Enter>", lambda e: AdvancedUI.on_button_hover_in(self.verify_button))
        self.verify_button.bind("<Leave>", lambda e: AdvancedUI.on_button_hover_out(self.verify_button))

    def verify(self):
        identifier = self.identifier.get()
        if identifier == "_master_password": #Master şifre ise doğrulama kesinlikle yapılmaz
            messagebox.showerror("Error", "Invalid identifier")
            self.verified = False
            self.entry_2.configure(state="disabled") #Doğrulanmayan veya master şifre olduğu tespit edilen identifier üzerinde değişiklik yapılmaması için bir önlem olarak girdi widget'ları kapatılır
            self.entry_3.configure(state="disabled")
            self.text.configure(state="disabled")
        else:
            if identifier not in get_passwords(): #Identifier yoksa doğrulama yapılamaz
                messagebox.showerror("Error", "Password Not Found")
                self.verified = False
                self.entry_2.configure(state="disabled")
                self.entry_3.configure(state="disabled")
                self.text.configure(state="disabled")
            else:
                messagebox.showinfo("Success", "Password Successfully Verified")
                self.entry_2.configure(state="normal")
                self.entry_3.configure(state="normal")
                self.text.configure(state="normal")
                self.verified = True
    
    def handle_change(self):
        if not self.verified == True:
            messagebox.showerror("Error", "Password Not Verified!")
        else:
            if messagebox.askyesno("Confirmation", f"Are you sure you want to delete the password with identifier '{self.identifier}'?"): #Şifre bilgileri değiştirilmeden önce doğrulama alınır
                try: #Doğrulama gerçekleştiyse şifre bilgileri değiştirilir
                    change_password(self.identifier.get(), self.username.get(), self.password.get(), self.text.get("1.0", "end")) #Ana modüldeki change_password metoduyla şifre bilgilerinde değişiklik yapılır
                    messagebox.showinfo("Success", "Password Successfully Changed!")
                    self.window.destroy()
                except:
                    messagebox.showerror("Error", "Password Not Changed!")
            else:
                pass

class DeletePasswordWindow: #Şifre silme ekranı
    def __init__(self, master):
        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.transient(master)
        self.window.geometry("250x120")
        self.window.configure(bg=BACKGROUND_COLOR)

        self.window.title("Delete Password")

        label = Label(self.window, text="Enter the identifier", font=TITLE_FONT, bg=BACKGROUND_COLOR)
        label.pack(pady=(10, 5))

        self.identifier = StringVar()
        self.entry = Entry(self.window, textvariable=self.identifier, font=MODERN_FONT, relief="flat", borderwidth=1, background="#FAFAFA")
        self.entry.pack(pady=(0, 10))

        self.button = Button(self.window, text="Delete", command=self.delete_password, font=MODERN_FONT, relief="flat", borderwidth=0, foreground="black", activeforeground="#888888", background=BACKGROUND_COLOR, activebackground=HOVER_COLOR, padx=10, pady=5)
        self.button.pack()

        self.entry.bind("<FocusIn>", lambda e: AdvancedUI.on_entry_focus_in(e))
        self.entry.bind("<FocusOut>", lambda e: AdvancedUI.on_entry_focus_out(e))

        self.button.bind("<Enter>", lambda e, b=self.button: AdvancedUI.on_button_hover_in(b))
        self.button.bind("<Leave>", lambda e, b=self.button: AdvancedUI.on_button_hover_out(b))

    def delete_password(self): #Şifre silme metodu
        identifier = self.identifier.get()
        if messagebox.askyesno("Confirmation", f"Are you sure you want to delete the password with identifier '{identifier}'?"): #Şifre silinmeden önce doğrulama alınır
            delete_password(identifier) #Doğrulama yapıldıysa silme işlemi gerçekleştirilir
            messagebox.showinfo("Success", "Password deleted successfully")
            self.window.destroy()
        else:
            pass

class InterfaceTitle: #Ana arayüz başlık widget'ı
    def __init__(self, master, text):
        self.frame = Frame(master, bg=BACKGROUND_COLOR)
        self.frame.pack(fill="both", expand=True)

        self.label = Label(self.frame, text=text, font=MAIN_TITLE_FONT, bg=BACKGROUND_COLOR)
        self.label.pack(pady=(10, 20))

class MainInterface: #Ana arayüz
    def __init__(self, master):
        self.master = master
        self.frame = Frame(master, bg=BACKGROUND_COLOR)
        self.frame.pack(expand=True, padx=20, pady=20)

        #Arayüzü modernleştirmek için buton metinleriyle birlikte semboller de kullandım
        buttons_data = [
            ("Add Password", "➕", self.add_password),
            ("List Passwords", "📋", self.list_passwords),
            ("Change Password", "🔏", self.change_password),
            ("Change Master Password", "🔑", self.change_master_password),
            ("Delete Password", "🚮", self.delete_password),
            ("Exit", "🚪", self.exit_app)
        ]

        #Her butonu ayrı ayrı tanımlayıp pack'ledim
        for text, icon, command in buttons_data:
            button = Button(self.frame, text=f"{icon} {text}", command=command,
                            font=MODERN_FONT, relief=FLAT, borderwidth=0,
                            foreground="black", activeforeground="#888888",
                            background=BACKGROUND_COLOR, activebackground=HOVER_COLOR,
                            padx=20, pady=10)
            button.bind("<Enter>", lambda e, b=button: AdvancedUI.on_button_hover_in(b)) #Her buton için hover in ve hover out metodlarını bind'leyerek Modern Web arayüzü tarzında bir işlevsellik oluşturdum
            button.bind("<Leave>", lambda e, b=button: AdvancedUI.on_button_hover_out(b))
            button.pack(fill='x', pady=5)

    def add_password(self): #Ana arayüzden çağırılır, şifre ekleme ekranına yönlendirir
        AddPasswordWindow(self.master)

    def list_passwords(self): #Ana arayüzden çağırılır, şifre listeleme ekranına yönlendirir
        ListPasswordsWindow(self.master)

    def change_password(self): #Ana arayüzden çağırılır, şifre bilgisi değiştirme ekranına yönlendirir
        ChangePasswordWindow(self.master)

    def change_master_password(self): #Ana arayüzden çağırılır, master şifre değiştirme ekranına yönlendirir
        MasterPasswordWindow(self.master, masterpass_exists="new")

    def delete_password(self): #Ana arayüzden çağırılır, şifre silme ekranına yönlendirir
        DeletePasswordWindow(self.master)

    def exit_app(self):
        sys.exit()
