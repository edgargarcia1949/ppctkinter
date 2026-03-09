import tkinter as tk
from datetime import datetime
import calendar
import textwrap
import os
import json
import time
import subprocess
import sys
from PIL import ImageGrab, Image, ImageTk
import ctypes

COLOURS = ["blue", "green", "maroon", "purple", "teal", "fuchsia", "lime", "olive", "navy", "red", "orange", "aqua"]
MONTH_STRINGS=["DECEMBER", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
            "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY"]
DAYS_OF_WEEK_LONG = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
DAYS_OF_WEEK_SHORT = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
DAY_NUMBERS=[" 1"," 2"," 3"," 4"," 5"," 6"," 7"," 8"," 9","10","11","12","13","14","15",
      "16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"]
CALC_X_AND_Y = (45, 119, 183)    # first 2 help calculate x value for day rectangle location, 3rd helps
                                         # calculate y value
STATIC_HOLIDAYS = "StaticHolidays.json"
FLOAT_HOLIDAYS = "FloatHolidays.json"
PERSONAL_EVENTS = "PersonalEvents.json"

RECTANGLES = [
    (45, 43, 238, 25, 2, 595),  # small calendar headings
    (45, 68, 34, 90, 7, 34),    # left small calendar columns
    (640, 68, 34, 90, 7, 34),   # right small calendar columns
    (45, 158, 119, 25, 7, 119), # weekday headings
    (283, 43, 357, 115, 1, 0),  # month and year rectangle
    (45, 43, 833, 620, 1, 0)    # main body rectangle
]

W1, W2 = 119, 34
X1, X2, X3, X4, X5, X6, X7, X8, X9 = 45, 595, 63, 658, 640, 165, 760, 283, 460
Y1, Y2, Y3, Y4 = 43, 56, 71, 132

DAYS_OF_WEEK_LONG_LOC = (105, 171)
DAYS_OF_WEEK_SHORT_LOC = (62, 76)
SMALL_RECT = 30
MONTH_ENTER = (165, 678)
MONTH_LABEL = (90, 678)
YEAR_ENTER = (280, 678)
YEAR_LABEL = (220, 678)
MINUS_BUTTON = (787, 1)
PLUS_BUTTON = (837, 1)
HELP_BUTTON = (687, 1)
PRINT_BUTTON = (587, 1)

Y_OFFSET4 = 120
Y_OFFSET5 = 96
Y_OFFSET6 = 80

class MonthClass:
    def __init__(self, name):
        self.name = name
        self.stday = 0
        self.dysinmth = 0
        self.yoffset = 0
        self.day_obj = []  # will hold 28 to 31 DayClass instances

class DayClass:
    def __init__(self, month, dy):
        self.month = month
        self.dy = dy
        self.x = 0      # will be used as pos x on screen
        self.y = 0      # will be used as pos y on screen
        self.holiday = ""   # will hold holiday string
        self.personal = ""  # will hold personal event string

def draw_calendar_template():
    # draw 25 rectangles
    for (x1, y1, x2, y2, qty, offset) in RECTANGLES:
        for i in range(qty):
            canvas.create_rectangle(x1+i*offset, y1, x1+i*offset+x2, y1+y2, outline="black", width=2)
    # draw days of week strings long
    for i in range(7):
        canvas.create_text(DAYS_OF_WEEK_LONG_LOC[0]+i*W1, DAYS_OF_WEEK_LONG_LOC[1], text = DAYS_OF_WEEK_LONG[i],
        font=("Arial", 16), fill="black")
    # draw days of week strings short twice
    for i in range(2):
        for j in range(7):
            canvas.create_text(DAYS_OF_WEEK_SHORT_LOC[0]+i*X2+j*W2, DAYS_OF_WEEK_SHORT_LOC[1],
            text = DAYS_OF_WEEK_SHORT[j], font=("Arial", 13), fill="black")

def initialize_month(yr):
    MV.mth_obj = []      # start with empty month instance list
    for i in range(12):
        MV.mth_obj.append(MonthClass(MONTH_STRINGS[i+1]))
        # create 12 instances of MonthClass each called mth_obj[i]
        temp = calendar.monthrange(yr, i+1)
        MV.mth_obj[i].stday = (temp[0]+1)%7     # calc start day for each month with week starting on Sunday
        MV.mth_obj[i].dysinmth = temp[1]        # calc number of days in month for each month
        for j in range(temp[1]):
            MV.mth_obj[i].day_obj.append(DayClass(i+1,j+1))
            # create 28 to 31 instances of DayClass in each month instance called mth_obj[i].day_obj[j]
    for i in range(12):
        MV.mth_obj[i].yoffset = Y_OFFSET5    # calc yoffsets for pleasing calendar rows
        if MV.mth_obj[i].stday >=5 and MV.mth_obj[i].dysinmth == 31:    # happens about 3 times a year
            MV.mth_obj[i].yoffset = Y_OFFSET6
        if MV.mth_obj[i].stday == 6 and MV.mth_obj[i].dysinmth >= 30:
            MV.mth_obj[i].yoffset = Y_OFFSET6
        if MV.mth_obj[1].stday == 0 and MV.mth_obj[1].dysinmth == 28:   # happens about once in 10 years
            MV.mth_obj[1].yoffset = Y_OFFSET4
    for i in range(12):
        ctr = MV.mth_obj[i].stday
        for j in range (MV.mth_obj[i].dysinmth):
            MV.mth_obj[i].day_obj[j].x = CALC_X_AND_Y[0] + ctr%7 * CALC_X_AND_Y[1]     # all days in year have x coordinate for display
            MV.mth_obj[i].day_obj[j].y = CALC_X_AND_Y[2] + ctr//7 * MV.mth_obj[i].yoffset    # all days in year have y coordinate
            ctr += 1

def load_json_files():
    filename = STATIC_HOLIDAYS  # load text file of holidays that do not change
    load_events(filename)
    filename = str(MV.year) + FLOAT_HOLIDAYS  # load text file of holidays that do change
    load_events(filename)
    filename = PERSONAL_EVENTS  # load file of personal birthdays, anniversaries and misc. days of importance
    load_events(filename)

def load_events(filename):
    """Loads events from a JSON file and validates the structure."""
    try:
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                events = json.load(f)
                if not isinstance(events, list):
                    handle_file_error(f"Structure error in {filename}: Expected a list.")
                    return
                for item in events:
                    # JSON loads tuples as lists, so we check for list length
                    if not (isinstance(item, list) and len(item) == 3):
                        handle_file_error(f"Format error in {filename}: Elements must be [month, day, 'text'].")
                        continue
                    m, d, text = item
                    if 1 <= m <= 12 and 1 <= d <= 31 and text != "":  # load only if date is valid
                        if filename == PERSONAL_EVENTS:
                            MV.mth_obj[m - 1].day_obj[d - 1].personal = text  # load a personal event
                        else:
                            if MV.mth_obj[m - 1].day_obj[d - 1].holiday == "":
                                MV.mth_obj[m - 1].day_obj[d - 1].holiday = text  # else load a holiday
                            else:
                                MV.mth_obj[m - 1].day_obj[
                                    d - 1].holiday += "    " + text  # a holiday already exists so add to it
    except (json.JSONDecodeError, IOError) as e:
        handle_file_error(f"Could not read {filename}: {str(e)}")


def handle_file_error(error_message):
    error_win = tk.Toplevel()
    error_win.configure(bg="white")
    error_win.title("Input File Error")
    error_win.geometry("600x200")
    error_win.grab_set()
    error_win.attributes("-topmost", True)
    label = tk.Label(error_win, text=error_message, font=("Arial", 12), fg="red", bg='white')
    label.pack(pady=40)
    continue_btn = tk.Button(error_win, text="Continue", command=error_win.destroy)
    continue_btn.pack(pady=10)

def do_small_calendar(mth):
    if MV.month == 0:
        temp = calendar.monthrange(MV.year - 1, 12)  # sets up December of previous year
        stdy = (temp[0] + 1)
        dsinmo = 31
    else:
        stdy = MV.mth_obj[mth - 1].stday  # otherwise sets up previous month
        dsinmo = MV.mth_obj[mth - 1].dysinmth
        do_small_calendar_month(stdy, dsinmo, X3)
    if MV.month == 11:
        temp = calendar.monthrange(MV.year + 1, 1)  # sets up January of next year
        stdy = (temp[0] + 1) % 7
        dsinmo = 31
    else:
        stdy = MV.mth_obj[mth + 1].stday  # otherwise sets up next month
        dsinmo = MV.mth_obj[mth + 1].dysinmth
        do_small_calendar_month(stdy, dsinmo, X4)

def do_small_calendar_month(stday, dsinmo, x):    # draws small calendars of previous month and next month
    for i in range(7):
        canvas.create_rectangle(x-17+i*W2, 81, x-17+i*W2+W2-2, 157, fill = 'white', width=0) # clear previous numbers
    ctr=stday    
    for i in range(dsinmo):    
        canvas.create_text(x+ctr%7*W2, 88+ctr//7*12, text=DAY_NUMBERS[i], font=("Arial", 13), fill="black")
        ctr+=1

def do_small_calendar_headings():        
    canvas.delete("smcal")  # clear previous month and year on both sides
    if MV.month == 0:   # if current month is January
        canvas.create_text(X6, Y2, text = MONTH_STRINGS[MV.month] + "  " + str(MV.year - 1), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # put December in left small calendar and previous year
        canvas.create_text(X7, Y2, text = MONTH_STRINGS[MV.month + 2] + "  " + str(MV.year), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # next month in right small calendar        
    elif MV.month == 11:  # if current month is December
        canvas.create_text(X7, Y2, text = MONTH_STRINGS[MV.month + 2] + "  " + str(MV.year + 1), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # put January in right small calendar and next year
        canvas.create_text(X6, Y2, text = MONTH_STRINGS[MV.month] + "  " + str(MV.year), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # previous month in left small calendar
    else:           
        canvas.create_text(X6, Y2, text = MONTH_STRINGS[MV.month] + "  " + str(MV.year), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # previous month in left small calendar
        canvas.create_text(X7, Y2, text = MONTH_STRINGS[MV.month + 2] + "  " + str(MV.year), font=("Arial", 18),\
                           fill = "black", tags="smcal")  # next month in right small calendar                   

def draw_month_and_year():  
    canvas.delete("mthandyr")    # erase month and year in rectangle
    canvas.create_text(X9, Y3, text = MV.mth_obj[MV.month].name, font=("Arial", 48, "bold"), fill = COLOURS[MV.month], tags="mthandyr")
    canvas.create_text(X9, Y4, text = str(MV.year), font = ("Arial", 48, "bold"), fill = COLOURS[MV.month], tags="mthandyr")

def draw_main_body():
    canvas.delete("day_element")     # erase main body rectangle of all elements
    for i in range(MV.mth_obj[MV.month].dysinmth):
        day = MV.mth_obj[MV.month].day_obj[i]
        if MV.year == MV.current_year and MV.month == MV.current_month-1 and i == MV.current_day-1:
            MV.current_day_rect_id = canvas.create_rectangle(day.x, day.y, day.x + W1, day.y + MV.mth_obj[MV.month].yoffset, outline="black", width=2,
            fill = "light green", tags="day_element")       # highlight current day
        else:
            canvas.create_rectangle(day.x, day.y, day.x + W1, day.y + MV.mth_obj[MV.month].yoffset, outline="black", width=2, tags="day_element")
        # draws big rectangle
        canvas.create_rectangle(day.x, day.y, day.x + SMALL_RECT, day.y + SMALL_RECT, outline="black", width=2, tags="day_element") # small rectangle
        canvas.create_text(day.x + 15, day.y + 16, text = DAY_NUMBERS[i], font = ("Arial", 18), fill = "black", tags="day_element")
        # number in small rectangle
        value1 = MV.mth_obj[MV.month].day_obj[i].holiday  # if there are holidays and personal events,
        value2 = MV.mth_obj[MV.month].day_obj[i].personal  # then word wrap them with 4 spaces in between
        if value1 != "":
            if value2 != "":
                value3 = value1 + "    " + value2
            else:
                value3 = value1
        else:
            value3 = value2
        if value3 != "":
            wrapper = textwrap.TextWrapper(width=15)
            word_list = wrapper.wrap(text=value3)
            ctr2 = 0
            for line in word_list:
                canvas.create_text(day.x+60, day.y+38 + (ctr2 * 12), text=line, font=("Arial", 13), tags="day_element")  # display it to screen
                ctr2 += 1  # one line at a time

def go_ahead():
    MV.month += 1
    if MV.month == 12:
        MV.month = 0
        MV.year += 1
    draw_calendar()
    MV.month_enter.delete(0, tk.END)
    MV.month_enter.insert(0, MV.month+1)
    MV.year_enter.delete(0, tk.END)
    MV.year_enter.insert(0, MV.year)
        
def go_back():
    MV.month -= 1
    if MV.month < 0:
        MV.month = 11
        MV.year -= 1
    draw_calendar()
    MV.month_enter.delete(0, tk.END)
    MV.month_enter.insert(0, MV.month+1)
    MV.year_enter.delete(0, tk.END)
    MV.year_enter.insert(0, MV.year)

def draw_calendar():
    initialize_month(MV.year)       # sets up start date and number of days in month for each month
    do_small_calendar(MV.month)     # displays small calendar for previous month and next month
    do_small_calendar_headings()    # displays month and year in small calendars
    draw_month_and_year()           # displays current month and year in big bold letters in color
    load_json_files()               # load holidays and personal events
    draw_main_body()                # draw 28 to 31 monthly calendar days

def validate_month(P):
    """ Real-time validation to restrict input to 2 digits from 1-12 """
    if P == "":
        return True
    if P.isdigit() and len(P) <= 2:
        return int(P) <= 12
    return False

def validate_year(P):
    """ Real-time validation to restrict input to 4 digits from 1000-9999 """
    if P.isdigit():
        return True
    elif P == "":
        return True
    else:
        return False

def on_year_enter(event):
    """ Logic to execute when Enter key is pressed """
    value = MV.year_enter.get()
    if not value:
        return
    year_val = int(value)
    if 1000 <= year_val <= 9999:
        MV.year = year_val
        initialize_month(MV.year)
        draw_calendar()
        MV.year_enter.delete(0, tk.END)
        MV.year_enter.insert(0, MV.year)
        root.focus_set()    # remove focus from year_enter box

def on_month_enter(event):
    """ Logic to execute when Enter key is pressed """
    value = MV.month_enter.get()
    if not value:
        return
    month_val = int(value)
    if 1 <= month_val <= 12:
        MV.month = month_val - 1
        draw_calendar()
        MV.month_enter.delete(0, tk.END)
        MV.month_enter.insert(0, MV.month+1)
        root.focus_set()    # remove focus from month_enter box

def create_month_input_box():
    vcmd = (root.register(validate_month), '%P')
    MV.month_enter = tk.Entry(root, validate="key", validatecommand=vcmd, width=3, justify='center',
        font=("Arial", 16, "bold"))
    MV.month_enter.insert(0, MV.month+1)
    MV.month_enter.bind("<Return>", on_month_enter)
    MV.month_enter.place(x=MONTH_ENTER[0], y=MONTH_ENTER[1])
    MV.month_label = tk.Label(root, text="MONTH:", font=("Arial", 16, "bold"))
    MV.month_label.place(x=MONTH_LABEL[0], y=MONTH_LABEL[1])
    MV.my_widgets.append(MV.month_enter)
    MV.my_widgets.append(MV.month_label)

def create_year_input_box():
    vcmd_year = (root.register(validate_year), '%P')
    MV.year_enter = tk.Entry(root, validate="key", validatecommand=vcmd_year, width=4, justify='center',
         font=("Arial", 16, "bold"))
    MV.year_enter.insert(0, MV.year)
    MV.year_enter.bind("<Return>", on_year_enter)
    MV.year_enter.place(x=YEAR_ENTER[0], y=YEAR_ENTER[1])
    MV.year_label = tk.Label(root, text="YEAR:", font=("Arial", 16, "bold"))
    MV.year_label.place(x=YEAR_LABEL[0], y=YEAR_LABEL[1])
    MV.my_widgets.append(MV.year_enter)
    MV.my_widgets.append(MV.year_label)

def on_left_click(event):
    # event.x and event.y contain cursor coordinates when left mouse button is clicked
    if MV.index == None:
        for i in range(MV.mth_obj[MV.month].dysinmth): 
            day = MV.mth_obj[MV.month].day_obj[i]
            if event.x>day.x and event.x<day.x+W1 and event.y>day.y and event.y<day.y+MV.mth_obj[MV.month].yoffset:
                MV.index = i    # we know which day was just clicked
                break
        if MV.index != None:    # if a day was clicked, create a text input box
            MV.text_input = tk.Text(root, height=3, width=14, font=("Arial", 13), wrap=tk.WORD)
            MV.text_input.place(x=MV.mth_obj[MV.month].day_obj[MV.index].x, y=MV.mth_obj[MV.month].day_obj[MV.index].y+30)
            MV.text_input.focus_set()
            MV.text_input.bind("<Return>", process_day_input)

def process_day_input(event):
    root.focus_set()
    temp = MV.text_input.get("1.0", tk.END)
    temp = temp.rstrip()        # remove /n from end of string
    if len(temp) > 50:
        temp = temp[:50]        # keep personal event at 50 characters or less
    MV.mth_obj[MV.month].day_obj[MV.index].personal = temp    # store in memory
    save_personal_events()      # save personal events to json file
    draw_main_body()       # done to show new personal event
    MV.text_input.destroy()     # remove from calendar, no longer needed
    MV.index = None

def save_personal_events():
        personal_events = []
        for i in range(12):     # go through memory and create personal events list
            for j in range(MV.mth_obj[i].dysinmth):
                if MV.mth_obj[i].day_obj[j].personal != "":
                    personal_events.append((MV.mth_obj[i].day_obj[j].month, \
                    MV.mth_obj[i].day_obj[j].dy, MV.mth_obj[i].day_obj[j].personal))
        with open(PERSONAL_EVENTS, "w") as f:
            json.dump(personal_events, f, indent=4)     # save personal_events list to file

def create_buttons_and_text_boxes():
    # Create 4 button widgets and 2 input widgets
    minus_button = tk.Button(root, text=" - ", font=("Arial", 20), command=go_back)
    minus_button.place(x=MINUS_BUTTON[0], y=MINUS_BUTTON[1])
    MV.my_widgets.append(minus_button)  # all these buttons and widgets are stored in a list for easy hiding
    plus_button = tk.Button(root, text=" + ", font=("Arial", 20), command=go_ahead)
    plus_button.place(x=PLUS_BUTTON[0], y=PLUS_BUTTON[1])
    MV.my_widgets.append(plus_button)
    help_button = tk.Button(root, text="Help", font=("Arial", 18), command=display_help)
    help_button.place(x=HELP_BUTTON[0], y=HELP_BUTTON[1])
    MV.my_widgets.append(help_button)
    print_button = tk.Button(root, text="Print", font=("Arial", 18), command=lambda: print_canvas())
    print_button.place(x=PRINT_BUTTON[0], y=PRINT_BUTTON[1])
    MV.my_widgets.append(print_button)
    # Create a month and year input box
    create_year_input_box()
    create_month_input_box()

def hide_buttons_and_text_boxes():  # hide buttons and text boxes and labels for cleaner printout
    for widget in MV.my_widgets:
        widget.place_forget()
        widget.update()          

def display_help():
    help_win = tk.Toplevel()
    help_win.configure(bg="white")
    help_win.title("Help")
    help_win.geometry("500x450")
    help_win.grab_set()
    help_win.attributes("-topmost", True)
    header_font = ("Arial", 18, "normal")
    desc_font = ("Arial", 16, "normal")
    header_color = "purple"
    desc_color = "blue"

    help_items = [
        (" -  button", "Goes back 1 month"),
        (" +  button", "Advances 1 month"),
        ("Print", "Removes Buttons and Text Boxes,\nSends screenshot to default printer,\nWaits 4 seconds"),
        ("Event", "Click on desired day, enter text,\nHit <Enter> to store"),
        ("Delete", "Click on desired personal event,\nHit <Enter>, event is deleted"),
        ("Month text box", "Enter month desired, hit <Enter>\nGoes to any month from 1-12"),
        ("Year text box", "Enter year desired, hit <Enter>\nGoes to any year from 1000-9999")
    ]
    for i, (head, desc) in enumerate(help_items):
        lbl_head = tk.Label(help_win, text=head, font=header_font, fg=header_color,
             bg="white", justify="right", anchor="e")
        lbl_head.grid(row=i, column=0, sticky="ne", padx=(20, 30), pady=10)
        lbl_desc = tk.Label(help_win, text=desc, font=desc_font, fg=desc_color,
             bg="white", justify="left", anchor="w")
        lbl_desc.grid(row=i, column=1, sticky="nw", pady=10)
    help_win.grid_columnconfigure(0, weight=1)
    help_win.grid_columnconfigure(1, weight=1)

def print_canvas():
    hide_buttons_and_text_boxes()     # used for cleaner printout
    canvas.itemconfig(MV.current_day_rect_id, fill = "white")  
    root.update_idletasks()           # hide current day)
    if sys.platform == 'win32':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    root.update()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = x + root.winfo_width()
    h = y + root.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, w, h))
    img.save("temp.png")
    fname = "temp.png"
    time.sleep(4)   # wait for file to be saved
    if sys.platform == 'win32': # call Windows print subprocess if this is Windows
        os.startfile(fname, "print")
    else:
        subprocess.run(['lpr', fname])  # call Linux print subprocess otherwise
    create_buttons_and_text_boxes()
    draw_main_body()
          
    #Main Variables
class MV:
    year = datetime.now().year
    current_year = year
    current_month = datetime.now().month
    current_day = datetime.now().day
    month = current_month - 1
    mth_obj = []    # will be list of 12 instances of MonthClass
    my_widgets = [] # will hold list of 8 widgets
    text_input = None   # used to input data into day rectangle
    index = None        # will hold which day was clicked on
    month_enter = None  # will hold text input box to enter month from 1-12
    month_label = None  # will hold the word "Month:"
    year_enter = None   # will hold year input box to enter year from 1000-9999
    year_label = None   # will hold the word "Year:"
    current_day_rect_id = None     # will hold id of rectangle highlighted to represent current day

# Create the main window
root = tk.Tk()
root.title("Monthly Calendar")

WIDTH = 924
HEIGHT = 714

# Create a canvas widget
global canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

create_buttons_and_text_boxes()     # creates 4 buttons and 2 text boxes

# Create cursor on left click event
root.bind("<Button-1>", on_left_click)  # log on left clicck
draw_calendar_template()  # draws parts that every monthly calendar has in common
draw_calendar()           # draws parts that change every month and year

# Run the Tkinter event loop
root.mainloop()
