from graph import graph
from dijkstra import *

def create_graph():
  return graph()

def add_node(gr, name):
  gr.add_node(name)

def add_edge(gr, one, two, wt):
  gr.add_edge((one, two), wt)


#print("start")
#print("creation")
#graph = create_graph()
#print("node 1")
#add_node(graph, 'n1')
#print("node 2")
#add_node(graph, 'n2')
#print("edge")
#add_edge(graph, 'n1', 'n2')
#print("print")
#print(graph)

graph = create_graph()

add_node(graph, 'n1')
add_node(graph, 'n2')
add_node(graph, 'n3')
add_node(graph, 'n4')
add_node(graph, 'n5')

add_edge(graph, 'n1', 'n2', 1)
add_edge(graph, 'n1', 'n3', 15)
add_edge(graph, 'n1', 'n4', 18)
add_edge(graph, 'n1', 'n5', 2)
add_edge(graph, 'n2', 'n3', 5)
add_edge(graph, 'n2', 'n5', 1)
add_edge(graph, 'n3', 'n4', 2)
add_edge(graph, 'n4', 'n5', 3)

#print(graph.edge_weight(('n2', 'n3')))
print(graph)
print('ok')
#add_node(graph, 'n1')

print(graph.has_edge(('n2', 'n1')))
#dijk = shortest_path(graph, 'n1')
#print(dijk)
#print(" ")
#dict = get_next_step(graph, 'n1')
#print(dict)


