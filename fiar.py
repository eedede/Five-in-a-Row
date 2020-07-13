from tkinter import *
import logging
import traceback
from inspect import currentframe, getframeinfo
import re
import os 

from five_in_a_row import fields, game_play, graphics

__author__    = "Eckhard Delfs"
__copyright__ = "2020"
__credits__   = ["{credit_list}"]
__license__   = "MIT"
__title__     = "Five In A Row"
__version__   = "0.1"
__status__    = "{dev_status}"


################################################
#
# Game play symbols and colors - edit here
#
################################################	

__symbol_p1__ = "X"              # symbol used for player 1
__symbol_p2__ = "O"              # symbol used for player 2
__color_p1_default__ = "black"   # default color of player 1
__color_p2_default__ = "blue"    # default color of player 2
__color_p1_win__ = "green"       # win sequence color of player 1
__color_p2_win__ = "red"         # win sequenec color of player 2


class game_control():

	def __init__(self, tk_main_frame, op_mode, rows, columns):
		self.tk_main = tk_main_frame
		self.command_list = [["click_field", " "   , self.field_click_event_handler],
							 ["remove",    "\u2bc7", self.remove_last_move],  # left arrow symbol
							 ["restore",   "\u2bc8", self.restore_last_move], # right arrow symbol
							 ["edit",      "Edit"  , self.setup_scenario],
							 ["symbol_st", "Start" , self.toggle_first_player_edit_mode],
							 ["new",       "New"   , self.reset],
							 ["load_scen", "Scen"  , self.load_scenario],
							 ["save",      "Save"  , self.save_game_to_file],
							 ["load",      "Load"  , self.load_game_from_file],
							 ["step",      "Step"  , self.run_single_step],
							 ["auto",      "Auto"  , self.run_auto_mode],
							 ["quit",      "Quit"  , self.game_exit],
							 ["done",      "Done"  , self.leave_setup_scenario],
							 ["symbol_p1", __symbol_p1__ , self.set_symbol_p1],
							 ["symbol_p2", __symbol_p2__ , self.set_symbol_p2],
							 ["symbol_cl", "Clear" , self.clear_symbol]]

							 
		self.menu_list = [["Load Game", self.load_game_dialogue],
						  ["Save Game", self.save_game_dialogue],
						  ["Options", self.set_game_options],
						  ["About", self.set_about_info],
						  ["Exit", self.game_exit]]		
		self.info = {"author": __author__, "copyright": __copyright__, "version": __version__, "title":__title__}					 
		self.move_list = []
		self.__total_moves_copy = rows*columns
		self.total_moves_left = rows*columns
		self.total_moves = 0
		self.finished = False
		self.play = game_play.play( rows, columns, "X", "O")
		self.stat = game_stat()
		self.last_moves = []        # move history buffer
		self.graphics = graphics.graphics( tk_main_frame, 
			(__symbol_p1__, __color_p1_default__,__color_p1_win__),
			(__symbol_p2__,__color_p2_default__,__color_p2_win__), 
			rows, columns, self.command_list, self.menu_list, op_mode, self.info)
		self.edit_mode = False
		self.edit_player = 1
		self.op_mode = op_mode      
		self.print_console = False  # controls debug info output on command shell (only from this class)
		self.win_list = []          # contains winning fields 
		self.winner =  0            # player who won last game (1,2)
		self.busy = False
		self.scenario_number = 0  # used to select predefined scenario 
		self.first_reset = True
		self.file_name = "match.txt"
		self.version_string = __version__
		self.first_player_edit_mode = 1
		
		
	def reset( self):
		if self.first_reset or self.total_moves != 0: 
			self.busy = True # set busy flag set since play.reset() takes some time to clean Tk gadget list
			self.play.reset()
			if self.op_mode != "auto":
				self.graphics.reset()	
			self.busy = False
			self.move_list = []
			self.total_moves_left = self.play.field.get_number_of_columns()*self.play.field.get_number_of_columns()
			self.total_moves = 0
			self.finished = False
			self.last_moves = []
			self.win_list = []
			self.winner = 0
			self.edit_mode = False
			self.first_reset = False		
			self.first_player_edit_mode = 1 # controls which player starts when edit mode is left
	
	
################################################
#
# Handle "Load Game" menu dialogue
#
# Default file name, otherwise last selected name
# in file menus
#
################################################	
	
	def load_game_dialogue( self):
		root_path = os.path.dirname(os.path.realpath(__file__))
		title = "Select game file to load"
		file_types = (("game files","*.txt"),("all files","*.*"))
		file_name = self.graphics.ask_file_name_dialogue( root_path, title, file_types)
		if len(file_name) == 0:
			return
		self.file_name = file_name
		self.load_game_from_file()
		return

################################################
#
# Handle "Save Game" menu dialogue
#
# Default file name, otherwise last selected name
# in file menu
#
################################################	
		
	def save_game_dialogue( self):
		root_path = os.path.dirname(os.path.realpath(__file__))
		title = "Select game file to save"
		file_types = (("game files","*.txt"),("all files","*.*"))
		file_handle = self.graphics.ask_file_name_save_dialogue( root_path, title, file_types)
		if file_handle == None:
			return
		else:
			self.save_game_to_file_pre_opened( file_handle)
		return	

################################################
#
# Handle "Options" menu dialogue
#
################################################	
		
	def set_game_options( self):
		# not implemented yet
		return		
	
################################################
#
# Handle "About" menu dialogue
#
################################################	

	def set_about_info( self):
		self.graphics.about_message( self.version_string)
		return		
		
	def set_symbol_p1( self):
		self.edit_player = 1 # player 1 uses default "X"
		return
		
	def set_symbol_p2( self):
		self.edit_player = 2 # player 2 uses default "O"
		return
	
	def clear_symbol( self):
		self.edit_player = 0 # used to clear field in edit mode
		return
			
	def game_exit( self):
		self.tk_main.destroy()
		
	def	save_game_to_file_pre_opened( self, file):
		list = self.convert_move_list_from_internal_to_standard()
		for item in list:
			file.write(str(item[0])+", "+ str(item[1])+"\n")
		file.close()        
		return
	
################################################
#
# Save game to file (quick button in command row)
#
################################################

	def	save_game_to_file( self):
		with open(self.file_name, "w") as file:
			list = self.convert_move_list_from_internal_to_standard()
			for item in list:
				file.write(str(item[0])+", "+ str(item[1])+"\n")
		file.close()        
		return
	

################################################
#
# Load game from file (quick button in command row)
#
################################################

	def	load_game_from_file( self):
		if self.total_moves != 0:
			self.reset()
		list = []	
		index = 1
		try:
			with open(self.file_name, "r") as file:
				print("reading", self.file_name)
				file_content = file.readlines()
				for item in file_content:
					if "," in item:
						list.append([index, item[item.find(","):]])
						index += 1
			file.close() 
		except:
			print("Error when trying to read", file_name)
			print(sys.exc_info()[0])		
		list = self.convert_move_list_from_standard_to_internal( list, self.play.field.get_number_of_rows(), self.play.field.get_number_of_columns()) 
		for item in range(len(list)):
			player = 1+item%2
			i,j = list[item][0], list[item][1]
			self.play.field.set(player, i, j)	
			self.win_list = self.play.field.check_if_won( player, i, j, False)
			if len( self.win_list) != 0:
				self.winner = player
				self.finished = True
				break
		for w in range(item+1):
			self.move_list.append([list[w][0], list[w][1]])
		self.total_moves = item+1
		self.total_moves_left = (self.play.field.get_number_of_rows()*self.play.field.get_number_of_columns()) - self.total_moves 
		self.depict_game_scenario()
		if len( self.win_list) != 0:
			self.graphics.depict_winning_pattern( player, self.win_list, False)
		return
		

		
	def set_op_mode( self, op_mode):
		self.op_mode = op_mode
		
	def get_op_mode( self):
		return self.op_mode
		
	def leave_edit_mode( self):
		self.edit_mode = False
		
	def enter_edit_mode( self):
		self.edit_mode = True

	def set_edit_player( self, player):
		self.edit_player = player
		
################################################
#
# Determine next player
# This is handled through number of moves
# - even number -> player 1
# - odd number  -> player 2
#
################################################	

	def get_next_player( self):
		if self.total_moves %2 == 0:
			player = 1
		else:
			player = 2
		return player
		
		
	def toggle_edit_player( self):
		if self.edit_player == 1:
			self.edit_player = 2
		else:
			self.edit_player = 1
		
		
	def update_move_list(self, i,j):
		self.move_list.append([i,j])
	
################################################
#
# Convert move list from internal (digit/digit) 
# to external (letter/digit) format
#
################################################		
	
	def convert_move_list_from_internal_to_standard( self):
		standard_list = []
		for i in range(len(self.move_list)):
			row_entry = self.play.field.get_number_of_rows() - self.move_list[i][0]
			column_entry = chr(65+self.move_list[i][1])
			standard_list.append([i+1, column_entry+str(row_entry)])	
		return standard_list

	
################################################
#
# Convert move list from external (letter/digit) 
# to external (digit/digit) format
#
################################################	
		
	def convert_move_list_from_standard_to_internal( self, standard_list, max_rows, max_columns):
		move_list = []
		for i, item in standard_list:
			#print(i, item)
			text = re.search(r"[a-oA-O]{1}[0-9]{1,2}",item)
			if text == None:
				return move_list
			column = ord(text[0][0].upper()) - ord(chr(65))
			if column > max_columns-1:
				return move_list
			row = max_rows - int(text[0][1:])
			if row > max_rows-1:
				return move_list
			move_list.append([row, column])
		#print(move_list)
		return move_list
	
################################################
#
# Print move list on command window
#
# (proprietary format with rows/lines ranging from 0..14/19
#
################################################	

	def print_move_list( self):
		print("Move list after", self.total_moves,"moves:")
		head_line_length = 5
		if self.total_moves < 10:
			head_line_length = 1+ self.total_moves >> 1
		for i in range( head_line_length):
			sys.stdout.write("{0:<9s}".format("Player1"))
			sys.stdout.write("{0:<9s}   ".format("Player2"))
		print("")
	
		diff = self.total_moves - len(self.move_list) 
		if diff & 1 != 0:
			sys.stdout.write("{0:<9s}".format(""))
			j = 1
		else:
			j = 0
		for i in self.move_list:
			if not j & 1:
				sys.stdout.write("{0:<9s}".format(str(i)))
			else:
				sys.stdout.write("{0:<9s}   ".format(str(i)))
			j +=1 
			if j % 10 == 0:
				print("")
		print("")
	
	def updateMoveCounters( self):
		if self.total_moves_left == 0:
			print("Error: updateMoveCounters", self.total_moves, self.total_moves_left)
			exit()
		self.total_moves+=1
		self.total_moves_left -=1
	
	def anyMoveLeft( self):
		return self.total_moves_left != 0
	def movesLeft( self):
		return self.total_moves_left
	def showMovesDone( self):
		return self.total_moves
			
################################################
#
# Step back by one move in history buffer
#
################################################		
						
	def remove_last_move( self):
		if self.total_moves > 0 and len(self.move_list) > 0:
			if self.finished:
				self.graphics.depict_winning_pattern( self.winner, self.win_list, True)
				self.finished = False
				self.winner = 0
				self.win_list = []
				
				self.play.win_path = []
				self.play.win_path_winner = 0
				self.play.win_mode = False
				
			i, j = self.move_list.pop()
			self.total_moves-=1
			self.total_moves_left+=1
			self.play.field.unset( i, j)
			self.last_moves += [(i, j)]	
			self.graphics.clear_field( i, j)
		return
		
################################################
#
# Advance by one move from history buffer
#
################################################				
		
	def restore_last_move( self):
		if self.last_moves:
		
			player = self.get_next_player()
			self.total_moves_left-=1
			i, j = self.last_moves.pop()
			self.move_list.append([i, j])
			self.play.field.set( player, i, j)
			if len(self.win_list) == 0:
				self.win_list = self.play.field.check_if_won( player, i, j, True)
				if len( self.win_list) != 0:
					self.graphics.depict_winning_pattern( player, self.win_list, False)
					self.winner = player
					self.finished = True
				else:
					self.graphics.depict_field( player, i, j)
			self.total_moves+=1		
		return	
		
	
################################################
#
# Load predefined scenario ("Scen")
#
# - each click on "Scen" button loads new scenario
# - used for debugging purposes only
#
################################################		

	def load_scenario_common( self, scenario):
		if self.total_moves != 0:
			self.reset()
		for item in scenario:
			self.play.field.set(*item)
		self.total_moves_left -= len(scenario)
		self.total_moves = len(scenario)
		self.depict_game_scenario()		

	def load_scenario( self):
		if not self.busy:
			scenarios = (((1,7, 7), (2,7, 8), (1,6, 7), (2,8, 7), (1,6, 9), (2,6, 8), (1,5, 8), (2,5, 7), (1,7, 6), (2,8, 5), (1,8, 8), (2,6, 6), (1,7, 9), (2,4, 9), (1,7, 5), (2,8, 6), (1,5, 9), (2,8, 9), (1,4, 8), (2,6, 10), (1,7, 10), (2,4, 7), (1,5, 10), (2,7, 4), (1,9, 6), (2,9, 7), (1,3, 8), (2,8, 4), (1,8, 3), (2,9, 4), (1,10, 4), (2,3, 7), (1,6, 4), (2,4, 6), (1,5, 5), (2,3, 5), (1,2, 4), (2,4, 4), (1,1, 7), (2,2, 8), (1,2, 6), (2,5, 3), (1,7, 3), (2,6, 3), (1,3, 3), (2,4, 5), (1,4, 3), (2,5, 2), (1,4, 1), (2,7, 2), (1,9, 12), (2,8, 11), (1,5, 11), (2,5, 12), (1,8, 2), (2,9, 1), (1,5, 4), (2,6, 2), (1,7, 1), (2,9, 3), (1,3, 2), (2,6, 5), (1,2, 1), (2,1, 0), (1,9, 2)),# (2,2, 3)),
			((1,7, 7), (2,7, 6), (1,6, 7), (2,6, 6), (1,5, 7), (2,4, 7), (1,5, 6), (2,5, 8), (1,7, 8), (2,8, 9), (1,6, 9), (2,8, 7), (1,6, 8), (2,8, 6), (1,8, 8), (2,7, 9), (1,5, 9), (2,9, 8), (1,10, 9), (2,9, 6), (1,10, 6), (2,10, 7), (1,4, 5), (2,3, 4), (1,4, 10), (2,3, 11), (1,6, 11), (2,6, 10), (1,11, 6), (2,8, 5), (1,11, 8), (2,6, 5), (1,5, 4), (2,9, 5), (1,5, 5), (2,5, 3), (1,9, 7)),# (2,7, 5), (1,10, 5), (2,11, 5)),
			
			
			
						 ((1,7,7), (2,6,7), (1,6,6), (2,7,6), (1,7,5), (2,8,5), (1,9,4), (2,8,6),
						  (1,8,4), (2,5,7), (1,5,5)),
						 ((1,6,5), (1,6,6), (1,6,7), (2,7,4), (2,7,5), (1,7,6), (2,7,7),( 2,8,4),
						  (1,8,5), (1,8,6), (1,8,7), (2,8,8), (2,9,4), (1,9,5), (2,9,6), (2,9,8),
						  (2,10,3),(1,10,4),(1,10,5),(1,10,6),(2,11,5)),
						 ((1,10,10),(1,9,10),(2,8,6),(2,7,4), (1,7,5), (1,7,6), (1,7,7), (2,6,5),
						  (1,6,8), (2,5,5), (1,5,7), (2,4,8) ,(1,1,1)), #,(2,4,6), 
						 ((1,10,10),(1,9,10),(2,8,6),(2,7,4), (1,7,5), (1,7,6), (1,7,7), (2,6,5),
						  (1,6,8), (2,5,5), (1,5,7), (2,4,6), (2,4,7), (2,4,8)),
						 ((1,5,7), (2,6,6), (2,7,5), (1,7,6), (1,7,7), (1,7,10),(2,8,6), (2,8,8)),
						 ((2,6,5), (1,6,6), (2,6,7), (1,7,5), (1,7,6), (2,7,8)),
						 ((2,4,10),(1,5,8), (1,5,9), (1,6,5), (2,6,6), (2,6,7), (1,6,8), (1,7,7),
						  (2,7,9),(2,8,8)))
			self.load_scenario_common( scenarios[self.scenario_number])			
			self.scenario_number += 1
			if self.scenario_number == len(scenarios):
				self.scenario_number = 0
				
################################################
#
# Toggle Start symbol in "Edit" mode
#
################################################	
				
	def toggle_first_player_edit_mode( self):
		if self.first_player_edit_mode == 1:
			self.first_player_edit_mode = 2
		else:
			self.first_player_edit_mode = 1
		i = self.play.field.get_number_of_rows()-1
		j = self.play.field.get_number_of_columns()-1
		self.graphics.clear_control_row( i)	
		self.graphics.depict_control_row_setup_scenario( i, j, self.first_player_edit_mode == 1)	
				
################################################
#
# Enter "Edit" mode
#
################################################					
		
	def setup_scenario( self):
		self.enter_edit_mode()
		self.set_edit_player(1)
		i = self.play.field.get_number_of_rows()-1
		j = self.play.field.get_number_of_columns()-1
		self.graphics.clear_control_row( i)	
		self.graphics.depict_control_row_setup_scenario( i, j, self.first_player_edit_mode == 1)	
		
################################################
#
# Leave "Edit" mode
#
################################################	

	def leave_setup_scenario( self):
		self.leave_edit_mode()
		self.finished = False
		i = self.play.field.get_number_of_rows()-1
		j = self.play.field.get_number_of_columns()-1
		self.graphics.clear_control_row( i)
		self.graphics.depict_control_row(i, j)
		self.edit_mode = False
		self.move_list  = []
		count = 0
		# calculate total number of moves by checking field usage
		for i in range(self.play.field.get_number_of_rows()):
			for j in range( self.play.field.get_number_of_columns()):
				if not self.play.field.is_free(i,j):
					count+=1
		# adjust number of moves in case that user has decided starting player at will			
		if ((self.first_player_edit_mode == 2 and count & 1 == 0) or
		   (self.first_player_edit_mode == 1 and count & 1 == 1)):
			count +=1
		
		self.total_moves = count
		self.total_moves_left = self.play.field.get_number_of_rows()*self.play.field.get_number_of_columns() - count
	
	
################################################
#
# Depict loaded game scenario on screen
#
################################################	
	
	def depict_game_scenario( self):
		for i in range( self.play.field.get_number_of_rows()):
			for j in range( self.play.field.get_number_of_columns()):
				if not self.play.field.is_free( i, j):
					self.graphics.depict_field( self.play.field.get_value(i, j), i, j)
		self.graphics.refresh()		
		
		
################################################
#
# Depict winning sequence on game field
#
################################################	
			
	def win_procedure( self, text1, text2):
		self.stat.update_wins_player( self.winner)
		if self.get_op_mode() != "auto":
			self.graphics.depict_winning_pattern( self.winner, self.win_list, False)
			self.graphics.finish_message(text1 + text2 +str( game.stat.get_wins_player( 1))+":"+str( game.stat.get_wins_player( 2)))
	
	def stale_result( self, text):
		if self.get_op_mode() != "auto":
			self.graphics.finish_message(text)
	
################################################
#
# Run next step by computer (player 1 or 2)
#
################################################
	
	def run_single_step( self):
		if not self.finished:
			self.last_moves = []
			self.computer_move()
			list = self.convert_move_list_from_internal_to_standard()
			self.convert_move_list_from_standard_to_internal( list, self.play.field.get_number_of_rows(), self.play.field.get_number_of_columns()) 

################################################
#
# Run full game in auto mode
#
################################################
			
	def run_auto_mode( self):
		while not self.finished:
			self.last_moves = []
			self.computer_move()
			if self.get_op_mode()  == "auto":
				sys.stdout.write("\rRunning game %i move %i" % (self.stat.get_total_matches()+1, self.total_moves) )
				sys.stdout.flush()
			sys.stdout.write("\r")
	
################################################
#
# Run next move by computer
#
################################################

	def computer_move( self):
		self.busy = True
		if self.showMovesDone() == 0:
			# always start in center position
			[i,j] = self.play.field.get_center_position()
		#elif self.showMovesDone() == 1:
			# 2nd move is always adjacent to first
			#[i,j] = self.play.get_random_move_from_list( self.play.field.get_list_of_surrounding_fields( 1,1))	
		else:
			# any other move gets processed
			result, [i,j] = self.play.get_next_move( self.get_next_player())
		if not self.play.field.set( self.get_next_player(), i, j):
			print("weird...")
			frameinfo = getframeinfo(currentframe())
			print(frameinfo.filename, frameinfo.lineno)
			self.debug()
	
		# for each new move, check if game is finished (True flag indicates that only 5 in a row count, e.g. 6 or 7 do not)
		self.win_list = self.play.field.check_if_won( self.get_next_player(), i, j, True)
		if len( self.win_list) != 0:
			self.finished = True
			self.winner = self.get_next_player()
			if self.print_console:
				print("Game end!!!")
				print(self.win_list)
			# highlight winning pattern on game field and run finish dialogue
			self.win_procedure( "Player " + str(self.graphics.get_symbols()[self.winner-1]) +
								" has won after " + str(self.total_moves+1) + " moves!\n\n", "Result: ")		
		else:
			if self.get_op_mode() != "auto":
				# update game field with computer move
				self.graphics.depict_field( self.get_next_player(), i, j)
				self.graphics.refresh()						
		self.updateMoveCounters()	
		self.update_move_list(i,j)		
		if self.print_console:
			self.print_move_list()
			self.play.field.print_game_field_on_console( self.graphics.get_symbols())
	
		if not self.anyMoveLeft():
			self.finished =  True
			self.stale_result("No winner!")
			self.stat.update_stale_counter()
		self.busy = False		
	
	
################################################
#
# Handle clicks on game field map during game
#
################################################
	
	def field_click_event_handler( self, i, j):
		if self.edit_mode:
			if self.play.field.is_free( i, j) and self.edit_player != 0:
				self.play.field.set( self.edit_player, i, j)
				self.graphics.depict_field( self.edit_player, i, j)
				self.graphics.refresh()
			elif self.edit_player == 0:
				self.play.field.unset( i, j)
				self.graphics.reset_game_field( i, j, self.field_click_event_handler)
		else:		
			# user has clicked on game field. Check if game is not yet finished and last computer move completed
			if not self.finished and not self.busy:
				player = self.get_next_player() 	  # get current player
				if self.play.field.is_free( i, j):    # ceck if field is free
					self.last_moves = []
					# mark selected field and enter symbol on game field
					self.play.field.set( player, i, j)
					self.updateMoveCounters()	
					self.update_move_list(i,j)	
					# check if game is finished (True flag indicates that only 5 in a row count, e.g. 6 or 7 do not)
					self.win_list = self.play.field.check_if_won( player, i, j, True)
					if len( self.win_list) != 0:
						self.winner = player
						self.finished = True
						if self.print_console:
							print("You have won!!!")
							print(self.win_list)
						# highlight winning pattern on game field and run finish dialogue	
						self.win_procedure( "You have won!\n\n", "Result: ")
						
					else:
						if self.anyMoveLeft():
							# update game field with players move 
							self.graphics.depict_field( player, i, j)
							self.graphics.refresh()
							self.computer_move() # computer takes next move
			
			
################################################
#
# Write game field and call stack in case of 
# observed error
#
################################################		

	def debug( self):
	
		self.play.field.print_game_field_on_console( self.graphics.get_symbols())
		for item in vars(self).items():
			print(item)
		
		print("==========================================")
		print("|            CALL TRACE START             ")
		print("==========================================")
		for line in traceback.format_stack():
			print(line.strip())
			
		print("==========================================")
		print("|            CALL TRACE END               ")
		print("==========================================")	
		input("check")
		exit()					

################################################
#
# class game_stat to maintain game statistical data
#
################################################		
		
class game_stat():
	def __init__( self):
		self.__player_1_wins = 0
		self.__player_2_wins = 0
		self.__stale_results = 0
		
	def update_wins_player( self, player):
		if player == 1:
			self.__player_1_wins +=1
		else:
			self.__player_2_wins +=1
			
	def get_total_matches( self):
		return self.__player_1_wins + self.__player_2_wins + self.__stale_results
		
	def update_stale_counter( self):
		self.__stale_results += 1
			
	def get_wins_player( self, player):
		if player == 1:
			return self.__player_1_wins 
		else:
			return self.__player_2_wins 
			
	
################################################
#
# Main processing loop
#
################################################

op_mode = "default"
for argument in sys.argv:
	if argument == "--auto":
		op_mode = "auto"
	elif argument == "--debug" or argument == "--d":
		op_mode = "debug"
	elif argument == "--h" or argument == "--help":
		print("Usage: ", sys.argv[0], "[--auto] [--d, --debug]")
		print("--auto:       computer plays against itself for 100 matches")
		print("--debug, --d: game field can be edited at will")
		exit()

# default run mode, either with or without debug features
# debug features allow to pre-edit game field 
if op_mode != "auto":
		master = Tk()
		master.resizable(False, False) # user cannot change game field window
		master.title(__title__)
		game = game_control( master, op_mode, 15,15)  # default game field size 15*15
		game.reset()
		master.mainloop()

		
# run mode without graphical UI. Computer plays against itself and win/loss ratio is reported for 100 consecutive games	
elif op_mode == "auto":
		game = game_control( None, op_mode, 15,15) # default game field size 15*15
		for i in range( 100): # 100 matches
			game.reset()
			game.run_auto_mode()
			print( "Result:", game.stat.get_wins_player( 1),":",game.stat.get_wins_player( 2), "with", game.total_moves, "moves." )
exit()


		
