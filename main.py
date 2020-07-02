"""
Comic Panel Splitter

@author: Hibiki Takaku
"""

import tkinter
import math
from PIL import Image, ImageDraw, ImageColor, ImageTk

class Features(object):
    def __init__(self,image,positions,lw,margin,userinput,advanced):
        self.image = image
        self.pos = positions
        self.margin = margin
        self.user_input = userinput
        self.lw = lw
        self.level = 1
        self.visible = True
        self.filled = False
        self.advanced = advanced
        self.alpha = False
    
    def copy(self):
        '''Returns a copy of itself... hopefully'''
        feats = Features(self.image,self.pos,self.lw,self.margin,self.user_input,self.advanced)
        feats.level = self.level
        feats.visible = self.visible
        feats.filled = self.filled
        return feats

class Diagonal(object):
    def __init__(self,angle,clockwise,left):
        self.angle = angle
        self.clockwise = clockwise
        self.is_left = left
        
    def get_offset(self,adjacent):
        '''Calculates and returns the offset required to achieve the angle.'''
        if self.angle >= 90:
            print("One of more angles have been capped to 89.")
            return adjacent * math.tan(89*math.pi/180)
        return adjacent * math.tan(self.angle*math.pi/180)
    
class Template(object):
    def __init__(self,line):
        # Current example: Help:2(1,1(2,1))n1(1,2)n|Image.png|500|500|3|10|10|30|30
        text = line.replace("-n","\n").split("|")
        self.info = text[0].split(":")
        for index in range(1,len(text)):
            self.info.append(text[index])
        print(self.info)
        
    def name(self):
        return self.info[0] 
    
    def info(self):
        return self.info

class Display(object):
    '''Displays the base menu'''
    def __init__(self, parent):
        # Configures all widget components
        self.frame = tkinter.Frame(parent,borderwidth=2,relief=tkinter.GROOVE,width=1000,height=700)
        self.header = tkinter.Label(self.frame,text='Comic Panel Template Maker version 1.1.0')
        self.author = tkinter.Label(self.frame,text='by Hibiki Takaku')
        self.lw_frame = tkinter.Frame(self.frame,borderwidth=0,relief=tkinter.GROOVE)
        self.linewidth_text = tkinter.Label(self.lw_frame,text='Line Width:')
        self.linewidth = tkinter.Entry(self.lw_frame,width=5)
        self.linewidth.insert(tkinter.END,'3')      # Default line width value
        self.marginw_text = tkinter.Label(self.lw_frame,text='Gutter Width: ')
        self.marginw = tkinter.Entry(self.lw_frame,width=5)
        self.marginw.insert(tkinter.END,'10')       # Default margin width
        self.marginh_text = tkinter.Label(self.lw_frame,text='Gutter Height: ')
        self.marginh = tkinter.Entry(self.lw_frame,width=5)
        self.marginh.insert(tkinter.END,'10')       # Default margin height
        # Page margin settings
        self.pagemargin_frame = tkinter.Label(self.frame)
        self.pagemarginw_text = tkinter.Label(self.pagemargin_frame,text='Page Margin Width: ')
        self.pagemarginw = tkinter.Entry(self.pagemargin_frame,width=5)
        self.pagemarginw.insert(tkinter.END,'30')       # Default page margin width
        self.pagemarginh_text = tkinter.Label(self.pagemargin_frame,text='Page Margin Height: ')
        self.pagemarginh = tkinter.Entry(self.pagemargin_frame,width=5)
        self.pagemarginh.insert(tkinter.END,'30')       # Default page margin height

        # Command window settings
        self.command_header = tkinter.Label(self.frame,text='Command Window')
        self.text = "2(1,1(2,1)),\n1(1,2)"
        self.input = tkinter.Text(self.frame,height=10,width=50)
        self.input.insert(tkinter.END,self.text);
        self.preview_frame = tkinter.Frame(self.frame,width=550,height=550)
        self.preview_label = tkinter.Label(self.preview_frame,text='Preview Image',justify=tkinter.RIGHT)
        self.canvas = tkinter.Canvas(self.preview_frame,height=500,width=500)
        self.option_frame = tkinter.Frame(self.frame,borderwidth=0,relief=tkinter.GROOVE)
        self.preview_option = tkinter.Button(self.option_frame,text='Preview',command=self.read_input)
        self.export_option = tkinter.Button(self.option_frame,text='Export',command=self.export_image)
        self.save_option = tkinter.Button(self.option_frame,text='Save Template',command=self.create_temp)
        
        # Save settings
        self.saves = []
        self.templates = []
        self.load_template_list()
        print(self.saves)
        self.savename = tkinter.StringVar()
        self.savename.set(self.saves[0])
        self.savename.trace('w',self.reload_temp)
        self.savelist = tkinter.OptionMenu(self.option_frame,self.savename,*self.saves)
        
        # Resolution settings
        self.resframe = tkinter.Frame(self.frame)
        self.reslabel = tkinter.Label(self.resframe,text='Resolution Settings:')
        self.resw = tkinter.Entry(self.resframe,width=5)
        self.resw.insert(tkinter.END,'500')
        self.resx = tkinter.Label(self.resframe,text='x')
        self.resh = tkinter.Entry(self.resframe,width=5)
        self.resh.insert(tkinter.END,'500')
        
        # Enabled diagonal settings
        self.diag_frame = tkinter.Frame(self.frame)
        self.diagonalenable = tkinter.Checkbutton(self.diag_frame,text='Enable Diagonals',command=self.lw_toggle)
        self.alpha_enable = tkinter.Checkbutton(self.diag_frame,text='Alpha Background',command=self.alpha_bg_toggle)
        
        # Export file name
        self.filename_frame = tkinter.Frame(self.frame)
        self.filenametext = tkinter.Label(self.filename_frame,text='Export file name: ')
        self.filename = tkinter.Entry(self.filename_frame,width=30)
        self.filename.insert(tkinter.END,'Image.png')
        
        self.consoletext = tkinter.Label(self.frame,text='Console')
        
        # Display and pack components in order
        self.frame.pack(pady=20)
        self.header.pack()
        self.author.pack()
        self.preview_frame.pack(side=tkinter.RIGHT)
        self.preview_label.pack()
        self.canvas.pack(padx=5)
        self.command_header.pack()
        self.input.pack(padx=10,pady=5)
        self.preview_frame.pack_propagate(0)
        
        self.option_frame.pack(pady=10)
        self.preview_option.pack(side=tkinter.LEFT,padx=10)
        self.export_option.pack(side=tkinter.LEFT,padx=10)
        self.save_option.pack(side=tkinter.LEFT,padx=10)
        self.savelist.pack(side=tkinter.LEFT)
        
        self.filename_frame.pack()
        self.filenametext.pack(side=tkinter.LEFT)
        self.filename.pack(side=tkinter.LEFT)
        
        self.resframe.pack(pady=5)
        self.reslabel.pack(side=tkinter.LEFT,padx=10)
        self.resw.pack(side=tkinter.LEFT)
        self.resx.pack(side=tkinter.LEFT)
        self.resh.pack(side=tkinter.LEFT)
        
        self.lw_frame.pack(pady=10)
        self.marginh.pack(side=tkinter.RIGHT)
        self.marginh_text.pack(side=tkinter.RIGHT)
        self.marginw.pack(side=tkinter.RIGHT)
        self.marginw_text.pack(side=tkinter.RIGHT)
        self.linewidth.pack(side=tkinter.RIGHT,padx=5)
        self.linewidth_text.pack()
        
        self.pagemargin_frame.pack()
        self.pagemarginw_text.pack(side=tkinter.LEFT)
        self.pagemarginw.pack(side=tkinter.LEFT)
        self.pagemarginh_text.pack(side=tkinter.LEFT)
        self.pagemarginh.pack(side=tkinter.LEFT)
        
        self.diag_frame.pack()
        self.diagonalenable.pack(pady=10)
        self.alpha_enable.pack()
        
        self.consoletext.pack(pady=10)
        
        self.image_size = int(self.resw.get()),int(self.resh.get())
        self.advanced_on = False
        self.bg_color = 'rgba(255,255,255,255)'
        
        # Open image on canvas
        # The line below needs to be commented out once if pyimage doesn't exist error pops out
        #'''
        
        self.image = Image.new('RGBA',self.image_size,self.bg_color)
        self.preview_image = self.image.copy()
        self.preview = ImageTk.PhotoImage(self.image) # Image object required to be in PhotoImage object for preview
        self.canvas.create_image(0,0,anchor=tkinter.NW, image=self.preview)
        #'''
    
    def reload_temp(self,*args):
        '''Calls this function whenever a template is selected'''
        for temp in self.templates:
            if self.savename.get() == temp.name():
                self.input.delete(1.0,tkinter.END)
                self.input.insert(tkinter.END,temp.info[1])
                self.filename.delete(0,tkinter.END)
                self.filename.insert(tkinter.END,temp.info[2])
                self.resw.delete(0,tkinter.END)
                self.resw.insert(tkinter.END,temp.info[3])
                self.resh.delete(0,tkinter.END)
                self.resh.insert(tkinter.END,temp.info[4])
                self.linewidth.delete(0,tkinter.END)
                self.linewidth.insert(tkinter.END,temp.info[5])
                self.marginw.delete(0,tkinter.END)
                self.marginw.insert(tkinter.END,temp.info[6])
                self.marginh.delete(0,tkinter.END)
                self.marginh.insert(tkinter.END,temp.info[7])
                self.pagemarginw.delete(0,tkinter.END)
                self.pagemarginw.insert(tkinter.END,temp.info[8])
                self.pagemarginh.delete(0,tkinter.END)
                self.pagemarginh.insert(tkinter.END,temp.info[9])
        self.console_output("Loaded template: "+self.savename.get())
    
    def create_temp(self):
        '''Creates a window for registering a new template'''
        self.namewindow = tkinter.Toplevel()
        self.namewindow.geometry('300x150')
        self.newname_text = tkinter.Label(self.namewindow,text='Enter a name for the template')
        self.newname_field = tkinter.Entry(self.namewindow,width=30)
        self.newname_options = tkinter.Frame(self.namewindow)
        self.newname_save = tkinter.Button(self.newname_options,text='Save',width=10,command=self.save_template)
        self.newname_cancel = tkinter.Button(self.newname_options,text='Cancel',width=10,command=self.exit_window)
        
        self.newname_text.pack(pady=10)
        self.newname_field.pack(pady=5)
        self.newname_options.pack(pady=10)
        self.newname_save.pack(side=tkinter.LEFT,padx=2)
        self.newname_cancel.pack(side=tkinter.LEFT,padx=2)
        
    def exit_window(self):
        '''Exits window.'''
        self.namewindow.destroy()
    
    def close_popup(self):
        '''Closes popup window'''
        self.errwin.destroy()
    
    def popup(self,string):
        '''Displays a pop-up window of the string.'''
        self.errwin = tkinter.Toplevel()
        self.errwin.geometry('250x120')
        self.err_text = tkinter.Label(self.errwin,text=string)
        self.err_confirm = tkinter.Button(self.errwin,text='OK',width=10,command=self.close_popup)
        # packs components
        self.err_text.pack(pady=10)
        self.err_confirm.pack(side=tkinter.BOTTOM,pady=10)
    
    def lw_toggle(self):
        '''Toggles linewidth on or off when checking enable diagonals'''
        self.advanced_on = True if not self.advanced_on else False
        
        if self.advanced_on: self.linewidth.config(state='disabled')
        else: self.linewidth.config(state='normal')
    
    def alpha_bg_toggle(self):
        '''Toggles transparent bg on/off'''
        self.bg_color = 'rgba(255,255,255,255)' if not self.alpha_enable else 'rgba(255,255,255,0)'
        
        
    def save_template(self):
        '''Writes template information to file and exits window. 
        Update load_template function whenever this is modified.
        '''
        try:
            file = open('template.txt','r')
            file.close()
        except:
            print("Creating new file.")
            file = open('template.txt','a')
            file.write("# This file is used for storing templates.\n")
            file.write('# Manually modifying this file may lead to errors.\n')
            file.close()
        if self.newname_field.get() == "":
            self.popup("Please enter a name.")
            return
        elif self.newname_field.get() in self.saves:
            self.popup("Name already exists.\nPlease enter a different name.")
            return
        # Record template information on a file
        file = open('template.txt','a')
        new_temp = self.newname_field.get()+":"
        new_temp += self.input.get(1.0,tkinter.END).replace('\n','-n')+"|"
        new_temp += self.filename.get()+"|"
        new_temp += self.resw.get()+"|"+self.resh.get()+"|"
        new_temp += self.linewidth.get()+"|"
        new_temp += self.marginw.get()+"|"+self.marginh.get()+"|"
        new_temp += self.pagemarginw.get()+"|"+self.pagemarginh.get()+"\n"
        file.write(new_temp)
        file.close()
        # Add template to dropdown list
        self.templates.append(Template(new_temp.strip('\n')))
        self.saves.append(self.templates[-1].name())
        # Refresh dropdown menu
        self.savelist.destroy()
        self.savelist = tkinter.OptionMenu(self.option_frame,self.savename,*self.saves)
        self.savelist.pack(side=tkinter.LEFT)
        print(self.saves)
        self.savename.set(self.saves[-1])
        self.namewindow.destroy()
        self.console_output(self.savename.get()+" is saved!")
    
    def load_template_list(self):
        '''Load a list of templates in the dropdown'''
        try: 
            file = open('template.txt','r')
        except:
            self.saves.append("None")
        else:    
            for line in file:
                print(line)
                if line[0]=='#':
                    continue
                else: 
                    self.templates.append(Template(line.strip('\n')))
                    self.saves.append(line.split(":")[0])
            
    def canvas_refresh(self):
        '''Refreshes the preview of the exported image'''
        self.canvas.delete("all")
        self.canvas.create_image(0,0,anchor=tkinter.NW, image=self.preview)
        
    def preview_rescale(self,size,preview):
        '''Scales the preview so the max width or height is 500.'''
        image = preview.copy()
        if size[0]>size[1]:
            self.canvas.config(height=500*size[1]/size[0],width=500)
            image = image.resize((500,int(500*size[1]/size[0])))
        elif size[0]<size[1]: 
            self.canvas.config(width=500*size[0]/size[1],height=500)
            image = image.resize((int(500*size[0]/size[1]),500))
        else: # same width and height
            self.canvas.config(width=500,height=500)
            image = image.resize((500,500))
        return image
        
    def rescale(self,size,margin):
        '''Adds a page margin by scaling down the entire image and pasting the image into the original resolution'''
        image = self.image.copy()
        image = image.resize((size[0]-margin[0],size[1]-margin[1]))
        im2 = Image.new('RGBA',size,self.bg_color)
        im2.paste(image,(int(margin[0]/2),int(margin[1]/2)))
        return im2
    
    def console_output(self,t_out):
        '''Outputs a console message to the user'''
        self.consoletext.config(text=t_out)
        
    def get_window(self):
        '''Returns main window, used for parenting.'''
        return self.frame
    
    def export_image(self):
        '''Exports image'''
        self.image.save(self.filename.get())
        self.console_output("Export complete.")
    
    def read_input(self):
        '''Reads information from player's text input and renders image.'''
        user_input = self.input.get(1.0,tkinter.END)
        print("Processing...");
        # Get line width and panel margin
        margin = (int(self.marginw.get()),int(self.marginh.get()))
        lw = int(self.linewidth.get())
        self.image_size = int(self.resw.get()),int(self.resh.get())
        # Renders the preview image
        image = Image.new('RGBA',self.image_size,self.bg_color)   # Creates new image
        size = (self.image_size[0]-margin[0],self.image_size[1]-margin[1])  # initial second position
        
        positions = [(margin[0],margin[1]),(size[0],margin[1]),(size[0],size[1]),(margin[0],size[1]) ]

        features = Features(image,positions,lw,margin,user_input,self.advanced_on)  # Compress features into a class
        self.image = self.render_panels(features)
        # Adds page margin
        p_margin = (int(self.pagemarginw.get()),int(self.pagemarginh.get()))
        self.image = self.rescale(self.image_size,p_margin)
        self.preview_image = self.preview_rescale(self.image_size,self.image)
        self.preview = ImageTk.PhotoImage(self.preview_image)
        self.canvas_refresh()
        self.console_output("Preview complete.")
        
       
    def reformat_diagonal(self,user_input):
        '''Reformats the diagonal indicators so it is splittable into an array'''
        new_string = ""
        ptr = counter = head = 0
        for string in user_input:
            if string == '/' or string == "\\":
                head = ptr
                counter = 1
            elif string == '*':
                new_string += user_input[head:ptr+1]+','+user_input[head:ptr]
                counter = 0
            ptr += 1
            if counter == 0: new_string += string
        return new_string
        
    def filter_input(self,user_input):
        '''Filters unnecessary chars in the user input. Includes space, tab, newspace.
        Also reformats diagonal indicators.'''
        return user_input.replace(' ','').replace('\t','').replace('\n','')
        
    def divide_input(self,user_input,level):
        '''Splits commas outside of parenthesis and returns an array of the divided input'''
        print("at level",level,"received:",user_input)
        array = []
        ptr = counter = head = 0
        diagonal = ''
        if user_input.find('(')==-1: # no recursion
            return user_input.split(',')
        while ptr < len(user_input):
            if user_input[ptr]==',' and counter == 0:
                array.append(user_input[head:ptr])
                head = ptr+1
            if user_input[ptr]=='(':
                counter += 1
                print(counter)
            if user_input[ptr]==')':
                counter -= 1
                print(counter)
            ptr += 1
        array.append(user_input[head:ptr])  # include last value
        return array
        
    def filter_diagonal(self,value):
        '''Filters out diagonal indicators from a value and returns it'''
        if value[0]=='/' or value[0]=='\\': value = value[value.find('*')+1:]
        if value[-1]=='*': # if * is last char
            if value.find('/')!=-1: value = value[:value.find('/')] # if this panel has diagonal side
            elif value.find('\\')!=-1: value = value[:value.find('\\')]
        return value
    
    def get_ratio_sum(self,array):
        '''Filters out diagonal sides, parenthesis and returns sum of ratio'''
        # WIP string isn't reading * for some reason when doing '\\'
        total = 0
        for value in array:
            print("sum: ",value)
            print(value[-1])
            value = value.replace('!','').replace('#','')   # filter out panel modes
            value = self.filter_diagonal(value)
            if value.find('(')==-1:
                total += float(value)
            else: 
                total += float(value[:value.find('(')])
        return total
    
    def get_ratio(self,value):
        '''Filters out diagonal sides, parenthesis and returns ratio of the value'''
        value = self.filter_diagonal(value)
        value = value.replace('!','').replace('#','')   # filter out panel modes 
        return float(value) if value.find('(')==-1 else float(value[:value.find('(')])
    
    def set_mode(self,panel,visible,filled):
        '''Filters diagonal indicators, gets and sets modes for the panel'''
        panel = self.filter_diagonal(panel)
        if panel[0]=='!':   visible = False   # if panel is invisible
        if panel[0]=='#':   filled = True   # if panel is filled
        return visible,filled
    
    def get_diagonals(self,value):
        '''Identifies and sets any diagonal sides of the panel. Returns an array of Diagonal classes'''
        d_left,d_right = Diagonal(45,True,True),Diagonal(45,True,True)
        d_list = []
        print("get_diagonals:",value)
        if value[0]=='/': # check lefthand side
            d_left.clockwise = True
            d_left.is_left = True
            d_left.angle = float(value[1:value.find('*')])
            value = value[value.find('*')+1:]   # trim the value
            d_list.append(d_left)
        elif value[0]=='\\':
            d_left.clockwise = False
            d_left.is_left = True
            d_left.angle = float(value[1:value.find('*')])
            value = value[value.find('*')+1:]
            d_list.append(d_left)
        if value[-1]=='*': # if * is last char
            if value.find(')')!=-1: value = value[value.rfind(')'):]
            if value.find('/')!=-1: 
                d_right.clockwise = True
                d_right.is_left = False
                d_right.angle = float(value[value.find('/')+1:value.find('*')]) 
                d_list.append(d_right)
            elif value.find('\\')!=-1:
                d_right.clockwise = False
                d_right.is_left = False
                d_right.angle = float(value[value.find('\\')+1:value.find('*')]) 
                d_list.append(d_right)
        print("d_list:",d_list)
        return d_list
    
    def assign_diagonals(self,pos,diagonals,level):
        '''Returns a 4 position list which calculates the diagonal sides based on previous positions and then the new changes'''
        print("Diagonals check:",diagonals)
        positions = pos.copy()
        if diagonals != None:
            for d in diagonals:
                if level == 0:
                    print("horizontal diagonal")
                    if d.is_left:
                        offset = d.get_offset(positions[3][1]-positions[0][1])
                        if d.clockwise:
                            positions[0] = (positions[0][0]+int(offset/2),positions[0][1])
                            positions[3] = (positions[3][0]-int(offset/2),positions[3][1])
                        else:
                            positions[0] = (positions[0][0]-int(offset/2),positions[0][1])
                            positions[3] = (positions[3][0]+int(offset/2),positions[3][1])
                    else:
                        offset = d.get_offset(positions[2][1]-positions[1][1])
                        if d.clockwise:
                            positions[1] = (positions[1][0]+int(offset/2),positions[1][1])
                            positions[2] = (positions[2][0]-int(offset/2),positions[2][1])
                        else:
                            positions[1] = (positions[1][0]-int(offset/2),positions[1][1])
                            positions[2] = (positions[2][0]+int(offset/2),positions[2][1])     
                else: # vertical diagonal
                    print("vertical diagonal")
                    if d.is_left:
                        offset = d.get_offset(positions[1][0]-positions[0][0])
                        if d.clockwise:
                            positions[1] = (positions[1][0],positions[1][1]+int(offset/2))
                            positions[0] = (positions[0][0],positions[0][1]-int(offset/2))
                        else:
                            positions[1] = (positions[1][0],positions[1][1]-int(offset/2))
                            positions[0] = (positions[0][0],positions[0][1]+int(offset/2))
                    else:
                        offset = d.get_offset(positions[2][0]-positions[3][0])
                        if d.clockwise:
                            positions[2] = (positions[2][0],positions[2][1]+int(offset/2))
                            positions[3] = (positions[3][0],positions[3][1]-int(offset/2))
                        else:
                            positions[2] = (positions[2][0],positions[2][1]-int(offset/2))
                            positions[3] = (positions[3][0],positions[3][1]+int(offset/2))
        return positions
    
    def draw_box(self,image,pos,lw,visible,filled,level,advanced):
        '''Draws a box based on given two coordinates. If diagonals aren't empty, draws a quadrilateral based on given angles'''
        print("pos in draw box:",pos)
        draw = ImageDraw.Draw(image)    # Shorten module
        if advanced:   
            if visible == False:
                draw.polygon(pos,fill=self.bg_color,outline=self.bg_color)
            elif filled == True:
                draw.polygon(pos,fill='rgba(0,0,0,255)',outline='rgb(0,0,0)')
                print("line width is:",lw)
                draw.line(pos,fill='rgba(0,0,0,255)',width=lw)
                draw.line([pos[0],pos[3]],fill='rgba(0,0,0,255)',width=lw)
            else: 
                draw.polygon(pos,fill=self.bg_color,outline='rgb(0,0,0)')
                draw.line(pos,fill='rgba(0,0,0,255)',width=lw)
                draw.line([pos[0],pos[3]],fill='rgba(0,0,0,255)',width=lw)
            # make the lines thicc
        else:
            if visible == False:
                draw.rectangle([pos[0],pos[2]],fill=self.bg_color,outline=self.bg_color,width=lw)
            elif filled == True:
                draw.rectangle([pos[0],pos[2]],fill='rgba(255,255,255,255)',outline='rgb(0,0,0)',width=lw)
            else: 
                draw.rectangle([pos[0],pos[2]],fill=self.bg_color,outline='rgb(0,0,0)',width=lw)
        print("Box drawn.")
    
     
    def get_next_level(self,value):
        '''Returns the values for the next subdivision level'''
        for index in range(len(value)-1,0,-1):
            if value[index]==')': return value[value.find('(')+1:index]
        return value[value.find('(')+1:]    # this is achieved in an error
    
    def render_panels(self, feats):
        '''Renders the panels recursively. Takes a list of 2 tuples'''
        print("Entering level",feats.level)
        print("Positions given:",feats.pos)
        diagonals = []  # a list that stores diagonal info
        
        # Return error if diagonal syntax detected
        if (feats.user_input.find('/')!=-1 or feats.user_input.find('\\')!=-1) and not feats.advanced:
            self.console_output('Error: Diagonal syntax detected.')
            return feats.image
                                                      
        # filter and split up user input
        if feats.level == 1: feats.user_input = self.reformat_diagonal(feats.user_input)
        feats.user_input = self.filter_input(feats.user_input)
        input_array = self.divide_input(feats.user_input,feats.level)
        while("" in input_array): input_array.remove("") # remove empty strings
        print("array after input passed:",input_array)
        # get sum and panel count of this level
        ratio_sum = self.get_ratio_sum(input_array)
        print("ratio sum:",ratio_sum)
        
        ratio_count = 0
        print("before loop:",feats.pos)
        for panel in input_array:
            next_visible,next_filled = feats.visible,feats.filled     # Inherits modes from the previous level
            next_visible,next_filled = self.set_mode(panel,feats.visible,feats.filled)
            ratio = self.get_ratio(panel)
            diagonals.clear()
            diagonals.extend(self.get_diagonals(panel))
            print("after diagonals add:",diagonals)
            if feats.level % 2 == 0:  # panel ratio horizontal
                lower_x = feats.pos[0][0]+(feats.pos[2][0]-feats.pos[0][0]+2*feats.margin[0])*ratio_count/ratio_sum    # set positions for second ratio
                upper_x = feats.pos[0][0]+(feats.pos[2][0]-feats.pos[0][0]+2*feats.margin[0])*(ratio_count+ratio)/ratio_sum-2*feats.margin[0]
                d_margin = 2*feats.margin[0]/(self.image_size[0]-2*feats.margin[0])
                new_y0 = feats.pos[0][1]+(feats.pos[1][1]-feats.pos[0][1])*(ratio_count/ratio_sum)
                new_y1 = feats.pos[0][1]+(feats.pos[1][1]-feats.pos[0][1])*((ratio_count+ratio)/ratio_sum)
                new_y2 = feats.pos[3][1]+(feats.pos[2][1]-feats.pos[3][1])*((ratio_count+ratio)/ratio_sum)
                new_y3 = feats.pos[3][1]+(feats.pos[2][1]-feats.pos[3][1])*(ratio_count/ratio_sum)
                print(feats.pos)
                positions = [(lower_x,new_y0),(upper_x,new_y1),(upper_x,new_y2),(lower_x,new_y3)] # reassign after calculation
                positions = self.assign_diagonals(positions, diagonals, feats.level%2)
                # lerp
                # check for another level
                if panel.find('(')==-1:
                    print("No recursion found.") 
                    self.draw_box(feats.image,positions,feats.lw,next_visible,next_filled,feats.level%2,feats.advanced)
                else:
                    next_feats = feats.copy()  # find another way to copy a class instance if this doesn't work
                    next_feats.user_input = self.get_next_level(panel)
                    next_feats.level += 1
                    next_feats.filled = next_filled
                    next_feats.visible = next_visible
                    next_feats.pos = positions
                    feats.image = self.render_panels(next_feats)
            else:   # panel ratio vertical
                print("ratio sum:",ratio_sum," ratio count:",ratio_count,"ratio:",ratio)
                lower_y = feats.pos[0][1]+(feats.pos[2][1]-feats.pos[0][1]+2*feats.margin[1])*ratio_count/ratio_sum
                upper_y = feats.pos[0][1]+(feats.pos[2][1]-feats.pos[0][1]+2*feats.margin[1])*(ratio_count+ratio)/ratio_sum-2*feats.margin[1]
                d_margin = 2*feats.margin[1]/(self.image_size[1]-feats.margin[1])
                new_x0 = feats.pos[0][0]+(feats.pos[3][0]-feats.pos[0][0])*(ratio_count/ratio_sum )
                new_x1 = feats.pos[1][0]+(feats.pos[2][0]-feats.pos[1][0])*(ratio_count/ratio_sum )
                new_x2 = feats.pos[1][0]+(feats.pos[2][0]-feats.pos[1][0])*((ratio_count+ratio)/ratio_sum)
                new_x3 = feats.pos[0][0]+(feats.pos[3][0]-feats.pos[0][0])*((ratio_count+ratio)/ratio_sum)
                positions = [(new_x0,lower_y),(new_x1,lower_y),(new_x2,upper_y),(new_x3,upper_y)] # reassign after calculation
                positions = self.assign_diagonals(positions, diagonals, feats.level%2)
                # check if there's another level
                if panel.find('(')==-1:
                    print("No recursion found.")
                    self.draw_box(feats.image,positions,feats.lw,next_visible,next_filled,feats.level%2,feats.advanced)
                else:
                    next_feats = feats.copy()
                    next_feats.user_input = self.get_next_level(panel)
                    next_feats.level += 1
                    next_feats.filled = next_filled
                    next_feats.visible = next_visible
                    next_feats.pos = positions
                    feats.image = self.render_panels(next_feats)
            ratio_count += ratio
            
        return feats.image

    
# Main code
if __name__ == "__main__":
    # Menu UI
    root = tkinter.Tk()             # Initialize root
    root.title('Comic Template Generator')    # Set program title
    root.geometry('1000x700')        # Set screen resolution
    display = Display(root)         # Init main display
    
    root.mainloop()       # Initializes GUI
    
    print("Process completed")        # Called upon proccess destroyed