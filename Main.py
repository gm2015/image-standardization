# Data Standardization
# By Dr. Ha Do with help from Tallen Smith, Zach Holden, Adom Simpey, and Hassan Abdulkareem, students at CSUPueblo
# 10/8/19

# Imports necessary libraries
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import tkinter.filedialog
from tkinter import messagebox
import time, os, math, io
import datetime
import json


# Creates a class to hold all the frame information
class App(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.img_folder = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
        self.img_folder = self.img_folder + "/images"
        if not os.path.isdir(self.img_folder):
            os.mkdir(self.img_folder)
        print(self.img_folder)
        # Isn't currently used
        self.IsLoaded = False
        # This setting will turn the outputted image greyscale
        self.IsGreyscale = False
        self.pack()
        # This is the title of the window
        self.master.title("Data Standardization")
        # This is the primary background color of the window
        self.master.tk_setPalette(background="#4d4d4d")
        # Windows have big spacing issues to think about when they get resized... so I don't let them be resized
        self.master.resizable(False, False)
        # The iconbitmap is the small image in the top left of the window
        self.master.iconbitmap('Wolf.ico')
        # This variable will house the loaded image
        self.loadedImage = 'none'
        # Frames to put the widgets into. Run the program to see where they are, since they're labeled currently
        ImageFrame = tk.Frame(self)
        ImageFrame.pack(side='left', padx=25)
        ProcessedFrame = tk.Frame(self)
        ProcessedFrame.pack(side='right')
        OptionsFrame = tk.Frame(ImageFrame)
        OptionsFrame.pack(side='bottom', pady=10)
        #SelectFrame = tk.Frame(ProcessedFrame, height=2)
        #SelectFrame.pack(side='top', padx=25)

        # This is where I labeled all the frames. We can delete this in the final product
        tk.Label(ImageFrame, text='This is the Image Frame').pack()
        tk.Label(ProcessedFrame, text='Processed Frame    ').pack()
        tk.Label(OptionsFrame, text='This is the Options Frame').pack()
        #tk.Label(SelectFrame, text='This is the Select Frame').grid(row=0, column=0, columnspan=2)

        # These are the variables to create the canvas where the image will be loaded onto
        canvasHeight = 1080 / 2
        canvasWidth = 1920 / 2
        canvasHeightRegion = 10000
        canvasWidthRegion = 10000
        self.canvas = tk.Canvas(ImageFrame, width=canvasWidth, height=canvasHeight, bg='white', scrollregion=(0,0,canvasHeightRegion,canvasWidthRegion))
        hbar = tk.Scrollbar(ImageFrame, orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        hbar.config(command=self.canvas.xview)
        vbar = tk.Scrollbar(ImageFrame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=canvasWidth, height=canvasHeight)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        #  Bind a click event of the mouse to the canvas
        self.canvas.bind("<Key>", self.Key)
        self.canvas.bind("<Button-1>", self.Single_Click)
        self.canvas.bind("<Double-1>", self.Double_Click)
        self.canvas.bind("<Motion>", self.pointer_move)

        # This is where I create all the buttons on the screen
        tk.Button(OptionsFrame, text='Load Image', command=self.Load_Image, bg='#6C6C6C', fg='white').pack(side='left',
                                                                                                           padx=10)
        tk.Button(OptionsFrame, text='Saved Folder', command=self.Select_Dir, bg='#6C6C6C', fg='white').pack(side='left',
                                                                                                           padx=10)
        self.folder_entry = tk.Entry(OptionsFrame, bg='#6C6C6C', fg='white')
        self.folder_entry.pack(side='left', padx=10)
        self.folder_entry.insert(0, self.img_folder)

        tk.Label(OptionsFrame, text='Image Name:').pack(side='left', padx=10)
        self.image_name_entry = tk.Entry(OptionsFrame, bg='#6C6C6C', fg='white', width = 8)
        self.image_name_entry.pack(side='left', padx=10)
        self.image_name_entry.insert(tk.END, "image")
        tk.Button(OptionsFrame, text='Update Box Size', command=self.Update_Box_Size, bg='#6C6C6C', fg='white').pack(side='left',
                                                                                                           padx=10)
        self.box_size_entry = tk.Entry(OptionsFrame, bg='#6C6C6C', fg='white', width = 10)
        self.box_size_entry.pack(side='left', padx=10)
        self.box_size_entry.insert(tk.END, "128x128")

        tk.Button(OptionsFrame, text='Update Key:Label', command=self.Update_Keys, bg='#6C6C6C', fg='white').pack(side='left', padx=10)
        self.keys_entry = tk.Entry(OptionsFrame, bg='#6C6C6C', fg='white', width=25)
        self.keys_entry.pack(side='left', padx=10)
        self.keys_entry.insert(tk.END, "{'c':['crack','red'], 'n':['no_crack','cyan']}")
        self.key_label = self.str2dict("{'c':['crack','red'], 'n':['no_crack','cyan']}")

        (self.box_width, self.box_height) = self.get_box_size(self.box_size_entry.get())
        tk.Button(ProcessedFrame, text='     Delete All     ', command=self.Select_All, bg='#6C6C6C', fg='white').pack(side='bottom', padx=10)
        tk.Button(ProcessedFrame, text='Delete Selected', command=self.Delete_Selected, bg='#6C6C6C', fg='white').pack(side='bottom', padx=10)
        tk.Button(ProcessedFrame, text='  Save Image   ', command=self.Save_Image, bg='#6C6C6C', fg='white').pack(
            side='bottom', padx=10)
        # This is for the options widgets at the bottom of the page
        # This checkbutton will determine if the output is greyscale or not
        #tk.Checkbutton(OptionsFrame, text='Greyscale', variable=self.IsGreyscale).pack(side='left', padx=30)
        # This creates the slider that will determine the size of the square that each image will be
        #self.resolution = tk.Scale(OptionsFrame, from_=10, to=500, orient='horizontal')
        #self.resolution.pack()
        # This sets the default size to be 125x125
        #self.resolution.set(125)

        # This loads up my 'No Image' picture onto the canvas. Just a placeholder.
        self.loadedImage = ImageTk.PhotoImage(Image.open('crack1.jpg'))
        self.orginalImage = Image.open('crack1.jpg')
        self.image_file = 'crack1.jpg'
        # This self object is required to prevent tkinter from deleting the picture in a trash roundup
        self.img_width = self.loadedImage.width()
        self.img_height = self.loadedImage.height()
        self.canvas.create_image(0, 0, anchor='nw', image=self.loadedImage)
        self.first_move = True
        self.list_file = []
        self.list_rect = []
        self.list_box_label = []

    # Convert str to dict
    def str2dict(self, str_msg):
        json_str = str_msg.replace("'", "\"")
        try:
            return json.loads(json_str)
        except:
            return False

    # Get correct canvas coordinate when scroll bars have moved
    def get_canvas_coordinate(self, event, canvas):
        x, y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))
        return x, y

    # Get movement direction
    def get_direction(self, pre_box, current_box):
        direction =  (current_box[0] - pre_box [0], current_box[1] - pre_box[1])
        return direction

    # Settings
    def Setting(self, box_height=128, box_width=128):
        self.box_height = box_height
        self.box_width = box_width

    # Convert box size text to number (128x128 -> (128, 128)
    def get_box_size(self, text):
        x = text.find('x')
        return (int(text[:x].strip()), int(text[x+1:].strip()))

    # Select a directory
    def Select_Dir(self):
        folder = tk.filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, folder)
            self.img_folder = folder

    # These callback functions for mouse and keyboard events
    def pointer_move(self, event):
        # print("Current pointer coordinates in the image", self.get_canvas_coordinate(event, self.canvas))
        xy = self.get_canvas_coordinate(event, self.canvas)
        box = tuple(self.get_box(xy, self.box_height, self.box_width, self.img_height, self.img_width))
        # draw a rectangle in canvas
        if self.first_move:
            self.rect = self.canvas.create_rectangle(box[0], box[1], box[2], box[3], outline='blue')
            self.pre_box = box
            self.first_move = False
        else:
            direction = self.get_direction(self.pre_box, box)
            self.canvas.move(self.rect, direction[0], direction[1])
            self.pre_box = box
        self.box_img = self.orginalImage.crop(self.pre_box)

    def Update_Keys(self):
        str_msg = self.keys_entry.get()
        if self.str2dict(str_msg):
            self.key_label = self.str2dict(str_msg)

    def Key(self, event):
        print("Key pressed", repr(event.char))
        if event.char.lower() in self.key_label.keys():
            label_color = self.key_label[event.char.lower()]
            print((label_color))
            print(self.img_folder)
            folder = self.img_folder + '/' + label_color[0]
            if not os.path.isdir(folder):
                os.mkdir(folder)
            filename = self.Generate_Filename(folder, self.image_name_entry.get(), 'crack', 'jpg')
            self.box_img.save(filename, quanlity=100)
            rect = self.canvas.create_rectangle(self.pre_box[0], self.pre_box[1], self.pre_box[2], self.pre_box[3],
                                                    outline=label_color[1])
            self.list_file.append(filename)
            self.list_rect.append(rect)
            self.list_box_label.append(
                    (((self.pre_box[0], self.pre_box[1]), (self.pre_box[2], self.pre_box[3])), label_color[1]))
        else:
            print("Label for Key", repr(event.char), "has not defined")

    def Generate_Filename(self, folder, basename, name, extention):
        uniq_filename = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':','-').replace('.','-')[0:11]
        return "{}/{}_{}_{}.{}".format(folder, basename, name, uniq_filename, extention)

    def get_box(self, center_point, box_height, box_width, img_heigh, img_width):
        box = [center_point[0] - math.ceil(box_width / 2), center_point[1] - math.ceil(box_height / 2),
               center_point[0] + math.floor(box_width / 2), center_point[1] + math.floor(box_height / 2)]
        # Correct if box is out of boundaries
        if box[0] < 0:
            box[2] = box[2] - box[0]
            box[0] = 0
        if box[1] < 0:
            box[3] = box[3] - box[1]
            box[1] = 0
        if box[2] > img_width:
            box[2] = img_width
            box[0] = box[2] - box_width
        if box[3] > img_heigh:
            box[3] = img_heigh
            box[1] = box[3] - box_height
        return box

    def Single_Click(self, event):
        print("Left button clicked")
        self.canvas.focus_set()

    def Double_Click(self, event):
        print("Left button double clicked at", event.x, event.y)
        self.canvas.focus_set()

    # These functions control what all the buttons do
    # PyCharm likes to complain because I like do write my functions Like_This
    def Load_Image(self):
        self.first_move = True
        # Troubleshooting dialog
        print('Loading Up Images!')
        # Removes the previously loaded images
        self.canvas.delete('all')
        # Opens up a dialog path where you can find the image you wish to load.
        self.image_file = tk.filedialog.askopenfilename()
        self.orginalImage = Image.open(self.image_file)
        if self.orginalImage.mode != 'RGB':
            # Convert any image mode to RGB, so we can save to any format
            self.orginalImage = self.orginalImage.convert('RGB')
        self.loadedImage = ImageTk.PhotoImage(self.orginalImage)
        self.canvas.create_image(0, 0, anchor='nw', image=self.loadedImage)
        self.IsLoaded = True
        # Image sizes
        self.img_width = self.loadedImage.width()
        self.img_height = self.loadedImage.height()

    def Update_Box_Size(self):
        self.canvas.delete(self.rect)
        self.first_move = True
        self.box_width, self.box_height = self.get_box_size(self.box_size_entry.get())

    def Save_Image(self):
        print('Saving Labelled Image!')
        save_file = tk.filedialog.asksaveasfilename(defaultextension='.jpg')
        if save_file != "":
            source_img = Image.open(self.image_file)
            if source_img != 'RGB':
                # Convert any image mode to RGB, so we can save to any format
                source_img = source_img.convert('RGB')
            draw = ImageDraw.Draw(source_img)
            for box in self.list_box_label:
                draw.rectangle(box[0], outline=box[1])
            source_img.save(save_file, "JPEG")

    def Select_All(self):
        # Show message to confirm
        MsgBox = tk.messagebox.askquestion('Delete ALL', 'Are you sure you want to delete ALL', icon='warning')
        if MsgBox == 'yes':
            while len(self.list_file) >= 1:
                try:
                    os.remove(self.list_file.pop())
                    self.canvas.delete(self.list_rect.pop())
                    self.list_box_label.pop()
                except:
                    None
            print('Selecting All!')

    def Delete_Selected(self):
        try:
            self.canvas.delete(self.list_rect.pop())
            os.remove(self.list_file.pop())
            self.list_box_label.pop()
            print('Delete Selected!')
        except:
            None

# I genuinely don't know what this does tbh. But it works so.
if __name__ == '__main__':
    # Uh... create a new window class named root
    root = tk.Tk()
    # Then... make an App with root in it?
    app = App(root)
    # This one runs the mainloop of the app! I know that one. This is what draws the window.
    app.mainloop()
