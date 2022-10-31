import application
#############
# Libraries #
#############

## Custom Libraries
import gambit 				# for the method names
import application_process
import params_vector
import data_vector

## Python Libraries
import multiprocessing
import time     # time.sleep()
import os       # os.cput_count()

## Gtk
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject


#############
# Constants #
#############

const_title     = "Adaptation Procedure on Misinformation Games"
const_icon_path = "./gui-images/forth-icon.png"

const_window_width  = 1280
const_window_height = 720

const_dialog_window_width   = 550
const_dialog_window_height  = 100

const_random_width  = 300
const_random_height = 360

const_init_file     = 100
const_init_random   = 200

###########
# Classes #
###########


class LeftColumnTabConst:
	statistics  = 0
	smes		= 1
	node_list   = 2
	mis_games   = 3

LeftColumnTabConst = LeftColumnTabConst()

left_column_tab_consts = [
	LeftColumnTabConst.statistics,
	LeftColumnTabConst.smes,
	LeftColumnTabConst.node_list,
	LeftColumnTabConst.mis_games
]


class LeftColumnTabNames:
	statistics  = "Statistics"
	smes		= "SMEs"
	node_list   = "Node List"
	mis_games   = "Misinformation Games"

LeftColumnTabNames = LeftColumnTabNames()

left_column_tab_names =[
	LeftColumnTabNames.statistics,
	LeftColumnTabNames.smes,
	LeftColumnTabNames.node_list,
	LeftColumnTabNames.mis_games
]




class RightColumnTabConst:
	tree    = 0
	root    = 1

RightColumnTabConst = RightColumnTabConst()

right_column_tab_consts = [
	RightColumnTabConst.tree,
	RightColumnTabConst.root
]



class RightColumnTabNames:
	tree    = "Tree"
	root    = "Root"

RightColumnTabNames = RightColumnTabNames()

right_column_tab_names = [
	RightColumnTabNames.tree,
	RightColumnTabNames.root
]

tab_names = left_column_tab_names + right_column_tab_names




###########################
# Text Display Tabs Class #
###########################

class DisplayTextTab(Gtk.TextView):
	
	def __init__(self, tab_name, tab_text=""):
		assert tab_name is not None
		
		## Initialize duper class
		super().__init__()
		
		self.tab_name = tab_name
		self.tab_text = tab_text
		
		## write text to textview
		self.textbuffer = self.get_buffer()
		self.textbuffer.set_text(self.tab_text)
		
		## properties
		self.set_editable(False)
		self.set_cursor_visible(False)
		#self.set_vscroll_policy()
	
	
	def update_displayed_text(self, tab_text):
		self.tab_text = tab_text
		self.textbuffer.set_text(tab_text)
	


###############
# Main Window #
###############

class MainWindow(Gtk.Window):
	
	##################
	# Initialization #
	##################
	
	def __init__(self):
		
		########################
		# Adaptation Procedure #
		########################
		
		self.total_mgs      = 100
		self.computed_mgs   = 0
		
		# parameters vector
		self.params_vector = params_vector.ParamsVector()
		
		# data vector
		self.data_vec = data_vector.DataVector()
		
		# adaptation procedure application process
		self.adapt_proc_app 	= None
		self.adapt_proc_queue	= None
		
		## States
		self.adapt_proc_running 	= False
		self.adapt_proc_concluded	= False
		
		
		##############
		# GUI States #
		##############
		
		self.help_is_showing		= False
		self.about_is_showing		= False
		self.settings_is_showing	= False
		
		
		#######
		# GUI #
		#######
		
		## Initialize super class
		super().__init__(title=const_title)
		self.set_icon_from_file(const_icon_path)
		self.connect("destroy", Gtk.main_quit)
		self.set_border_width(20)
		self.set_default_size(const_window_width, const_window_height)
		
		## Boxes
		# Horizontal Main Area
		self.main_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
		self.main_area.set_homogeneous(False)
		self.main_area.set_hexpand(True)
		
		## Main Menu
		self.main_menu = Gtk.MenuBar()
		self.main_area.add(self.main_menu)
		
		## Render the Main Menu
		self.create_main_menu()
		
		# Left Column
		self.left_column_tabs = []  # A list of DisplayTextTab instances
		
		self.left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		self.left_column.set_homogeneous(False)
		self.left_column.set_size_request(int(const_window_width/2) + 1, const_window_height)
		self.left_column.set_hexpand(True)
		
		# Right Column
		self.right_column_tabs = [] # A list of DisplayTextTab instances
		
		self.right_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		self.right_column.set_homogeneous(False)
		self.right_column.set_size_request(int(const_window_width/2) + 1, const_window_height)
		self.right_column.set_hexpand(True)
		
		# Pack Columns to Main Area
		#self.main_area.pack_start(self.left_column, True, True, 0)
		self.main_area.add(self.left_column)
		#self.main_area.pack_start(Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=20), True, True, 0)
		#self.main_area.pack_start(self.right_column, True, True, 0)
		self.main_area.add(self.right_column)
		
		# Pack Main Area to Window
		self.add(self.main_area)
		
		## Render the two Columns
		self.render_columns()
		
		## Render the Parent Window
		self.show_all()
		
		## Open Initialization Dialog
		self.dialog = WizardDialogWindow(self)
		response = self.dialog.run()
		self.dialog.destroy()
		
		self.resolve_init_dialog(response)
		
	
	
	###################################
	# Adaptation Procedure Connection #
	###################################
	
	def create_and_run_adapt_proc(self):
		assert self.params_vector.is_initialised()
		assert self.adapt_proc_running == False
		
		self.adapt_proc_queue = multiprocessing.Queue()
		args = self.params_vector.create_command_vector()
		self.adapt_proc_app = multiprocessing.Process(
			target=application_process.process_app,
			args=(
				args,
				self.adapt_proc_queue
			)
		)
		
		self.adapt_proc_app.start()
		self.adapt_proc_running = True
		
		self.total_mgs = int(self.adapt_proc_queue.get())
	
		
	def destroy_adapt_proc(self):
		assert self.adapt_proc_running == True
		
		## Terminate the child-process
		self.adapt_proc_app.terminate()
		
		## Reset the variables and states
		self.adapt_proc_app 		= None
		self.adapt_proc_queue		= None
		self.adapt_proc_running		= False
		self.adapt_proc_concluded	= False
		
		## Reset the input parameters
		self.params_vector.reset_input()
	
	
	#################
	# Retrieve Data #
	#################
	## Only demos for now
	
	def retrive_data(self, data):
		assert data in tab_names
		
		## Left Column
		if data == LeftColumnTabNames.statistics: 	return self.data_vec.get_statistics()
		if data == LeftColumnTabNames.smes:			return self.data_vec.get_smes()
		if data == LeftColumnTabNames.node_list: 	return self.data_vec.get_node_list()
		if data == LeftColumnTabNames.mis_games: 	return self.data_vec.get_mis_game_list()
		
		## Right Columns
		if data == RightColumnTabNames.tree: return self.data_vec.get_tree()
		if data == RightColumnTabNames.root: return self.data_vec.get_root_file()
		
		## Else: This should never happend
		print("Error: retrieve data!" + str(data))
		exit(1)
	
	##################
	# Render Columns #
	##################
	
	def render_columns(self):
		self.render_left_column()
		self.render_right_column()
	
	def render_left_column(self):
		self.left_column_notebook = Gtk.Notebook()
		self.left_column.add(self.left_column_notebook)
		
		for tab in left_column_tab_consts:
			page = Gtk.ScrolledWindow()
			page.set_hexpand(True)
			page.set_vexpand(True)
			
			self.left_column_notebook.append_page(page, Gtk.Label(left_column_tab_names[tab]))
			
			tab_content = DisplayTextTab(left_column_tab_names[tab], self.retrive_data(left_column_tab_names[tab]))
			self.left_column_tabs.append(tab_content)
			
			page.add(tab_content)
	
	def render_right_column(self):
		self.right_column_notebook = Gtk.Notebook()
		self.right_column.add(self.right_column_notebook)
		
		for tab in right_column_tab_consts:
			page = Gtk.ScrolledWindow()
			page.set_hexpand(True)
			page.set_vexpand(True)
			
			self.right_column_notebook.append_page(page, Gtk.Label(right_column_tab_names[tab]))
			
			tab_content = DisplayTextTab(right_column_tab_names[tab], self.retrive_data(right_column_tab_names[tab]))
			self.right_column_tabs.append(tab_content)
			
			page.add(tab_content)
	
	
	
	###################
	# Render Main Menu#
	###################
	
	def initialize_random(self, widget=None):
		
		rand_dialog = InitRandomForm(self)
		response = rand_dialog.run()
		
		while response == Gtk.ResponseType.OK:
			if rand_dialog.check_entries():
				## Everything checks out -->
				## Initiate the adaptation Procedure
				
				# make sure to start from a blank param vec
				self.params_vector.reset_input()
				
				# reset data vector
				self.data_vec.reset()
				
				# configure the parameter vector,
				# for init random
				self.params_vector.set_init_random(
					rand_dialog.get_num_players(),
					rand_dialog.get_strategies(),
					rand_dialog.get_max_utility(),
					rand_dialog.get_seed()
				)
				
				# create the adaptation procedure child-process
				self.create_and_run_adapt_proc()
				
				# show the progress bar
				self.show_progress_bar()
				
				# break the loop
				break
			else:
				dialog = Gtk.MessageDialog(
					transient_for=self,
					flags=0,
					message_type=Gtk.MessageType.ERROR,
					buttons=Gtk.ButtonsType.OK,
					text="Error!"
				)
				dialog.format_secondary_text(rand_dialog.get_error_message())
				dialog.run()
				dialog.destroy()
			
			response = rand_dialog.run()
			
		rand_dialog.destroy()
	
	
	def open_root(self, widget=None):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Select the Root of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.OPEN
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_OPEN,   Gtk.ResponseType.OK)
		
		## Add filters
		filter_mg = Gtk.FileFilter()
		filter_mg.set_name("Misinformation Game Files")
		filter_mg.add_pattern("*.mg")
		dialog.add_filter(filter_mg)
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			
			# start from a fresh param vector
			self.params_vector.reset_input()
			
			# reset data vector
			self.data_vec.reset()
			
			# init param vector from file
			self.params_vector.set_init_file(dialog.get_filename())
			
			# create the adaptation procedure child-process
			self.create_and_run_adapt_proc()
			
			# Destroy dialog
			dialog.hide()
			
			# Show progress
			self.show_progress_bar()
		
		dialog.destroy()
		
	
	def save_all(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Select a Folder to Export All the Data of the Adapt. Proc.",
			parent=self,
			action=Gtk.FileChooserAction.SELECT_FOLDER
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_all(filename)
		
		dialog.destroy()
		
	def save_root(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Root of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		#filter_mg = Gtk.FileFilter()
		#filter_mg.set_name("Misinformation Game Files")
		#filter_mg.add_pattern("*.mg")
		#dialog.add_filter(filter_mg)
		dialog.set_current_name("root.mg")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_root_file(filename)
		
		
		dialog.destroy()
		
	
	def save_smes(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Stable Misinformed Equilibria",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		#filter_mg = Gtk.FileFilter()
		#filter_mg.set_name("Misinformation Game Files")
		#filter_mg.add_pattern("*.mg")
		#dialog.add_filter(filter_mg)
		dialog.set_current_name("smes.txt")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_smes(filename)
		
		dialog.destroy()
	
	
	def save_statistics(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Statistics of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		# filter_mg = Gtk.FileFilter()
		# filter_mg.set_name("Misinformation Game Files")
		# filter_mg.add_pattern("*.mg")
		# dialog.add_filter(filter_mg)
		dialog.set_current_name("statistics.txt")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_statistics(filename)
		
		dialog.destroy()
	
	
	def save_nodes(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Node List of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		#filter_mg = Gtk.FileFilter()
		#filter_mg.set_name("Misinformation Game Files")
		#filter_mg.add_pattern("*.mg")
		#dialog.add_filter(filter_mg)
		dialog.set_current_name("nodes.txt")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_node_list(filename)
		
		dialog.destroy()
	
	def save_tree(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Tree of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		# filter_mg = Gtk.FileFilter()
		# filter_mg.set_name("Misinformation Game Files")
		# filter_mg.add_pattern("*.mg")
		# dialog.add_filter(filter_mg)
		dialog.set_current_name("tree.txt")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_tree(filename)
		
		dialog.destroy()
	
	
	def save_mis_game_list(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Save the Mis. Games List of the Adaptation Procedure",
			parent=self,
			action=Gtk.FileChooserAction.SAVE
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		
		## Add filters
		# filter_mg = Gtk.FileFilter()
		# filter_mg.set_name("Misinformation Game Files")
		# filter_mg.add_pattern("*.mg")
		# dialog.add_filter(filter_mg)
		dialog.set_current_name("mis_games_list.txt")
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.save_mis_game_list(filename)
		
		dialog.destroy()
	
	
	def export_mis_games(self, widget):
		## Initialization
		dialog = Gtk.FileChooserDialog(
			title="Select a Folder to Export Misinformation Games",
			parent=self,
			action=Gtk.FileChooserAction.SELECT_FOLDER
		)
		
		## Add buttons
		dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
		
		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			self.data_vec.export_mg_files(filename)
		
		dialog.destroy()
	
	
	def exit(self, widget):
		self.destroy()
	
	def help_showing_reset(self, widget):
		self.help_is_showing = False
	
	def help(self, widget):
		if self.help_is_showing: return
		self.help_is_showing = True
		
		help_dialog = Gtk.Dialog(title="Help",  transient_for=self, flags=0)
		help_dialog.set_default_size(const_dialog_window_width, const_dialog_window_height)
		help_dialog.set_modal(True)
		
		
		help_message = Gtk.Label()
		#help_message.set_max_width_chars(60)
		#help_message.set_line_wrap(True)
		help_message.set_markup(
			"1. Start by secelcting an initialization method:"
			"\n\n\tGo to File > Random Root to create a new root .mg file, by setting some parameters."
			"\n\tAlternatively, go to File > Open Root to open an existing .mg file as root."
			"\n\n2. The generated root can be saves from File > Save Root."
			"\n\n3. In the Node tab, on the left column, a list of all Adaptation Tree nodes is presented."
			"\n\tNote that some nodes may correspond to the same Misinformation Game."
			"\n\n4. In the Misinformation Games tab, we present a list of the <i>unique</i> misinformation games."
			"\n\n5. On the right column we present the Adaptation Tree as a text based graph, and the root .mg file."
			"\n\n6. From File > Export .mg Files you can export all the unique Misinformation Games, as .mg files."
			"\n\n\nIn this project we use GAMBIT package for finding Nash Equilibria in Normal Form Games,\n "
			"version 15.1.1, you can find more about the GAMBIT commands "
			"<a href=\"https://gambitproject.readthedocs.io/en/latest/\">here</a>."
			"\n\nWe also use the <a href=\"https://potassco.org/\">CLINGO</a> language for "
			"Answer Set Programming, version 5.4.0."
		)
		#help_message.set_justify(Gtk.Justification.FILL)
		#help_message.
		
		box = help_dialog.get_content_area()
		box.add(help_message)
		box.set_margin_top(20)
		box.set_margin_bottom(20)
		box.set_margin_left(20)
		box.set_margin_right(20)
		help_dialog.show_all()
		
		#help_dialog.destroy()
		#self.help_is_showing = False
		help_dialog.connect("destroy", self.help_showing_reset)
	
	
	def about_showing_reset(self, widget):
		self.about_is_showing = False
	
	def about(self, widget):
		if self.about_is_showing: return
		self.about_is_showing = True
		
		about_dialog = Gtk.Dialog(title="About", transient_for=self, flags=0)
		about_dialog.set_default_size(const_dialog_window_width, const_dialog_window_height)
		about_dialog.set_modal(True)
		
		about_message = Gtk.Label()
		about_message.set_markup(
			"<a href=\"http://users.ics.forth.gr/~fgeo/files/SETN22.pdf\"><big><b>An Implementation of the Adaptation Procedure in Mininformation Games</b></big></a>\n"
			"Authors: Merkouris Papamichail, Constantinos Varsos, Giorgos Flouris\n"
			"<a href=\"https://hilab.di.ionio.gr/setn2022/\">SETN 2022\n</a>"
			"email: mercoyris@ics.forth.gr\n"
			"Institute of Computer Science, Foundation of Research and Technology, Hellas\n"
			"2022\n\n"
			"<b>Technologies Used:</b>\n"
			"<a href=\"https://gambitproject.readthedocs.io/en/latest/\">GAMBIT</a>, version 15.1.1, "
			"<a href=\"https://potassco.org/\">CLINGO</a>, version 5.4.0, "
			"<a href=\"https://anytree.readthedocs.io/en/latest/\">Any Tree</a>, version 2.8.0"
		)
		# help_message.set_line_wrap(True)
		# help_message.set_justify(Gtk.Justification.FILL)
		about_message.set_max_width_chars(60)
		# help_message.
		
		box = about_dialog.get_content_area()
		box.set_spacing(20)
		box.set_margin_top(20)
		box.set_margin_bottom(20)
		box.set_margin_left(20)
		box.set_margin_right(20)
		
		box.add(about_message)
		
		ics_fort_logo = Gtk.Image()
		ics_fort_logo.set_from_file("gui-images/ICS-FORTH-small.png")
		box.add(ics_fort_logo)
		
		about_dialog.show_all()
		
		about_dialog.connect("destroy", self.about_showing_reset)
	
	def settings(self, widget):
		settings_dialog = SettingsWindow(self)
		response = settings_dialog.run()
		
		if response == Gtk.ResponseType.OK:
			self.params_vector.set_settings(
				settings_dialog.get_nash_equilibria_method(),
				settings_dialog.get_decimal_points(),
				settings_dialog.get_is_fast_mode(),
				settings_dialog.get_num_threads()
			)
		
		if response == Gtk.ResponseType.CANCEL:
			self.params_vector.reset_default_settings()
		
		settings_dialog.destroy()
	
	def create_main_menu(self):
	
		## Drop Down File menu
		file_menu = Gtk.Menu()
		file_menu_dropdown = Gtk.MenuItem("File")
		
		## File menu items
		file_new = Gtk.MenuItem("New Random Root")
		file_open   = Gtk.MenuItem("Open Root File")
		
		file_save           	= Gtk.MenuItem("Save All")
		file_save_root      	= Gtk.MenuItem("Save Root")
		file_save_smes 			= Gtk.MenuItem("Save SMEs")
		file_save_stats			= Gtk.MenuItem("Save Statistics")
		file_save_nodes     	= Gtk.MenuItem("Save Nodes List")
		file_save_tree 			= Gtk.MenuItem("Save Tree")
		file_save_mis_games 	= Gtk.MenuItem("Save Mis. Games List")
		file_export_mis_games	= Gtk.MenuItem("Export Mis. Games")
		
		file_exit   = Gtk.MenuItem("Exit")
		
		## Append Menu Items
		file_menu_dropdown.set_submenu(file_menu)
		file_menu.append(file_new)
		file_menu.append(file_open)
		file_menu.append(Gtk.SeparatorMenuItem())
		file_menu.append(file_save)
		file_menu.append(file_save_root)
		file_menu.append(file_save_smes)
		file_menu.append(file_save_stats)
		file_menu.append(file_save_nodes)
		file_menu.append(file_save_tree)
		file_menu.append(file_save_mis_games)
		file_menu.append(file_export_mis_games)
		file_menu.append(Gtk.SeparatorMenuItem())
		file_menu.append(file_exit)
		
		## Connect Actions
		file_new.connect("activate", self.initialize_random)
		file_open.connect("activate", self.open_root)
		file_save.connect("activate", self.save_all)
		file_save_root.connect("activate", self.save_root)
		file_save_smes.connect("activate", self.save_smes)
		file_save_stats.connect("activate", self.save_statistics)
		file_save_nodes.connect("activate", self.save_nodes)
		file_save_tree.connect("activate", self.save_tree)
		file_save_mis_games.connect("activate", self.save_mis_game_list)
		file_export_mis_games.connect("activate", self.export_mis_games)
		file_exit.connect("activate", self.exit)
		
		## Append File submenu to main menu
		self.main_menu.append(file_menu_dropdown)
		
		## Help
		help_menu = Gtk.MenuItem("Help")
		self.main_menu.append(help_menu)
		help_menu.connect("activate", self.help)
		
		## About
		about_menu = Gtk.MenuItem("About")
		self.main_menu.append(about_menu)
		about_menu.connect("activate", self.about)
		
		## Settings
		about_menu = Gtk.MenuItem("Settings")
		self.main_menu.append(about_menu)
		about_menu.connect("activate", self.settings)
		
	#########################
	# Initialization Dialog #
	#########################
	
	def resolve_init_dialog(self, response):
		if response == const_init_file:
			self.open_root()
		elif response == const_init_random:
			self.initialize_random()
	
	
	################
	# Progress Bar #
	################
	
	def show_progress_bar(self):
		#print("show_progress_bar")
		
		## Initialize dialog window
		
		progress_window = ProgressBarWindow(self, self.total_mgs)
		progress_window.show_all()
		
		while self.adapt_proc_running:
			status = self.get_current_progress()
			if status == application_process.ComProtocol.adapt_proc_ended:
				self.adapt_proc_running 	= False
				self.adapt_proc_concluded	= True
				self.get_adapt_proc_results()
				break
			else:
				progress_window.update_progress(status)
		
		progress_window.hide()
	
	def get_adapt_proc_results(self):
		#print("get_adapt_proc_results")
		assert self.adapt_proc_running == False
		assert self.adapt_proc_concluded == True
		
		while True:
			token = self.adapt_proc_queue.get()
			#print("token = " + str(token))
			if token == application_process.ComProtocol.eof:
				break
			
			if token == application_process.ComProtocol.root:
				self.data_vec.set_root_file(self.adapt_proc_queue.get())
				self.right_column_tabs[RightColumnTabConst.root].update_displayed_text(
					self.data_vec.get_root_file()
				)
			
			if token == application_process.ComProtocol.smes:
				self.data_vec.set_smes(self.adapt_proc_queue.get())
				self.left_column_tabs[LeftColumnTabConst.smes].update_displayed_text(
					self.data_vec.get_smes()
				)
				
			
			if token == application_process.ComProtocol.statistics:
				self.data_vec.set_statistics(self.adapt_proc_queue.get())
				#print(self.data_vec.get_statistics())
				self.left_column_tabs[LeftColumnTabConst.statistics].update_displayed_text(
					self.data_vec.get_statistics()
				)

			
			if token == application_process.ComProtocol.nodes_list:
				self.data_vec.set_node_list(self.adapt_proc_queue.get())
				#print(self.data_vec.get_node_list())
				self.left_column_tabs[LeftColumnTabConst.node_list].update_displayed_text(
					self.data_vec.get_node_list()
				)
			
			
			if token == application_process.ComProtocol.tree:
				self.data_vec.set_tree(self.adapt_proc_queue.get())
				self.right_column_tabs[RightColumnTabConst.tree].update_displayed_text(
					self.data_vec.get_tree()
				)
			
			
			if token ==  application_process.ComProtocol.mis_games_list:
				self.data_vec.set_mis_game_list(self.adapt_proc_queue.get())
				#print(self.data_vec.get_mis_game_list())
				self.left_column_tabs[LeftColumnTabConst.mis_games].update_displayed_text(
					self.data_vec.get_mis_game_list()
				)
			
			
			if token == application_process.ComProtocol.num_unique_mgs:
				self.data_vec.set_num_unique_mgs(self.adapt_proc_queue.get())
				#print("self.data_vec.get_num_uniue_mgs() = " + str(self.data_vec.get_num_uniue_mgs()))
			
			
			if token == application_process.ComProtocol.uniq_mg_files:
				
				self.data_vec.set_uniq_mg_files(self.adapt_proc_queue.get())
				#print(self.data_vec.get_uniq_mg_files())
			
			
		
	def get_current_progress(self):
		#print("get_current_progress")
		assert self.adapt_proc_running == True
		
		## Listen the queue
		progress = self.adapt_proc_queue.get()
		if progress != application_process.ComProtocol.adapt_proc_ended:
			#assert progress.isdigit()
			return int(progress)
		else:
			return progress
	


########################
# Wizard Dialog Window #
########################

class WizardDialogWindow(Gtk.Dialog):
	
	def __init__(self, parent):
		
		## Initialization of the parent class
		super().__init__(title="Initialization Wizard", transient_for=parent, flags=0)
		self.set_modal(True) ## Freezing main window.
		
		## Seting a default width and height
		self.set_default_size(const_dialog_window_width, const_dialog_window_height)
		
		## Customize content area
		box = self.get_content_area()
		box.set_spacing(10)
		
		## Display Message
		initial_message = Gtk.Label()
		initial_message.set_markup("<big>Where would you like to begin?</big>")
		box.add(initial_message)
		
		explain_message = Gtk.Label()
		explain_message.set_markup(
			"Select a way to initialize a root Misinformation Game of the Adaptation Procedure."
			"\n\nSelect <b>File</b> to open an existing .mg file."
			"\nAlternatively, select <b>Random</b> to create a root randomly."
		)
		explain_message.set_line_wrap(True)
		explain_message.set_justify(Gtk.Justification.FILL)
		explain_message.set_max_width_chars(32)
		box.add(explain_message)
		
		## Add Buttons
		self.add_button("File", const_init_file)
		self.add_button("Random", const_init_random)
		
		
		## Display all
		self.show_all()



##########################
# Initialize Random Form #
##########################


class InitRandomForm(Gtk.Dialog):
	
	def __init__(self, parent):
		## Initialization of the parent class
		super().__init__(title="Set Random Parameters", transient_for=parent, flags=0)
		self.set_modal(True)  ## Freezing main window.
		
		## set default size
		self.set_default_size(const_random_width, const_random_height)
		
		## Customize content area
		box = self.get_content_area()
		box.set_spacing(20)
		box.set_border_width(20)
		
		## add vbox
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		box.add(vbox)

		## add hbox
		# hbox, num players
		hbox_num_players = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		hbox_num_players.set_hexpand(True)
		num_player_label = Gtk.Label("<b>Number of Players</b>",use_markup=True)
		num_player_label.set_tooltip_text("Specify the number of players. It is recommended to be <= 3 players.")
		hbox_num_players.add(num_player_label)
		self.num_player_entry = Gtk.Entry()
		self.num_player_entry.set_tooltip_text("Specify the number of players. It is recommended to be <= 3 players.")
		hbox_num_players.add(self.num_player_entry)
		vbox.add(hbox_num_players)
		
		# hbox strategies
		# strategies header
		hbox_strtategies_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		hbox_strtategies_1.set_hexpand(True)
		strategies_label = Gtk.Label("<b>Strategies for each player</b>",use_markup=True)
		strategies_label.set_tooltip_text(
			"Specify the number of strategies for each player. "
			"It is recommended each player to have <= 4 strategies. "
			"Fill only the first n boxes, where n is the number of players.")
		hbox_strtategies_1.add(strategies_label)
		vbox.add(hbox_strtategies_1)
		
		# strategies entries
		hbox_strtategies_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		hbox_strtategies_2.set_hexpand(True)
		vbox.add(hbox_strtategies_2)
		
		# player 1
		pl1_strat_label = Gtk.Label("Pl. 1")
		pl1_strat_label.set_tooltip_text("Number of strategies for player 1.")
		self.pl1_strat_entry = Gtk.Entry()
		self.pl1_strat_entry.set_width_chars(1)
		self.pl1_strat_entry.set_tooltip_text("Number of strategies for player 1.")
		hbox_strtategies_2.add(pl1_strat_label)
		hbox_strtategies_2.add(self.pl1_strat_entry)
		
		# player 2
		pl2_strat_label = Gtk.Label("Pl. 2")
		pl2_strat_label.set_tooltip_text("Number of strategies for player 2.")
		self.pl2_strat_entry = Gtk.Entry()
		self.pl2_strat_entry.set_width_chars(1)
		self.pl2_strat_entry.set_tooltip_text("Number of strategies for player 2.")
		hbox_strtategies_2.add(pl2_strat_label)
		hbox_strtategies_2.add(self.pl2_strat_entry)
		
		# player 3
		pl3_strat_label = Gtk.Label("Pl. 3")
		pl3_strat_label.set_tooltip_text("Number of strategies for player 3.")
		self.pl3_strat_entry = Gtk.Entry()
		self.pl3_strat_entry.set_width_chars(1)
		self.pl3_strat_entry.set_tooltip_text("Number of strategies for player 3.")
		hbox_strtategies_2.add(pl3_strat_label)
		hbox_strtategies_2.add(self.pl3_strat_entry)
		
		# player 4
		pl4_strat_label = Gtk.Label("Pl. 4")
		pl4_strat_label.set_tooltip_text("Number of strategies for player 4.")
		self.pl4_strat_entry = Gtk.Entry()
		self.pl4_strat_entry.set_width_chars(1)
		self.pl4_strat_entry.set_tooltip_text("Number of strategies for player 4.")
		hbox_strtategies_2.add(pl4_strat_label)
		hbox_strtategies_2.add(self.pl4_strat_entry)
		
		# hbox max utility
		hbox_max_util = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		hbox_max_util.set_hexpand(True)
		max_util_label = Gtk.Label("<b>Maximum Utility</b>", use_markup=True)
		max_util_label.set_tooltip_text(
			"Specify the maximum utility for each player."
			"If u the maximum utility, the players will have"
			"randomly chosen utilities in {0, 1, 2, ..., u}."
		)
		hbox_max_util.add(max_util_label)
		self.max_util_entry = Gtk.Entry()
		self.max_util_entry.set_text("10")
		self.max_util_entry.set_tooltip_text(
			"Specify the maximum utility for each player."
			"If u the maximum utility, the players will have"
			"randomly chosen utilities in {0, 1, 2, ..., u}."
		)
		hbox_max_util.add(self.max_util_entry)
		vbox.add(hbox_max_util)
		
		# seed box
		hbox_seed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		hbox_seed.set_hexpand(True)
		seed_label = Gtk.Label("<b>Seed</b>", use_markup=True)
		seed_label.set_tooltip_text(
			"Set the random number generator seed."
			"If left blank, seed = 0"
		)
		hbox_seed.add(seed_label)
		self.seed_entry = Gtk.Entry()
		self.seed_entry.set_text("0")
		self.seed_entry.set_tooltip_text(
			"Set the random number generator seed."
			"If left blank, seed = 0"
		)
		hbox_seed.add(self.seed_entry)
		vbox.add(hbox_seed)
		
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		
		## Current Error Message (if any)
		self.current_error_message = None
		
		## Display all
		self.show_all()
	
	#############
	# Accessors #
	#############
	
	def get_seed(self):
		return int(self.seed_entry.get_text())

		
	def get_num_players(self):
		return int(self.num_player_entry.get_text())
	
	def get_max_utility(self):
		return int(self.max_util_entry.get_text())
	
	def get_strategies(self):
		strategies = []
		strategies.append(int(self.pl1_strat_entry.get_text()))
		strategies.append(int(self.pl2_strat_entry.get_text()))
		if self.get_num_players() >= 3:
			strategies.append(int(self.pl3_strat_entry.get_text()))
		if self.get_num_players() >= 4:
			strategies.append(int(self.pl4_strat_entry.get_text()))
		
		return strategies
	
	
	##########
	# Checks #
	##########
	
	def check_num_players(self):
		num_players = self.num_player_entry.get_text()
		if not num_players.isdigit():
			self.current_error_message = "Number of player should be a number!"
			return False
		
		num_players = int(num_players)
		if not (2 <= num_players and num_players <= 4):
			self.current_error_message = "Number of player must be between 2 and 4!"
			return False
		
		return True
	
	def check_max_utilities(self):
		max_utility = self.max_util_entry.get_text()
		if not max_utility.isdigit():
			self.current_error_message = "Maximum utility should be a number!"
			return False
		
		max_utility = int(max_utility)
		if not max_utility > 0:
			self.current_error_message = "Maximum utility must be > 0!"
			return False
		
		return True
	
	def check_seed(self):
		seed = self.seed_entry.get_text()
		if not seed.isdigit():
			self.current_error_message = "Random number generator's seed should be a number!"
			return False
		
		seed = int(seed)
		if not seed >= 0:
			self.current_error_message = "Random number generator's seed must be > 0!"
			return False
		
		return True
	
	# A note regarding the correctness of this method:
	# -------------------------------------------------------------
	#   check_strategies() must be called *after* a successful
	#   check of check_num_players(). This is because we should
	#   know the correct number of players to check the strategies
	#   entries.
	def check_strategies(self):
		assert self.check_num_players()
		
		num_players = self.get_num_players()
		
		## Check if digits
		pl1_strat = self.pl1_strat_entry.get_text()
		if not pl1_strat.isdigit():
			self.current_error_message = "Please, give a number of strategies for player 1!"
			return False
		
		pl2_strat = self.pl2_strat_entry.get_text()
		if not pl2_strat.isdigit():
			self.current_error_message = "Please, give a number of strategies for player 2!"
			return False
		
		pl3_strat = self.pl3_strat_entry.get_text()
		if num_players >= 3 and not pl3_strat.isdigit():
			self.current_error_message = "Please, give a number of strategies for player 3!"
			return False
		
		pl4_strat = self.pl4_strat_entry.get_text()
		if num_players >= 4 and not pl4_strat.isdigit():
			self.current_error_message = "Please, give a number of strategies for player 4!"
			return False
		
		## Check if in the correct range
		pl1_strat = int(pl1_strat)
		if not pl1_strat >= 2 or pl1_strat > 9:
			self.current_error_message = "Number of strategies for player 1, must be between 2 and 9!"
			return False
		
		pl2_strat = int(pl1_strat)
		if not pl2_strat >= 2 or pl2_strat > 9:
			self.current_error_message = "Number of strategies for player 2, must be between 2 and 9!"
			return False
		
		# for 2 players stop here
		if num_players <= 2: return True
		
		pl3_strat = int(pl1_strat)
		if not pl3_strat >= 2 or pl3_strat > 9:
			self.current_error_message = "Number of strategies for player 3, must be between 2 and 9!"
			return False
		
		# for 3 players stop here
		if num_players <= 3: return True
		pl4_strat = int(pl1_strat)
		if not pl4_strat >= 2 or pl4_strat > 9:
			self.current_error_message = "Number of strategies for player 4, must be between 2 and 9!"
			return False
		
		
		return True
	
	
	def check_entries(self):
		
		return  self.check_num_players()     and\
				self.check_seed()            and\
				self.check_max_utilities()   and\
				self.check_strategies()
	
	def get_error_message(self):
		return self.current_error_message
	
	def get_parameters(self):
		params =[
			self.get_num_players(),
			self.get_strategies(),
			self.get_max_utility(),
			self.get_seed()
		]
		
		return params


################
# Progress Bar #
################

class ProgressBarWindow(Gtk.Dialog):

	def __init__(self, parent, total_mgs):
		
		## Progress Parameters
		self.computed_mgs   = 0
		self.total_mgs      = total_mgs
		
		## Initialization of the parent class
		self.parent = parent
		super().__init__(title="Computing the Adaptation Procedure",transient_for=parent,flags=0)
		self.set_modal(True)  ## Freezing main window.
		
		## set default size
		self.set_default_size(const_dialog_window_width, const_dialog_window_height)
		
		## Customize content area
		box = self.get_content_area()
		box.set_spacing(20)
		box.set_border_width(20)
		
		## add vbox
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		box.add(vbox)
		
		## conforting message
		conforting_label = Gtk.Label("This might take a while..")
		vbox.add(conforting_label)
		
		## add the progress bar
		self.progress_bar = Gtk.ProgressBar()
		vbox.add(self.progress_bar)
		
		## add some text
		self.progress_bar_label = Gtk.Label()
		vbox.add(self.progress_bar_label)
		self.update_label()
		
		## add button
		#self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		self.cancel_button = Gtk.Button("Cancel")
		self.cancel_button.connect("clicked", self.do_you_wanna_quit)
		vbox.add(self.cancel_button)
		
		## triger "do you wanna quit" when hitting close button
		self.connect("destroy", self.terminate_adapt_proc)
		
	#############
	# Accessors #
	#############
	
	#def is_active(self):
	#	return self.progress_active
	
	def update_label(self):
		self.progress_bar_label.set_text(
			"Computed " + str(self.computed_mgs) + " of " + str(self.total_mgs) + "."
		)
		#while Gtk.events_pending(): Gtk.main_iteration().
	
	def update_progress(self, computed_mgs):
		assert computed_mgs >= 0
		assert computed_mgs >=  self.computed_mgs
		
		self.computed_mgs = computed_mgs
		self.progress_bar.set_fraction(self.computed_mgs / self.total_mgs)
		self.update_label()
		
		# Some Gtk alchemies
		while Gtk.events_pending(): Gtk.main_iteration()
		
		
	
	def do_you_wanna_quit(self, widget):
		question = Gtk.MessageDialog(
			transient_for=self,
			flags=0,
			message_type=Gtk.MessageType.QUESTION,
			buttons=Gtk.ButtonsType.YES_NO,
			text="Do you really want to quit?"
		)
		
		question.format_secondary_text(
			"Do you really want to quit? All the progress will be lost."
		)
		
		quest_response = question.run()
		if quest_response == Gtk.ResponseType.YES:
			self.destroy()
			question.destroy()
			self.terminate_adapt_proc()
			
		question.destroy()
	
	def terminate_adapt_proc(self, widget=None):
		self.parent.destroy_adapt_proc()
		

############
# Settings #
############

class SettingsWindow(Gtk.Dialog):
	
	def __init__(self, parent):
		## Initialization of the parent class
		super().__init__(title="Settings", transient_for=parent, flags=0)
		self.set_modal(True)  ## Freezing main window.
		
		## set default size
		self.set_default_size(const_random_width, const_random_height)
		
		## add buttons
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		
		## Customize content area
		box = self.get_content_area()
		box.set_spacing(20)
		box.set_border_width(20)
		
		
		## add vbox
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
		hbox.set_hexpand(True)
		box.add(hbox)
		
		## add left column
		self.left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		self.left_column.set_vexpand(True)
		hbox.add(self.left_column)
		
		## add right column
		self.right_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		self.right_column.set_vexpand(True)
		hbox.add(self.right_column)
		
		
		#########################
		# Configure left column #
		#########################
		
		# Nash Equilibria Method
		ne_label = Gtk.Label("<b>Nash Equilibria Method</b>", use_markup=True)
		ne_label_box = Gtk.HBox()
		ne_label_box.set_border_width(7)
		ne_label_box.set_tooltip_markup(
			"Choose one method to compute the Nash Equilibria for a Normal Form Game. "
			"4 methods of the "
			"<a href=\"https://gambitproject.readthedocs.io/en/latest/tools.html#gambit-enumpoly-compute-equilibria-of-a-game-using-polynomial-systems-of-equations\">GAMBIT</a> "
			"package are supported. We recommend using the \"Support Enumeration\" method. Please , note that "
			"the \"Enumerate Prure\" method only considers pure Nash Equilibria. "
			"For more information see the GAMBIT's official documentation."
		)
		ne_label_box.add(ne_label)
		self.left_column.add(ne_label_box)
		
		
		# Number of Decimal Points
		decimal_label = Gtk.Label("<b>Decimal Points</b>", use_markup=True)
		decimal_box = Gtk.HBox()
		decimal_box.set_border_width(7)
		decimal_box.set_tooltip_markup(
			"Set the number of decimal points of the floating number computations. "
			"Note that if decimal point precision is too great, due to inevitable rounding errors, "
			"a Nash Equilibrium may appear multiple times. We recommend 8 points of precision."
		)
		decimal_box.add(decimal_label)
		self.left_column.add(decimal_box)
		
		# Fast Mode
		fast_mode_label = Gtk.Label("<b>Fast Mode</b>", use_markup=True)
		fast_mode_box = Gtk.HBox()
		fast_mode_box.set_border_width(7)
		fast_mode_box.set_tooltip_markup(
			"The fast mode uses the following fact, to reduce the number "
			"of the nodes of the adaptation tree, without losing SMEs. "
			"<i>A subtree of the adaptation procedure is characterized "
			"by the history of the position that lead to its root.</i> "
			"It is recommended to stay on. "
			"Note: Only in fast mose is allowed multithreading."
		)
		fast_mode_box.add(fast_mode_label)
		self.left_column.add(fast_mode_box)
		
		# Multithreading
		self.multithreading_label = Gtk.Label("<b>Number of Threads</b>", use_markup=True)
		multithreading_box = Gtk.HBox()
		multithreading_box.set_border_width(7)
		multithreading_box.set_tooltip_markup(
			"Configure the number of threads. Only available in Fast Mode. "
			"We recommend to use <i>at least</i> 4 threads."
		)
		multithreading_box.add(self.multithreading_label)
		self.left_column.add(multithreading_box)
		
		
		##########################
		# Configure Right Column #
		##########################
		
		# Nash Equilibria Method
		gui_ne_methods = Gtk.ListStore(str)
		ne_method_list =[
			gambit.method_names.pol,  	# Support Enumeration
			gambit.method_names.gnm,	# Generalized Newton Method
			gambit.method_names.xpe,	# Extreme Point Enumeration
			gambit.method_names.enp		# Enumerate Pure Nash Equilibria
		]
		for ne_method in ne_method_list: gui_ne_methods.append((ne_method,))
		
		self.gui_ne_methods_combobox = Gtk.ComboBox.new_with_model(gui_ne_methods)
		#self.gui_ne_methods_country_combo.connect("changed", self.on_country_combo_changed)
		renderer_text = Gtk.CellRendererText()
		self.gui_ne_methods_combobox.pack_start(renderer_text, True)
		self.gui_ne_methods_combobox.add_attribute(renderer_text, "text", 0)
		self.gui_ne_methods_combobox.set_active(0)
		self.gui_ne_methods_combobox.set_tooltip_markup(
			"Choose one method to compute the Nash Equilibria for a Normal Form Game. "
			"4 methods of the "
			"<a href=\"https://gambitproject.readthedocs.io/en/latest/tools.html#gambit-enumpoly-compute-equilibria-of-a-game-using-polynomial-systems-of-equations\">GAMBIT</a> "
			"package are supported. We recommend using the \"Support Enumeration\" method. Please , note that "
			"the \"Enumerate Pure\" method only considers pure Nash Equilibria. "
			"For more information see the GAMBIT's official documentation."
		)
		self.right_column.add(self.gui_ne_methods_combobox)
		
		# Decimal Points Method
		gui_decimal = Gtk.ListStore(int)
		for d in range(1, 17): gui_decimal.append((d,))
		
		self.gui_decimal_combobox = Gtk.ComboBox.new_with_model(gui_decimal)
		# self.gui_ne_methods_country_combo.connect("changed", self.on_country_combo_changed)
		renderer_text = Gtk.CellRendererText()
		self.gui_decimal_combobox.pack_start(renderer_text, True)
		self.gui_decimal_combobox.add_attribute(renderer_text, "text", 0)
		self.gui_decimal_combobox.set_active(7)
		self.gui_decimal_combobox.set_tooltip_markup(
			"Set the number of decimal points of the floating number computations. "
			"Note that if decimal point precision is too great, due to inevitable rounding errors, "
			"a Nash Equilibrium may appear multiple times. We recommend 8 points of precision."
		)
		self.right_column.add(self.gui_decimal_combobox)
		
		# Fast Mode
		self.fast_mode_switch = Gtk.Switch()
		self.fast_mode_switch.set_tooltip_markup(
			"The fast mode uses the following fact, to reduce the number "
			"of the nodes of the adaptation tree, without losing SMEs. "
			"<i>A subtree of the adaptation procedure is characterized "
			"by the history of the position that lead to its root.</i> "
			"It is recommended to stay on. "
			"Note: Only in fast mose is allowed multithreading."
		)
		self.fast_mode_switch.connect("notify::active", self.fast_mode_active)
		self.fast_mode_switch.set_active(True)
		self.right_column.add(self.fast_mode_switch)
		
		# Multithreading
		gui_multithread = Gtk.ListStore(int)
		for d in range(1, os.cpu_count()+1): gui_multithread.append((d,))
		
		self.gui_multithread_combobox = Gtk.ComboBox.new_with_model(gui_multithread)
		# self.gui_ne_methods_country_combo.connect("changed", self.on_country_combo_changed)
		renderer_text = Gtk.CellRendererText()
		self.gui_multithread_combobox.pack_start(renderer_text, True)
		self.gui_multithread_combobox.add_attribute(renderer_text, "text", 0)
		self.gui_multithread_combobox.set_active(min(3, os.cpu_count()))
		self.gui_multithread_combobox.set_tooltip_markup(
			"Configure the number of threads. Only available in Fast Mode. "
			"We recommend to use <i>at least</i> 4 threads."
		)
		self.right_column.add(self.gui_multithread_combobox)
		
		## Display all
		self.show_all()
	
	
	###########
	# Signals #
	###########
	
	def fast_mode_active(self, widget, gparam):
		if widget.get_active():
			self.multithreading_label.show()
			self.gui_multithread_combobox.show()
		else:
			self.multithreading_label.hide()
			self.gui_multithread_combobox.hide()
	
	
	#############
	# Accessors #
	#############

	def get_nash_equilibria_method(self):
		active_choice = self.gui_ne_methods_combobox.get_active_iter()
		if active_choice is not None:
			model = self.gui_ne_methods_combobox.get_model()
			ne_method = model[active_choice][0]
			
			# Support Enumeration
			if ne_method == gambit.method_names.pol:
				return application.NE_methods.pol
			
			# Generalized Gambit Method
			if ne_method == gambit.method_names.gnm:
				return application.NE_methods.gnm
			
			# Extreme Point Enumeration
			if ne_method == gambit.method_names.xpe:
				return application.NE_methods.enummixed
			
			# Enumerate Pure
			if ne_method == gambit.method_names.enp:
				return application.NE_methods.enp
	
	def get_decimal_points(self):
		active_choice = self.gui_decimal_combobox.get_active_iter()
		if active_choice is not None:
			model = self.gui_decimal_combobox.get_model()
			decimal_digits = int(model[active_choice][0])
			
			return decimal_digits
	
	def get_is_fast_mode(self):
		return self.fast_mode_switch.get_active()
	
	def get_num_threads(self):
		active_choice = self.gui_multithread_combobox.get_active_iter()
		if active_choice is not None:
			model = self.gui_multithread_combobox.get_model()
			num_threads = int(model[active_choice][0])
			
			return num_threads