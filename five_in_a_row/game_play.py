import random
import numpy as np
from copy import deepcopy  
import logging
import traceback
from inspect import currentframe, getframeinfo
from five_in_a_row import fields
import sys

class play():
		
	def __init__(self, rows, columns, symbol_1, symbol_2 ):
		self.level = 0                              # level of get_next_move() in recursive move search
		self.win_path = []                          # contains list of next moves for presumable winner
		self.win_path_winner = 0                    # identifies player related to self.win_path
		self.win_mode = False                       # identifies if winning path has been found
		self.move_counter = 0                       # counts attempts to find winning sequence 
		self.last_move = []                    
		self.print_console = False                  # flag to control debug output
		self.search_for_win = 0                     # flag to check if a win search recursion is active
		self.forcing3_mode = False                  # flag to indicate that current player is forcing opponent with 3
		self.forcing4_mode = False                  # flag to indicate that current player is forcing opponent with 4
		self.forced3_mode = False                   # flag to indicate that current player is forced with 3
		self.forced4_mode = False                   # flag to indicate that current player is forced with 4
		self.search_for_forcing3 = False            # flag to indicate that algorithm looks for forcing-3 sequence
		self.search_for_forcing4 = False            # flag to indicate that algorithm looks for forcing-4 sequence 
		self.move_storage = []	                    # temporary buffer used during move search
		self.field = fields.field(rows, columns)    # game field
		self.symbols = [symbol_1, symbol_2]         # symbols used for player in game field (needed for console print out)

	def reset( self):
		random.seed()
		self.level = 0
		self.win_path = []
		self.win_path_winner = 0
		self.win_mode = False
		self.search_for_win = 0
		self.move_counter = 0
		self.last_move = []
		self.field.reset()
		self.forcing3_mode = False
		self.forcing4_mode = False
		self.forced3_mode = False
		self.forced4_mode = False
		self.search_for_forcing3 = False
		self.search_for_forcing4 = False
		self.move_storage = []	
			
	def switchPlayer( self, player):
		if player == 1:
			return 2
		else:
			return 1		


###########################################################
#
# search_for_win_in_2_moves()
#
# Using input list of all game fields with missing
# 2 fields to reach 5, functions looks for win pattern
# for current player.
# 
# This can be:
# - if additional move generates a free 4 sequence
# - if additional move generates at least 2 crossing 
#   bounded 4 bars 
# - if additional move generates one bounded 4 sequence which 
#   crosses a free 3-sequence 
#  (the latter scenario may not always lead to win and
#  needs to be verified, i.e. when opponent attaches
#  to free 3-sequence in a way that he takes over a forcing
#  4-sequence.
#
###########################################################	
			
	def search_for_win_in_2_moves( self, player, move_list_2):
	
		# search for empty position which can be filled up towards FXXXXF
		moves = self.search_for_free4_move( player, move_list_2)
		if len(moves) != 0:		
			return True, moves
			
		# search for empty position which triggers two crossing bound 4 i.e. 0XXXX + 0XXXX
		moves = self.search_for_multiple_bounded4_move( player, move_list_2)
		if len(moves) != 0:
			return True, moves
			
		# search for empty position which triggers crossing bound 4 and free 3 0XXXX + FXXXF
		moves = self.search_for_crossing_bounded4_and_free3_move( player, move_list_2)
		if len(moves) != 0:
			return True, moves
			
		return False, [0,0] 
	
###########################################################
#
# search_for_win_in_3_moves()
#
# Using input list of all game fields with missing
# 3 fields to reach 5, functions looks for win pattern, 
# i.e. at least two crossing 3-sequences.
#
###########################################################		
	
	def search_for_win_in_3_moves( self, player, move_list_3):
		
		# search for empty position which triggers at least two crossing free 3 bars, i.e. FXXXF and FXXXF 
		moves = self.search_for_crossingfree3_move( player, move_list_3)
		if len(moves) != 0:
			return True, moves
			
		return False, [0,0] 

###########################################################
#
# search_for_free4_move()
#
# Using input list of selected game fields, functions looks
# which of these satisfy the condition FXXXXF for a given 
# player, i.e.
# a 4-sequence pattern surrounded by a free field at each end. 
# This check if done for any direction (horiz, vert, diag/
# anti-diag). 
#
###########################################################				
		
	def search_for_free4_move( self, player, move_list):
		l = [] 
		for w in move_list:
			if np.sum(self.field.check_for_free( player, 4, False, w)) != 0:
				l.append(np.ndarray.tolist(w))
		return  l
		
###########################################################
#
# search_for_multiple_bounded4_move()
#
# Using input list of selected game fields, functions looks
# which of these satisfy the condition BXXXXF for at least
# two bars for a given player, i.e.
# at least two 4-sequence patterns sorrounded by a bound 
# at one end (either through opponent or the game field end) 
# and a free position at the other end.
#
###########################################################	
			
	def search_for_multiple_bounded4_move( self, player, move_list):
		l = [] 
		for w in move_list:
			if np.sum(self.field.check_for_bounded_free( player, 4, w)) > 1:
				l.append(np.ndarray.tolist(w))

		return  l
			
###########################################################
#
# search_for_crossing_bounded4_and_free3_move()
#
# Using input list of selected game fields, functions looks
# which of these satisfy the condition BXXXXF for one
# direction for a given player, and the condition FXXXF for
# any of the remaining 3 directions, i.e.
# 
# a bounded 4-sequence pattern crossing a 3-sequence pattern,
# the latter encapsulated by 2 free fields.
#
###########################################################	
			
	def search_for_crossing_bounded4_and_free3_move( self, player, move_list):
		l = [] 
		for w in move_list:
			n = self.field.check_for_bounded_free( player, 4, w)
			if np.sum(n) == 1:
				m = self.field.check_for_free( player, 4, True, w)
				if np.sum(np.invert(n) & m) >=1:
					l.append(np.ndarray.tolist(w))
	
		return  l
			
			
###########################################################
#
# search_for_crossingfree3_move()
#
# Using input list of selected game fields, functions looks
# which of these satisfy the condition FXXXF for at least
# two direction for a given player,
# 
# two or more 3-sequences surrounded by at least one
# free field at each of their ends.
#
###########################################################	
	
	def search_for_crossingfree3_move( self, player, move_list):
		l = []
		for w in move_list:
			if np.sum(self.field.check_for_free( player, 4, True, w)) > 1:
				l.append(np.ndarray.tolist(w))
		return  l


###########################################################
#
# select_best_random_move()
#
# Using the current game field scenario, function suggests a next
# move for a given player.
# This is done by setting up a list of potential fields, which
# is assembled by all free fields surrounding the fields which
# are already is used by the player or its opponent.
# This list is then filtered according to criteria defined in
# filter_move_list(), see below.
#
###########################################################	
	
	def select_best_random_move( self, player, variant1, variant2):
	
		moves = self.field.get_list_of_surrounding_fields( player, 1)
		moves2 = self.field.get_list_of_surrounding_fields( player, 2)
		
		if variant2:
			for item in moves2:
				if item not in moves:
					moves.append( item)
		
		if len( moves) > 1:
			moves = self.filter_move_list( player, moves, variant1 )
		elif len( moves) == 1:
			moves = moves[0]
		else:
			# remaining fields are surrounded by opponent; take first available
			moves = self.field.get_first_empty_field()
		return moves
		

###########################################################
#
# filter_move_list()
#
# Using a given input list of possible game fields, this function
# decides which of the options shall be taken as next move for
# a given player.
# This is done by calculating a value for each of the entries.
# - If one option gets the highest value, it is chosen.
# - If multiple options contain the highest value, a random choice
#   is done among these.
#
# The value calculation for each of the fields is based on the 
# sum of two sub-values:
# - the value of this field for the player
# - the value of this field for the opponent
# 
# The subvalue for the player(opponent) is done as follows:
# 1) the position is marked as used by the player(opponent)
# 2) the function calculates how many fields would still need to be
#    set in each of the four directions to reach 5. This value is 
#    subtracted from 4, and afterwards all values are added up 
#   for each of the four bars: horiz, vert, diag, anti-diag.
# 3) A field with a sequence of only one missing element is 
#    filtered away, since it has already been analyzed during
#    the "search for forcing-4 sequence)" without success.
#    Hence, this position shall not be "wasted" for a random
#    attempt.
#
###########################################################	
			
	def filter_move_list( self, player, moves, variant ):
	
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		f_moves = []	
		
		count_max = 0
		for w in moves:
			# estimate value of move for player
			if not self.field.set( pattern, w[0],w[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			#value_p = self.calc_points( self.field.calc_moves_4_directions( pattern, anti_pattern, w[0], w[1]))	
			x = self.field.calc_moves_4_directions( pattern, anti_pattern, w[0], w[1])
			if variant:
				if 1 in x:
					#print(w, "filtered out for player", player)
					x = [6,6,6,6] # unlist
					#print(w, "delisted")
			value_p = self.calc_points(x)
			#print(self.field.calc_moves_4_directions( pattern, anti_pattern, w[0], w[1]))
			self.field.unset( w[0],w[1])

			if not self.field.set( anti_pattern, w[0],w[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			#value_o = self.calc_points( self.field.calc_moves_4_directions( anti_pattern, pattern, w[0], w[1]))	
			y = self.field.calc_moves_4_directions( anti_pattern, pattern, w[0], w[1])
			if variant:
				if 2 in y:
			#		print(w, "promoted for player", player)
					y = [1,1,1,1] # promote
					#print(w, "promoted")
			value_o = self.calc_points(y)
			#print(self.field.calc_moves_4_directions( anti_pattern, pattern, w[0], w[1]))
			self.field.unset( w[0],w[1])
			if value_p+value_o > count_max:
				f_moves = [[w[0], w[1]]]
				count_max = value_p+value_o
			elif value_p + value_o == count_max:
				f_moves.append([w[0], w[1]])
		
		if len( f_moves) > 1:
			best_move = self.get_random_move_from_list( f_moves)
		else:
			best_move = f_moves[0]
		
		return best_move	
	
			
	
	def calc_points( self, dist):
		p = 0
		for i in dist:
			if i == 6:
				continue
			p+= (4-i)
		return p
	

####################################################################
#
# search_forced_1_recursion()
#
# Using input list of selected game fields for the given player,
# the functions searches for a winning sequence of consecutive 
# "forcing-1" moves, i.e. moves with a (4 out of 5) sequence, 
# that require the opponent to fill the missing field as
# otherwise the match would be lost.
#
# The function is based on a recursive call of get_next_move(),
# where each call level consists of a players move and the (forced)
# opponent response. The recursion is finished when a winning
# sequence has been found, or when all attempts have been 
# simulated without finding a win scenario for the player.
#
# The win scenario needs to be verified in case that it consists
# of a crossing-3 scenario (since in this case the opponent might
# take back control).
#
# In order to limit the number of variants, the input list of 
# possible game field settings is reduced. The reduction algorithm
# considers the fact that a win scenario a ususally achieved by 
# consecutively occupying game fields which are located in 
# a line of sight.
#
# Note that a winning sequence may be setup by:
# - a consecutive list of only forcing-1 moves
# - at least one forcing-1 move followed by 
#    - one or multiple forcing-2 moves, or
#    - a combination of forcing-1 and forcing-2 moves
#
# Some of the moves, inclduingthe first, may be redundant
# to achieve a victory condition.
# 
###################################################################

	def search_forced_1_recursion( self, player, pos_2_own):
	
	# in level 0 some search variables are reset
		if self.level == 0:
			self.search_for_win = player
			self.move_counter = 0
			self.win_mode = False
			
		if self.level <= 1:
			self.last_move = []
		
		if self.print_console: 
			print("search_forced_1_recursion", self.last_move, "for player", player)	
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		
		# now setup a list of promising forcing-1 moves containing move and counter-move, using the line-of-sight approach
		moves_forcing = self.build_list_of_promising_forcing_moves( player, pos_2_own)
	
		if self.print_console: 
			print("search_forced_1_recursion", self.last_move, "for player", player, "with moves", moves_forcing)	
		
		# now try to find a winning sequence for each of the moves
		for item in moves_forcing:
			self.push_move( item, player)  # push the current move attempt with some associated data to a local stack
			self.last_move = item
			self.level +=2   # level is lifted by two since we simulate move/counter-move in one shot
			self.move_counter += 1 # count search attempts (for future limit filtering)
			self.search_for_forcing4 = True # indicate that we search for a forcing-1 (aka forcing4) sequence
			result, move = self.get_next_move( player) # here we run the recursion for this level
			self.level -=2
			
			if self.print_console:
				print("search_forced_1_recursion in loop", self.last_move, "for player", player, "at level", self.level, "with", result, move)	
			
			if self.win_mode:
				# the recursion is in bail out mode where we only need to construct the winning-sequence from the local stack
				self.win_path.insert(0, self.pop_move())
				if self.print_console:
					print("search_forced_1_recursion: branching out at level", self.level)
				return True
			
			elif result < 0:
				# this scenario caused the opponent to win, so drop it
				self.pop_move()
				continue
				
			elif result == 2:
				# we found a possible winning sequence, but it needs to be verified
				if self.verify_win_scenario( player, move):
					result = 1 # confirmed win for player
				else:
					result = 0 # does not lead to players win
				
			if result == 1:
				# we found a winning sequence
				self.win_mode = True # set win indicator so that recursion can be left to level 0 
				self.win_path_winner = player
				if self.print_console:
					print("win scenario found for player", player, "in level", self.level+2, "with move:", move)
					self.field.print_game_field_on_console( self.symbols)
					print("Options needed:", self.move_counter)
				self.win_path = [move]
				self.win_path.insert(0, self.pop_move())
				#while( len(self.move_storage) != 0):
					#self.win_path.insert(0, self.pop_move())
				if self.print_console:	
					print("victory (4) for player", player, "in level", self.level)
				return True
				
			else:		
				# neither win nor loss, so ignore move
				self.pop_move()
	
		if self.level == 0:
			if self.print_console:
				print("Options-4 considered:", self.move_counter)
		return False
	

##########################################################################
#
# find_forcing_combinations()
#
# Using a list of forcing-1 combinations, this function
# searches for the three most attractive elements.
#
# This function is called during the search_forced_1_recursion()
# search. 
# In level 0, the search is done as follows:
# - for each combination, the value for player and opponent are calculated
#     for a first move
#   - in a second step the value for player and opponent are calculated
#     for a second move
#     - in a third step, the value for player/opponent are calculated
#       for a third move
#  - for each combination is calculated by the subtraction of maximum
#    value for the player and the corresponding opponent value
#  - a new list is setup, which contains a value for each combination,
#    and the three moves with the highest values are returned
# 
# In all higher levels, the previous move is taken as reference and
# all combinations which may fall in a line of sight towards that
# move are assembled in a new list. At most three combinations are
# returned.
#   
##########################################################################
	
	def find_forcing_combinations( self,  pattern, anti_pattern, moves_forcing):
		moves = []
		points = []
		
		# for recursion level > 1, look for at most 3 moves which build a line of sight
		# towards previous move (self.last_move)
		if self.level > 0 and len(self.last_move) > 0:
			# setup list to contain moves in same line of sight as last move
			for w in moves_forcing:
				if self.field.check_line_of_sight( anti_pattern, w[0], self.last_move[0]):
					moves.append(w)
			
			tmp_list = []
			for i in range(min(3,len( moves))): 
				tmp_list.append(moves[i])		
			return tmp_list
			
		# for recursion level 0, look for 3 most attractive moves	
		else:
			for w in moves_forcing:
				if not self.field.set( pattern, w[0][0], w[0][1]):
					frameinfo = getframeinfo(currentframe())
					print(frameinfo.filename, frameinfo.lineno)
					self.debug()
				if not self.field.set( anti_pattern, w[1][0], w[1][1]):
					frameinfo = getframeinfo(currentframe())
					print(frameinfo.filename, frameinfo.lineno)
					self.debug()
				dist1_p = self.field.calc_moves_4_directions( pattern, anti_pattern, w[0][0], w[0][1])
				dist1_o = self.field.calc_moves_4_directions( anti_pattern, pattern, w[1][0], w[1][1])
				points_p = self.calc_points( dist1_p)
				points_o = self.calc_points( dist1_o)
				
				for v in moves_forcing:
					if self.field.is_free(v[0][0], v[0][1]) and self.field.is_free(v[1][0], v[1][1]):
						self.field.set( pattern, v[0][0], v[0][1])
						self.field.set( anti_pattern, v[1][0], v[1][1])
						dist2_p = self.field.calc_moves_4_directions( pattern, anti_pattern, w[0][0], w[0][1])
						dist2_o = self.field.calc_moves_4_directions( anti_pattern, pattern, w[1][0], w[1][1])	
						points_2p = self.calc_points( dist2_p)
						points_2o = self.calc_points( dist2_o)
								
						if points_2p > points_p:
							points_p = points_2p
							points_o = points_2o
						
							for x in moves_forcing:
								if self.field.is_free(x[0][0], x[0][1]) and self.field.is_free(x[1][0], x[1][1]):
									self.field.set( pattern, x[0][0], x[0][1])
									self.field.set( anti_pattern, x[1][0], x[1][1])
									dist3_p = self.field.calc_moves_4_directions( pattern, anti_pattern, w[0][0], w[0][1])
									dist3_o = self.field.calc_moves_4_directions( anti_pattern, pattern, w[1][0], w[1][1])	
									points_3p = self.calc_points( dist3_p)
									points_3o = self.calc_points( dist3_o)
									
									if points_3p > points_p:
										points_p = points_3p
										points_o = points_3o
							
									self.field.unset( x[0][0], x[0][1])
									self.field.unset( x[1][0], x[1][1])
		
						self.field.unset( v[0][0], v[0][1])
						self.field.unset( v[1][0], v[1][1])	
				
				moves.append(w)
				points.append( points_p - points_o)
				self.field.unset( w[0][0], w[0][1])
				self.field.unset( w[1][0], w[1][1])
				
			score_s = sorted(range(len(points)), key=lambda k: points[k])	
		
			tmp_list = []
			for i in range(min(3,len( moves))):
				tmp_list.append(moves[score_s[::-1][i]])	
			
			return tmp_list
	


################################################################
#
# build_list_of_promising_forcing_moves()
#
# Using a list of game fields with missing two elements for
# any of the 4 bars, the function identifies which subset
# builds a bounded row, i.e. TXXX__, TX_XX_, TXX_X_, TX__XX, 
# where T may be an opponent field or the game boundary.
# From this subset, a list of forcing-1 moves is setup 
# that consists of players move and opponents counter move.
# Note that for a given bar, always two scenarios are possible,
# e.g. TXXX__ -> TXXXXO or TXXXOX
#
# This function is called during the search_forced_1_recursion()
# search. 
#
################################################################			
	
	def	build_list_of_promising_forcing_moves( self, player, pos_2_own):
		
		# generate list of 3 most promising forcing moves which require immediate response
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		# generate list of possible moves and responses
		moves_forcing = []
		for w in pos_2_own:
			moves_forcing.append( self.field.generate_list_with_bounded4_bars( player, w))
		
		# find the three most attractive pairs
		moves_forcing = self.find_forcing_combinations( pattern, anti_pattern, moves_forcing)
		
		return moves_forcing
	
	
#####################################################################
#
# push_move()
#
# During search_forced_1_recursion() and search_forced_2_recursion(),
# this function modifies the game field by setting the requested
# combination of move and counter-move(s) and pushes the related data
# including current forcing/forced mode status flags to a dedicated 
# stack used during the recursion.
# 
######################################################################
	
	def push_move( self, item_list, player):
		if self.print_console: 
			print("push", item_list, "for", player, self.search_for_win)
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		self.move_storage.append( [self.search_for_win, item_list, 
								self.forcing3_mode, 
								self.forcing4_mode, 
								self.forced3_mode, 
								self.forced4_mode, 
								self.search_for_forcing3,
								self.search_for_forcing4])
		if not self.field.set( pattern, item_list[0][0], item_list[0][1]):
			frameinfo = getframeinfo(currentframe())
			print(frameinfo.filename, frameinfo.lineno)
			self.debug()
		if not type(item_list[1][0]) == list:
			if not self.field.set( anti_pattern, item_list[1][0], item_list[1][1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
		else:
			for w in item_list[1]:
				if not self.field.set( anti_pattern, w[0], w[1]):	
					frameinfo = getframeinfo(currentframe())
					print(frameinfo.filename, frameinfo.lineno)
					self.debug()

#####################################################################
#
# pop_move()
#
# During search_forced_1_recursion() and search_forced_2_recursion(),
# this function undoes the game field modifications done by
# push_move() using the recursion stack and restores the 
# related forcing/forced mode status flags.
# 
# It returns the move/counter-move info to the caller. 
#####################################################################	
					
	def pop_move( self):
		if self.print_console: 
			print("pop", self.search_for_win)
		[self.search_for_win,
		item_list, 
		self.forcing3_mode, 
		self.forcing4_mode, 
		self.forced3_mode, 
		self.forced4_mode, 
		self.search_for_forcing3, 
		self.search_for_forcing4] = self.move_storage.pop()
		
		self.field.unset( item_list[0][0], item_list[0][1])
		if not type(item_list[1][0]) == list:
			self.field.unset( item_list[1][0], item_list[1][1])
		else:	
			for w in item_list[1]:
				self.field.unset( w[0], w[1])
		return item_list[0]
		

####################################################################
#
# search_forced_2_recursion()
#
# Using input list of selected game fields for the given player,
# the functions searches for a winning sequence of consecutive 
# "forcing-2" moves, i.e. moves with an unbounded 3-out-of-5 sequence, 
# that require the opponent to fill one of the missing fields as
# otherwise the match would be lost.
# Examples are FXXXF, FX_XXF, FXX_XF
#
# The function is based on a recursive call of get_next_move(),
# where each call level consists of a players move and the (forced)
# opponent responses. To reduce the number of alternatives, the 
# algorithm simlulates all counter-moves (opponent responses) which
# may be taken by the opponent, i.e. a scenario
# FXXXF will be simulated by 0XXX0, and FXX_XF by 0XX0X0
#
# The recursion is finished when a winning
# sequence has been found, or when all attempts have been 
# simulated without finding a win scenario for the player.
#
# The win scenario needs to be verified in case that it consists
# of a crossing-3 scenario (since in this case the opponent might
# take back control).  FIXME > missing!
#
# Note that a winning sequence may be setup by:
# - a consecutive list of only forcing-2 moves
# - at least one forcing-2 move followed by 
#    - one or multiple forcing-1 moves, or
#    - a combination of forcing-1 and forcing-2 moves
#
# Some of the moves, including the first, may be redundant
# to achieve a victory condition for the player.
# 
###################################################################
		
	def search_forced_2_recursion( self, player, pos_3_own, pos_4_opp):
	
		if self.level == 0:
			self.move_counter = 0
			self.search_for_win = player
			
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		moves_forcing = []
		
		# generate list of forcing-3 options with all(!) potential responses from opponent
		for w in pos_3_own:
			responses = self.field.generate_list_with_unbounded3_bars( player, w)
			if len(responses) != 0:
				moves_forcing.append([[w[0], w[1]], responses])
		
		#print("before filtering", moves_forcing)
		# remove options which do not generate a new forcing-3 option in another row/column/diagonale
		# from the remaining, remove those which may result in loss of forcing mode and forcing4_option is not present
	
		#self.field.print_game_field_on_console( self.symbols)
		
		# the player may be in a forced situation currently, but may take back control through counter-threatening
		if self.forced3_mode:
			moves_filtered = moves_forcing
		
		else:
			moves_filtered = []
			for item in moves_forcing:
				list = []
				self.push_move( item, player)
				# check if current move triggers at least one free pair in another bar for the player
				if np.sum( self.field.check_for_free( player, 4, True, item[0])) > 0:
					suitable = True
					# if so, check if current move does not trigger at least one free pair for the opponent
					# ( to prevent counter-threatening and loss of game control)
					for response in item[1]:
						if np.sum( self.field.check_for_free( self.switchPlayer(player), 4, False, response)) > 0:
							suitable = False
					if suitable:
						# if both checks apply, take this move combination as candidate
						moves_filtered.append(item)	
					# FIXME there is no length limitation for moves_filtered[]
				self.pop_move()
	
		if self.print_console: 
			self.field.print_game_field_on_console( self.symbols)
			#if forcing4_option:
			#	print("run search_forced_2_recursion in level", self.level, "for player", player, "with forcing option and mode", 
			#	self.forced3_mode, "and move list", moves_filtered)
			
			print("run search_forced_2_recursion in level", self.level, "for player", player, "without forcing option and mode", self.forced3_mode,
				self.forced3_mode, "and move list", moves_filtered)	
	
		
		# now do the recursion	
		for item in moves_filtered:
			self.push_move( item, player)
		
			self.last_move = item
			self.level +=2 #  step by 2 since we simulate move and counter-moves
			self.move_counter += 1
			self.search_for_forcing3 = True
			result, move = self.get_next_move( player)
			self.level -=2 
	
			if self.print_console:
				print("search_forced_2_recursion in loop for player", player, "at level", self.level, "with", result, move)	
			
			if self.win_mode:
				# bail out in win mode and construct the winning sequence (potentially still with redundant steps)
				self.win_path.insert(0, self.pop_move())
				if self.print_console:
					print("search_forced_2_recursion: branching out at level", self.level)
				return True
			
			elif result < 0:
				result = False
				self.pop_move()
				continue
				
			elif result > 0: # FIXME: win scenario needs to be verified!
				self.win_mode = True
				self.win_path_winner = player
				if self.print_console:
					print("win scenario (2) found for player", player, "in level", self.level+2)
					self.field.print_game_field_on_console( self.symbols)
					print("Options needed:", self.move_counter)
				self.win_path = [move]
				self.win_path.insert(0, self.pop_move())
				
				if self.print_console:
					print("victory (3) for player", player, "in level", self.level, "with", self.win_path)
				return True
			else:		
				#print("warning", item, "triggers forced move for player. Stop",  player, self.win_path)
				self.pop_move()
	
		if self.level == 0:
			if self.print_console:
				print("Options-3 considered:", self.move_counter)
				
		return False
	
	
###################################################################
#
# verify_win_scenario()
#
# Using input move, this function verifies whether the 
# given player will win the match.
# 
# This is required in the search for win recursion in case
# that get_next_move() responded with a "2" return code instead
# of "1" (confirmed win).
# Therefore this function continues to simulate subsequent
# moves in order to see if get_next_move() returns "1" for player.
# In a negative scenario the win move, e.g. a two-crossing 3-bars,
# may trigger the opponent to setup a forcing-1 move, which then
# removes game control for the player.
#
###################################################################		

	def verify_win_scenario( self, player, move):
	
		assessment = False # default result
		opponent = self.switchPlayer( player)
		list = []

		pattern, anti_pattern = self.field.set_pattern_antipattern( player)	
		if self.print_console:
			print("verify_win_scenario for player", player,  move)	
			self.field.print_game_field_on_console( self.symbols)
		level = self.level #memorize level to unwind actions at function end
		
		finished = False
		while not finished:
			self.level +=1 # increase level by one, as we do not know opponents response yet
			# now simulate presumable winning move 
			if not self.field.set( pattern, move[0], move[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			list.append(move)
			# and get opponent response
			result, move = self.get_next_move( opponent)
			
			if (not (self.forcing4_mode or self.forced4_mode) or result > 0):
				# win scenario validation failed if result > 0 (opponent!) or 
				# neither player nor opponent take a forcing-1 threat. 
				# Note that a forcing-1 threat by the opponent may still turn
				# a forcing-1 threat for the player in subsequent move!
				#print("win scenario validation 1 failed for", move, "with result", result)
				#self.field.print_game_field_on_console( self.symbols)
				break
			self.level +=1
			# now simulate opponents move
			if not self.field.set( anti_pattern, move[0], move[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			list.append(move)
			
			# and get players response
			result, move = self.get_next_move( player)
			if result == 1:
				# return code is one, player will win
				if self.print_console:
					print("win scenario validation succeeded for ", move)
					self.field.print_game_field_on_console( self.symbols)
				assessment = True
				finished = True
			elif result == -1 or (result == 0 and not (self.forcing4_mode or self.forced4_mode)):
				# see above
				if self.print_console:
					self.field.print_game_field_on_console( self.symbols)
					print("win scenario validation failed 2 for", move, "with result", result)
				break
		
		# undo all game field changes
		for item in list:
			self.field.unset(item[0], item[1])
			
		self.level = level # restore level
		
		if self.print_console:
			print("verify_win_scenario for player", player, "finished with verdict", assessment)	
		
		return assessment	
	
	

###########################################################
#
# can_win_path_be_shortened()
#
# This functions checks if a win path can be shortened for 
# the winner, i.e. if one more several moves can be omitted.
# 
# Currently only designed for forcing-1 combinations, there-
# fore not used.
#
###########################################################		
	
	def can_win_path_be_shortened( self, player):
		opponent = 1
		if player == 1:
			opponent = 2
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		win_path_try = deepcopy( self.win_path)
		#print("checking removal of", self.win_path[0])
		win_path_try.pop(0)
		if len(win_path_try) >= 1:
		
			failure = False
			for item in win_path_try:
				if not self.field.set( pattern, item[0], item[1]):
					frameinfo = getframeinfo(currentframe())
					print(frameinfo.filename, frameinfo.lineno)
					self.debug()
				self.level += 1
				result, next_move = self.get_next_move( opponent)
				if self.print_console:
					print(next_move, item[1])
				if next_move[0] == item[1][0] and next_move[1] == item[1][1]:
					if not self.field.set( anti_pattern, item[1][0], item[1][1]):
						frameinfo = getframeinfo(currentframe())
						print(frameinfo.filename, frameinfo.lineno)
						self.debug()
					self.level +=1
				else:
					failure = True
					break
		
			if not failure:
				result, next_move = self.get_next_move( player)
				if result != 1:
					failure = True	
					
			for item in win_path_try:
				self.field.unset( item[0][0], item[0][1])
				self.field.unset( item[1][0], item[1][1])
			self.level = 0
		
			if not failure:
				return True
	
		return False
		

###########################################################
#
# get_random_move_from_list()
#
# Given a list, the function returns a random entry
#
###########################################################		
		
	def get_random_move_from_list(self, l=[]):
		if len(l) == 0:
			print("error: game.get_random_move_from_list")
			exit(1)
		else:
			random_value = random.randint(0, len(l)-1)
		return l[random_value]		


###########################################################
#
# choose_best_option()
#
# When the player is threatened and has multiple options 
# to respond, this function looks for the best move.
#
###########################################################		
		
	def choose_best_option( self, moves, player):
	
		if len(moves) == 1:
			return moves[0]
	
		if len(moves) == 4: # FIXME, is this possible
			return self.get_random_move_from_list( moves)
	
		if self.print_console:
			print("choose for player", player,"at level", self.level, self.search_for_win, moves, self.win_mode)
			self.field.print_game_field_on_console( self.symbols)
			
		if (self.level != 0 and player == self.search_for_win) or self.win_mode:
		# when searching for a win scenario, or in a confirmed win case, we take a random walk (don't care)
			return self.get_random_move_from_list( moves)
		
		elif self.level == 0:
			self.search_for_win = self.switchPlayer( player)

		
		result_moves = []
		found = False
		pattern, anti_pattern = self.field.set_pattern_antipattern( player)
		
		# now simulate all move candidates
		for w in moves:
			if self.print_console:
				print("testing choose option", w, "for player", player)
			stack = []
			# set the move, and get the opponent response
			if not self.field.set( pattern, w[0], w[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			self.level +=1
			#self.field.print_game_field_on_console( self.symbols)
		
			next_player = self.switchPlayer( player)
			result, next_move = self.get_next_move( next_player)
			next_pattern = next_player
			
			# now we stay in a get_next_move() recursion as long as 
		    # - a win scenario is not found for player/opponent and
			# - the player/opponent are still in forced-1 mode 
			# FIXME: this condition is not fully clear and forced-2 is not yet considered 
			while not self.win_mode and (self.forced4_mode or result == 0) and len(next_move) != 0:
				if not self.field.set( next_pattern, next_move[0], next_move[1]):
					frameinfo = getframeinfo(currentframe())
					print(frameinfo.filename, frameinfo.lineno)
					self.debug()
				self.level +=1
				stack.append(next_move)
				#self.field.print_game_field_on_console( self.symbols)
				#print("this round", next_player, next_pattern)
				#print("next round", self.switchPlayer( next_player), self.switchPlayer( next_player))
				next_player = self.switchPlayer( next_player)
				result, next_move = self.get_next_move( next_player)
				#print("choose loop result", result, next_move, self.forced4_mode, "with win_mode", self.win_mode)
				next_pattern = next_player			
			
			#print("result win mode is", self.win_mode, "with winner", self.win_path_winner)
			if not ((self.win_mode and self.win_path_winner == self.search_for_win) or (result==1 and next_player == self.search_for_win)):
				if self.print_console:
					print("option", w, "does not cause opponent win")
				# add w as candidate to result list, since opponent does not win in this case
				result_moves.append(w)
				
			for x in stack:
				self.field.unset( x[0], x[1])	
				self.level -=1
			self.field.unset( w[0], w[1])
			self.level -=1
			self.win_mode = False
			self.win_path_winner = 0
			self.win_path = []
			#print("result level is", self.level)	
			
		if len( result_moves) == 0:	
			if self.print_console:
				print("player", player,"looses in any scenario.")
			
			return self.get_random_move_from_list( moves)
		else:		
			return self.get_random_move_from_list( result_moves)

	
				
	
###########################################################
#
# get_next_move()
#
# Returns next best move for the player and a return
# indicating:
#  1: defined win
#  2: presumable win
# -1: loss
#  0: none of the above
#
###########################################################		
	
	def get_next_move( self, player):
	
		if self.print_console:
			print("get_next_move for", player, "at level", self.level)
	
		result = 0
		found = False
		opponent = self.switchPlayer( player)
		self.forcing3_mode, self.forced3_mode = False, False
		self.forcing4_mode, self.forced4_mode = False, False
		
		if self.level == 0:
			self.search_for_win = 0
		next_move = []	
		
		# setup lists which contain missing fields to reach a 5-row/column/diagonale
		# pos_ply[0]: fields which complete a 5-row/column/diagonale for player
		# pos_ply[1]: fields which enable a 5-row/column/diagonale for player with one missing element
		# pos_ply[2]: fields which enable a 5-row/column/diagonale for player with two missing elements
		pos_ply, pos_opp = self.field.calc_metric_moves( player, opponent)
	
		# can player win with current move?
		if len( pos_ply[0]) != 0:
			found, result, next_move = True, 1, self.get_random_move_from_list( pos_ply[0])
			
		# can opponent win next move?	
		elif len( pos_opp[0]) != 0:
			found, result, next_move = True, 0, self.get_random_move_from_list( pos_opp[0])
			self.forced4_mode = True
			if len(pos_opp[0]) > 1: # opponent will win
				result = -1
				
	
		# can player win in 2 moves? 
		if not found and len(pos_ply[1]) != 0:
			found, moves =  self.search_for_win_in_2_moves( player, pos_ply[1])
			if found: 
				# verify correctness
				for w in moves:
					if self.verify_win_scenario( player, w):
						next_move =  w
						result = 1
						break
				if next_move == []:
					found = False
			
				
		# check if win_mode active -> if so, pick next move from list
		if not found and self.level == 0 and self.win_path_winner == player and self.win_mode:
			if len(self.win_path) > 1:
				self.win_path.pop(0)
				if self.field.is_free( self.win_path[0][0], self.win_path[0][1]):
					found, result, next_move = True, 1, self.win_path[0]
				else:
					# if move from win_list is already used, the win scenario was wrong !
					if self.print_console:
						print("win scenario failed for player", self.win_path_winner)
					self_win_mode = False
					self.win_path_winner = 0
					self.win_path = []		
				
				
		# check if list of forcing-1 moves can be generated	
		if not found and not self.win_mode and len( pos_ply[1] != 0):
			#print("search for forcing-4 moves")
			found = self.search_forced_1_recursion( player, pos_ply[1])
			if found:
				#print(self.level, self.win_path)
				result, next_move = 0, self.win_path[0]
				
		# can opponent win in 2 moves?
		if not found and len(pos_opp[1]) != 0:
			found, moves = self.search_for_win_in_2_moves( opponent, pos_opp[1])
			if found:
				self.forced3_mode = True
				if opponent == self.win_path_winner and len(pos_ply[1] != 0):
					# if opponent wins the game and is in forcing-3 mode, we 
					# delay the victory by generating forcing-4 moves as long as available
					result, next_move = 0, self.get_random_move_from_list( pos_ply[1])
					self.forcing4_mode = True
					if self.print_console:
						print("delay opponent win with", next_move)
					for item in np.ndarray.tolist(pos_ply[1]):
						if item in moves:
							next_move = item
							if self.print_console:
								print("correction .... delay opponent win with", next_move)
							break
				else:			
					next_move = self.choose_best_option( moves, player)
					result = -1
			
				
		# can player win in 3 moves? 
		if not found and len(pos_ply[2]) != 0:# and self.level != 0:
			found, moves =  self.search_for_win_in_3_moves( player, pos_ply[2])
			if found: 
				# verify correctness
				#print("get_next_move 2, self.verify_win_scenario", self.level, "to verify", moves)
				for w in moves:
					if self.verify_win_scenario( player, w):
						#print("result is TRUE!!!!!!!!!!!!!! for", w, "at level", self.level)
						next_move =  w
						result = 1
						self.forcing3_mode = True #??
						break

				if next_move == []:
					found = False
					result = 0
					#print("result is FALSE !!!!!!!!!! for ", moves, "at level", self.level)
					if self.win_mode and self.win_path_winner==opponent and len(self.win_path) != 0:
						if self.field.is_free( self.win_path[0][0], self.win_path[0][1]):
							next_move = self.win_path[0]
							#print("next move is .. ", next_move, self.win_path, self.level)
							found = True
							self.win_mode = False
							self.win_path = []
			
				
		if not found and len( pos_ply[2]) != 0:
			found = self.search_forced_2_recursion( player, pos_ply[2], pos_opp[1])
			if found:
				next_move = self.win_path[0]
			else:
				pass
	
		
		# can opponent win in 3 moves? 
		if not found and len(pos_opp[2]) != 0 and self.level == 0:
			found, moves =  self.search_for_win_in_3_moves( opponent, pos_opp[2])
			if found: 
				#print("opponent may win in 3", next_move)
				next_move = self.get_random_move_from_list( moves)	
				result = -2	
		
		if not found:
			if self.level == 0 and player == 1:
				next_move = self.select_best_random_move( player, True,False)
				if self.print_console:
					print("next move", next_move)
					
			if self.level == 0 and player == 2:
				next_move = self.select_best_random_move( player, True ,False)
				if self.print_console:
					print("next move", next_move)		
			
			
		if self.level == 0:
			if self.print_console:
				print("Next move for player", player, "is", next_move)
		

		return result, next_move
	

			
################################################
#
# Write game field and call stack in case of 
# observed error
#
################################################		

	def debug( self):
	
		self.field.print_game_field_on_console( self.symbols)
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


		
