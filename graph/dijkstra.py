from graph import graph


def shortest_path(graph, sourceNode, dist = {}, previous = {}):
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
    
#    dist = {}
#    previous = {}
    
    for v in vertices:
        dist[v] = float('inf')
        previous[v] = None ;
  
    dist[sourceNode] = 0

    while vertices: 
        temp_dist = float('inf')
        u = None
        for node in vertices:
            if dist[node] <= temp_dist:
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

def get_next_step(graph, sourceNode):
    ''' Returns a dictionnary with a key for each vertex in the graph (except sourceNode)
        and as value the next step form sourceNode in order to reach the key 
        by the smallest path.
    '''
    #print(graph)
    dist = {}
    previous = {}
    shortest_path(graph, sourceNode, dist, previous)
    #print('dist', dist)
    #print('prev', previous)
    
    result = {}
    vertices = graph.nodes()
    vertices.remove(sourceNode)
    to_pop = []
    for key in dist:
        if not previous[key]:
            to_pop += [key]
    for key in to_pop:
        dist.pop(key)
        
    #print('dist2', dist)
    #dist.pop(sourceNode)

    while dist:
        value = 0
        nextkey = None
        for key in dist:
            if dist[key] > value:
                value = dist[key]
                nextkey = key
            
        treated = []

        while previous[nextkey] != sourceNode:
            treated += [nextkey]
            nextkey = previous[nextkey]
        
        for node in treated:
            result[node] = nextkey
            if node in dist:
                dist.pop(node)
        result[nextkey] = nextkey
        #print(dist)
        #print(nextkey)
        if nextkey in dist:
            dist.pop(nextkey)
        
    return result
            
    
