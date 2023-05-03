import logging

def get_most_constrained(c, assigned, unspillable):
	"""
	Finds the most constrained node in the graph.
	Prioritizes unspillable variables.
	"""
	count = -1
	most_constrained = None
	
	for node in c:
		if not assigned[node]:
			if len(c[node]) > count:
				most_constrained = node
				count = len(c[node])
			elif len(c[node]) == count and node in unspillable:
				most_constrained = node
				count = len(c[node])
			
	return most_constrained

def all_assigned(a):
	"""
	A function to check if all variables have been assigned.
	"""
	for node in a:
		if not a[node]:
			return False
		
	return True

def color_graph(graph, unspillable):
	"""
	Uses the graph coloring algorithm to color the graph nodes, returns a dict [var -> assignment].
	"""
	logging.getLogger(__name__)
	
	current_stack = 4
	priorities = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
	
	assigned = {}
	# for each node store a list of illegal colors
	illegal_colors = {}
	
	# calculate initial illegal colors
	for node in graph:
		# only do this for variables
		if node not in priorities:
			illegal_colors[node] = []
			assigned[node] = None
			
			for edge in graph[node]:
				if edge in priorities:
					illegal_colors[node].append(priorities.index(edge))
	logging.info(f"Initial Saturation")	
	logging.info(f"{illegal_colors}\n")
	
	# While not all variables have register/stack assignments
	while not all_assigned(assigned):
		
		# Get the most constrained node
		most_constrained = get_most_constrained(illegal_colors, assigned, unspillable)
		logging.info(f"Most constrained node: {most_constrained}")
		
		# Find the highest available priority for this node and assign it.
		# Then propagate the new illegal priority to connected nodes.
		reached_end = True
		for i, reg in enumerate(priorities):
			if i not in illegal_colors[most_constrained]:
				assigned[most_constrained] = reg
				illegal_colors[most_constrained].append(i)

				for edge in graph[most_constrained]:
					if edge not in priorities:
						illegal_colors[edge].append(i)
				
				reached_end = False
				break
				
		# If we couldn't assign to a reg, assign to stack, add new priority.
		# Then propagate the new illegal priority to connected nodes.
		if reached_end:
			priorities.append(f"-{current_stack}(%ebp)")
			current_stack += 4
			
			assigned[most_constrained] = priorities[-1]
			illegal_colors[most_constrained].append(len(priorities) - 1)

			for edge in graph[most_constrained]:
				if edge not in priorities:
					illegal_colors[edge].append(len(priorities) - 1)
		logging.info(f"{illegal_colors}\n")
		
	logging.info(f"Final Assignments\n{assigned}")
	return assigned
