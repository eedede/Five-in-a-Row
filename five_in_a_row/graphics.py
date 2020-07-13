from tkinter import *
from tkinter import messagebox	
import itertools		
from tkinter import filedialog
	
	
class graphics():		
	def __init__( self, tk_master, cfg_player1, cfg_player2, rows, columns, command_list, menu_list, op_mode, info):
		self.__symbol_p1    = cfg_player1[0]
		self.__fg_color_p1  = cfg_player1[1]
		self.__win_color_p1 = cfg_player1[2]
		self.__symbol_p2    = cfg_player2[0]
		self.__fg_color_p2  = cfg_player2[1]
		self.__win_color_p2 = cfg_player2[2]
		self.__tkmaster = tk_master
		self.__rows = rows
		self.__columns = columns
		self.__command_list = command_list
		self.__menu_list = menu_list
		self.__op_mode = op_mode
		self.__info = info 
	

	def reset( self):
		# delete tk buttons/lables of previous session
		list = self.__tkmaster.grid_slaves()	
		for l in list:
			l.destroy()
			
		# depict top row with letters, starting with "A" from left
		for j in range( self.__columns):
			self.depict_top_row_field( j, chr(65+j))
		# depict right column	
		for i in range( self.__rows):		
			self.depict_right_column_field( i+2, self.__columns+2)
		# depict left column with numbers, starting with 1 from top
		for i in range( self.__rows):	
			self.depict_left_column_field( i, self.__rows-i) #i+1 	
		# depict bottom control bar		
		self.depict_control_row( i, j)	
		# depict game field
		for i, j in itertools.product( range(self.__rows), range(self.__columns)):
			self.clear_field( i, j)

		self.setup_menu_bar()
		self.refresh()
		

################################################
#
# setup Tk Menu Bar
#
################################################	
		
	def setup_menu_bar( self):
		menubar = Menu(self.__tkmaster)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label=self.__menu_list[0][0], command=self.__menu_list[0][1])
		filemenu.add_command(label=self.__menu_list[1][0], command=self.__menu_list[1][1])
		filemenu.add_command(label=self.__menu_list[2][0], command=self.__menu_list[2][1])
		filemenu.add_separator()
		filemenu.add_command(label=self.__menu_list[3][0], command=self.__menu_list[3][1])
		filemenu.add_separator()
		filemenu.add_command(label=self.__menu_list[4][0], command=self.__menu_list[4][1])
		menubar.add_cascade(label="Menu", menu=filemenu)
		self.__tkmaster.config(menu=menubar)			

################################################
#
# Handle dialogue to load game from file system
#
################################################	
		
	def ask_file_name_dialogue( self, root_dir, question, file_type):

		self.__tkmaster.filename = filedialog.askopenfilename(initialdir = root_dir,title = question ,filetypes = file_type)	
		return self.__tkmaster.filename
		
################################################
#
# Handle dialogue to store game to file system
#
################################################		
	
	def ask_file_name_save_dialogue( self, root_dir, question, file_type):
	
		file_handle = filedialog.asksaveasfile(mode="w", initialdir = root_dir,title = question ,filetypes = file_type)	
		return file_handle
		
################################################
#
# Clear game field at position row=i, column=j
#
################################################
	
	def clear_field( self, i, j):
		t, function = self.get_dialogue_attributes("click_field")
		g = Button(self.__tkmaster, text=t, width=4, height=1, borderwidth=1, command=lambda row=i, column=j: function( row, column))
		#g = Label(self.__tkmaster, text=t, width=4, height=1, borderwidth=1)
		#g.bind("<Button-1>", lambda row=i, column=j: function( row, column))
		g.grid(padx=1, pady=1, row=i+2, column=j+2)
	
	def get_dialogue_attributes( self, pattern):
		for item in self.__command_list:
			if item[0] == pattern:
				t = item[1]
				function = item[2]
				break
		return t, function
	
		
	def refresh( self):
		self.__tkmaster.update()		
		
	def get_symbols( self):
		return self.__symbol_p1, self.__symbol_p2 

		
################################################
#
# Update game field at position row=i, column=j
#
################################################	
	
	def depict_field( self, player, i, j):
		if player == 1:
			symbol_color = self.__fg_color_p1
			symbol_sign = self.__symbol_p1
		else:
			symbol_color = self.__fg_color_p2
			symbol_sign = self.__symbol_p2
	
		f = Label(self.__tkmaster, text=symbol_sign, width=2, height=1, borderwidth=1, fg=symbol_color, font="Verdana 10 bold")
		f.grid(padx=1, pady=1, row=i+2, column=j+2)	
		
		
################################################
#
# Depict top row field with symbol <char>
#
################################################
			
	def depict_top_row_field( self, j, char):
		f = Label(self.__tkmaster, text=char, width=4, height=1, borderwidth=1, fg="black")
		f.grid(padx=1, pady=1, row=1, column=j+2)		

################################################
#
# Depict left game field column with <number>
#
################################################	
	
	def depict_left_column_field( self, i, number):
		f = Label(self.__tkmaster, text=number, width=4, height=1, borderwidth=1, fg="black")
		f.grid(padx=1, pady=1, row=i+2, column=1)			

################################################
#
# Depict right game field column 
#
################################################	
		
	def depict_right_column_field( self, i, j):
		f = Label(self.__tkmaster, width=2, height=1)
		f.grid(row=i, column=j)	

################################################
#
# Depict bottom control row in normal and debug 
# mode
#
################################################		

	def on_enter(self, event):
		self.showtip(text)
	def on_leave(self, event):
		self.hidetip()
	
	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
	
		x, y, cx, cy = self.__tkmaster.widget.bbox("insert")
		x = x + self.__tkmaster.widget.winfo_rootx() + 57
		y = y + cy + self.__tkmaster.widget.winfo_rooty() +27
		self.tipwindow = tw = Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()
	
	def depict_control_row(self, i, j):		
		g = Label(self.__tkmaster, text="", width=4,  height=2, borderwidth=1)		
		g.grid(padx=1, pady=1,row = i+4, column = 2)
		t, function = self.get_dialogue_attributes( "remove")
		g = Button(self.__tkmaster, text=t, width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 2)
		t, function = self.get_dialogue_attributes( "restore")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 3)
		t, function = self.get_dialogue_attributes( "new")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)
		g.grid(padx=1, pady=1,row = i+4, column = 5)
		if self.__op_mode == "debug":
			t, function = self.get_dialogue_attributes( "edit")
			g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
			g.grid(padx=1, pady=1,row = i+4, column = 7)
			t, function = self.get_dialogue_attributes( "load_scen")
			g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
			g.grid(padx=1, pady=1,row = i+4, column = 8)
		t, function = self.get_dialogue_attributes( "save")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 10)
		t, function = self.get_dialogue_attributes( "load")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 11)
		t, function = self.get_dialogue_attributes( "step")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		
		
		#g.bind("<Enter>", self.showtip)
		#g.bind("<Leave>", self.on_leave)
		
		
		g.grid(padx=1, pady=1,row = i+4, column = j-1)
		t, function = self.get_dialogue_attributes( "auto")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = j)
		t, function = self.get_dialogue_attributes( "quit")
		g = Button(self.__tkmaster, text=t, width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = j+2)

    
################################################
#
# Clear game field in edit mode
#
################################################	
	
	def reset_game_field( self, i, j, function):	
		list = self.__tkmaster.grid_slaves(row=i+2, column = j+2)
		for l in list:
			l.destroy()	
		g = Button(self.__tkmaster, text="", width=4, height=1, borderwidth=1, command=lambda row=i, column=j: function( row, column))
		g.grid(padx=1, pady=1, row=i+2, column=j+2)	
		
################################################
#
# Clear bottom control row
#
################################################			
		
	def clear_control_row( self, i):	
		list = self.__tkmaster.grid_slaves(row=i+4)
		for l in list:
			l.destroy()

################################################
#
# Depict bottom control row in edit mode
#
################################################	
			
	def depict_control_row_setup_scenario(self, i, j, start_with_p1):	
	
		g = Label(self.__tkmaster, text="", width=4,  height=2, borderwidth=1)		
		g.grid(padx=1, pady=1,row = i+4, column = 2)	
		t, function = self.get_dialogue_attributes( "symbol_p1")
		g = Button(self.__tkmaster, text=t,width=2,  height=1, borderwidth=1, relief=RAISED, fg=self.__fg_color_p1, font="Verdana 10 bold", command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 2)
		t, function = self.get_dialogue_attributes( "symbol_p2")
		g = Button(self.__tkmaster, text=t,width=2,  height=1, borderwidth=1, relief=RAISED, fg=self.__fg_color_p2, font="Verdana 10 bold",  command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 3)
		t, function = self.get_dialogue_attributes( "symbol_cl")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 4)
		
		t, function = self.get_dialogue_attributes( "symbol_st")
		g = Button(self.__tkmaster, text=t,width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = 7)
		if start_with_p1:
			f = Label(self.__tkmaster, text="X", width=2, height=1, borderwidth=1, fg=self.__fg_color_p1, font="Verdana 10 bold")
			f.grid(padx=1, pady=1, row=i+4, column=8)
		else:
			f = Label(self.__tkmaster, text="O", width=2, height=1, borderwidth=1, fg=self.__fg_color_p2, font="Verdana 10 bold")
			f.grid(padx=1, pady=1, row=i+4, column=8)		
		
		t, function = self.get_dialogue_attributes( "done")
		g = Button(self.__tkmaster, text=t, width=4,  height=1, borderwidth=1, relief=RAISED, command=function)		
		g.grid(padx=1, pady=1,row = i+4, column = j+2)
		self.refresh()	


################################################
#
# Hightlight symbols of player who won the game
#
################################################	
		
	def depict_winning_pattern(self, player, pattern_list, reverse_mode):
		if player == 1:
			symbol_color = self.__win_color_p1
			if reverse_mode:
				symbol_color = self.__fg_color_p1
			symbol_sign = self.__symbol_p1
		else:
			symbol_color = self.__win_color_p2
			if reverse_mode:
				symbol_color = self.__fg_color_p2	
			symbol_sign = self.__symbol_p2
			
		for n in pattern_list:
			f = Label(self.__tkmaster, text=symbol_sign, width=2, height=1, borderwidth=1, fg=symbol_color, font="Verdana 10 bold")
			f.grid(padx=1, pady=1, row=n[0]+2, column=n[1]+2)	
		self.refresh()		
	
################################################
#
# Handle end game dialogue
#
################################################
	
	def finish_message( self, text):
		MsgBox = messagebox.showinfo(title="Game over", message=text)
	
	def finish_dialogue( self, text, result):
		MsgBox = messagebox.askquestion (text, "One more round?\n\n"+result,icon = "warning")
		if MsgBox == "no":
			exit()
	  		

################################################
#
# Handle "about" menu item
#
################################################		
	def about_message( self, version):
		MsgBox = messagebox.showinfo(title=self.__info["title"], 
				 message="Version " + self.__info["version"] + "\n\n(C) "+self.__info["copyright"]+ " by " + self.__info["author"])	
