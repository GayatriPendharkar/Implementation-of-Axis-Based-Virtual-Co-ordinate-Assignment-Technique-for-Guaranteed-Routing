from numpy import array
import matplotlib.pyplot as plt
import networkx as nx


'''FUNCTIONS FOR PATH CALCULATION'''

def dijkstra_path(G, source, cutoff = None, weight=1):
    (length, path) = nx.single_source_dijkstra(G, source, cutoff=cutoff, weight=weight)
    return path

def short_path(G, source, target, weight='weight'):
    (length, path) = nx.single_source_dijkstra(G, source, target=target,weight=weight)

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

    len_list = []
    W=int(raw_input('Enter the desired node ID of sink node: '))
    nodes = []
    max_len_paths = []
    wsn_nodes = []

    with open('19_nodes_edges.txt') as file:
        GnodeXY = array([[int(float(digit)) for digit in line.split()] for line in file])


    for i in range(len(GnodeXY)):
        for j in range(len(GnodeXY[i])):
            node = GnodeXY[i][j]
            if node not in nodes:
                nodes.append(node)
            else:
                pass

    '''CONSTRUCT A NETWORKX GRAPH'''

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(GnodeXY)

    X = Anchor_Selection(G,W)
    Y = Anchor_Selection(G,X)

    anchors = [X,Y]

    length = short_path(G,X,Y)[0]

    '''FIND PARALLEL OF LATITUDE'''

    parallelOfLatitude = short_path(G,X,Y)[1]

    Z = max(AnchorSelectionZs(G,W))
    anchors.append(Z)
    Zp = max(AnchorSelectionZs(G,Z))
    anchors.append(Zp)

    parallel_l = []
    for i in range(len(parallelOfLatitude)-1):
        try:
            a = parallelOfLatitude[i],parallelOfLatitude[i+1]
            if parallelOfLatitude[i] > parallelOfLatitude[i+1]:
                a = parallelOfLatitude[i+1],parallelOfLatitude[i]
        except:
            pass
        parallel_l.append(a)

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
            meridian_Zp = meridianSelection(G,value,W)
            meridians.append(meridian_Zp)
        except:
            pass

        parallelOfLatitude.append(value)

    meridian_paths = []

    for i in meridians:
        try:
            for j in range(len(i)):
                try:
                    links = i[j],i[j+1]
                    if i[j] > i[j+1]:
                        links = i[j+1],i[j]
                except:
                    pass
                j-=1
                meridian_paths.append(links)
        except:
            pass

    '''PLOTTING THE GRAPHS EQUIVALENT TO THE DATA'''

    edgeColor = []
    for edge in G.edges():
        if edge in parallel_l:
            c = "black"
            edgeColor.append(c)
        elif edge in meridian_paths:
            c = "red"
            edgeColor.append(c)
        else:
            c = "white"
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
        nodeSizes[i] = 1000
        nodeColors[i] = 'blue'

    for j in anchors:
        nodeSizes[j] = 2000
        nodeColors[j] = 'white'
        nodeLabels[j] = labels[name]
        name+=1


    meridian_nodes = [item for sublist in meridians for item in sublist]
    meridian_nodes = list(set(meridian_nodes))


    '''CALCULATING THE FIRST THREE VIRTUAL COORDINATES: LONGITUDE,LATITUDE AND RIPPLE'''

    Vcs = []*5

    filename = "VirtualCoordinates.txt"
    VC = open(filename,'wb')

    for node in nodes:
        VC.write('\n')
        if node in parallelOfLatitude:
            del Vcs[:]
            V0 = short_path(G,node,X)[0]
            V1 = 0
            V2= 0
            Vcs = [V0,V1,V1]
            VC.write('\n'+'#Virtual Coordinate for node '+str(node)+'\n')
            VC.write(','.join(str(x) for x in Vcs))

        elif node in meridian_nodes:
            VC.write('\n'+'#Virtual Coordinates for node '+str(node)+'\n')
            for subMeridians in meridians:
                if node in subMeridians:
                    del Vcs[:]
                    V0 = short_path(G,subMeridians[0],X)[0]
                    if Z in subMeridians:
                        Z_co_source = short_path(G,subMeridians[0],Z)[0]
                        Z_co_nnode = short_path(G,node,Z)[0]
                        V1 = Z_co_source-Z_co_nnode
                    elif Zp in subMeridians:
                        Zp_co_source = short_path(G,subMeridians[0],Zp)[0]
                        Zp_co_nnode = short_path(G,node,Zp)[0]
                        V1 = Zp_co_nnode-Zp_co_source
                    V2 = 0

                    Vcs = [V0,V1,V2]
                    VC.write(','.join(str(x) for x in Vcs)+'\n')
        else:
            VC.write('\n'+'Virtual Coordinates for non-axial node '+str(node)+'\n')
            Vcs = []
            neighbors = list(nx.all_neighbors(G,node))

            aneighbors = []
            mneighbors = []
            naneighbors = []

            for n in neighbors:
                if n in parallelOfLatitude:
                    aneighbors.append(n)
                elif n in meridian_nodes:
                    mneighbors.append(n)
                else:
                    naneighbors.append(n)

            if aneighbors:
                axn = max(aneighbors)
                V0 = short_path(G,axn,X)[0]
                Zc = short_path(G,node,Z)[0]
                Zpc =short_path(G,node,Zp)[0]

                if Zc > Zpc:
                    Z_c_neighbor = short_path(G,axn,Z)[0]
                    V1 = Z_c_neighbor-Zc
                else:
                    Z_c_neighbor = short_path(G,axn,Zp)[0]
                    V1 = Zc-Z_c_neighbor

                V2 = short_path(G,axn,node)[0]
                Vcs = [V0, V1, V2]
                VC.write(','.join(str(x) for x in Vcs)+'\n')

            if not Vcs:
                if mneighbors:
                    axn = max(mneighbors)
                    for subMeridians in meridians:
                        if axn in subMeridians:
                            del Vcs[:]
                            V0 = short_path(G,subMeridians[0],X)[0]
                            if Z in subMeridians:
                                Z_co_source = short_path(G,subMeridians[0],Z)[0]
                                Z_co_nnode = short_path(G,axn,Z)[0]
                                V1 = Z_co_source-Z_co_nnode
                            elif Zp in subMeridians:
                                Zp_co_source = short_path(G,subMeridians[0],Zp)[0]
                                Zp_co_nnode = short_path(G,axn,Zp)[0]
                                V1 = Zp_co_nnode-Zp_co_source
                            V2 = short_path(G,node,axn)[0]

                            Vcs = [V0,V1,V2]
                            VC.write(','.join(str(x) for x in Vcs)+'\n')


    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos=pos, node_list=nodes, node_size=nodeSizes.values(), node_color=nodeColors.values(),edge_color=edgeColor,width=2,labels=nodeLabels)
    #nx.relabel_nodes(G,nodeLabels)
    plt.title('ESTABLISHMENT OF AXES FOR SAMPLE 19 NODE NETWORK',fontsize=28)
    limits=plt.axis('off')
    plt.show()




