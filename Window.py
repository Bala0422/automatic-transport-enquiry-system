import tkinter as tk
import vlc
from tkinter import Canvas, Label, StringVar, messagebox
from tkinter import ttk, StringVar, Label, Canvas, Entry, Button
import MySQLdb
import speech_recognition
from gtts import gTTS
from gtts.tokenizer import pre_processors


# To run a function in a Thread
def NewThread(Function):
    def Wrapper(*args):
        from _thread import start_new_thread
        start_new_thread(Function, tuple(arg for arg in args))

    return Wrapper


# class where the UI runs
class Window:
    def __init__(self, Parent):
        self.Parent = Parent
        self.view = None
        self.Image = None
        self.Frame = None
        self.img_main = None
        self.Pos = {"X": 0, "Y": 0}
        self.C_pos = {"X": 50, "Y": 50}
        self.Width = 600
        self.Height = 600
        self.place = None
        self.destination_out = None
        self.arrival_out = None
        self.timing = None
        self.sorry = "Sorry i didn't get you . Try speaking again"
        self.welcomeNote = '''Welcome to the Transport Enquiry System. you can view the bus timings and cost.
                        you can also book your ticket here. '''

    # To give a welcome note and a sorry text if some errors happened in recognizing voice
    @NewThread
    def Exceptions(self, text):

        input_text = text
        out = pre_processors.abbreviations(input_text)
        out = pre_processors.word_sub(out)

        output = gTTS(out, lang='en', slow=False)
        try:
            output.save("speech.mp3")
            media = vlc.MediaPlayer("speech.mp3")
            media.play()
        except ValueError:
            w.Exceptions(text)

    # The first page of the UI
    def OnCreate(self):

        bg = "#80c1ff"
        # To establish a connection between the python and the database
        db = MySQLdb.connect(host='localhost',
                             user='root',
                             passwd='balas11c1',
                             db='test')

        cur = db.cursor()
        cur2 = db.cursor()
        cur3 = db.cursor()

        cur.execute('select * from test.route')
        cur2.execute('select * from test.busroute')
        cur3.execute('select * from test.bus')

        origin = []
        route_id = []
        dest = {}
        arr = {}

        for i in cur.fetchall():
            route_id.append(i[0])
            arr[i[2]] = i[0]
            dest[i[1]] = i[0]
            origin.append(i[1] + " - to - " + i[2])

        bus_id = {}
        r_time = {}
        route_id2 = []
        time = []
        for j in cur2.fetchall():
            route_id2.append(j[1])
            bus_id[j[1]] = j[0]
            time.append(j[2])
            r_time[j[0]] = j[2]

        fare = {}
        b_id2 = []
        for k in cur3.fetchall():
            b_id2.append(k[0])
            fare[k[0]] = k[2]

        # To give speech output
        def speech(text, x):
            try:
                output = gTTS(text, lang='en', slow=False)
                try:
                    output.save("speech.mp3")
                    try:
                        self.output.destroy()
                    except AttributeError:
                        pass
                    self.output = Label(self.Frame, bg=bg, text=x)
                    self.output.place(x=dept_label.winfo_reqwidth() + 20, y=departure.winfo_reqheight() + 70)
                    media = vlc.MediaPlayer("speech.mp3")
                    media.play()
                except ValueError:
                    speech(text, x)
            except AssertionError:
                print('Enter a text to get the speech')

        w.Exceptions(self.welcomeNote)

        self.Parent.configure(height=600, width=600)
        from PIL import Image, ImageTk
        img = Image.open("C:/Users/Hp/Downloads/bus.jpeg")
        img = img.resize((1500, 1500))
        self.Image = ImageTk.PhotoImage(img)
        self.view = Canvas(self.Parent, width=600, height=600, bd=4, bg='lightblue')
        self.view.create_image(0, 0, image=self.Image)
        self.view.place(x=self.Pos["X"], y=self.Pos["Y"])

        self.Frame = Canvas(self.view, width=500, height=500, cursor="circle", bd=4, bg=bg)
        self.Frame.place(x=self.C_pos["X"], y=self.C_pos["Y"])

        heading = Label(self.Frame, bg=bg, text="Enquiry System")
        heading.place(x=220, y=5)

        dept_label = Label(self.Frame, bg=bg, text="Select the Departure and Destination:-")
        dept_label.place(x=3, y=55)

        dept_var = StringVar()
        departure = ttk.Combobox(self.Frame, width=20, textvariable=dept_var)
        departure.place(x=dept_label.winfo_reqwidth() + 20, y=50)

        departure['values'] = tuple(origin)

        def on_click():
            r_id = None
            b_id = None
            b_t = None
            self.place = dept_var.get()
            val = self.place.split()
            try:
                if val[0] in dest.keys():
                    r_id = dest.get(val[0])

                if r_id in bus_id.keys():
                    b_id = bus_id.get(r_id)

                if b_id in fare.keys():
                    cost = fare.get(b_id)
                    if b_id in r_time.keys():
                        out2 = r_time.get(b_id)
                    out = f'''Total fair from {self.place}: {cost} $ 
    
                    Bus arrival time {out2} 
                       '''

                last = self.place.split()
                self.arrival_out = last[0]
                self.destination_out = last[4]
                self.timing = out2
                input_text = out
                text = pre_processors.abbreviations(input_text)
                text = pre_processors.word_sub(text)
                from _thread import start_new_thread
                start_new_thread(speech, (text, out))
            except IndexError:
                pass

        submit = Button(self.Frame, text='Say Cost and Time', command=on_click)
        submit.place(x=self.Frame.winfo_reqwidth() / 2, y=self.Frame.winfo_reqheight() / 2, anchor="center")

        def Next():
            w.Destroy()
            w.SecondWindow()

        book_ticket = Button(self.Frame, text='Book a Ticket', command=Next)
        book_ticket.place(x=200, y=300)

        # To get a voice input from the user
        @NewThread
        def listener():

            try:
                Reg = speech_recognition.Recognizer()
                with speech_recognition.Microphone() as source:
                    audio = Reg.listen(source)
                    inp_voice = Reg.recognize_google(audio)

                if inp_voice[0] == 's':
                    on_click()
                elif inp_voice[0] == 'b':
                    Next()
                else:
                    w.Exceptions(self.sorry)

            except Exception as e:
                w.Exceptions(self.sorry)

        voice_inp = Button(self.Frame, text='Give a voice command', command=listener)
        voice_inp.place(x=200, y=400)

        db.close()

    def Destroy(self):
        self.Frame.destroy()

    def SecondWindow(self):

        bg = "#80c1ff"

        self.Parent.config(height=600, width=600, bg='lightblue')

        from PIL import Image, ImageTk
        img = Image.open("C:/Users/Hp/Downloads/bus.jpeg")
        img = img.resize((1500, 1500))
        self.Image = ImageTk.PhotoImage(img)
        self.view = Canvas(self.Parent, width=600, height=600, bd=4, bg='lightblue')
        self.view.create_image(0, 0, image=self.Image)
        self.view.place(x=self.Pos["X"], y=self.Pos["Y"])

        self.Frame = Canvas(self.view, height=500, width=500, cursor='circle', bd=4, bg=bg)
        self.Frame.place(x=50, y=50)

        heading = Label(self.Frame, text='Enter the following information :-', bg=bg, font='italics')
        heading.place(x=10, y=5)

        name = Label(self.Frame, text='Name    :', bg=bg)
        name.place(x=10, y=60)

        Name = StringVar()
        name_text = Entry(self.Frame, bd=4, textvariable=Name)
        name_text.place(x=name.winfo_reqwidth() + 40, y=60)

        age = Label(self.Frame, text='Age       :', bg=bg)
        age.place(x=name_text.winfo_reqwidth() + 120, y=60)

        Age = StringVar()
        age_text = Entry(self.Frame, bd=4, textvariable=Age)
        age_text.place(x=age.winfo_reqwidth() + 300, y=60)

        gender = Label(self.Frame, text="Gender    :", bg=bg)
        gender.place(x=10, y=name.winfo_reqheight() + 100)

        Gender = StringVar()
        gender_text = ttk.Combobox(self.Frame, width=10, textvariable=Gender)
        gender_text.place(x=gender.winfo_reqwidth() + 50, y=name.winfo_reqheight() + 100)

        g_values = ('Male', 'Female', 'Other')
        gender_text['values'] = g_values

        phone_no = Label(self.Frame, text='Phone No.    :', bg=bg)
        phone_no.place(x=gender_text.winfo_reqwidth() + 165, y=name.winfo_reqheight() + 100)

        Phone_no = StringVar()
        phone_text = Entry(self.Frame, bd=4, textvariable=Phone_no)
        phone_text.place(x=phone_no.winfo_reqwidth() + 275, y=name.winfo_reqheight() + 97)

        email = Label(self.Frame, text="E-mail ID       :", bg=bg)
        email.place(x=10, y=name.winfo_reqheight() + 160)

        Email_ID = StringVar()
        email_text = Entry(self.Frame, bd=4, width=50, textvariable=Email_ID)
        email_text.place(x=email.winfo_reqwidth() + 30, y=name.winfo_reqheight() + 160)

        departure = Label(self.Frame, text='Departure    :', bg=bg)
        departure.place(x=10, y=email.winfo_reqheight() + 230)

        Departure = StringVar()
        departure_text = ttk.Combobox(self.Frame, width=20, textvariable=Departure)
        departure_text.place(x=departure.winfo_reqwidth() + 30, y=email.winfo_reqheight() + 230)

        departure_text['values'] = self.arrival_out

        destination = Label(self.Frame, text='Destination    :', bg=bg)
        destination.place(x=departure.winfo_reqwidth() + 180, y=email.winfo_reqheight() + 230)

        Destination = StringVar()
        destination_text = ttk.Combobox(self.Frame, width=20, textvariable=Destination)
        destination_text.place(x=departure.winfo_reqwidth() + 280, y=email.winfo_reqheight() + 230)

        destination_text['values'] = self.destination_out

        date = Label(self.Frame, text="Date of travel  :", bg=bg)
        date.place(x=10, y=destination_text.winfo_reqheight() + 290)

        Month = StringVar()
        date_month = ttk.Combobox(self.Frame, width=3, textvariable=Month)
        date_month.place(x=date.winfo_reqwidth() + 20, y=destination_text.winfo_reqheight() + 290)
        month = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
        date_month['values'] = month

        Day = StringVar()
        date_day = ttk.Combobox(self.Frame, width=3, textvariable=Day)
        date_day.place(x=date.winfo_reqwidth() + 65, y=destination_text.winfo_reqheight() + 290)
        dates = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
        for i in range(10, 32):
            dates.append(i)

        date_day['values'] = dates

        Years = StringVar()
        date_year = ttk.Combobox(self.Frame, width=4, textvariable=Years)
        date_year.place(x=date.winfo_reqwidth() + 110, y=destination_text.winfo_reqheight() + 290)
        year = []
        for i in range(2020, 2030):
            year.append(i)

        date_year['values'] = year

        time = Label(self.Frame, text="Time of travel  :", bg=bg)
        time.place(x=250, y=destination_text.winfo_reqheight() + 290)

        Time = StringVar()
        time_text = ttk.Combobox(self.Frame, width=20, textvariable=Time)
        time_text.place(x=350, y=destination_text.winfo_reqheight() + 290)

        time_text["values"] = self.timing

        def validate():
            try:
                if int(Age.get()) <= 0 or int(Age.get()) > 150:
                    messagebox.showerror("ERROR", "Enter a valid AGE")
            except ValueError:
                pass
            if not Name.get():
                messagebox.showerror("ERROR", "Enter the Name")
            elif not Age.get():
                messagebox.showerror("ERROR", "Enter the Age")
            elif not (Phone_no.get().isnumeric()):
                messagebox.showerror("ERROR", 'Enter a valid PHONE NUMBER')
            elif (int(Phone_no.get()) >= 9999999999) or (int(Phone_no.get()) < 1000000000):
                messagebox.showerror("ERROR", 'Enter a valid PHONE NUMBER')
            elif not Gender.get():
                messagebox.showerror("ERROR", "Enter the Gender")
            elif not Email_ID.get():
                messagebox.showerror("ERROR", "Enter the Email-ID")
            elif not Phone_no.get():
                messagebox.showerror("ERROR", "Enter the Phone no.")
            elif not Departure.get():
                messagebox.showerror("ERROR", "Select the Departure")
            elif not Destination.get():
                messagebox.showerror("ERROR", "Select the Destination")
            elif not Time.get():
                messagebox.showerror("ERROR", "Select the Time of travel")
            elif not Month.get():
                messagebox.showerror("ERROR", "Enter the Month of travel")
            elif not Years.get():
                messagebox.showerror("ERROR", "Enter the Year of travel")
            elif not Day.get():
                messagebox.showerror("ERROR", "Enter the Day of travel")
            else:
                messagebox.showinfo('COMPLETED', 'YOUR TICKET IS BOOKED SUCCESSFULLY')
                w.OnCreate()

        submit = tk.Button(self.Frame, text='Book Ticket', command=validate)
        submit.place(x=200, y=400)


root = tk.Tk()
w = Window(root)
w.OnCreate()

root.mainloop()
