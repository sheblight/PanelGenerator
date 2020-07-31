# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 20:15:30 2020

@author: bkand
"""
import math

class Features(object):
    def __init__(self,image,i_size,positions,lw,margin,userinput,advanced):
        self.image = image
        self.image_size = i_size
        self.pos = positions
        self.margin = margin
        self.user_input = userinput
        self.lw = lw
        self.level = 1
        self.visible = True
        self.filled = False
        self.advanced = advanced
        self.alpha = False
        self.cout = "Default Message" # console output message
    
    def copy(self):
        '''Returns a copy of itself... hopefully'''
        feats = Features(self.image,self.image_size,self.pos,self.lw,self.margin,self.user_input,self.advanced)
        feats.level = self.level
        feats.visible = self.visible
        feats.filled = self.filled
        return feats

class Diagonal(object):
    '''Holds data for a diagonals'''
    def __init__(self,angle,clockwise,left):
        self.angle = angle
        self.clockwise = clockwise
        self.is_left = left
    
    def __repr__(self):
        '''Representative'''
        if self.is_left:
            return '/' if self.clockwise else '\\' + str(self.angle)
        else: 
            return str(self.angle) + '/' if self.clockwise else '\\'
    
    def __str__(self):
        '''Prints diagonals as string'''
        if self.is_left:
            return '/' if self.clockwise else '\\' + str(self.angle)
        else: 
            return str(self.angle) + '/' if self.clockwise else '\\'
    
    def get_offset(self,adjacent):
        '''Calculates and returns the offset required to achieve the angle.'''
        if self.angle >= 90:
            print("One of more angles have been capped to 89.")
            return adjacent * math.tan(89*math.pi/180)
        return adjacent * math.tan(self.angle*math.pi/180)
    
class Panel(object):
    '''Holds fill type and position coordinate information'''
    def __init__(self,pos,visible,filled):
        self.pos = pos
        if not visible:
            self.fill = -1
        elif filled:
            self.fill = 1
        else:
            self.fill = 0
    
    def value(self):
        '''Return itself in a list format with first item determining fill type and rest are positions'''
        lst = [self.fill]
        lst.extend(self.pos)
        return lst
    
    def add_margin(self,w,h):
        '''Adds gutter margin'''
        self.pos[0] = (self.pos[0][0]+w,self.pos[0][1]+h)
        self.pos[1] = (self.pos[1][0]-w,self.pos[1][1]+h)
        self.pos[2] = (self.pos[2][0]-w,self.pos[2][1]-h)
        self.pos[3] = (self.pos[3][0]+w,self.pos[3][1]-h)

class Comic(object):
    def __init__(self,features):
        '''Takes Features object. Calculates panels on initialization.'''
        self.features = features
        self.panels, self.cout = self.calculate_panels(self.features)
    
    def __repr__(self):
        return self.panels
    
    def check_syntax(self,feats):
        '''Checks for syntax errors in user input. Returns is error detected bool and error result string'''
        u_in = feats.user_input
        advanced = feats.advanced
        keywords = [',,','/*','\\*','*/','*\\',"/,","\\,"] # ',/',",\\",
        acceptable = ['0','1','2','3','4','5','6','7','8','9','0',',','/','\\','*','(',')','\n',' ','\t','.','!','#']
        for char in u_in:
            if char not in acceptable:
                err = "Error: Invalid char detected: \""+char+"\"\nPlease fix your command prompt and try again."
                return True,err
        if u_in.count('(') != u_in.count(')'):
            err = "Error: Extra key detected: "
            err += "\"(\"" if u_in.count('(')>u_in.count(')') else "\")\""
            err += "\nPlease check your command prompt and try again."
            return True,err
        elif (u_in.find('/')>-1 or u_in.find('\\')>-1) and not advanced: 
            err = "Error: Diagonal syntax detected. Enable Advanced Mode."
            return True,err
        elif (u_in.count('/')+u_in.count('\\') != u_in.count('*')):
            err = "Error: Uneven count of slashes and stars detected.\nPlease check your command prompt and try again."
            return True,err
        for k in keywords:
            if (u_in.find(k)>-1): 
                err = "Error: Detected invalid syntax: \""+ k +"\"\nPlease check your command prompt and try again."
                return True,err
        err = "Process completed."
        return False,err
    
    def filter_input(self,user_input):
        '''Filters unnecessary chars in the user input. Includes space, tab, newspace, and user comments. ~ character is used 
        as a substitute of the newline char'''
        u_in = list(user_input.replace('\n','~'))
        u_in += "~" # in case a comment exists on last line
        count = 0
        c_bool, multic_bool = False,False
        while count != len(u_in)-1:
            print(u_in[count],c_bool)
            if c_bool: # waiting to find end of single line comment
                if u_in[count] == "~": c_bool = False
                else: u_in[count] = " "
            elif multic_bool: # waiting to find end of multiline comment
                if u_in[count] == "*" and u_in[count+1] == "/": 
                    multic_bool = False
                    u_in[count] = " "
                    u_in[count+1] = " "
                else:  u_in[count] = " "
            else:
                if u_in[count] == "/" and u_in[count+1] == "/" and not c_bool:
                    c_bool = True
                    u_in[count] = " "
                    u_in[count+1] = " "
                elif u_in[count] == "/" and u_in[count+1] == "*" and not multic_bool:
                    multic_bool = True
                    u_in[count] = " "
                    u_in[count+1] = " "
                    
            count += 1
        u_in = " ".join(u_in)
        print("after filter,",u_in)
        return u_in.replace('~','').replace(' ','').replace('\t','')
    
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
    
    def reformat_diagonal(self,user_input):
        '''Reformats the diagonal indicators so it is splittable into an array and each panel values have their corresponding diagonals'''
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
    
     
    def get_next_level(self,value):
        '''Returns the values for the next subdivision level'''
        for index in range(len(value)-1,0,-1):
            if value[index]==')': return value[value.find('(')+1:index]
        return value[value.find('(')+1:]    # this is achieved in an error
    
    def calculate_panels(self,feats):
        '''Returns a list of Panel objects and a console message to print'''
        print("At level",feats.level,"received:",feats.user_input)
        panels,diagonals = [],[]  # a list that stores diagonal info
        feats.user_input = self.filter_input(feats.user_input) # filter input
        print("Check syntax:",feats.user_input)
        err_found,cout = self.check_syntax(feats) # checks for user input syntax errors
        if err_found: return panels,cout # return if error is found
        
        # filter and split up user input
        if feats.level == 1: feats.user_input = self.reformat_diagonal(feats.user_input)
        
        input_array = self.divide_input(feats.user_input,feats.level)
        while("" in input_array): input_array.remove("") # remove empty strings
        #print("array after input passed:",input_array)
        # get sum and panel count of this level
        ratio_sum = self.get_ratio_sum(input_array)
        #print("ratio sum:",ratio_sum)
        
        ratio_count = 0
        #print("before loop:",feats.pos)
        
        for panel in input_array: # for each panel
            next_visible,next_filled = feats.visible,feats.filled     # Inherits modes from the previous level
            next_visible,next_filled = self.set_mode(panel,feats.visible,feats.filled)
            ratio = self.get_ratio(panel)
            diagonals.clear()
            diagonals.extend(self.get_diagonals(panel))
            #print("after diagonals add:",diagonals)
            if feats.level % 2 == 0:  # panel ratio horizontal
                lower_x = feats.pos[0][0]+(feats.pos[2][0]-feats.pos[0][0])*ratio_count/ratio_sum    # set positions for second ratio
                upper_x = feats.pos[0][0]+(feats.pos[2][0]-feats.pos[0][0])*(ratio_count+ratio)/ratio_sum
               
                new_y0 = feats.pos[0][1]+(feats.pos[1][1]-feats.pos[0][1])*(ratio_count/ratio_sum)
                new_y1 = feats.pos[0][1]+(feats.pos[1][1]-feats.pos[0][1])*((ratio_count+ratio)/ratio_sum)
                new_y2 = feats.pos[3][1]+(feats.pos[2][1]-feats.pos[3][1])*((ratio_count+ratio)/ratio_sum)
                new_y3 = feats.pos[3][1]+(feats.pos[2][1]-feats.pos[3][1])*(ratio_count/ratio_sum)
                #print(feats.pos)
                positions = [(lower_x,new_y0),(upper_x,new_y1),(upper_x,new_y2),(lower_x,new_y3)] # reassign after calculation
                positions = self.assign_diagonals(positions, diagonals, feats.level%2)
                # check for another level
                if panel.find('(')==-1:
                    print("No recursion found.")
                    # new panel is created and added
                    panels.append(Panel(positions,next_visible,next_filled))
                else:
                    next_feats = feats.copy()  # find another way to copy a class instance if this doesn't work
                    next_feats.user_input = self.get_next_level(panel)
                    next_feats.level += 1
                    next_feats.filled = next_filled
                    next_feats.visible = next_visible
                    next_feats.pos = positions
                    new_panels,cout = self.calculate_panels(next_feats)
                    panels.extend(new_panels)
            else:   # panel ratio vertical
                #print("ratio sum:",ratio_sum," ratio count:",ratio_count,"ratio:",ratio)
                lower_y = feats.pos[0][1]+(feats.pos[2][1]-feats.pos[0][1])*ratio_count/ratio_sum
                upper_y = feats.pos[0][1]+(feats.pos[2][1]-feats.pos[0][1])*(ratio_count+ratio)/ratio_sum
                
                new_x0 = feats.pos[0][0]+(feats.pos[3][0]-feats.pos[0][0])*(ratio_count/ratio_sum )
                new_x1 = feats.pos[1][0]+(feats.pos[2][0]-feats.pos[1][0])*(ratio_count/ratio_sum )
                new_x2 = feats.pos[1][0]+(feats.pos[2][0]-feats.pos[1][0])*((ratio_count+ratio)/ratio_sum)
                new_x3 = feats.pos[0][0]+(feats.pos[3][0]-feats.pos[0][0])*((ratio_count+ratio)/ratio_sum)
                positions = [(new_x0,lower_y),(new_x1,lower_y),(new_x2,upper_y),(new_x3,upper_y)] # reassign after calculation
                positions = self.assign_diagonals(positions, diagonals, feats.level%2)
                # check if there's another level
                if panel.find('(')==-1:
                    print("No recursion found.")
                    panels.append(Panel(positions,next_visible,next_filled))
                else:
                    next_feats = feats.copy()
                    next_feats.user_input = self.get_next_level(panel)
                    next_feats.level += 1
                    next_feats.filled = next_filled
                    next_feats.visible = next_visible
                    next_feats.pos = positions
                    new_panels,cout = self.calculate_panels(next_feats)
                    panels.extend(new_panels)
            ratio_count += ratio
        
        return panels,cout
    
        