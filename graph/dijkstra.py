from graph import graph

def shortest_path(graph, sourceNode):
    """
    Return the shortest path distance between sourceNode and all other nodes
    using Dijkstra's algorithm.  See
    http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm.  
   
    @attention All weights must be nonnegative.

    @type  graph: graph
    @param graph: Graph.

    @type  sourceNode: node
    @param sourceNode: Node from which to start the search.

    @rtype  tuple
    @return A tuple containing two dictionaries, each keyed by
        targetNodes.  The first dictionary provides the shortest distance
        from the sourceNode to the targetNode.  The second dictionary
        provides the previous node in the shortest path traversal.
        Inaccessible targetNodes do not appear in either dictionary.
    """
    vertices = graph.nodes()
    
    # dist and previous are dictionnaries where the key is the node and 
    # the value is respectively the distance and the previous node.
    
    dist = {}
    previous = {}
    
    for v in vertices:
        dist[v] = float('inf')
        previous[v] = None ;
  
    dist[sourceNode] = 0

    while vertices: 
        temp_dist = float('inf')
        u = None
        for node in vertices:
            if dist[node] < temp_dist:
                temp_dist = dist[node]
                u = node
        
        vertices.remove(u)        
        
        if dist[u] == float('inf'):
            break
        
        neighbours = graph.neighbors(u)
        for v in neighbours:
                       
            alt = dist[u] + graph.edge_weight((u, v))
            if alt < dist[v]:
                dist[v] = alt ;
                previous[v] = u ;
    
    return dist;
    
