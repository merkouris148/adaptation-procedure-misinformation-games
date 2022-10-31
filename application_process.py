############
# Librares #
############

## Custom Libraries
import application


## Python Libraries
import threading
import time


#############
# Constants #
#############


class ComProtocol:
	adapt_proc_ended	= "# Adapt. Proc. End"
	root            	= "# Root"
	smes				= "# SMEs"
	statistics      	= "# Statistics"
	nodes_list      	= "# Nodes"
	tree            	= "# Tree"
	mis_games_list  	= "# Misinformation Games"
	num_unique_mgs  	= "# Number of Unique MGs"
	uniq_mg_files		= "# Unique MG Files"
	eof             	= "# EOF"

#com_protocol = ComProtocol()



#############
# Functions #
#############


def processing_thread(app, queue):
	## Exacute the Adaptation Procedure
	app.exec()
	
	## Inform the GUI that Adapt Proc has concluded
	## (the if-statement is just a precaution)
	if app.get_is_adaptation_concluded():
		queue.put(ComProtocol.adapt_proc_ended)
		#print("put adapt proc ended")
	
	## Return Results
	
	# Put Root
	queue.put(ComProtocol.root)
	queue.put(app.get_root())
	
	# Put SMEs
	queue.put(ComProtocol.smes)
	queue.put(app.get_SMEs())
	
	# Put statistcs
	queue.put(ComProtocol.statistics)
	queue.put(app.export_stats())
	
	# Put node list
	queue.put(ComProtocol.nodes_list)
	queue.put(app.get_nodes())
	
	# Put Tree
	queue.put(ComProtocol.tree)
	queue.put(app.get_tree())
	
	# Put MG list
	queue.put(ComProtocol.mis_games_list)
	queue.put(app.get_mg_pool())
	
	# Put unique MG files
	queue.put(ComProtocol.num_unique_mgs)
	queue.put(app.get_num_uniq_mgs())
	
	queue.put(ComProtocol.uniq_mg_files)
	queue.put(app.get_uniq_mg_files())
	
	# EOF
	queue.put(ComProtocol.eof)


def messages_thread(app, queue):
	queue.put(app.get_total_mgs())
	
	while not app.get_is_adaptation_concluded():
		time.sleep(0.1)
		queue.put(app.get_progress_computed_mgs())



def process_app(args, queue):
	# Create a single app instance
	app = application.Application(args)
	
	# Create two parallel threads
	msg_thread  = threading.Thread(target=messages_thread, args=(app, queue,))
	work_thread = threading.Thread(target=processing_thread, args=(app, queue,))
	
	## statring threads
	work_thread.start()
	msg_thread.start()
	
	
	## join threads
	work_thread.join()
	msg_thread.join()