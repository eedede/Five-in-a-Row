import numpy as np
import sys

class field():
	def __init__( self, rows, columns):
		if ((rows < 5 or rows > 19) or (columns < 5 or columns > 19)):
			print("Game field size limited to 5..19 x 5..19.")
			exit()
		self.__rows = rows
		self.__columns = columns
		self.__rows_to_win = 5
		self.__field  = np.zeros(( rows,columns), dtype=np.int)
		self.__metric_moves = np.zeros(( 2, rows,columns), dtype=np.int)
		#self.__metric_moves2 = np.zeros(( 2, rows,columns), dtype=np.int)

		
	def reset( self):
		self.__field  = np.zeros(( self.__rows, self.__columns), dtype=np.int)
		self.__metric_moves = np.zeros(( 2, self.__rows, self.__columns), dtype=np.int)
		
		
	def	get_number_of_rows( self):
		return self.__rows
	
	def	get_number_of_columns( self):
		return self.__columns
	
	def is_free( self, i, j):
		return (self.__field[i,j] == 0)
		
	def get_value( self, i, j):
		return self.__field[i,j]	
	
	def get_center_position( self):
		return [self.__rows>>1, self.__columns>>1]	
		
	def set( self, player, i, j):
		if self.__field[i,j] == 0:
			self.__field[i,j] = player
			return True	
		else:
			print("Error in field.set() for player",player,". Field (", i, j, ") is already occupied with value", self.__field[i,j])
			return False
			
	def unset( self, i, j):
		self.__field[i,j] = 0		
		
	
	def get_list_of_empty_positions( self):
		moves = []
		for i in range( self.__rows):
			for j in range( self.__columns): 
				if self.__field[i,j] == 0:
					moves.append([i,j])		
		return moves
	

################################################################
#
# set_pattern_antipattern()
#
# This function discriminates which flag a player shall 
# use to indicate a game field as used.
# "1" is used by player 1. Opponent flag (anti_pattern) is "2".
# "2" is used by player 2. Opponent flag (anti_pattern) is "1".
#
################################################################
	
	def set_pattern_antipattern( self, player):
		
		if player == 1:
			return 1,2
		else:
			return 2,1
		
################################################################
#
# get_first_empty_field()
#
# Returns two indices of first game field starting from top left
# corner, which is still free.
#
################################################################
		
	def get_first_empty_field( self):
		for i in range( self.__rows):
			for j in range( self.__columns): 
				if self.is_free( i,j):
					return [i,j]
		
################################################################
#
# get_list_of_surrounding_fields()
#
# Returns list of game field indices containing all fields
# which surround game fields already in use.
#
# The parameter depth indicates the distance from a field in
# use.
#
################################################################		
		
	def add_to_list( self, l, x, y):
		if [x,y] not in l:
			l.append([x,y])
		return l
				
	def get_list_of_surrounding_fields( self, player, depth):
		l = []
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		
		for i in range( self.__rows):
			for j in range( self.__columns): 
				#if self.__field[i,j] == pattern:
				if self.__field[i,j] != 0:
						if i-depth >= 0:
							if self.is_free( i-depth, j):
								l = self.add_to_list( l, i-depth, j)
							if j-depth >= 0 :
								if self.is_free( i-depth, j-depth):
									l = self.add_to_list( l, i-depth, j-depth)
								if self.is_free( i,j-depth):
									l = self.add_to_list( l, i, j-depth)	
							if j + depth < self.get_number_of_columns():
								if self.is_free( i-depth,j+depth):
									l = self.add_to_list( l, i-depth, j+depth)
								if self.is_free( i,j+depth):
									l = self.add_to_list( l, i, j+depth)		
						if i+depth < self.get_number_of_rows():
							if self.is_free( i+depth,j):
								l = self.add_to_list( l, i+depth, j)
							if j-depth >= 0:
								if self.is_free( i+depth,j-depth):
									l = self.add_to_list( l, i+depth, j-depth)	
								if self.is_free( i,j-depth):
									l = self.add_to_list( l, i, j-depth)		
							if j+depth < self.get_number_of_columns():
								if self.is_free( i+depth,j+depth):
									l = self.add_to_list( l, i+depth, j+depth)	
								if self.is_free( i,j+depth):
									l = self.add_to_list( l, i, j+depth)		
		return l				

################################################################
#
# check_line_of_sight()
#
# Given two game fields, the function checks whether they are 
# in a line of sight, i.e. between them there is no game field
# used by the opponent (anti_pattern) and that their distance
# is not exceeding 4.
#
################################################################	

	def	check_line_of_sight( self, anti_pattern, pos1, pos2):
		
		r1, c1 = pos1[0], pos1[1]
		r2, c2 = pos2[0], pos2[1]
		
		if r1 == r2:
			start, length = min(c2,c1), abs(c2-c1)
			if length > 4:
				return False
			elif length <= 1:
				return True
			for i in range(length-1):
				if self.__field[r1, 1+start+i] == anti_pattern:
					return False
			return True
		
		elif c1 == c2:
			start, length = min(r2,r1), abs(r2-r1)
			if length > 4:
				return False
			elif length <= 1:
				return True
			for i in range(length-1):
				if self.__field[1+start+i,c1] == anti_pattern:
					return False
			return True
		
		elif abs(r1-r2) == abs(c1-c2):
			length = abs(c1-c2)
			if length > 4:
				return False
			elif length <= 1:
				return True
			if ((r1 > r2 and c1 > c2) or (r1 < r2 and c1 < c2)):
				# falling diagonale
				start_r, start_c, length = min(r1, r2), min(c1, c2), abs(r2-r1)
				for i in range( length-1):
					if self.__field[min(self.get_number_of_rows()-1,1+start_r+i),min(self.get_number_of_columns()-1,1+start_c+i)] == anti_pattern:
						return False	
				return True	
			else:
			# rising diagonale
				start_r, start_c, length = max(r1, r2), min(c1, c2), abs(r2-r1)
				for i in range( length-1):
					if self.__field[min(self.get_number_of_rows()-1,1+start_r+i),min(self.get_number_of_columns()-1,1+start_c+i)] == anti_pattern: # first index out of bounds
						return False	
				return True			
		return False


	"""
	def calc_max_available_moves( self, data, pattern, anti_pattern ):		
		
		count_max = 1
		if len( data) >= 5:
			frames = len(data) - 5
			
			for w in range(frames+1):
				existing_fields = 0
				for w in data[w:w+5]:
					if w == anti_pattern:
						existing = 6
						break
					elif w == pattern:
						existing_fields +=1
				if existing_fields > count_max:
					count_max = existing_fields
					
		return count_max	
	"""
	
######################################################################
#
# calc_min_required_moves()
#
# For a given data bar (row/column/diag/anti-diag), the function
# determines the minimal number of fields which are 
# needed within this bar to build an "all-5" sequence with "pattern".
#
######################################################################	
	
	def calc_min_required_moves( self, data, pattern, anti_pattern):	
	
		count_min = 6
		if len( data) >= 5:
			frames = len(data) - 5
			for w in range(frames+1):
				missing_fields = 0
				for w in data[w:w+5]:
					if w == anti_pattern:
						missing_fields = 6
						break
					elif w == 0:
						missing_fields +=1
				if missing_fields < count_min:
					count_min = missing_fields
						
		return count_min
	
######################################################################
#
# calc_min_required_moves2()
#
# For a given data bar (row/column/diag/anti-diag) with an offset
# for the curent field, function determines the minimal number of fields 
# which are needed within this bar to build an "all-5" sequence 
# with "pattern" (including the field with the offset).
#
######################################################################	
				
	def calc_min_required_moves2( self, data, offset, pattern, anti_pattern):	
	
		count_min = 6
		start_left = max( 0, offset - 4)
		end_right = min( offset+4, len(data)-1)
		
		frames = max(0, end_right - start_left - 3)
		
		if frames > 0:
			for w in range(frames):
				missing_fields = 0
				for u in data[start_left + w:start_left + w + 5]:
					if u == anti_pattern:
						missing_fields = 6
						break
					elif u == 0:
						missing_fields +=1
				if missing_fields < count_min:
					count_min = missing_fields
					
		return count_min
		
######################################################################
#
# calc_moves_4_directions()
#
# For a given game field with indices i,j, the function determines
# the minimal number of fields which are needed to build
# an "all-5" sequence with "pattern" in any bar direction (horiz, vert,
# diag, anti-diag).
#
######################################################################	
		
	def calc_moves_4_directions( self, pattern, anti_pattern, i, j):
	
		count_min = []
		
		for direction in range(4):
			bar, offset = self.return_4plus4_bar_by_direction( direction, i, j)
			count_min.append( self.calc_min_required_moves2( bar, offset, pattern, anti_pattern))
		
		return count_min
		
######################################################################
#
# calc_moves()
#
# For a given game field with indices i,j, the function determines
# the minimal number of fields which are needed to build
# an "all-5" sequence with "pattern" in any bar direction (horiz, vert,
# diag, anti-diag). During the bar assessment the offset of the field
# within the bar is not considered.
#
######################################################################	
	
	def calc_moves( self, pattern, anti_pattern, i, j):
				
		bar, offset = self.return_4plus4_bar_by_direction( 0, i, j)
		count_min = self.calc_min_required_moves( bar, pattern, anti_pattern)
		
		for direction in range(1,4):
			bar, offset = self.return_4plus4_bar_by_direction( direction, i, j)
			count_min = min( count_min, self.calc_min_required_moves( bar, pattern, anti_pattern))
		
		return count_min
	
	
######################################################################
#
# calc_metric_moves()
#
# Function determines for each unused game field the minimum number
# of moves which are needed to build an "all-5" sequence 
# in any bar direction (horiz, vert, diag, anti-diag). 
# This calculation is done for both player and opponent and stored
# in an internal matrix self.__metric_moves.
#
# The function returns 4 lists for player and opponent:
# - all game fields with 1 missing element to reach "5"
# - all game fields with 2 missing elements to reach "5"
# - all game fields with 3 missing elements to reach "5"
# - all game fields with 4 missing elements to reach "5"
#
######################################################################	
		
	def calc_metric_moves( self, index1, index2 ):
	
		for p in range(2):
			pattern, anti_pattern = self.set_pattern_antipattern( p+1)
			for i in range( self.__rows):
				for j in range( self.__columns): 
					if self.__field[i,j] == 0:
						self.__metric_moves[p,i,j] = self.calc_moves( pattern, anti_pattern, i, j)
					else:
						self.__metric_moves[p,i,j] = 0
						
		# setup ordered list of possible moves for player and opponent
		pos_ply, pos_opp = [], []
		for i in range(4):
			pos_ply.append(self.get_metric_fields( index1, i+1))
			pos_opp.append(self.get_metric_fields( index2, i+1))				
						
		return pos_ply, pos_opp
		
		
	def get_metric_fields( self, player, index):
		if player == 1 or player == 2:		
			if index >= 1 and index < 5:
				return np.argwhere( self.__metric_moves[player-1] == index)
		else:
			print("get_metric_field(). Wrong parameters", player, index)
			exit()	
		
		
	"""
	def calc_metric_moves2( self ):
	
		for p in range(2):
			pattern, anti_pattern = self.set_pattern_antipattern( p+1)
			#print(player, pattern, anti_pattern)
			for i in range( self.__rows):
				for j in range( self.__columns): 
					if self.__field[i,j] == 0:
						self.__metric_moves2[p,i,j] = self.calc_moves( pattern, anti_pattern, i, j)
					else:
						self.__metric_moves2[p,i,j] = 0
		return 		
		
	
	def get_metric_fields2( self, player, index):
		if player == 1 or player == 2:		
			if index >= 1 and index < 5:
				return np.argwhere( self.__metric_moves2[player-1] == index)
		else:
			print("get_metric_field(). Wrong parameters", player, index)
			exit()
	"""
		
		
######################################################################
#
# find_5_equals()
#
# For a given data bar, the function determines the maximum count of
# consecutive patterns (when larger or equal to 5) and the offset
# of the element which completes the sequence.
#
# Otherwise it returns 0,0
#
######################################################################			
		
	def find_5_equals( self, pattern, data):
	
		count = 0
		count_max = 0
		m_store = 0
		
		for m in range( len( data)):
			if data[m] == pattern:
				count +=1
				if count >= 5:
					count_max = count
					m_store = m	
			else:
				count = 0

		return count_max, m_store		
	
######################################################################
#
# return_full_bar_by_direction()
#
# For a given game field with indices i,j and a requested direction index
# the function returns the associated bar with the offset of the related
# field in this bar.
#
# The direction indices are:
# 0: horizontal
# 1: vertical
# 2: diagonal (bottom left to upper right)
# 3: anti/inverse diagonal
#
######################################################################	
	
	def return_full_bar_by_direction( self, direction, i, j):
		if direction == 0:    # horizontal
			return (self.__field[i]), j
		elif direction == 1:  # vertical
			return (self.__field[:,j]), i
		elif direction == 2:  # diagonal
			return (np.diag(self.__field, j-i)), min(i,j)
		elif direction == 3:  # inverse diagonal
			return (np.diag(self.__field[:,::-1], (self.__columns-1-j) -i)[::-1]), min(self.__rows-1-i, j)
		else:
			print("ERROR: return_full_bar_by_direction() called with wrong index", index)
			
###########################################################################
#
# return_4plus4_bar_by_direction()
#
# For a given game field with indices i,j and a requested direction index
# the function returns the associated game field bar with indices -4..+4
# in relation to the index (i,j).
# The maximum length of the returned bar is 9, the minimum is 1.
# A bar with only one entry is returned if the indices indicate a game
# field corner and the requested direction is a diagonale that goes
# beyond the game field scope.
# On the other hand, a horizontal direction for the upper or lower right corner
# gives only 5 values with indices -4, -3, -2, -1, 0.
#
# The direction indices are:
# 0: horizontal
# 1: vertical
# 2: diagonal (bottom left to upper right)
# 3: anti/inverse diagonal
#
###########################################################################	

	def return_4plus4_bar_by_direction( self, direction, i, j):
		if direction == 0:    # horizontal
			range_horizontal_min = max(0, j-(self.__rows_to_win-1))
			range_horizontal_max = min(self.__columns, j+self.__rows_to_win)
			return (self.__field[i,range_horizontal_min:range_horizontal_max]), j-range_horizontal_min
			
		elif direction == 1:  # vertical
			range_vertical_min = max(0, i-(self.__rows_to_win-1))
			range_vertical_max = min(self.__rows, i+(self.__rows_to_win))
			return (self.__field[range_vertical_min:range_vertical_max,j]), i-range_vertical_min
			
		elif direction == 2:  # diagonal	
			diag = np.diag(self.__field, j-i)
			positions_left = min(i, j)
			positions_right = min(self.__rows-1-i,self.__columns-1-j)
		
			offset_left, offset_right = 0,0
			if positions_left > 4:
				offset_left = positions_left - 4
				diag = diag[offset_left:] 
			if positions_right > 4:	
				offset_right = positions_right - 4
				diag = diag[:-offset_right] 
			return ( diag), positions_left-offset_left
			
		elif direction == 3:  # inverse diagonal
			diag_inv = np.diag(self.__field[:,::-1], (self.__columns-1-j) -i)[::-1]
			positions_left = min(self.__rows-1-i, j)
			positions_right = min(i,self.__columns-1-j)
			
			offset_left, offset_right = 0,0
			if positions_left > 4:
				offset_left = positions_left - 4
				diag_inv = diag_inv[offset_left:] 
			if positions_right > 4:	
				offset_right = positions_right - 4
				diag_inv = diag_inv[:-offset_right] 	
			return ( diag_inv), positions_left-offset_left
		else:
			print("ERROR: return_4plus4_bar_by_direction() called with wrong index", index)	
			
######################################################################
#
# check_for_free()
#
# For a given game field with indices in w[], the function dermines
# in how many of the 4 directions (horiz, vert, diag, anti-diag), there
# are a sufficient number of unused game fields available which allow
# to setup a consecutive sequence of (length-1) fields for a given
# player, which are surrounded by 2 empty fields.
# 
# The result is returned in a list with 4 entries [0,1].
#
# If flag is set to True, only (length-2) fields are required.
#
######################################################################			
		
	def check_for_free( self, player, length, flag, w):
	
		matches = np.zeros(4, dtype=np.int)
		i,j = w[0], w[1]
		for direction in range(4):
			bar, index = self.return_full_bar_by_direction( direction, i, j)
			if self.check_for_free_space_in_bar( bar, index, player, length, flag):
				matches[direction] = 1
		return matches

	def check_for_free_space_in_bar( self, bar, index, player, length, flag):
		# search for length-1 pattern matches in [length] block which is encapsulated by surrounding free positions
		# when option flag is set, only length-2 matches are required
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		
		pattern_count = length-1
		if flag == True:
			pattern_count -=1 
			
		for n in range(length):
			local_count=0
			if index-1-n >= 0 and index+length-n < len( bar):
				if bar[index-1-n] != anti_pattern and bar[index+length-n] != anti_pattern:
					for m in range(length):
						value = bar[index+m-n]
						if value == anti_pattern:
							local_count = 0
							break
						elif value == pattern:
							local_count +=1
					if local_count >= pattern_count:
						return True
			
		return False	
		
######################################################################
#
# check_for_bounded_free()
#
# For a given game field with indices in w[], the function dermines
# in how many of the 4 directions (horiz, vert, diag, anti-diag), there
# are a sufficient number of unused game fields available which allow
# to setup a consecutive sequence of (length-1) fields for a given
# player, which is surrounded by at least one opponent field.
# 
# The result is returned in a list with 4 entries [0,1].
#
# If flag is set to True, only (length-2) fields are required.
#
######################################################################		
	
	def check_for_bounded_free( self, player, length, w):
		
		matches = np.zeros(4, dtype=np.int)
		i,j = w[0], w[1]
		for direction in range(4):
			bar, index = self.return_full_bar_by_direction( direction, i, j)
			if self.check_for_bounded_free_space_in_bar( bar, index, player, length):
				matches[direction] = 1
		return matches
	

	def check_for_bounded_free_space_in_bar( self, bar, index, player, length):
		# search for length-1 pattern matches in [length] block which may be sorrounded by anti-pattern or bar end
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		
		pattern_count = length-1
		
		for n in range(5):
			local_count=0
			if index-n >= 0 and index+5-1-n < len( bar):
				for m in range(5):
					value = bar[index+m-n]
					if value == anti_pattern:
						local_count = 0
						break
					elif value == pattern:
						local_count +=1
				if local_count >= pattern_count:
					return True
		
		return False	
			
	
					
	
	
	"""
	def check_for_opponent_threat( self, player, fields_to_check):
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		
		for item in fields_to_check:
			if not self.set( pattern, item[0], item[1]):
				frameinfo = getframeinfo(currentframe())
				print(frameinfo.filename, frameinfo.lineno)
				self.debug()
			hits = np.sum( self.check_for_free( player, 4, False, item))
			self.unset( item[0], item[1])
			if hits != 0:
				return True
		return False
	"""
	
######################################################################
#
# generate_list_with_unbounded3_bars()
#
# For a given game field entry with indices in w[], the function dermines
# the possible opponent responses in order to address the open-3
# threat raised by player through setting the field in w[].
# 
# First the function converts an unbounded players 2-sequence e.g. FFXXFF 
# into a forcing-3 sequence,e.g.
# FXXXF, FXFXXF, FXXFXF which requires an opponent response.
# 
# The result list contains all possible opponent responses in order
# to address the players open-3 threat.
#
# This search is done for any of the 4 bars (horiz/vert/diag/anti-diag)
######################################################################	
	
	def generate_list_with_unbounded3_bars( self, player, w):
		
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		i, j = w[0],w[1]
		if not self.set( pattern, i, j):
			frameinfo = getframeinfo(currentframe())
			print(frameinfo.filename, frameinfo.lineno)
			self.debug()
		force_list = []
		
		bar, index = self.return_full_bar_by_direction( 0, i, j)
		offsets = self.return_response_indices_in_3_bar( bar, index, player )
		if offsets != []:
			force_list = [[i, j+o-index] for o in offsets]
		
		else:
			bar, index = self.return_full_bar_by_direction( 1, i, j)
			offsets = self.return_response_indices_in_3_bar( bar, index, player )
			if offsets != []:
				force_list = [[i+o-index, j] for o in offsets]
			else:
				bar, index = self.return_full_bar_by_direction( 2, i, j)
				offsets = self.return_response_indices_in_3_bar( bar, index, player )
				if offsets != []:
					base_v = min(self.get_number_of_rows()-1, max(0,i-j))  # FIXME
					base_h = max(0, j-i)
					force_list = [[base_v+o, base_h+o] for o in offsets]
				else:
					bar, index = self.return_full_bar_by_direction( 3, i, j)
					offsets = self.return_response_indices_in_3_bar( bar, index, player )
					if offsets != []:
						base_v = min(self.get_number_of_rows()-1, i+j)  # FIXME
						base_h = max(0, j-(self.get_number_of_columns()-1-i)) # FIXME
						force_list = [[base_v-o, base_h+o] for o in offsets]	

		self.unset( i, j)	
		return force_list
		
		
######################################################################
#
# return_response_indices_in_3_bar()
#
# For a given data bar, the function determines the bar offsets
# which would allow the opponent to respond to an open-3 threat
# by the player, e.g.
# - in a scenario FXXXF, the two indices for the Fs would be returned.
# - in a scenario FXXFXF, the three indices for the Fs would be returned
# - dito for FXFFXF
#
# If an open-3 threat is found, the indices are returned in a list.
# if no open-3 threat is found, an empty list is returned.
#
######################################################################

	def return_response_indices_in_3_bar( self, bar, index, player):

		pattern, anti_pattern = self.set_pattern_antipattern( player)
		
		pattern_count = 3
		length = 4
		pos = 0
		indices = []
			
		for n in range(length):
			local_count=0
			if index-1-n >= 0 and index+length-n < len( bar):
				if bar[index-1-n] != anti_pattern and bar[index+length-n] != anti_pattern:
					pos = 99 # FIXME is this needed?
					for m in range(length):
						value = bar[index+m-n]
						if value == anti_pattern:
							local_count = 0
							break
						elif value == pattern:
							local_count +=1
						else:
							pos = m
							
					if local_count == pattern_count:
						if bar[index-n] == pattern and bar[index-n+length-1] == pattern:
							indices = [index-1-n,index+pos-n,index-n+length]
						elif bar[index-n] == pattern:
							indices = [index-1-n,index-n+length-1]
						else:
							indices = [index-n,index-n+length]
						return indices	
			
		return []		
		
	"""
	def get_response_index_when_forcing_with_unbounded3( self, bar, index, pattern, anti_pattern):
	
		forced_response_index = 99
			
		for n in range( 5):
			local_count = 0		
			if index-n >= 0 and index+5-1-n < len( bar):
				for m in range( 5):
					value = bar[index+m-n]
					if value == anti_pattern:
						local_count = 0
						break
					elif value == pattern:
						local_count +=1
					else:
						local_resp = m-n
				if local_count == 4:
					forced_response_index = local_resp
					break
						
		return forced_response_index		
	"""
	
######################################################################
#
# generate_list_with_bounded4_bars()
#
# For a given game field entry with indices in w[], the function dermines
# the offset pairs (player/opponent) which are needed in order to 
# convert a bounded a players 3-sequence e.g. TXXXFF into a
# a completed sequence of type:
# TXXXXO, TXXXOX, TXXOXX, TXOXXX, TOXXXX 
# 
# The first offset is always determined by the values in w[], the second
# is obtained from get_response_index_when_forcing_with_bounded4().
#
# The output is referred to as force list, as it contains first an
# offset pair for the player in order to threaten the opponent, and 
# then the corresponding opponent response.
#
# This search is done for any of the 4 bars (horiz/vert/diag/anti-diag)
######################################################################	
	
	def generate_list_with_bounded4_bars( self, player, w):
		
		pattern, anti_pattern = self.set_pattern_antipattern( player)
		i, j = w[0],w[1]
		if not self.set( pattern, i, j):
			frameinfo = getframeinfo(currentframe())
			print(frameinfo.filename, frameinfo.lineno)
			self.debug()
		force_list = []
		
		bar, index = self.return_full_bar_by_direction( 0, i, j)
		#print(bar, index)
		response_index = self.get_response_index_when_forcing_with_bounded4( bar, index, pattern, anti_pattern)
		if response_index != 99:
			force_list += [[i,j], [i, index + response_index]]	
		bar, index = self.return_full_bar_by_direction( 1, i, j)
		#print(bar, index)
		response_index = self.get_response_index_when_forcing_with_bounded4( bar, index, pattern, anti_pattern)
		if response_index != 99:
			force_list += [[i,j],[index + response_index, j]]
		bar, index = self.return_full_bar_by_direction( 2, i, j)
		#print(bar, index)
		response_index = self.get_response_index_when_forcing_with_bounded4( bar, index, pattern, anti_pattern)
		if response_index != 99:
			force_list += [[i,j],[i + response_index, j + response_index]]
		bar, index = self.return_full_bar_by_direction( 3, i, j)
		#print(bar, index)
		response_index = self.get_response_index_when_forcing_with_bounded4( bar, index, pattern, anti_pattern)
		if response_index != 99:
			force_list += [[i,j],[i - response_index, j + response_index]]
		self.unset( i, j)	
		return force_list
			
		
######################################################################
#
# get_response_index_when_forcing_with_bounded4()
#
# For a given bar with an offset (index), the function determines
# for a bounded 4-sequence, e.g. TXXXXF, TXXXFX, TXXFXX, TXFXXX
# the sequence index that requires to be set in order to achieve
# an all-5 sequence.
# This is needed during the forcing-1 search, in order to determine
# the opponent response when the player forces with a bounded-4 threat.
#
# If not bounded 4-sequence is found, the value 99 is returned.
#
######################################################################
		
	def get_response_index_when_forcing_with_bounded4( self, bar, index, pattern, anti_pattern):
	
		forced_response_index = 99
			
		for n in range( 5):
			local_count = 0		
			if index-n >= 0 and index+5-1-n < len( bar):
				for m in range( 5):
					value = bar[index+m-n]
					if value == anti_pattern:
						local_count = 0
						break
					elif value == pattern:
						local_count +=1
					else:
						local_resp = m-n
				if local_count == 4:
					forced_response_index = local_resp
					break
						
		return forced_response_index	
		
######################################################################
#
# check_if_won()
#
# For a given game field with index i,j the function dermines if it
# is part of a winning sequence in any of the 4 directions. If so, 
# the function returns a list of all associated game field positions 
# including index i,j which determine the winning sequence.
# 
# The flag "only_5_win" determines whether just all-5 sequences are
# checked for a victory condition, i.e. longer sequences are excluded.
#
# If a winning sequence is not found, the function returns an empty list.
#
######################################################################	
		
	def check_if_won( self, player, i, j, only_5_win):	
		#compare = np.ndarray.tolist(np.argwhere(row == pattern))
		positions = []
		pattern = player
			
		# check for winning pattern in current row
		bar, offset = self.return_4plus4_bar_by_direction( 0, i, j)
		count_max, pos = self.find_5_equals( pattern, bar)
		if ((only_5_win and count_max == 5) or
		    (not only_5_win and count_max >= 5)):
			for m in range(count_max):
				positions += [(i, pos - m + j - offset)]
		
		# check for winning pattern in current column		
		bar, offset = self.return_4plus4_bar_by_direction( 1, i, j)
		count_max, pos = self.find_5_equals( pattern, bar)
		if ((only_5_win and count_max == 5) or
		    (not only_5_win and count_max >= 5)):
			for m in range(count_max):
				positions += [(pos - m + i - offset, j)]
			
		# check for winning pattern in falling diagonale
		bar, offset = self.return_4plus4_bar_by_direction( 2, i, j)
		count_max, pos = self.find_5_equals( pattern, bar)
		if ((only_5_win and count_max == 5) or
		    (not only_5_win and count_max >= 5)):
			for m in range(count_max):
				positions += [(pos-offset + i-m , pos-offset + j-m)]
			
		# check for winning pattern in rising diagonale
		bar, offset = self.return_4plus4_bar_by_direction( 3, i, j)
		count_max, pos = self.find_5_equals( pattern, bar)
		if ((only_5_win and count_max == 5) or
		    (not only_5_win and count_max >= 5)):
			for m in range(count_max):
				positions += [(offset - pos + i+m , pos - offset + j-m)]
		
		return( positions)
		
	
######################################################################
#
# print_game_field_on_console()
#
# Print game field with internal notation for rows/columns on terminal
# window.
#
######################################################################		

	def print_game_field_on_console(self, symbols):
		print("    ",end="")
		for i in range(self.__columns):
			sys.stdout.write("{0:<3}".format(i))
		print("")
		for i in range(self.__rows):
			sys.stdout.write("{0:>3} ".format(i))
			for j in range(self.__columns):
				symbol = "."
				if self.__field[i][j] == 1:
					symbol = symbols[0]
				elif self.__field[i][j] == 2:
					symbol = symbols[1]
				sys.stdout.write("{0:<3s}".format(symbol))
			print("")		
	
"""
	def print_metric_on_console(self):
		print("    ",end="")
		for i in range(self.__columns):
			sys.stdout.write("{0:<3}".format(i))
		print("")
		for i in range(self.__rows):
			sys.stdout.write("{0:>3} ".format(i))
			for j in range(self.__columns):
				sys.stdout.write("{0:<3}".format(self.__metric[i,j]))
			print("")	
"""	
	