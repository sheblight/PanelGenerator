"""
Comic Panel Splitter

@author: Hibiki Takaku

Provides an interface for the comic panels.

"""

import tkinter
import math
from panelMath import *
from PIL import Image, ImageDraw, ImageColor, ImageTk

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
        self.diagonalenable = tkinter.Checkbutton(self.diag_frame,text='Enable Diagonals (Experimental)',command=self.lw_toggle)
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
        
        positions = [(0,0),(size[0],0),(size[0],size[1]),(0,size[1])]

        features = Features(image,self.image_size,positions,lw,margin,user_input,self.advanced_on)  # Compress features into a class
        
        comic = Comic(features) # calculates all upon initialization
        self.image = self.render_panels(comic)
        #self.image = self.render_panels(features) # Soon to be the function that draws out on image
        print("Calculation complete.");
        # Adds page margin
        p_margin = (int(self.pagemarginw.get()),int(self.pagemarginh.get()))
        self.image = self.rescale(self.image_size,p_margin)
        self.preview_image = self.preview_rescale(self.image_size,self.image)
        self.preview = ImageTk.PhotoImage(self.preview_image)
        self.canvas_refresh()
      
    def draw_box(self,comic):
        '''Draws a box based on given two coordinates. If diagonals aren't empty, draws a quadrilateral based on given angles'''
        draw = ImageDraw.Draw(comic.features.image)    # Shorten module
        for panel in comic.panels:
            if comic.features.advanced:   
                if panel.fill == -1:
                    draw.polygon(panel.pos,fill=self.bg_color,outline=self.bg_color)
                elif panel.fill == 1:
                    draw.polygon(panel.pos,fill='rgba(0,0,0,255)',outline='rgb(0,0,0)')
                    # change line width by drawing over the polygon with line tool
                    draw.line(panel.pos,fill='rgba(0,0,0,255)',width=comic.features.lw)
                    draw.line([panel.pos[0],panel.pos[3]],fill='rgba(0,0,0,255)',width=comic.features.lw)
                else: 
                    draw.polygon(panel.pos,fill=self.bg_color,outline='rgb(0,0,0)')
                    draw.line(panel.pos,fill='rgba(0,0,0,255)',width=comic.features.lw)
                    draw.line([panel.pos[0],panel.pos[3]],fill='rgba(0,0,0,255)',width=comic.features.lw)
                # make the lines thicc
            else:
                if panel.fill == -1: # not filled
                    draw.rectangle([panel.pos[0],panel.pos[2]],fill=self.bg_color,outline=self.bg_color,width=comic.features.lw)
                elif panel.fill == 1:
                    draw.rectangle([panel.pos[0],panel.pos[2]],fill='rgba(0,0,0,255)',outline='rgb(0,0,0)',width=comic.features.lw)
                else: 
                    draw.rectangle([panel.pos[0],panel.pos[2]],fill=self.bg_color,outline='rgb(0,0,0)',width=comic.features.lw)
            print("Box drawn.")
        return comic.features.image
    
    
    def render_panels(self,comic):
        '''Function where all panels coordinates are adjusted by gutter margin and rendered on the image.'''
        print("Console result:",comic.cout)
        self.console_output(comic.cout)
        for panel in comic.panels: # add margin
            panel.add_margin(comic.features.margin[0], comic.features.margin[1])
        image = self.draw_box(comic)
        return image
    
    
# Main code
if __name__ == "__main__":
    # Menu UI
    root = tkinter.Tk()             # Initialize root
    root.title('Comic Template Generator')    # Set program title
    root.geometry('1000x700')        # Set screen resolution
    display = Display(root)         # Init main display
    
    root.mainloop()       # Initializes GUI
    
    print("Process completed")        # Called upon proccess destroyed