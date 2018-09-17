import scipy.spatial.distance as d
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

'''FUNCTIONS FOR PATH CALCULATION'''

def dijkstra_path(G, source):

    (length, path) = nx.single_source_dijkstra(G, source)
    return path

def short_path(G, source, target):

    (length, path) = nx.single_source_dijkstra(G, source)
    try:
        a = path[target]
        return len(a)-1,a
    except KeyError:
        raise nx.NetworkXNoPath(
            "node %s not reachable from %s" % (source, target))


'''FUNCTION FOR SELECTION OF ANCHORS X,Y'''

def Anchor_Selection(G,node):

    paths = dijkstra_path(G,node).values()
    for i in paths:
        len_path = len(i)
        len_list.append(len_path)
        min_path_length = max(len_list)
    for j in paths:
        if len(j) >= min_path_length:
            max_len_paths.append(j)

    poss_anchors = []
    for i in range(len(max_len_paths)):
        for j in range(len(max_len_paths[i])):
            anchor = max_len_paths[-1][-1]
            poss_anchors.append(anchor)
    return max(poss_anchors)


'''FUNCTION FOR SELECTION OF ANCHORS Z AND ZP'''

def AnchorSelectionZs(G, node):

    paths = dijkstra_path(G,node).values()

    all_poss_anchors = []
    for path in paths:
        poss_anchor = path[-1]
        all_poss_anchors.append(poss_anchor)

    poss_anchors = []

    for anchorsZ in all_poss_anchors:
        Xcoor = short_path(G,anchorsZ,X)[0]
        Ycoor = short_path(G,anchorsZ,Y)[0]
        if (anchorsZ not in anchors and anchorsZ not in parallelOfLatitude):
            if Xcoor == Ycoor + 1 or Xcoor == Ycoor - 1:
                poss_anchors.append(anchorsZ)
            else:
                pass
        else:
            pass

    return poss_anchors


'''FUNCTION FOR MERIDIANS SELECTION'''

def distBetweenNodes(nodeA,nodeB):
    AcX = short_path(G,nodeA,X)[0]
    AcY = short_path(G,nodeA,Y)[0]
    BcX = short_path(G,nodeB,X)[0]
    BcY = short_path(G,nodeB,Y)[0]

    return abs(AcX-BcX) + abs(AcY-BcY)

def meridianSelection(G,n,Zc):

    dist_from_node = {}

    nextNode = n
    predeccessors = [nextNode]

    while(nextNode != Zc):

        neighbor_nodes = list(nx.all_neighbors(G,nextNode))

        Z_co_node = short_path(G,nextNode,Zc)[0]

        for node in neighbor_nodes:
            if node not in parallelOfLatitude:
                if node not in predeccessors:
                    Zcoor = short_path(G,node,Zc)[0]
                    if Zcoor <= Z_co_node-1:
                        dist_from_node[node] = distBetweenNodes(n,node)

        if len(dist_from_node)>1:
            for key, val in dist_from_node.items():
                if val == min(dist_from_node.values()):
                    nextNode = key
        else:
            nextNode = dist_from_node.keys()[0]
        dist_from_node.clear()
        predeccessors.append(nextNode)

    return predeccessors


if __name__=="__main__":

    W=int(raw_input('Enter the desired node ID of sink node: '))
    r = 1.5

    len_list = []
    nodes = []
    max_len_paths = []
    wsn_nodes = []
    edges = []
    nodes = []

    with open('buildingnetwork.txt') as file:
        GnodeXY = np.array([[int(float(digit)) for digit in line.split()] for line in file])

    a = GnodeXY.tolist()
    pos = (())
    for i in range(len(a)):
        tup = tuple(a[i])
        pos = pos + (tup,)
    list_nodes = list(pos)

    for i in range(1,len(list_nodes)+1):
        nodeid = i
        nodes.append(nodeid)

    dist_matrix = d.pdist(GnodeXY)
    sqform_matrix = d.squareform(dist_matrix)

    for i in range(len(sqform_matrix)):
        for j in range(len(sqform_matrix)):
            if sqform_matrix[i][j] >0 and sqform_matrix[i][j]<= r:
                edge = nodes[i],nodes[j]
                edges.append(edge)

    '''CONSTRUCT A NETWORKX GRAPH'''

    G = nx.Graph()

    for i in nodes:
        G.add_node(i,pos=list_nodes[i-1])

    G.add_edges_from(edges)

    X = Anchor_Selection(G,W)
    Y = Anchor_Selection(G,X)
    anchors = [X,Y]

    length = short_path(G,X,Y)[0]

    '''FIND PARALLEL OF LATITUDE'''

    parallelOfLatitude = short_path(G,X,Y)[1]

    Z = min(AnchorSelectionZs(G,W))
    anchors.append(Z)

    Zp = max(AnchorSelectionZs(G,Z))
    anchors.append(Zp)


    ''' FIND THE MERIDIAN AXES'''

    meridians = []

    for i in parallelOfLatitude:

        value = parallelOfLatitude[0]
        parallelOfLatitude.pop(0)
        pl_elem = parallelOfLatitude

        try:
            meridian_Z = meridianSelection(G,value,Z)
            meridians.append(meridian_Z)
        except:
            pass
        try:
            meridian_Zp = meridianSelection(G,value,Zp)
            meridians.append(meridian_Zp)
        except:
            pass

        parallelOfLatitude.append(value)

    parallel_l_paths = []

    for i in range(len(parallelOfLatitude)-1):
        try:
            a = parallelOfLatitude[i],parallelOfLatitude[i+1]
            if parallelOfLatitude[i] > parallelOfLatitude[i+1]:
                a = parallelOfLatitude[i+1],parallelOfLatitude[i]
        except:
            pass
        parallel_l_paths.append(a)

    meridian_paths = []

    for i in meridians:
        if i:
            try:
                for j in range(len(i)):
                    links = i[j],i[j+1]
                    if i[j] > i[j+1]:
                        links = i[j+1],i[j]
                    j=j-1
                    meridian_paths.append(links)
            except:
                pass


    '''PLOTTING THE GRAPHS EQUIVALENT TO THE DATA'''

    edgeColor = []
    for edge in G.edges():
        if edge in parallel_l_paths:
            c = "black"
            edgeColor.append(c)
        elif edge in meridian_paths:
            c = "red"
            edgeColor.append(c)
        else:
            c = "0.75"
            edgeColor.append(c)

    for node in nodes:
        if node not in anchors:
            wsn_nodes.append(node)

    nodeSizes = {}
    nodeColors = {}
    nodeLabels = {}
    labels = ['X','Y','Z','Zp']
    name =0
    for i in wsn_nodes:
        nodeSizes[i] = 10
        nodeColors[i] = 'blue'

    for j in anchors:
        nodeSizes[j] = 500
        nodeColors[j] = 'white'
        nodeLabels[j] = labels[name]
        name+=1

    posi=nx.get_node_attributes(G,'pos')
    nx.draw_networkx(G, pos=posi, node_list=nodes, node_size=nodeSizes.values(), node_color=nodeColors.values(),edge_color=edgeColor,width=2,labels=nodeLabels)
    limits=plt.axis('off')
    plt.title('ESTABLISHMENT OF AXES FOR NODES PLACED IN A 30X30 GRID',fontsize=28)
    plt.text(14,33,'ODD NETWORK',fontsize=22)
    plt.text(7,-3,'Parallel of Latitude -- BLACK     Meridians -- RED',fontsize=20)
    plt.show()